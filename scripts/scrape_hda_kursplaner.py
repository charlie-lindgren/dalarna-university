#!/usr/bin/env python3
"""
Scraper för ALLA kursplaner vid Högskolan Dalarna från du.se → Obsidian vault.

Upptäcker alla ämnen vid samtliga fyra institutioner (IIT, IHV, IKS, ISLL),
hämtar kurslistor per ämne via söksidans API, och skrapar varje kursplan
(svenska + engelska). Genererar Obsidian markdown-filer organiserade
per institution och ämne med MOC-filer.

Användning:
    python3 scrape_hda_kursplaner.py                    # discovery + dry-run
    python3 scrape_hda_kursplaner.py --apply             # discovery + skriv
    python3 scrape_hda_kursplaner.py --institution IIT   # bara IIT
    python3 scrape_hda_kursplaner.py --subject DTA       # bara Datateknik
    python3 scrape_hda_kursplaner.py --list-institutions # visa institutioner
    python3 scrape_hda_kursplaner.py --list-subjects     # visa ämnen, avsluta
    python3 scrape_hda_kursplaner.py --list-courses      # visa alla kurser
    python3 scrape_hda_kursplaner.py --skip-existing      # hoppa över redan skrapade
    python3 scrape_hda_kursplaner.py GIK29B GDT34Z       # enskilda kurser
"""

import argparse
import hashlib
import math
import os
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

VAULT = Path(__file__).resolve().parent.parent / "vault-dalarna-university"
INST_DIR_NAME = {"IIT": "01 IIT", "IHV": "02 IHV", "IKS": "03 IKS", "ISLL": "04 ISLL"}


def institution_dir(inst_code: str) -> Path:
    return VAULT / INST_DIR_NAME[inst_code]


def kursplaner_dir(inst_code: str) -> Path:
    return institution_dir(inst_code) / "Kursplaner"


def utbildningsplaner_dir(inst_code: str) -> Path:
    return institution_dir(inst_code) / "Utbildningsplaner"

# Institutioner vid Högskolan Dalarna
INSTITUTIONS = {
    "IIT": {
        "name": "Institutionen för information och teknik",
        "short": "IIT",
        "url": "https://www.du.se/sv/medarbetarwebb/organisation_styrning/organisation/institutioner/institutionen-for-information-och-teknik/",
    },
    "IHV": {
        "name": "Institutionen för hälsa och välfärd",
        "short": "IHV",
        "url": "https://www.du.se/sv/medarbetarwebb/organisation_styrning/organisation/institutioner/institutionen-for-halsa-och-valfard/",
    },
    "IKS": {
        "name": "Institutionen för kultur och samhälle",
        "short": "IKS",
        "url": "https://www.du.se/sv/medarbetarwebb/organisation_styrning/organisation/institutioner/institutionen-for-kultur-och-samhalle/",
    },
    "ISLL": {
        "name": "Institutionen för språk, litteratur och lärande",
        "short": "ISLL",
        "url": "https://www.du.se/sv/medarbetarwebb/organisation_styrning/organisation/institutioner/institutionen-for-sprak-litteratur-och-larande/",
    },
}

SEARCH_API = "https://www.du.se/search/Search/Search"
SV_URL = "https://www.du.se/sv/utbildning/kurser/kursplan/?code={code}"
EN_URL = "https://www.du.se/en/study-at-du/kurser/syllabus/?code={code}"

REQUEST_DELAY = 1.0  # sekunder mellan anrop

# Sektioner vi vill ha i filen, i ordning.
SECTION_MAP_SV = {
    "Lärandemål": ["Lärandemål", "Mål"],
    "Innehåll": ["Innehåll"],
    "Examinationsformer": ["Examinationsformer"],
    "Arbetsformer": ["Arbetsformer"],
    "Betyg": ["Betyg"],
    "Förkunskapskrav": ["Förkunskapskrav"],
    "Övrigt": ["Övrigt"],
    "Litteratur": ["Litteratur"],
}

SECTION_MAP_EN = {
    "Learning Outcomes": ["Learning Outcomes", "Objectives"],
    "Course Content": ["Course Content"],
    "Assessment": ["Assessment"],
    "Forms of Study": ["Forms of Study"],
    "Grades": ["Grades"],
    "Prerequisites": ["Prerequisites"],
    "Other": ["Other"],
    "Reading List": ["Reading List"],
}

SECTION_ORDER_SV = [
    "Lärandemål", "Innehåll", "Examinationsformer", "Arbetsformer",
    "Betyg", "Förkunskapskrav", "Övrigt", "Litteratur",
]

SECTION_ORDER_EN = [
    "Learning Outcomes", "Course Content", "Assessment", "Forms of Study",
    "Grades", "Prerequisites", "Other", "Reading List",
]

RESULTS_PER_PAGE = 20
CODE_PATTERN_RE = re.compile(r"^([A-ZÅÄÖ]{3})(\d{3})([A-Z]?)$")


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "HDa-kursplan-scraper/1.0 (intern översikt HDa)"
})


def fetch_page(url: str, params: dict | None = None) -> BeautifulSoup | None:
    try:
        resp = SESSION.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        print(f"  ⚠ Kunde inte hämta {url}: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Steg 1: Upptäck ämnen från institutionssidorna
# ---------------------------------------------------------------------------

def discover_all_subjects() -> dict[str, list[dict]]:
    """
    Skrapar alla institutionssidor och returnerar ämnen per institution.
    Returnerar: {inst_code: [subject_dicts]}
    """
    all_subjects = {}
    for inst_code, inst_info in INSTITUTIONS.items():
        print(f"  Hämtar ämnen från {inst_info['name']}...")
        subjects = discover_subjects_for_institution(inst_code, inst_info)
        all_subjects[inst_code] = subjects
        print(f"    Hittade {len(subjects)} ämnen")
        time.sleep(REQUEST_DELAY)
    return all_subjects


def discover_subjects_for_institution(inst_code: str, inst_info: dict) -> list[dict]:
    """
    Skrapar en institutions medarbetarsida och returnerar lista med ämnen.
    Varje ämne: {name, code, esu, huvudomrade, type, institution}

    Hanterar två HTML-mönster:
    1. Accordion-paneler med collapse-ID (IIT-mönstret) — har esu-ID
    2. Enklare ämneslista utan accordion — saknar esu-ID, behöver sökas via namn
    """
    soup = fetch_page(inst_info["url"])
    if soup is None:
        print(f"    Kunde inte hämta {inst_code}-sidan!", file=sys.stderr)
        return []

    subjects = []

    # --- Försök med accordion-paneler (IIT-mönstret) ---
    subj_accordion = soup.find("ul", id="subjects-accordion")
    if subj_accordion:
        for li in subj_accordion.find_all("li", class_="panel", recursive=False):
            subj = _parse_accordion_panel(li, "subject", inst_code)
            if subj:
                subjects.append(subj)

    research_accordion = soup.find("ul", id="postgraduatesubjects-accordion")
    if research_accordion:
        for li in research_accordion.find_all("li", class_="panel", recursive=False):
            subj = _parse_accordion_panel(li, "research", inst_code)
            if subj:
                subjects.append(subj)

    # --- Fallback: parsa ämneslista utan accordion (IHV, IKS, ISLL-mönstret) ---
    if not subjects:
        subjects = _parse_subject_list(soup, inst_code)

    return subjects


def _parse_accordion_panel(li: Tag, subject_type: str, inst_code: str) -> dict | None:
    """Parsar ett ämnes-panel (li) i accordion-format och returnerar ämnesdikt."""
    button = li.find("button")
    if not button:
        return None

    name = button.get_text(strip=True)

    # Hitta ämnes-kod från collapse-ID (t.ex. collapse-DTA → DTA)
    panel_body = li.find("div", class_="panel-body")
    if not panel_body:
        return None
    collapse_id = panel_body.get("id", "")
    code = collapse_id.replace("collapse-", "") if collapse_id.startswith("collapse-") else ""

    # Hitta esu-ID från söklänken
    esu = ""
    search_link = panel_body.find("a", href=re.compile(r"esu="))
    if search_link:
        m = re.search(r"esu=(\d+)", search_link["href"])
        if m:
            esu = m.group(1)

    # Huvudområde/Område
    huvudomrade = ""
    dl = panel_body.find("dl")
    if dl:
        for dt in dl.find_all("dt"):
            key = dt.get_text(strip=True)
            dd = dt.find_next_sibling("dd")
            if dd and key in ("Huvudområde(n):", "Område:"):
                huvudomrade = dd.get_text(strip=True)

    return {
        "name": name,
        "code": code,
        "esu": esu,
        "huvudomrade": huvudomrade,
        "type": subject_type,
        "institution": inst_code,
    }


def _parse_subject_list(soup: BeautifulSoup, inst_code: str) -> list[dict]:
    """
    Parsar ämneslista från institutionssidor som inte har accordion-format.
    Letar efter rubriken "Institutionens ämnen" och "Forskarutbildningsämnen"
    och extraherar ämnesnamn från efterföljande element.
    """
    subjects = []

    # Hitta sektioner via h2-rubriker
    for h2 in soup.find_all("h2"):
        heading = h2.get_text(strip=True)
        if heading == "Institutionens ämnen":
            names = _extract_subject_names_after(h2)
            for name in names:
                code = _generate_subject_code(name)
                subjects.append({
                    "name": name,
                    "code": code,
                    "esu": "",
                    "huvudomrade": "",
                    "type": "subject",
                    "institution": inst_code,
                })
        elif heading == "Forskarutbildningsämnen":
            names = _extract_subject_names_after(h2)
            for name in names:
                code = _generate_subject_code(name)
                subjects.append({
                    "name": name,
                    "code": code,
                    "esu": "",
                    "huvudomrade": "",
                    "type": "research",
                    "institution": inst_code,
                })

    return subjects


def _extract_subject_names_after(h2: Tag) -> list[str]:
    """
    Extraherar ämnesnamn från element som följer efter en h2-rubrik.
    Hanterar både listor och löpande text med ämnesnamn.
    """
    names = []

    # Sök genom syskon efter h2
    sibling = h2.find_next_sibling()
    while sibling:
        # Stopp vid nästa h2
        if sibling.name == "h2":
            break

        # Kolla om det finns en lista med ämnesnamn
        # Vanligt mönster: div/section med text-noder separerade av mellanrum
        text = sibling.get_text(separator="\n", strip=True)
        if text:
            # Dela på radbrytningar och filtrera bort tomma rader
            for line in text.split("\n"):
                line = line.strip()
                # Filtrera bort datum, "Senast granskad", rubriker etc.
                if (line and
                    not line.startswith("Senast granskad") and
                    not re.match(r"^\d", line) and
                    not line.startswith("Relaterade") and
                    not line.startswith("Beslut") and
                    not line.startswith("Kalender") and
                    not line.startswith("Högre seminariet") and
                    not line.startswith("Språkstödet") and
                    not line.startswith("Huvudarbetsmiljöombud") and
                    len(line) > 2 and len(line) < 60):
                    # Ytterligare sanity check: ämnesnamn börjar med stor bokstav
                    if line[0].isupper():
                        names.append(line)

        sibling = sibling.find_next_sibling()

    # Deduplicera men behåll ordning
    seen = set()
    unique = []
    for n in names:
        if n not in seen:
            seen.add(n)
            unique.append(n)

    return unique


def _generate_subject_code(name: str) -> str:
    """
    Genererar en kort ämneskod från ämnesnamnet.
    T.ex. "Omvårdnad" → "OMV", "Socialt arbete" → "SOA",
    "Svenska som andraspråk" → "SVA"
    """
    # Ta de tre första bokstäverna av varje ord, sedan de tre första av resultatet
    words = name.split()
    if len(words) == 1:
        return name[:3].upper()
    elif len(words) == 2:
        return (words[0][0] + words[1][0] + words[1][1]).upper()
    else:
        return (words[0][0] + words[1][0] + words[2][0]).upper()


# ---------------------------------------------------------------------------
# Steg 2: Hämta kurskoder per ämne via sök-API
# ---------------------------------------------------------------------------

def discover_courses_for_subject(subject: dict) -> list[dict]:
    """
    Hämtar alla kurser för ett ämne via söksidans API.
    Försöker med esu-ID först, annars med ämnesnamn som sökterm.
    Returnerar lista av {code, name}.
    """
    if subject["esu"]:
        return _search_courses_by_esu(subject["esu"])
    else:
        return _search_courses_by_name(subject["name"])


def _search_courses_by_esu(esu: str) -> list[dict]:
    """Hämtar kurser via esu-ID (sök-API parametern)."""
    courses = []
    seen_codes = set()
    page = 1

    while True:
        params = {
            "search": "true", "q": "", "l": "sv", "sb": "Relevans",
            "ssv": "1", "f": "2", "cs": "4", "pi": str(page), "esu": esu, "et": "2",
        }
        soup = fetch_page(SEARCH_API, params=params)
        if soup is None:
            break

        total = _extract_total_results(soup)
        page_courses = _extract_course_links(soup, seen_codes)
        courses.extend(page_courses)

        if total == 0 or len(courses) >= total or not page_courses:
            break

        page += 1
        time.sleep(REQUEST_DELAY)

    return courses


def _search_courses_by_name(subject_name: str) -> list[dict]:
    """
    Hämtar kurser genom att söka på ämnesnamnet.
    Söker med ämnesnamnet som query i sök-API:t.
    """
    courses = []
    seen_codes = set()
    page = 1

    while True:
        params = {
            "search": "true", "q": subject_name, "l": "sv", "sb": "Relevans",
            "ssv": "1", "f": "2", "cs": "4", "pi": str(page), "et": "2",
        }
        soup = fetch_page(SEARCH_API, params=params)
        if soup is None:
            break

        total = _extract_total_results(soup)
        page_courses = _extract_course_links(soup, seen_codes)
        courses.extend(page_courses)

        if total == 0 or len(courses) >= total or not page_courses:
            break

        page += 1
        time.sleep(REQUEST_DELAY)

    return courses


def _extract_total_results(soup: BeautifulSoup) -> int:
    """Extraherar totalt antal resultat från sökresultatsidan."""
    for el in soup.find_all(string=re.compile(r"Resultat \d+ - \d+ av \d+ träffar")):
        m = re.search(r"av (\d+) träffar", el)
        if m:
            return int(m.group(1))
    return 0


def _extract_course_links(soup: BeautifulSoup, seen_codes: set) -> list[dict]:
    """Extraherar kurskoder och namn från söksidans länkar."""
    courses = []
    for a in soup.find_all("a", href=True):
        if "/kurser/kurs/?code=" in a["href"]:
            code = a["href"].split("code=")[1]
            name = a.get_text(strip=True)
            if code not in seen_codes:
                seen_codes.add(code)
                courses.append({"code": code, "name": name})
    return courses


def kursplan_exists_by_code(code: str) -> bool:
    """Returnerar True om kursplan-sidan finns för koden och kursen inte
    är markerad som nedlagd/upphörd/avvecklad."""
    soup = fetch_page(SV_URL.format(code=code))
    if soup is None:
        return False
    h1 = soup.find("h1")
    if not h1 or not h1.find("span", property="name"):
        return False
    text_lower = soup.get_text(" ", strip=True).lower()
    if "nedlagd" in text_lower or "upphörd" in text_lower or "avvecklad" in text_lower:
        return False
    return True


KURSPLAN_INDEX_URL = "https://www.du.se/sv/utbildning/kursplaner/Search/"


def discover_all_kursplan_codes() -> set[str]:
    """Returnerar samtliga kurskoder som har en publicerad kursplan på du.se.

    Använder du.se:s fullständiga kursplan-index (DataTables-baserade
    `/sv/utbildning/kursplaner/Search/` med wildcardet `code=%` och
    `status=active`), vilket returnerar samtliga kursplaner som **inte**
    är nedlagda — alltså både aktiva och vilande — i ett enda anrop.
    Detta är det kanoniska universummet av kursplan-koder att skrapa
    och innehåller även gamla legacy-kursplaner som inte syns i du.se:s
    vanliga sökindex (t.ex. GIK375, GIK2YR).

    Nedlagda kursplaner är redan bortfiltrerade här, men `scrape_course`
    har en defensiv kontroll på sidnivå som skyddsnät.
    """
    params = {"status": "active", "searchtype": "code", "code": "%"}
    soup = fetch_page(KURSPLAN_INDEX_URL, params=params)
    if soup is None:
        return set()
    codes: set[str] = set()
    for a in soup.select("table#coursesTable tbody a[href*='code=']"):
        m = re.search(r"code=([A-Z0-9]+)", a["href"])
        if m:
            codes.add(m.group(1))
    return codes


def discover_stray_codes_from_known(known_codes: set[str], padding: int = 0) -> set[str]:
    """Hittar strökoder via du.se:s fullständiga kursplan-index.

    Sedan vi använder `/sv/utbildning/kursplaner/Search/?code=%` som källa
    täcks hela katalogen (aktiva, vilande och nedlagda) i ett anrop, så
    strökoder = index − kända. `padding` används inte längre men behålls
    av bakåtkompatibilitet med `hda.sh`.
    """
    canonical = discover_all_kursplan_codes()
    return canonical - known_codes


# ---------------------------------------------------------------------------
# Steg 3: Skrapa enskild kursplan
# ---------------------------------------------------------------------------

def html_to_markdown(element) -> str:
    if element is None:
        return ""
    parts = []
    _walk(element, parts)
    text = "".join(parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _walk(node, parts, list_depth=0):
    if isinstance(node, str):
        text = re.sub(r"[ \t]+", " ", str(node))
        parts.append(text)
        return
    if not isinstance(node, Tag):
        return

    tag = node.name
    if tag in ("ul", "ol"):
        parts.append("\n")
        for child in node.children:
            _walk(child, parts, list_depth + 1)
        parts.append("\n")
    elif tag == "li":
        indent = "  " * list_depth
        parts.append(f"\n{indent}- ")
        for child in node.children:
            _walk(child, parts, list_depth)
    elif tag == "br":
        parts.append("  \n")
    elif tag == "p":
        parts.append("\n\n")
        for child in node.children:
            _walk(child, parts, list_depth)
        parts.append("\n")
    elif tag in ("strong", "b"):
        parts.append("**")
        for child in node.children:
            _walk(child, parts, list_depth)
        parts.append("**")
    elif tag in ("em", "i"):
        parts.append("_")
        for child in node.children:
            _walk(child, parts, list_depth)
        parts.append("_")
    elif tag == "sup":
        pass
    elif tag in ("span", "div", "a"):
        for child in node.children:
            _walk(child, parts, list_depth)
    elif tag == "h3":
        parts.append("\n\n### ")
        for child in node.children:
            _walk(child, parts, list_depth)
        parts.append("\n\n")
    else:
        for child in node.children:
            _walk(child, parts, list_depth)


def extract_course_name(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        span = h1.find("span", property="name")
        if span:
            return span.get_text(strip=True)
        return h1.get_text(strip=True)
    return ""


def extract_metadata(soup: BeautifulSoup) -> dict:
    meta = {}
    dl = soup.find("dl", class_="dl-horizontal")
    if not dl:
        return meta
    for dt in dl.find_all("dt"):
        key = dt.get_text(strip=True)
        dd = dt.find_next_sibling("dd")
        if dd:
            meta[key] = dd.get_text(" ", strip=True)
    return meta


def extract_sections(soup: BeautifulSoup, section_map: dict) -> dict:
    article = soup.find("article", id="PageArticleArea")
    if not article:
        article = soup

    sections = {}
    for h2 in article.find_all("h2"):
        heading = h2.get_text(strip=True)
        target_key = None
        for key, aliases in section_map.items():
            if heading in aliases:
                target_key = key
                break
        if target_key is None:
            target_key = heading

        content_parts = []
        sibling = h2.find_next_sibling()
        while sibling and sibling.name != "h2":
            content_parts.append(sibling)
            sibling = sibling.find_next_sibling()

        md_parts = [html_to_markdown(p) for p in content_parts]
        md_text = "\n\n".join(p for p in md_parts if p)
        if md_text:
            sections[target_key] = md_text

    return sections


def scrape_course(code: str) -> dict | None:
    # Hämta svensk och engelsk kursplan parallellt — halverar väggtiden
    # per kurs och besöker varje URL exakt en gång.
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=2) as ex:
        sv_fut = ex.submit(fetch_page, SV_URL.format(code=code))
        en_fut = ex.submit(fetch_page, EN_URL.format(code=code))
        sv_soup = sv_fut.result()
        en_soup = en_fut.result()

    if sv_soup is None:
        return None

    # Hoppa över nedlagda kursplaner — de är inte intressanta för QA.
    page_text_lower = sv_soup.get_text(" ", strip=True).lower()
    if (
        "nedlagd" in page_text_lower
        or "upphörd" in page_text_lower
        or "avvecklad" in page_text_lower
    ):
        return None

    return {
        "code": code,
        "name_sv": extract_course_name(sv_soup),
        "name_en": extract_course_name(en_soup) if en_soup else "",
        "metadata": extract_metadata(sv_soup),
        "sections_sv": extract_sections(sv_soup, SECTION_MAP_SV),
        "sections_en": extract_sections(en_soup, SECTION_MAP_EN) if en_soup else {},
    }


# ---------------------------------------------------------------------------
# Ämnes-/institutionsklassificering från kursplanens metadata
# ---------------------------------------------------------------------------

INSTITUTION_TEXT_TO_CODE = {
    "Institutionen för information och teknik": "IIT",
    "Institutionen för hälsa och välfärd": "IHV",
    "Institutionen för kultur och samhälle": "IKS",
    "Institutionen för språk, litteratur och lärande": "ISLL",
}


def parse_amnestillhorighet(meta: dict) -> tuple[str, str] | None:
    """
    Parsar 'Ämnestillhörighet' från kursplanens metadata.
    Returnerar (subject_name, subject_code) eller None.

    Format: "Byggteknik (BYA)", "Datateknik (DTA)", etc.
    """
    raw = meta.get("Ämnestillhörighet", "").strip()
    if not raw:
        return None
    m = re.match(r"^(.+?)\s*\(([A-ZÅÄÖ][A-ZÅÄÖ0-9]+)\)\s*$", raw)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    # Fallback: no code in parens, use name + generate code
    return (raw, _generate_subject_code(raw))


def parse_institution_from_meta(meta: dict) -> str | None:
    """
    Parsar 'Institution' från kursplanens metadata.
    Returnerar institutionskod (IIT, IHV, IKS, ISLL) eller None.
    """
    raw = meta.get("Institution", "").strip()
    return INSTITUTION_TEXT_TO_CODE.get(raw)


# ---------------------------------------------------------------------------
# Filhantering
# ---------------------------------------------------------------------------

def content_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def normalize_for_compare(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def build_course_markdown(scraped: dict, subject_name: str, subject_code: str,
                          inst_code: str,
                          extra_tags: list[str] | None = None,
                          extra_cssclasses: list[str] | None = None) -> str:
    """Bygger en komplett kursplansfil från skrapade data."""
    code = scraped["code"]
    name_sv = scraped["name_sv"]
    name_en = scraped["name_en"]
    meta = scraped["metadata"]

    scraped_text_for_hash = str(scraped["sections_sv"]) + str(scraped["sections_en"])
    s_hash = content_hash(scraped_text_for_hash)

    # Frontmatter
    lines = [
        "---",
        f"kurskod: {code}",
        f"kursnamn: \"{name_sv}\"",
    ]
    if name_en and name_en != name_sv:
        lines.append(f"course_name: \"{name_en}\"")
    if "Poäng" in meta:
        lines.append(f"hp: {meta['Poäng']}")
    if "Nivå" in meta:
        lines.append(f"niva: \"{meta['Nivå']}\"")
    if "Kursen kan ingå i följande huvudområde(n)" in meta:
        lines.append(f"huvudomrade: \"{meta['Kursen kan ingå i följande huvudområde(n)']}\"")
    lines.append(f"amne: \"{subject_name}\"")
    lines.append(f"amne_kod: \"{subject_code}\"")
    lines.append(f"institution: \"{inst_code}\"")
    tag_list = ["kursplan", subject_code, inst_code]
    if extra_tags:
        for tag in extra_tags:
            if tag and tag not in tag_list:
                tag_list.append(tag)
    lines.append(f"tags: [{', '.join(tag_list)}]")
    if extra_cssclasses:
        css_unique = []
        for css in extra_cssclasses:
            if css and css not in css_unique:
                css_unique.append(css)
        if css_unique:
            lines.append(f"cssclasses: [{', '.join(css_unique)}]")
    lines.append(f"scrape_hash: {s_hash}")
    lines.append(f"url: {SV_URL.format(code=code)}")
    lines.append(f"up: \"[[{subject_name} MOC]]\"")
    lines.append("---")
    lines.append("")

    # Header
    lines.append(f"# {code}")
    lines.append("")
    lines.append(f"[Kursplan på du.se →]({SV_URL.format(code=code)})")
    lines.append("")
    lines.append(f"**Kursnamn:** {name_sv}")
    if name_en and name_en != name_sv:
        lines.append(f"**Course Name:** {name_en}")
    lines.append("")

    # Metadata-block
    meta_keys = ["Poäng", "Nivå", "Kursen kan ingå i följande huvudområde(n)", "Ämnestillhörighet", "Fastställd"]
    for key in meta_keys:
        if key in meta:
            lines.append(f"- **{key}:** {meta[key]}")
    if any(k in meta for k in meta_keys):
        lines.append("")

    # Svenska sektioner
    for section_name in SECTION_ORDER_SV:
        text = scraped["sections_sv"].get(section_name, "")
        if text:
            lines.append(f"## {section_name}")
            lines.append("")
            lines.append(text)
            lines.append("")

    # Engelska sektioner
    en_parts = []
    for section_name in SECTION_ORDER_EN:
        text = scraped["sections_en"].get(section_name, "")
        if text:
            en_parts.append(f"### {section_name}\n\n{text}")
    if en_parts:
        lines.append("## English Version")
        lines.append("")
        lines.append("\n\n".join(en_parts))
        lines.append("")

    return "\n".join(lines)


def update_existing_file(path: Path, scraped: dict, subject_name: str,
                         subject_code: str, inst_code: str) -> list[str]:
    """Uppdaterar en befintlig fil. Returnerar lista av ändringar."""
    text = path.read_text(encoding="utf-8")
    changes = []

    # Parse existing
    result = {"frontmatter": "", "header_block": "", "sections": {}, "section_order": []}

    fm_match = re.match(r"^---\n(.*?\n)---\n", text, re.DOTALL)
    if fm_match:
        result["frontmatter"] = fm_match.group(0)
        rest = text[fm_match.end():]
    else:
        rest = text

    first_section = re.search(r"^## ", rest, re.MULTILINE)
    if first_section:
        result["header_block"] = rest[:first_section.start()].rstrip("\n")
        sections_text = rest[first_section.start():]
    else:
        result["header_block"] = rest.rstrip("\n")
        sections_text = ""

    section_re = re.compile(r"^## (.+)$", re.MULTILINE)
    matches = list(section_re.finditer(sections_text))
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(sections_text)
        body = sections_text[start:end].strip()
        result["sections"][name] = body
        result["section_order"].append(name)

    # Check for content changes
    for section_name in SECTION_ORDER_SV:
        scraped_sv = scraped["sections_sv"].get(section_name, "")
        if not scraped_sv:
            continue
        if section_name in result["sections"]:
            if normalize_for_compare(result["sections"][section_name]) != normalize_for_compare(scraped_sv):
                changes.append(f"  ↻ {section_name}")
        else:
            changes.append(f"  + {section_name}")

    en_parts = []
    for section_name in SECTION_ORDER_EN:
        scraped_en = scraped["sections_en"].get(section_name, "")
        if scraped_en:
            en_parts.append(f"### {section_name}\n\n{scraped_en}")
    if en_parts:
        new_en = "\n\n".join(en_parts)
        existing_en = result["sections"].get("English Version", "")
        if not existing_en:
            changes.append("  + English Version")
        elif normalize_for_compare(existing_en) != normalize_for_compare(new_en):
            changes.append("  ↻ English Version")

    # Update scrape_hash in frontmatter
    scraped_text_for_hash = str(scraped["sections_sv"]) + str(scraped["sections_en"])
    new_hash = content_hash(scraped_text_for_hash)
    fm = result["frontmatter"]
    if "scrape_hash:" in fm:
        old_hash = re.search(r"scrape_hash: (\S+)", fm)
        if old_hash and old_hash.group(1) == new_hash and not changes:
            return []  # Ingen förändring

    return changes


def write_course_file(
    code: str, scraped: dict, subject_name: str, subject_code: str,
    inst_code: str, subject_dir: Path, apply: bool, quiet: bool,
    extra_tags: list[str] | None = None,
    extra_cssclasses: list[str] | None = None,
) -> int:
    """Skriver/uppdaterar en kursplansfil. Returnerar antal ändringar."""
    file_path = subject_dir / f"{code}.md"

    if file_path.exists():
        changes = update_existing_file(file_path, scraped, subject_name,
                                       subject_code, inst_code)
        if not changes:
            if not quiet:
                print("inga ändringar")
            return 0
        if not quiet:
            print(f"{len(changes)} ändring(ar)")
            for c in changes:
                print(c)
        if apply:
            new_text = build_course_markdown(scraped, subject_name, subject_code,
                                             inst_code, extra_tags,
                                             extra_cssclasses)
            file_path.write_text(new_text, encoding="utf-8")
            if not quiet:
                print(f"  ✓ Uppdaterad: {file_path.relative_to(VAULT)}")
        return len(changes)
    else:
        # Ny fil
        if not quiet:
            print("ny kurs")
        if apply:
            new_text = build_course_markdown(scraped, subject_name, subject_code,
                                             inst_code, extra_tags,
                                             extra_cssclasses)
            file_path.write_text(new_text, encoding="utf-8")
            if not quiet:
                print(f"  ✓ Skapad: {file_path.relative_to(VAULT)}")
        return 1


# ---------------------------------------------------------------------------
# MOC-generering
# ---------------------------------------------------------------------------

def build_subject_moc(subject: dict, courses: list[dict]) -> str:
    """Bygger en ämnes-MOC fil."""
    name = subject["name"]
    code = subject["code"]
    inst_code = subject["institution"]
    inst_name = INSTITUTIONS[inst_code]["name"]
    huvudomrade = subject.get("huvudomrade", "")
    stype = subject["type"]
    type_label = "Forskarutbildningsämne" if stype == "research" else "Ämne"

    lines = [
        "---",
        f"aliases: [{name}]",
        f"cssclasses: [moc-page]",
        f"tags: [MOC, amne, {code}, {inst_code}]",
        f"up: \"[[{inst_code} MOC]]\"",
        "---",
        "",
        f"# {name} MOC",
        "",
        f"> {type_label} vid {inst_name}, Högskolan Dalarna.",
    ]
    if huvudomrade:
        lines.append(f"> Huvudområde: {huvudomrade}")
    lines.append("")

    unique_courses = {c["code"]: c for c in courses}
    lines.append(f"## Kurser ({len(unique_courses)} st)")
    lines.append("")

    if unique_courses:
        for c in sorted(unique_courses.values(), key=lambda x: x["code"]):
            lines.append(f"- [[{c['code']}]] — {c['name']}")
    else:
        lines.append("_Inga kurser hittade._")
    lines.append("")

    return "\n".join(lines)


def build_subject_stray_moc(subject: dict, courses: list[dict]) -> str:
    """Bygger separat MOC för strökurser inom ett ämne."""
    name = subject["name"]
    code = subject["code"]
    inst_code = subject["institution"]
    inst_name = INSTITUTIONS[inst_code]["name"]

    lines = [
        "---",
        f"aliases: [Stray {name}]",
        f"cssclasses: [moc-page, vilande]",
        f"tags: [MOC, amne, stray, vilande, {code}, {inst_code}]",
        f"up: \"[[{name} MOC]]\"",
        "---",
        "",
        f"# Stray {name} MOC",
        "",
        f"> Strökurser i {name} vid {inst_name}, Högskolan Dalarna.",
        "> Dessa ligger utanför ordinarie ämnes-/programindex och markeras som vilande.",
        "",
    ]
    unique_courses = {c["code"]: c for c in courses}
    lines.append(f"## Kurser ({len(unique_courses)} st)")
    lines.append("")

    if unique_courses:
        for c in sorted(unique_courses.values(), key=lambda x: x["code"]):
            lines.append(f"- [[{c['code']}]] — {c['name']}")
    else:
        lines.append("_Inga strökurser hittade._")
    lines.append("")

    return "\n".join(lines)


def build_institution_moc(inst_code: str, subjects: list[dict],
                          course_counts: dict[str, int],
                          programmes: list[dict] | None = None) -> str:
    """Bygger en institutions-MOC fil."""
    inst_name = INSTITUTIONS[inst_code]["name"]

    lines = [
        "---",
        f"aliases: [{inst_code}, {inst_name}]",
        f"cssclasses: [moc-page]",
        f"tags: [MOC, institution, {inst_code}]",
        "---",
        "",
        f"# {inst_code} MOC",
        "",
        f"> {inst_name}, Högskolan Dalarna.",
        "",
    ]

    if programmes:
        lines.append(f"## Program ({len(programmes)} st)")
        lines.append("")
        for p in sorted(programmes, key=lambda x: x["name_sv"]):
            lines.append(f"- [[{p['code']}]] — {p['name_sv']}")
        lines.append("")

    regular = [s for s in subjects if s["type"] == "subject"]
    research = [s for s in subjects if s["type"] == "research"]

    if regular:
        lines.append("## Ämnen")
        lines.append("")
        for s in sorted(regular, key=lambda x: x["name"]):
            count = course_counts.get(s["code"], 0)
            lines.append(f"- [[{s['name']} MOC|{s['name']}]] ({count} kurser)")
        lines.append("")

    if research:
        lines.append("## Forskarutbildningsämnen")
        lines.append("")
        for s in sorted(research, key=lambda x: x["name"]):
            count = course_counts.get(s["code"], 0)
            lines.append(f"- [[{s['name']} MOC|{s['name']}]] ({count} kurser)")
        lines.append("")

    # Kvalitetsanalys per institution: länka till institutionens egen Analys-mapp.
    inst_dir = {"IIT": "01 IIT", "IHV": "02 IHV", "IKS": "03 IKS", "ISLL": "04 ISLL"}.get(inst_code)
    if inst_dir:
        analys_files = [
            "Stavfel och språkbruk",
            "Introfras",
            "Frasningskonsistens",
            "Omfång på lärandemål",
            "Bloom-taxonomi",
            "Examinationsformer",
            "Betygsskalor",
            "Samstämmighet svenska och engelska",
            "Vilande kursplaner",
        ]
        lines.append("## Kvalitetsanalys")
        lines.append("")
        for name in analys_files:
            lines.append(f"- [[{inst_dir}/Analys/{name}|{name}]]")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Huvudprogram
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Skrapar alla kursplaner vid Högskolan Dalarna från du.se till Obsidian-vaulten."
    )
    parser.add_argument(
        "courses", nargs="*",
        help="Specifika kurskod(er). Utelämna för alla."
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Skriv ändringar till disk (annars dry-run)."
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true",
        help="Minimal utskrift."
    )
    parser.add_argument(
        "--institution", "-i", action="append",
        help="Begränsa till specifik institution (kod, t.ex. IIT). Kan anges flera gånger."
    )
    parser.add_argument(
        "--subject", "-s", action="append",
        help="Begränsa till specifikt ämne (kod, t.ex. DTA). Kan anges flera gånger."
    )
    parser.add_argument(
        "--list-institutions", action="store_true",
        help="Lista alla institutioner och avsluta."
    )
    parser.add_argument(
        "--list-subjects", action="store_true",
        help="Lista alla ämnen per institution och avsluta."
    )
    parser.add_argument(
        "--list-courses", action="store_true",
        help="Lista alla kurser per ämne och avsluta."
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Hoppa över kurser som redan finns i vaulten (för att återuppta avbruten körning)."
    )
    parser.add_argument(
        "--discover-stray", action="store_true",
        help="Försök hitta strökurser genom att testa luckor i kurskodsserier."
    )
    parser.add_argument(
        "--stray-padding", type=int, default=0,
        help="Utöka testspannet för strökoder med N nummer före/efter kända serier."
    )
    parser.add_argument(
        "--concurrency", type=int, default=6,
        help="Antal parallella anrop vid kurssidshämtning (standard: 6)."
    )
    args = parser.parse_args()

    # --- Lista institutioner ---
    if args.list_institutions:
        print("\nInstitutioner vid Högskolan Dalarna:\n")
        for code, info in INSTITUTIONS.items():
            print(f"  {code:6s} {info['name']}")
        return

    # --- Steg 1: Upptäck ämnen ---
    print("Hämtar ämnen från institutionssidorna...")
    all_subjects = discover_all_subjects()

    total_subjects = sum(len(v) for v in all_subjects.values())
    print(f"\n  Totalt: {total_subjects} ämnen vid {len(all_subjects)} institutioner")

    if args.list_subjects:
        print()
        for inst_code in ["IIT", "IHV", "IKS", "ISLL"]:
            subjects = all_subjects.get(inst_code, [])
            inst_name = INSTITUTIONS[inst_code]["name"]
            print(f"\n  {inst_name} ({inst_code}) — {len(subjects)} ämnen:")
            for s in sorted(subjects, key=lambda x: x["name"]):
                label = "F" if s["type"] == "research" else " "
                esu = s["esu"] or "?"
                print(f"    [{label}] {s['code']:12s} {s['name']:40s} esu={esu}")
        return

    # Filtrera institutioner om --institution angivits
    if args.institution:
        codes = set(c.upper() for c in args.institution)
        all_subjects = {k: v for k, v in all_subjects.items() if k.upper() in codes}
        if not all_subjects:
            print(f"Inga institutioner matchade: {args.institution}", file=sys.stderr)
            sys.exit(1)

    # Filtrera ämnen om --subject angivits
    if args.subject:
        codes = set(c.upper() for c in args.subject)
        for inst_code in list(all_subjects.keys()):
            all_subjects[inst_code] = [
                s for s in all_subjects[inst_code] if s["code"].upper() in codes
            ]
        # Ta bort tomma institutioner
        all_subjects = {k: v for k, v in all_subjects.items() if v}
        if not all_subjects:
            print(f"Inga ämnen matchade: {args.subject}", file=sys.stderr)
            sys.exit(1)

    # --- Steg 2: Hämta kurser per ämne ---
    print("\nHämtar kurslistor per ämne...")
    # subject_code -> [course_dicts]
    subject_courses: dict[str, list[dict]] = {}

    for inst_code in ["IIT", "IHV", "IKS", "ISLL"]:
        subjects = all_subjects.get(inst_code, [])
        if not subjects:
            continue
        inst_name = INSTITUTIONS[inst_code]["name"]
        print(f"\n  {inst_name} ({inst_code}):")

        for s in subjects:
            print(f"    {s['name']}...", end=" ", flush=True)
            courses = discover_courses_for_subject(s)
            subject_courses[s["code"]] = courses
            print(f"{len(courses)} kurser")
            time.sleep(REQUEST_DELAY)

    total_courses = sum(len(v) for v in subject_courses.values())
    print(f"\n  Totalt: {total_courses} kurser")

    if args.list_courses:
        print()
        for inst_code in ["IIT", "IHV", "IKS", "ISLL"]:
            subjects = all_subjects.get(inst_code, [])
            if not subjects:
                continue
            inst_name = INSTITUTIONS[inst_code]["name"]
            print(f"\n  ═══ {inst_name} ({inst_code}) ═══")
            for s in sorted(subjects, key=lambda x: x["name"]):
                courses = subject_courses.get(s["code"], [])
                print(f"\n    {s['name']} ({s['code']}):")
                for c in sorted(courses, key=lambda x: x["code"]):
                    print(f"      {c['code']:10s} {c['name']}")
        return

    # Om specifika kurskoder angetts, filtrera
    manual_codes_not_found: set[str] = set()
    if args.courses:
        target_codes = set(c.upper() for c in args.courses)
        for code in subject_courses:
            subject_courses[code] = [
                c for c in subject_courses[code] if c["code"].upper() in target_codes
            ]
        total_courses = sum(len(v) for v in subject_courses.values())
        manual_codes_not_found = target_codes - {
            c["code"].upper()
            for courses in subject_courses.values()
            for c in courses
        }
        if manual_codes_not_found:
            print(
                f"\n  ⚠ Kurskoder ej funna i något ämne: "
                f"{', '.join(sorted(manual_codes_not_found))}"
            )

    auto_stray_codes: set[str] = set()
    if args.discover_stray:
        known_codes = {
            c["code"].upper()
            for courses in subject_courses.values()
            for c in courses
        }
        if known_codes:
            print("\nSöker strökurser via du.se:s kurssearch (kanonisk universum)...")
            auto_stray_codes = discover_stray_codes_from_known(
                known_codes,
                padding=args.stray_padding,
            )
            if auto_stray_codes:
                print(
                    f"  Hittade {len(auto_stray_codes)} möjlig(a) strökod(er): "
                    f"{', '.join(sorted(auto_stray_codes))}"
                )
            else:
                print("  Inga strökoder hittades.")

    direct_codes = sorted(manual_codes_not_found | auto_stray_codes)
    total_to_process = total_courses + len(direct_codes)

    # --- Steg 3: Skrapa och skriv ---
    mode = "SKRIVER" if args.apply else "DRY-RUN"
    print(f"\n╔══════════════════════════════════════════════╗")
    print(f"║  HDa Kursplan-scraper — {mode:8s}            ║")
    print(f"║  {total_to_process:4d} kurs(er) att bearbeta               ║")
    print(f"╚══════════════════════════════════════════════╝\n")

    total_changes = 0
    total_errors = 0
    total_skipped = 0
    course_num = 0

    # Pre-scan existing files for --skip-existing
    existing_codes: set[str] = set()
    existing_files: dict[str, Path] = {}  # code → path, for reading frontmatter
    if args.skip_existing:
        for inst_code in INST_DIR_NAME:
            kp = kursplaner_dir(inst_code)
            if not kp.exists():
                continue
            for md in kp.rglob("*.md"):
                if "MOC" not in md.stem:
                    existing_codes.add(md.stem)
                    existing_files[md.stem] = md
        if existing_codes:
            print(f"  --skip-existing: {len(existing_codes)} kurser redan i vaulten, hoppar över dem.")

    # --- Pre-fetch alla kursplaner parallellt ---
    # Vi samlar alla kurskoder som ska skrapas (per ämne + direktkoder),
    # filtrerar bort de som ska hoppas över, och hämtar svensk + engelsk
    # kursplan parallellt med ThreadPoolExecutor. Filskrivning förblir
    # sekventiell i huvudslingorna nedan.
    codes_to_prefetch: list[str] = []
    seen_pf: set[str] = set()
    for inst_code in ["IIT", "IHV", "IKS", "ISLL"]:
        for s in all_subjects.get(inst_code, []):
            for c in subject_courses.get(s["code"], []):
                code = c["code"]
                if code in existing_codes or code in seen_pf:
                    continue
                seen_pf.add(code)
                codes_to_prefetch.append(code)
    for code in direct_codes:
        if code in existing_codes or code in seen_pf:
            continue
        seen_pf.add(code)
        codes_to_prefetch.append(code)

    prefetched: dict[str, dict | None] = {}
    if codes_to_prefetch:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        workers = max(1, args.concurrency)
        print(f"\n  Pre-hämtar {len(codes_to_prefetch)} kursplaner parallellt "
              f"(concurrency={workers})...")
        t0 = time.time()
        done = 0
        with ThreadPoolExecutor(max_workers=workers) as ex:
            fut_to_code = {ex.submit(scrape_course, c): c for c in codes_to_prefetch}
            for fut in as_completed(fut_to_code):
                code = fut_to_code[fut]
                try:
                    prefetched[code] = fut.result()
                except Exception:
                    prefetched[code] = None
                done += 1
                if done % 100 == 0 or done == len(codes_to_prefetch):
                    rate = done / max(0.001, time.time() - t0)
                    eta = (len(codes_to_prefetch) - done) / max(0.001, rate)
                    print(f"    [{done}/{len(codes_to_prefetch)}] "
                          f"{rate:.1f} kurser/s · ETA {eta:.0f}s",
                          flush=True)
        elapsed = time.time() - t0
        print(f"  Klart på {elapsed:.1f}s "
              f"({len(codes_to_prefetch)/max(0.001,elapsed):.1f} kurser/s).")

    # Collect real subject→courses mappings from Ämnestillhörighet.
    # Keys: subject_code → {"name", "code", "institution", "type", "courses": [...]}
    real_subjects: dict[str, dict] = {}

    for inst_code in ["IIT", "IHV", "IKS", "ISLL"]:
        subjects = all_subjects.get(inst_code, [])
        if not subjects:
            continue

        for s in subjects:
            courses = subject_courses.get(s["code"], [])
            if not courses:
                continue

            if not args.quiet:
                print(f"\n── {s['name']} ({s['code']}) @ {inst_code} ──")

            for c in sorted(courses, key=lambda x: x["code"]):
                course_num += 1
                code = c["code"]

                if code in existing_codes:
                    total_skipped += 1
                    if not args.quiet:
                        print(f"  [{course_num}/{total_to_process}] {code} — finns redan, hoppar över")
                    # Still track for MOC generation by reading frontmatter
                    ep = existing_files.get(code)
                    if ep and ep.exists():
                        try:
                            fm = ep.read_text(encoding="utf-8", errors="replace")
                            fm_amne = re.search(r'^amne:\s*"(.+)"', fm, re.MULTILINE)
                            fm_kod = re.search(r'^amne_kod:\s*"?(\w+)"?', fm, re.MULTILINE)
                            fm_inst = re.search(r'^institution:\s*"?(\w+)"?', fm, re.MULTILINE)
                            fm_namn = re.search(r'^kursnamn:\s*"(.+)"', fm, re.MULTILINE)
                            fm_tags = re.search(r'^tags:\s*\[(.+)\]', fm, re.MULTILINE)
                            is_stray = bool(fm_tags and "stray" in fm_tags.group(1))
                            sc = fm_kod.group(1) if fm_kod else s["code"]
                            sn = fm_amne.group(1) if fm_amne else s["name"]
                            ic = fm_inst.group(1) if fm_inst else inst_code
                            cn = fm_namn.group(1) if fm_namn else c["name"]
                            if sc not in real_subjects:
                                real_subjects[sc] = {
                                    "name": sn, "code": sc,
                                    "institution": ic, "type": "subject",
                                    "courses": [],
                                }
                            real_subjects[sc]["courses"].append(
                                {"code": code, "name": cn, "stray": is_stray}
                            )
                        except Exception:
                            pass
                    continue

                if not args.quiet:
                    print(f"  [{course_num}/{total_to_process}] {code} ({c['name']})...",
                          end=" ", flush=True)

                try:
                    scraped = (prefetched[code] if code in prefetched
                               else scrape_course(code))
                    if scraped is None:
                        if not args.quiet:
                            print("misslyckades")
                        total_errors += 1
                        continue

                    # Use Ämnestillhörighet from the course page as the
                    # authoritative subject (not the search query that found it).
                    real_subj = parse_amnestillhorighet(scraped["metadata"])
                    real_inst = parse_institution_from_meta(scraped["metadata"])

                    if real_subj:
                        subj_name, subj_code = real_subj
                    else:
                        subj_name, subj_code = s["name"], s["code"]

                    if real_inst:
                        file_inst_code = real_inst
                    else:
                        file_inst_code = inst_code

                    subject_dir = kursplaner_dir(file_inst_code) / subj_code
                    if args.apply:
                        subject_dir.mkdir(parents=True, exist_ok=True)

                    n = write_course_file(
                        code, scraped, subj_name, subj_code,
                        file_inst_code, subject_dir, args.apply, args.quiet
                    )
                    total_changes += n

                    # Track real subjects for MOC generation
                    if subj_code not in real_subjects:
                        real_subjects[subj_code] = {
                            "name": subj_name,
                            "code": subj_code,
                            "institution": file_inst_code,
                            "type": "subject",
                            "courses": [],
                        }
                    real_subjects[subj_code]["courses"].append({
                        "code": code,
                        "name": scraped["name_sv"] or c["name"],
                        "stray": False,
                    })

                except Exception as e:
                    total_errors += 1
                    print(f"\n  ✗ Fel vid {code}: {e}", file=sys.stderr)

    # Direktbearbetning av strökoder / manuellt angivna koder utanför ämneslistorna
    if direct_codes and not args.quiet:
        print("\n── Direktbearbetning av externa kurskoder ──")

    selected_insts = set(c.upper() for c in args.institution) if args.institution else None

    for code in direct_codes:
        course_num += 1

        if code in existing_codes:
            total_skipped += 1
            if not args.quiet:
                print(f"  [{course_num}/{total_to_process}] {code} — finns redan, hoppar över")
            continue

        if not args.quiet:
            print(f"  [{course_num}/{total_to_process}] {code} (direkt)...", end=" ", flush=True)

        try:
            scraped = (prefetched[code] if code in prefetched
                       else scrape_course(code))
            if scraped is None:
                if not args.quiet:
                    print("misslyckades")
                total_errors += 1
                continue

            real_subj = parse_amnestillhorighet(scraped["metadata"])
            real_inst = parse_institution_from_meta(scraped["metadata"])

            if real_subj:
                subj_name, subj_code = real_subj
            else:
                subj_name, subj_code = ("Okänt ämne", "OKANT")

            if real_inst:
                file_inst_code = real_inst
            elif selected_insts and len(selected_insts) == 1:
                file_inst_code = list(selected_insts)[0]
            else:
                file_inst_code = "IIT"

            subject_dir = kursplaner_dir(file_inst_code) / subj_code
            if args.apply:
                subject_dir.mkdir(parents=True, exist_ok=True)

            n = write_course_file(
                code,
                scraped,
                subj_name,
                subj_code,
                file_inst_code,
                subject_dir,
                args.apply,
                args.quiet,
                extra_tags=["stray", "vilande"],
                extra_cssclasses=["vilande"],
            )
            total_changes += n

            if subj_code not in real_subjects:
                real_subjects[subj_code] = {
                    "name": subj_name,
                    "code": subj_code,
                    "institution": file_inst_code,
                    "type": "subject",
                    "courses": [],
                }
            real_subjects[subj_code]["courses"].append({
                "code": code,
                "name": scraped["name_sv"] or code,
                "stray": True,
            })

        except Exception as e:
            total_errors += 1
            print(f"\n  ✗ Fel vid {code}: {e}", file=sys.stderr)

    # --- Steg 4: Uppdatera MOC-filer ---
    if args.apply:
        print("\nUppdaterar MOC-filer...")

        # Build per-institution subject lists from real_subjects
        inst_subjects: dict[str, list[dict]] = {}
        all_course_counts: dict[str, int] = {}
        for subj_code, info in real_subjects.items():
            ic = info["institution"]
            if ic not in inst_subjects:
                inst_subjects[ic] = []
            inst_subjects[ic].append(info)
            all_course_counts[subj_code] = len(info["courses"])

        # Ämnes-MOC:ar (per institution)
        for subj_code, info in real_subjects.items():
            ic = info["institution"]
            subject_dir = kursplaner_dir(ic) / subj_code
            subject_dir.mkdir(parents=True, exist_ok=True)
            moc_path = kursplaner_dir(ic) / f"{info['name']} MOC.md"
            moc_text = build_subject_moc(info, info["courses"])
            moc_path.write_text(moc_text, encoding="utf-8")
            if not args.quiet:
                print(f"  ✓ {moc_path.name}")

            stray_courses = [c for c in info["courses"] if c.get("stray")]
            if stray_courses:
                stray_moc_path = kursplaner_dir(ic) / f"Stray {info['name']} MOC.md"
                stray_moc_text = build_subject_stray_moc(info, stray_courses)
                stray_moc_path.write_text(stray_moc_text, encoding="utf-8")
                if not args.quiet:
                    print(f"  ✓ {stray_moc_path.name}")

        # Institutions-MOC:ar (med utbildningsplaner)
        inst_programmes: dict[str, list[dict]] = {ic: [] for ic in INSTITUTIONS}
        for ic in INST_DIR_NAME:
            utb_dir = utbildningsplaner_dir(ic)
            if not utb_dir.exists():
                continue
            for md in utb_dir.rglob("*.md"):
                if "MOC" in md.name:
                    continue
                try:
                    text = md.read_text(encoding="utf-8")
                    pname = md.stem
                    for line in text.split("\n"):
                        if line.startswith("programnamn:"):
                            pname = line.split(":", 1)[1].strip().strip('"')
                            break
                    inst_programmes[ic].append({"code": md.stem, "name_sv": pname})
                except Exception:
                    pass

        for ic in INST_DIR_NAME:
            subjects = inst_subjects.get(ic, [])
            if not subjects:
                continue
            moc_path = institution_dir(ic) / f"{ic} MOC.md"
            progs = inst_programmes.get(ic, [])
            moc_text = build_institution_moc(
                ic, subjects, all_course_counts, progs or None
            )
            moc_path.write_text(moc_text, encoding="utf-8")
            if not args.quiet:
                print(f"  ✓ {ic} MOC.md")

    # Summering
    skip_msg = f", {total_skipped} hoppade över" if total_skipped else ""
    print(f"\nKlart! {course_num} kurser bearbetade, "
          f"{total_changes} ändring(ar), {total_errors} fel{skip_msg}.")

    if not args.apply and total_changes > 0:
        print("Kör igen med --apply för att spara ändringarna.")


if __name__ == "__main__":
    main()
