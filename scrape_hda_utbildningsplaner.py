#!/usr/bin/env python3
"""
Scraper för utbildningsplaner (programplaner) vid Högskolan Dalarna.

Upptäcker alla program via söksidans API och skrapar varje utbildningsplan
(svenska). Genererar Obsidian markdown-filer organiserade per institution.

Varje program tilldelas en institution (IIT/IHV/IKS/ISLL) via:
  1. "Fastställd"-texten (prefekt/områdesnämnd)
  2. Fallback: majoritetsmatchning mot kursplaner i vaulten

Användning:
    python3 scrape_hda_utbildningsplaner.py                  # discovery + dry-run
    python3 scrape_hda_utbildningsplaner.py --apply           # discovery + skriv
    python3 scrape_hda_utbildningsplaner.py --list-programmes # visa program
    python3 scrape_hda_utbildningsplaner.py LGGYA GDW         # enskilda program
"""

import argparse
import hashlib
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

VAULT_UTBILDNINGSPLANER = (
    Path(__file__).resolve().parent / "vault-dalarna-university" / "02 Utbildningsplaner"
)
VAULT_KURSPLANER = (
    Path(__file__).resolve().parent / "vault-dalarna-university" / "01 Kursplaner"
)

INSTITUTIONS = {
    "IIT": "Institutionen för information och teknik",
    "IHV": "Institutionen för hälsa och välfärd",
    "IKS": "Institutionen för kultur och samhälle",
    "ISLL": "Institutionen för språk, litteratur och lärande",
}

SEARCH_API = "https://www.du.se/search/Search/Search"
PLAN_SV_URL = "https://www.du.se/sv/utbildning/Program/utbildningsplan/?code={code}"
PLAN_EN_URL = "https://www.du.se/en/study-at-du/Program/curriculum/?code={code}"

REQUEST_DELAY = 1.0
RESULTS_PER_PAGE = 20

# Sektioner i utbildningsplaner, i ordning.
SECTION_ORDER = [
    "1. Mål",
    "2. Huvudsaklig uppläggning",
    "3. Programmets kurser",
    "4. Examensbenämning",
    "5. Behörighet",
    "6. Summary in English",
    "7. Övrigt",
]

# Mappning: nyckelord i Fastställd-text → institutionskod
_FASTSTALLD_INSTITUTION_MAP = {
    "institutionen för information och teknik": "IIT",
    "institutionen för hälsa och välfärd": "IHV",
    "institutionen för kultur och samhälle": "IKS",
    "institutionen för språk, litteratur och lärande": "ISLL",
    "institutionen för lärarutbildning": "ISLL",
    "teknik och naturvetenskap": "IIT",
    "vård och omsorg": "IHV",
    "samhällsvetenskap": "IKS",
    "humaniora och språk": "ISLL",
    "utbildningsvetenskap": "IKS",
}


def detect_institution_from_faststalld(faststalld_text: str) -> str | None:
    """Försök avgöra institution från Fastställd-texten."""
    lower = faststalld_text.lower()
    for keyword, inst in _FASTSTALLD_INSTITUTION_MAP.items():
        if keyword in lower:
            return inst
    return None


def build_kursplan_index() -> dict[str, tuple[str, str]]:
    """Bygg index kursnamn → (kurskod, institution) från befintliga kursplaner.

    Returnerar dict med lowercase kursnamn som nyckel.
    """
    index = {}
    for md_file in VAULT_KURSPLANER.rglob("*.md"):
        if "MOC" in md_file.name:
            continue
        code = md_file.stem
        institution = None
        kursnamn = None
        try:
            text = md_file.read_text(encoding="utf-8")
            for line in text.split("\n"):
                if line.startswith("institution:"):
                    institution = line.split(":", 1)[1].strip().strip('"')
                elif line.startswith("kursnamn:"):
                    kursnamn = line.split(":", 1)[1].strip().strip('"')
                if institution and kursnamn:
                    break
        except Exception:
            continue
        if kursnamn and institution:
            index[kursnamn.lower()] = (code, institution)
    return index


def _normalize_course_name(raw: str) -> str:
    """Strip common prefixes/suffixes to get a clean course name for index lookup."""
    name = re.sub(r"^[\-–—•*]+\s*", "", raw.strip())
    name = re.sub(r"\*+$", "", name).strip()
    # Strip trailing level qualifiers: ", avancerad nivå", ", grundnivå"
    name = re.sub(r",\s*(?:avancerad|grund)\s*nivå$", "", name, flags=re.I).strip()
    # Strip parenthesized subject tags: "(FÖ)", "(EU)", "(Idrott- och hälsovetenskap)"
    name = re.sub(r"\s*\([^)]+\)\s*$", "", name).strip()
    # Strip trailing "– VAL" / "- VAL"
    name = re.sub(r"\s*[–-]\s*VAL$", "", name, flags=re.I).strip()
    return name


# HP patterns for parsing course lines
_HP_EXPLICIT_RE = re.compile(
    r"[,\s]+(\d[\d,]*(?:[.,]\d+)?\s*(?:hp|högskolepoäng))",
    re.I,
)
_HP_BARE_RE = re.compile(
    r"[,\s]+(\d+[.,]\d+)\s*(?:[–(*†\[]|$)",  # decimal number (7,5) without unit
)


def _parse_course_line(line: str) -> tuple[str, str] | None:
    """Parse a course line into (raw_name, hp_text) or None if not a course."""
    # Strategy 1: explicit hp/högskolepoäng
    m = _HP_EXPLICIT_RE.search(line)
    if m:
        name = line[:m.start()].strip()
        if name:
            return (name, m.group(1).strip())
    # Strategy 2: bare decimal number (7,5 / 15,0) — avoids matching headings like "År 1"
    m = _HP_BARE_RE.search(line)
    if m:
        name = line[:m.start()].strip()
        if name:
            return (name, m.group(1).strip())
    return None


def _lookup_course(raw_name: str, kursplan_index: dict) -> tuple[str, str] | None:
    """Try progressively more aggressive normalization against the index."""
    # 1. Direct lookup (after stripping bullets)
    clean = re.sub(r"^[\-–—•*]+\s*", "", raw_name.strip()).rstrip("*").strip()
    lookup = clean.lower()
    if lookup in kursplan_index:
        return kursplan_index[lookup]
    # 2. Dash-normalized (en-dash → hyphen)
    dash_norm = lookup.replace("\u2013", "-").replace("\u2014", "-")
    if dash_norm != lookup and dash_norm in kursplan_index:
        return kursplan_index[dash_norm]
    # 3. Full normalization (strip qualifiers, VAL, parens, etc.)
    normalized = _normalize_course_name(raw_name).lower()
    if normalized != lookup and normalized in kursplan_index:
        return kursplan_index[normalized]
    return None


def detect_institution_from_courses(course_section: str,
                                     kursplan_index: dict) -> str | None:
    """Avgör institution genom att matcha kursnamn mot kursplanindex.

    Returnerar institutionskod baserat på majoritet.
    """
    if not course_section:
        return None

    inst_votes: dict[str, int] = {}
    for line in course_section.split("\n"):
        line = line.strip()
        if not line:
            continue
        parsed = _parse_course_line(line)
        if not parsed:
            continue
        hit = _lookup_course(parsed[0], kursplan_index)
        if hit:
            _, inst = hit
            inst_votes[inst] = inst_votes.get(inst, 0) + 1

    if not inst_votes:
        return None
    return max(inst_votes, key=inst_votes.get)


def match_courses_to_codes(course_section: str,
                           kursplan_index: dict) -> list[tuple[str, str, str | None]]:
    """Matcha kursnamn i programkurser mot kursplankoder.

    Returnerar lista av (kursnamn, hp_text, kurskod_eller_None).
    """
    courses = []
    if not course_section:
        return courses

    for line in course_section.split("\n"):
        line = line.strip()
        if not line:
            continue
        parsed = _parse_course_line(line)
        if not parsed:
            continue
        raw_name, hp = parsed
        name = _normalize_course_name(raw_name)
        hit = _lookup_course(raw_name, kursplan_index)
        code = hit[0] if hit else None
        courses.append((name, hp, code))
    return courses


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "HDa-utbildningsplan-scraper/1.0 (intern översikt HDa)"
})


def fetch_page(url: str, params: dict | None = None, quiet: bool = False) -> BeautifulSoup | None:
    try:
        resp = SESSION.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        if not quiet:
            print(f"  ⚠ Kunde inte hämta {url}: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Steg 1: Upptäck program via sök-API
# ---------------------------------------------------------------------------

def discover_all_programmes() -> list[dict]:
    """
    Hämtar alla program genom att skrapa sökresultat.

    Söksidans HTML har denna struktur per resultat:
        div.viewrich-content
          div.du-title > a   (programnamn)
          div.du-summary     (beskrivning)
          div.du-summary     (hp, nivå)
          div.du-type        ("Program KODXX" eller "Program KODXX ALIGNMENT")

    Returnerar lista av {code, name, hp, niva}.
    """
    programmes = []
    seen_codes = set()
    page = 1

    while True:
        params = {
            "search": "true", "q": "", "l": "sv", "sb": "Relevans",
            "ssv": "1", "f": "2", "cs": "4", "pi": str(page), "et": "1",
        }
        resp = SESSION.get(SEARCH_API, params=params, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Extrahera totalt antal
        total = 0
        m = re.search(r"av (\d+) träffar", resp.text)
        if m:
            total = int(m.group(1))

        # Hitta alla sökresultatblock (div.viewrich-content)
        page_found = 0
        for block in soup.find_all("div", class_="viewrich-content"):
            # Programnamn från du-title > a
            title_div = block.find("div", class_="du-title")
            name = title_div.get_text(strip=True) if title_div else ""

            # Programkod från du-type div: "Program KODXX [ALIGNMENT]"
            type_div = block.find("div", class_="du-type")
            if not type_div:
                continue
            type_text = type_div.get_text(" ", strip=True)
            # Extrahera programkod (första token efter "Program")
            code_match = re.search(r"Program\s+([A-Z][A-Z0-9]{2,5})", type_text)
            if not code_match:
                continue
            code = code_match.group(1)

            if code in seen_codes:
                continue
            seen_codes.add(code)

            # HP och nivå från du-summary
            hp = ""
            niva = ""
            for summary in block.find_all("div", class_="du-summary"):
                stxt = summary.get_text(" ", strip=True)
                hp_m = re.search(r"(\d[\d\s–-]*)\s*högskolepoäng", stxt)
                if hp_m:
                    hp = hp_m.group(1).strip()
                if "Grundnivå" in stxt:
                    niva = "Grundnivå"
                elif "Avancerad nivå" in stxt:
                    niva = "Avancerad nivå"

            programmes.append({
                "code": code,
                "name": name,
                "hp": hp,
                "niva": niva,
            })
            page_found += 1

        if total == 0 or not page_found:
            break
        if len(programmes) >= total:
            break

        page += 1
        time.sleep(REQUEST_DELAY)

    return programmes


# ---------------------------------------------------------------------------
# Steg 2: Skrapa enskild utbildningsplan
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
    elif tag == "h4":
        parts.append("\n\n#### ")
        for child in node.children:
            _walk(child, parts, list_depth)
        parts.append("\n\n")
    else:
        for child in node.children:
            _walk(child, parts, list_depth)


def extract_programme_name(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        name_span = h1.find("span", attrs={"property": "name"})
        if name_span:
            return name_span.get_text(strip=True)
        return h1.get_text(strip=True)
    return ""


def extract_programme_metadata(soup: BeautifulSoup) -> dict:
    """Extraherar metadata (Programkod, Fastställd, etc.) från utbildningsplan."""
    meta = {}
    # Metadata finns ofta i en lista med strong-taggar
    article = soup.find("article", id="PageArticleArea")
    if not article:
        article = soup

    for li in article.find_all("li"):
        text = li.get_text(" ", strip=True)
        if text.startswith("Programkod"):
            meta["Programkod"] = text.replace("Programkod", "").strip()
        elif text.startswith("Fastställd"):
            meta["Fastställd"] = text.replace("Fastställd", "").strip()
        elif text.startswith("Reviderad"):
            meta["Reviderad"] = text.replace("Reviderad", "").strip()
        elif text.startswith("Programansvarig"):
            meta["Programansvarig"] = text.replace("Programansvarig", "").strip()

    # Alternativt: metadata i dl-lista
    dl = article.find("dl", class_="dl-horizontal") if article else None
    if dl:
        for dt in dl.find_all("dt"):
            key = dt.get_text(strip=True)
            dd = dt.find_next_sibling("dd")
            if dd:
                meta[key] = dd.get_text(" ", strip=True)

    return meta


def extract_plan_sections(soup: BeautifulSoup) -> dict:
    """Extraherar sektioner från utbildningsplan."""
    article = soup.find("article", id="PageArticleArea")
    if not article:
        article = soup

    sections = {}
    for h2 in article.find_all("h2"):
        heading = h2.get_text(strip=True)

        content_parts = []
        sibling = h2.find_next_sibling()
        while sibling and sibling.name != "h2":
            content_parts.append(sibling)
            sibling = sibling.find_next_sibling()

        md_parts = [html_to_markdown(p) for p in content_parts]
        md_text = "\n\n".join(p for p in md_parts if p)
        if md_text:
            sections[heading] = md_text

    return sections


def scrape_programme(code: str) -> dict | None:
    soup = fetch_page(PLAN_SV_URL.format(code=code))
    time.sleep(REQUEST_DELAY)

    if soup is None:
        return None

    name = extract_programme_name(soup)
    metadata = extract_programme_metadata(soup)
    sections = extract_plan_sections(soup)

    # Försök hämta engelska versionen (many programmes lack one, so quiet=True)
    en_soup = fetch_page(PLAN_EN_URL.format(code=code), quiet=True)
    time.sleep(REQUEST_DELAY)

    en_name = ""
    en_sections = {}
    if en_soup:
        en_name = extract_programme_name(en_soup)
        en_sections = extract_plan_sections(en_soup)

    return {
        "code": code,
        "name_sv": name,
        "name_en": en_name,
        "metadata": metadata,
        "sections": sections,
        "sections_en": en_sections,
    }


# ---------------------------------------------------------------------------
# Filhantering
# ---------------------------------------------------------------------------

def content_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def build_programme_markdown(scraped: dict, kursplan_index: dict) -> str:
    """Bygger en utbildningsplansfil från skrapade data."""
    code = scraped["code"]
    name_sv = scraped["name_sv"]
    name_en = scraped["name_en"]
    meta = scraped["metadata"]
    sections = scraped["sections"]
    institution = scraped.get("institution", "")

    scraped_text = str(sections) + str(scraped.get("sections_en", {}))
    s_hash = content_hash(scraped_text)

    lines = [
        "---",
        f"programkod: {code}",
        f"programnamn: \"{name_sv}\"",
    ]
    if name_en and name_en != name_sv:
        lines.append(f"programme_name: \"{name_en}\"")
    if institution:
        lines.append(f"institution: \"{institution}\"")
    if meta.get("Fastställd"):
        lines.append(f"faststalld: \"{meta['Fastställd']}\"")
    if institution:
        lines.append(f"tags: [utbildningsplan, program, {institution}]")
    else:
        lines.append(f"tags: [utbildningsplan, program]")
    lines.append(f"scrape_hash: {s_hash}")
    if institution:
        lines.append(f"up: \"[[{institution} MOC]]\"")
    lines.append("---")
    lines.append("")

    # Header
    lines.append(f"# {code}")
    lines.append("")
    lines.append(f"**Programnamn:** {name_sv}")
    if name_en and name_en != name_sv:
        lines.append(f"**Programme Name:** {name_en}")
    lines.append("")

    # Metadata
    meta_keys = ["Programkod", "Programansvarig", "Fastställd", "Reviderad"]
    for key in meta_keys:
        if key in meta:
            lines.append(f"- **{key}:** {meta[key]}")
    if any(k in meta for k in meta_keys):
        lines.append("")

    # Sektioner — kursavsnittet cross-linkas
    for section_name in SECTION_ORDER:
        text = sections.get(section_name, "")
        if not text:
            continue

        lines.append(f"## {section_name}")
        lines.append("")

        if section_name == "3. Programmets kurser":
            matched = match_courses_to_codes(text, kursplan_index)
            if matched:
                current_heading = None
                for raw_line in text.split("\n"):
                    stripped = raw_line.strip()
                    if not stripped:
                        continue
                    # Check if this is a year/section heading (no hp pattern)
                    parsed = _parse_course_line(stripped)
                    if not parsed:
                        if current_heading is not None:
                            lines.append("")
                        lines.append(f"**{stripped}**")
                        lines.append("")
                        current_heading = stripped
                        continue
                    # Course line — try to match
                    raw_name, hp = parsed
                    cname = _normalize_course_name(raw_name)
                    hit = _lookup_course(raw_name, kursplan_index)
                    if hit:
                        lines.append(f"- [[{hit[0]}|{cname}]], {hp}")
                    else:
                        lines.append(f"- {cname}, {hp}")
                lines.append("")
            else:
                lines.append(text)
                lines.append("")
        else:
            lines.append(text)
            lines.append("")

    # Övriga sektioner som inte är i ordningen
    for name, text in sections.items():
        if name not in SECTION_ORDER and text:
            lines.append(f"## {name}")
            lines.append("")
            lines.append(text)
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Huvudprogram
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Skrapar utbildningsplaner vid Högskolan Dalarna från du.se till Obsidian-vaulten."
    )
    parser.add_argument(
        "programmes", nargs="*",
        help="Specifika programkod(er). Utelämna för alla."
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
        "--list-programmes", action="store_true",
        help="Lista alla program och avsluta."
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Hoppa över program som redan finns."
    )
    args = parser.parse_args()

    # --- Bygg kursplanindex för cross-referens ---
    print("Bygger kursplanindex...")
    kursplan_index = build_kursplan_index()
    print(f"  {len(kursplan_index)} kursnamn indexerade")

    # --- Steg 1: Upptäck program ---
    print("Hämtar programlista från söksidan...")
    programmes = discover_all_programmes()
    print(f"  Hittade {len(programmes)} program")

    if args.list_programmes:
        print()
        for p in sorted(programmes, key=lambda x: x.get("name", x["code"])):
            hp = p.get("hp", "?")
            niva = p.get("niva", "?")
            print(f"  {p['code']:10s} {p.get('name', '?'):60s} {hp} hp  {niva}")
        return

    # Filtrera om specifika koder angetts
    if args.programmes:
        target_codes = set(c.upper() for c in args.programmes)
        programmes = [p for p in programmes if p["code"].upper() in target_codes]
        not_found = target_codes - {p["code"].upper() for p in programmes}
        if not_found:
            for code in not_found:
                programmes.append({"code": code, "name": code})

    # --- Pre-scan existing files for --skip-existing ---
    existing_codes: set[str] = set()
    existing_programmes: dict[str, dict] = {}  # code → {institution, name_sv}
    if args.skip_existing:
        for md_file in VAULT_UTBILDNINGSPLANER.rglob("*.md"):
            if "MOC" in md_file.name:
                continue
            code = md_file.stem
            existing_codes.add(code)
            # Read frontmatter for institution MOC generation
            inst = None
            name_sv = code
            try:
                text = md_file.read_text(encoding="utf-8")
                for line in text.split("\n"):
                    if line.startswith("institution:"):
                        inst = line.split(":", 1)[1].strip().strip('"')
                    elif line.startswith("programnamn:"):
                        name_sv = line.split(":", 1)[1].strip().strip('"')
                    if inst and name_sv != code:
                        break
            except Exception:
                pass
            if inst:
                existing_programmes[code] = {"institution": inst, "name_sv": name_sv}

    # --- Steg 2: Skrapa och skriv ---
    mode = "SKRIVER" if args.apply else "DRY-RUN"
    print(f"\n╔══════════════════════════════════════════════════╗")
    print(f"║  HDa Utbildningsplan-scraper — {mode:8s}        ║")
    print(f"║  {len(programmes):4d} program att bearbeta                    ║")
    print(f"╚══════════════════════════════════════════════════╝\n")

    total_changes = 0
    total_errors = 0
    total_skipped = 0
    # Tracks institution → list of {code, name_sv} for MOC generation
    inst_programmes: dict[str, list[dict]] = {ic: [] for ic in INSTITUTIONS}
    unassigned: list[dict] = []

    # Populate from skipped existing programmes
    for code, info in existing_programmes.items():
        inst = info["institution"]
        if inst in inst_programmes:
            inst_programmes[inst].append({"code": code, "name_sv": info["name_sv"]})

    for i, p in enumerate(sorted(programmes, key=lambda x: x["code"]), 1):
        code = p["code"]

        # Skip existing
        if args.skip_existing and code in existing_codes:
            if not args.quiet:
                print(f"  [{i}/{len(programmes)}] {code} — finns redan, hoppar över")
            total_skipped += 1
            continue

        if not args.quiet:
            print(f"  [{i}/{len(programmes)}] {code} ({p.get('name', '?')})...",
                  end=" ", flush=True)

        try:
            scraped = scrape_programme(code)
            if scraped is None:
                if not args.quiet:
                    print("misslyckades")
                total_errors += 1
                continue

            # --- Determine institution ---
            faststalld = scraped["metadata"].get("Fastställd", "")
            institution = detect_institution_from_faststalld(faststalld)

            if not institution:
                # Fallback: match courses against kursplanindex
                course_text = scraped["sections"].get("3. Programmets kurser", "")
                institution = detect_institution_from_courses(course_text, kursplan_index)

            if institution:
                scraped["institution"] = institution
                inst_programmes[institution].append({
                    "code": code, "name_sv": scraped["name_sv"]
                })
            else:
                scraped["institution"] = ""
                unassigned.append({"code": code, "name_sv": scraped["name_sv"]})

            # --- Write file to institution subfolder ---
            if institution:
                folder = VAULT_UTBILDNINGSPLANER / institution
            else:
                folder = VAULT_UTBILDNINGSPLANER

            file_path = folder / f"{code}.md"
            new_text = build_programme_markdown(scraped, kursplan_index)

            if file_path.exists():
                existing = file_path.read_text(encoding="utf-8")
                if existing.strip() == new_text.strip():
                    if not args.quiet:
                        print(f"inga ändringar [{institution or '?'}]")
                    continue
                if not args.quiet:
                    print(f"uppdaterad [{institution or '?'}]")
                total_changes += 1
                if args.apply:
                    file_path.write_text(new_text, encoding="utf-8")
            else:
                if not args.quiet:
                    print(f"ny [{institution or '?'}]")
                total_changes += 1
                if args.apply:
                    folder.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(new_text, encoding="utf-8")

        except Exception as e:
            total_errors += 1
            print(f"\n  ✗ Fel vid {code}: {e}", file=sys.stderr)

    # --- Steg 3: Summering ---
    if unassigned:
        print(f"\n  ⚠ {len(unassigned)} program utan institution:")
        for u in unassigned:
            print(f"    {u['code']} — {u['name_sv']}")

    skip_msg = f", {total_skipped} hoppade över" if total_skipped else ""
    print(f"\nKlart! {len(programmes)} program bearbetade, "
          f"{total_changes} ändring(ar), {total_errors} fel{skip_msg}.")

    if not args.apply and total_changes > 0:
        print("Kör igen med --apply för att spara ändringarna.")


if __name__ == "__main__":
    main()
