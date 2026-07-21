#!/usr/bin/env python3
"""
Kvalitetskontroll av alla kursplaner i vault-dalarna-university/01 Kursplaner/.

Körning:
    python3 qa/check_kursplaner.py                # rapport till stdout
    python3 qa/check_kursplaner.py --out rapport   # skriver även rapport.md

Kontroller som körs:
  1.  Dubblerade ord
  2.  Kända felstavningar (svensk ordlista)
  3.  Hunspell stavning svenska (sv_SE)
  4.  Hunspell stavning engelska (en_US) — English Version-sektionen
  5a. Introfras (existens)
  5b. Frasningskonsistens (introfras matchar referensformen)
  6.  Betygsskala — inkonsekvent delskalor
  7.  Examinationsformer — hp-summa i Betyg matchar inte kursens hp
  8.  Omfång lärandemål — för få (< 4) eller för många (> 12)
  9.  Långa bullets (> 25 ord)
  10. Bloom-taxonomi — avancerade kurser med enbart låga nivåer
  11. Svenska/engelska paritet — varje skillnad i antal lärandemål (diff ≥ 1)
  12. Förkunskapskrav — sektion saknas helt
  13. Förkunskapskrav — endast engelsk variant finns
  16. Betyg — sektionen saknar punktlista (rapportering i löpande text)
  16b. Förkunskapskrav — refererar HDa-kurs som inte finns i vaulten
  20. Övrigt — sektionen saknas helt
  21. Övrigt — saknar standardfras om pedagogiskt stöd
"""

import argparse
import re
import sys
from pathlib import Path

from checks_common import (
    build_report,
    check_dup_words,
    check_hunspell_en,
    check_hunspell_sv,
    check_known_typos,
    course_code,
    extract_section,
    is_draft,
    is_hub,
    strip_frontmatter,
    subject,
)
from bloom_verbs import bloom_level

VAULT = Path(__file__).resolve().parent.parent / "vault-dalarna-university"
INST_DIRS = ["01 IIT", "02 IHV", "03 IKS", "04 ISLL"]


def load_files() -> list[Path]:
    files: list[Path] = []
    for inst in INST_DIRS:
        kp = VAULT / inst / "Kursplaner"
        if kp.exists():
            files.extend(
                p for p in kp.rglob("*.md")
                if not is_hub(p) and not is_draft(p)
            )
    return sorted(files)


# ─────────────────────────────────────────────────────────────────────────────
# Check 5a — Introfras (rubriken följs direkt av en *Efter ...*-fras)
# Check 5b — Frasningskonsistens (introfras matchar referensformen)
# ─────────────────────────────────────────────────────────────────────────────
GOLD_INTRO_TEXT = "Efter godkänd kurs ska studenten kunna:"
DELKURS_INTRO_TEXT = "Efter avslutad delkurs ska den studerande kunna:"

# Forskarkurser använder en parallell konvention: ``doktoranden`` eller
# ``den forskarstuderande`` istället för ``studenten``, och en mindre strikt
# inledning ("Efter avslutad kurs" snarare än "Efter godkänd kurs"). Båda
# varianterna räknas som godkända introfraser för forskarkurser.
FORSKAR_INTRO_TEXTS = {
    "Efter avslutad kurs ska doktoranden kunna:",
    "Efter avslutad kurs ska den forskarstuderande kunna:",
    "Efter godkänd kurs ska doktoranden kunna:",
    "Efter godkänd kurs ska den forskarstuderande kunna:",
}

_NIVA_HEAD_RE = re.compile(r'^niva:\s*"?([^"\n]+)"?', re.MULTILINE)


def is_forskar_kurs(path: Path) -> bool:
    """Returnerar True om kursplanen är på forskarnivå.

    Identifieras via frontmatter-fältet ``niva: Forskarnivå`` (mest tillförlitligt
    på vault-filer) eller — som fallback — via ``forskarutbildning``-taggen."""
    try:
        head = path.read_text(encoding="utf-8")[:2000]
    except OSError:
        return False
    m = _NIVA_HEAD_RE.search(head)
    if m and "forskar" in m.group(1).lower():
        return True
    return "forskarutbildning" in head


# Bologna-domänrubriker som legitimt får inleda en lärandemålssektion.
# De räknas som "skip and look further" snarare än som introfraser.
BOLOGNA_HEADING_RE = re.compile(
    r"^[\s_*]*(?:kunskap\s+och\s+förståelse"
    r"|färdighet\s+och\s+förmåga"
    r"|värderingsförmåga\s+och\s+förhållningssätt)"
    r"[\s_*:]*$",
    re.IGNORECASE,
)


def _first_significant_line(section: str) -> str | None:
    """Returnera första raden som varken är tom eller en Bologna-domänrubrik."""
    for ln in section.splitlines():
        s = ln.strip()
        if not s:
            continue
        if BOLOGNA_HEADING_RE.match(s):
            continue
        return s
    return None


def _starts_with_bologna_heading(section: str) -> bool:
    """Den äldre konventionen: lärandemålen inleds med en Bologna-domänrubrik
    (*Kunskap och förståelse* osv.) före introfrasen. Tekniskt inte fel, men
    vi har gått ifrån den — och flaggar inte sådana fall."""
    for ln in section.splitlines():
        s = ln.strip()
        if not s:
            continue
        return bool(BOLOGNA_HEADING_RE.match(s))
    return False


def check_introfras(files: list[Path]) -> list[dict]:
    """Flagga kursplaner där rubriken ``## Lärandemål`` inte följs direkt
    av en fras som börjar med *"Efter ..."*.

    Lärandemålen förväntas inledas med en fras som börjar på *Efter*
    (t.ex. *"Efter godkänd kurs ska studenten kunna:"* eller
    *"Efter avslutad kurs skall den studerande kunna:"*). Står det
    inledande prosa, en delkurs-rubrik eller bara punktlista där, flaggas
    det här. Frasens exakta formulering granskas separat i
    [[Frasningskonsistens]].
    """
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        lo_section = extract_section(body, "Lärandemål")
        if not lo_section:
            continue
        if _starts_with_bologna_heading(lo_section):
            continue
        first_line = _first_significant_line(lo_section)
        if first_line is None:
            continue
        if first_line.lower().startswith("efter"):
            continue
        snippet = first_line[:120]
        findings.append({
            "check": "introfras-fore-fras",
            "code": course_code(p),
            "subj": subject(p),
            "detail": f"Lärandemål inleds inte med 'Efter ...': {snippet}…",
        })
    return findings


def check_frasning(files: list[Path]) -> list[dict]:
    """Matchar första raden i ## Lärandemål referensformen
    'Efter godkänd kurs ska studenten kunna:'?

    Kör endast på kursplaner där rubriken följs direkt av en *Efter ...*-fras.
    Står det prosa eller delkurs-rubrik först är det [[Introfras]]:s ansvar
    — vi flaggar inte samma kursplan på två ställen.
    """
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        lo_section = extract_section(body, "Lärandemål")
        if not lo_section:
            continue
        if _starts_with_bologna_heading(lo_section):
            # Äldre konvention med Bologna-rubrik före introfrasen — flaggas inte.
            continue
        first_line = _first_significant_line(lo_section)
        if first_line is None:
            continue
        if not first_line.lower().startswith("efter"):
            # Fallet "prosa före introfras" hanteras av check_introfras.
            continue
        if first_line == GOLD_INTRO_TEXT:
            continue
        if first_line == DELKURS_INTRO_TEXT:
            continue
        # Forskarkurser har sin egen konvention med ``doktoranden`` /
        # ``den forskarstuderande`` istället för ``studenten``.
        if is_forskar_kurs(p) and first_line in FORSKAR_INTRO_TEXTS:
            continue
        snippet = first_line[:120]
        findings.append({
            "check": "frasning-avviker",
            "code": course_code(p),
            "subj": subject(p),
            "detail": f"{snippet}…",
        })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 6 — Betygsskala
# ─────────────────────────────────────────────────────────────────────────────
AF_RE = re.compile(r"\bA\s*[–\-]\s*F\b|\bA,\s*B,\s*C,\s*D,\s*E\b", re.IGNORECASE)
# Äkta inkonsekvens = två distinkta numeriska skalor i samma kurs: kursnivå
# U,3,4,5 men VG nämns någonstans (VG hör till U,G,VG-skalan). En blandning
# med rena U,G-delmoment är däremot legitim — t.ex. att seminarier/labbar
# bedöms godkänt/underkänt medan det slutliga kursbetyget sätts på 3/4/5-
# skalan utifrån en tentamen. Tidigare regex matchade både `U,G` och `U,VG`
# vilket gav falska positiva för GMT228, GBY2ME m.fl.
MIXED_SCALE_RE = re.compile(r"\bU\s*[,/]\s*3\b.*?\bV\s*G\b", re.DOTALL | re.IGNORECASE)


def check_betygsskala(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        betyg_section = extract_section(body, "Betyg")
        if not betyg_section:
            continue
        if MIXED_SCALE_RE.search(betyg_section):
            findings.append({
                "check": "betygsskala-inkonsekvent",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 6b — Betygsrapportering utan punktlista
# ─────────────────────────────────────────────────────────────────────────────
BETYG_BULLET_RE = re.compile(r"^\s*[-*]\s+\S", re.MULTILINE)


def check_betyg_punktlista(files: list[Path]) -> list[dict]:
    """Flagga kursplaner där `## Betyg`-sektionen saknar punktlista. Konventionen
    är att modul- och delkursbetygsrapportering listas som bullets. Sektioner
    skrivna helt i löpande text granskas inte vidare här — endast existensen
    av minst en bullet kontrolleras."""
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        betyg_section = extract_section(body, "Betyg")
        if not betyg_section.strip():
            continue
        if not BETYG_BULLET_RE.search(betyg_section):
            snippet = " ".join(betyg_section.split())[:120]
            findings.append({
                "check": "betyg-saknar-punktlista",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"Betyg skrivet utan punktlista: {snippet}…",
            })
    return findings


# Frontmatter-fältet `hp:` används av flera checkar (Omfång lärandemål m.fl.).
TOTAL_HP_RE = re.compile(r"^hp:\s*(\d+(?:[,.]\d+)?)", re.MULTILINE)


# ─────────────────────────────────────────────────────────────────────────────
# Check 7b — Examinationsformer skrivna som punktlista
# ─────────────────────────────────────────────────────────────────────────────
EXAM_BULLET_RE = re.compile(r"^\s*[-*]\s+\S", re.MULTILINE)


def check_examinationsformer_format(files: list[Path]) -> list[dict]:
    """Flagga kursplaner där ## Examinationsformer-sektionen inte är skriven
    som punktlista (- eller * som listmarkör).
    """
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        section = extract_section(body, "Examinationsformer")
        # extract_section returnerar tom sträng både för saknad och tom
        # sektion — i båda fallen är det inget för punktlista-checken att säga.
        content = section.strip()
        if not content:
            continue
        bullet_count = len(EXAM_BULLET_RE.findall(section))
        if bullet_count == 0:
            snippet = " ".join(content.split())[:120]
            findings.append({
                "check": "examinationsformer-utan-punktlista",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"Examinationsformer skrivet som löpande text: {snippet}…",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 8 — Omfång lärandemål
# ─────────────────────────────────────────────────────────────────────────────
LO_BULLET_RE = re.compile(r"^\s*[-*]\s+.+", re.MULTILINE)


def lo_bounds(hp: float) -> tuple[int, int]:
    """Rimligt antal lärandemål skalat efter kursens hp."""
    if hp <= 3:
        return (1, 4)
    if hp <= 5:
        return (2, 6)
    if hp <= 7.5:
        return (3, 8)
    if hp <= 15:
        return (4, 10)
    if hp <= 30:
        return (5, 12)
    return (6, 15)


def check_omfang(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        raw = p.read_text(encoding="utf-8")
        m_hp = TOTAL_HP_RE.search(raw)
        if not m_hp:
            continue
        course_hp = float(m_hp.group(1).replace(",", "."))
        lo_min, lo_max = lo_bounds(course_hp)
        body = strip_frontmatter(raw)
        lo_section = extract_section(body, "Lärandemål")
        if not lo_section:
            continue
        bullets = LO_BULLET_RE.findall(lo_section)
        n = len(bullets)
        if n < lo_min:
            findings.append({
                "check": "omfång-få-mål",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"{n} lärandemål (minimum rekommenderat: {lo_min} för {course_hp:g} hp)",
            })
        elif n > lo_max:
            findings.append({
                "check": "omfång-många-mål",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"{n} lärandemål (maximum rekommenderat: {lo_max} för {course_hp:g} hp)",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 9 — Långa bullets (> 25 ord)
# ─────────────────────────────────────────────────────────────────────────────
LONG_BULLET_THRESHOLD = 25


def check_long_bullets(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        lo_section = extract_section(body, "Lärandemål")
        if not lo_section:
            continue
        for m in LO_BULLET_RE.finditer(lo_section):
            line = m.group(0).strip()
            words = len(line.split())
            if words > LONG_BULLET_THRESHOLD:
                findings.append({
                    "check": "långt-lärandemål",
                    "code": course_code(p),
                    "subj": subject(p),
                    "detail": f"{words} ord: {line[:80]}…",
                })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 10 — Bloom-taxonomi (deterministisk 6-nivå-analys)
# ─────────────────────────────────────────────────────────────────────────────
NIVA_RE = re.compile(r'^niva:\s*"?([^"\n]+?)"?\s*$', re.MULTILINE)
BULLET_RE = re.compile(r"^\s*[-*]\s+(.+)$", re.MULTILINE)
WORD_RE = re.compile(r"\b([a-zåäö][a-zåäö-]+)\b", re.IGNORECASE)
UNKNOWN_VERB_THRESHOLD = 3            # bullets utan klassbart verb innan kursen flaggas
HIGH_GRUND_DOMINANCE_RATIO = 0.60     # andel värdera/skapa-bullets för att flagga grundkurs


def _bullet_levels(lo_section: str) -> tuple[list[int], int, int]:
    """Returnera (per-bullet-nivåer, totalt antal bullets, antal okända bullets).

    För varje bullet letas efter det **första** ordet som finns i Bloom-
    lexikonet. Det innebär att inledande adverb/prepositioner (*självständigt*,
    *muntligt*, *utifrån*, …) hoppas över naturligt — de saknas i lexikonet.
    Bullets där inget ord matchar räknas som okända.
    """
    levels: list[int] = []
    total = 0
    unknown = 0
    for m in BULLET_RE.finditer(lo_section):
        total += 1
        bullet = m.group(1).lower()
        found = None
        for w_match in WORD_RE.finditer(bullet):
            lvl = bloom_level(w_match.group(1))
            if lvl is not None:
                found = lvl
                break
        if found is None:
            unknown += 1
        else:
            levels.append(found)
    return levels, total, unknown


def _distribution(levels: list[int]) -> list[int]:
    """6-cells histogram över nivåer 1..6."""
    hist = [0] * 6
    for l in levels:
        if 1 <= l <= 6:
            hist[l - 1] += 1
    return hist


def check_bloom(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        raw = p.read_text(encoding="utf-8")
        m_niva = NIVA_RE.search(raw)
        niva = m_niva.group(1).strip().lower() if m_niva else ""
        body = strip_frontmatter(raw)
        lo_section = extract_section(body, "Lärandemål")
        if not lo_section:
            continue

        levels, total_bullets, unknown = _bullet_levels(lo_section)
        if total_bullets == 0:
            continue
        hist = _distribution(levels)
        hist_str = ",".join(str(c) for c in hist)
        n_classified = len(levels)

        # Regel 1: Avancerad kurs utan höga verb (nivå ≥ 4)
        if niva.startswith("avancerad") and n_classified > 0:
            high_count = sum(hist[3:])  # nivå 4,5,6
            if high_count == 0:
                findings.append({
                    "check": "bloom-låg-avancerad",
                    "code": course_code(p),
                    "subj": subject(p),
                    "detail": f"Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [{hist_str}]",
                })

        # Regel 2: Grundkurs där värdera+skapa dominerar (≥ 60 % av klassade bullets)
        if niva.startswith("grund") and n_classified > 0:
            top_count = hist[4] + hist[5]  # värdera + skapa
            if top_count / n_classified >= HIGH_GRUND_DOMINANCE_RATIO:
                findings.append({
                    "check": "bloom-hög-grund",
                    "code": course_code(p),
                    "subj": subject(p),
                    "detail": f"Grundkurs domineras av värdera/skapa; fördelning [{hist_str}]",
                })

        # Regel 3: Många okända ledande verb (signal till lexikonutökning)
        if unknown >= UNKNOWN_VERB_THRESHOLD:
            findings.append({
                "check": "bloom-okant-verb",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"{unknown} av {total_bullets} bullets har okänt ledande verb",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 11 — Svenska/engelska paritet
# ─────────────────────────────────────────────────────────────────────────────
PARITY_THRESHOLD = 0
EN_LO_RE = re.compile(
    r"^#{2,3}\s+Learning Outcomes\s*\n(.+?)(?=^#{2,3}\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
EN_VERSION_RE = re.compile(r"^## English Version\b", re.MULTILINE)


def _count_outcomes(section: str) -> int:
    """Antal lärandemål i en sektion. Räknar bullets (``- `` / ``* ``) i första
    hand; faller tillbaka till antalet styckesblock om sektionen är skriven i
    löpande text. Stycken som slutar med ``:`` (introfraser av typen
    *"Efter avslutad kurs ska studenten kunna:"*) räknas inte."""
    bullets = len(LO_BULLET_RE.findall(section))
    if bullets > 0:
        return bullets
    count = 0
    for para in re.split(r"\n\s*\n", section.strip()):
        text = para.strip()
        if not text:
            continue
        if text.rstrip().endswith(":"):
            continue
        count += 1
    return count


def check_lo_bullets(files: list[Path]) -> list[dict]:
    """Flagga kursplaner där lärandemål är skrivna i löpande text istället
    för punktlista. Rapporteras separat per språksida — kvarstår även när
    antalet mål är i paritet, eftersom punktlistformen är en strukturell
    konvention som efterfrågas oberoende av översättningens antal."""
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        sv_lo = extract_section(body, "Lärandemål")
        if sv_lo and not LO_BULLET_RE.search(sv_lo):
            n = _count_outcomes(sv_lo)
            if n > 0:
                findings.append({
                    "check": "lo-saknar-bullets-sv",
                    "code": course_code(p),
                    "subj": subject(p),
                    "detail": f"Lärandemål skrivet som löpande text ({n} mål utan punktlista)",
                })
        m = EN_LO_RE.search(body)
        if m:
            en_lo = m.group(1)
            if en_lo and not LO_BULLET_RE.search(en_lo):
                n = _count_outcomes(en_lo)
                if n > 0:
                    findings.append({
                        "check": "lo-saknar-bullets-en",
                        "code": course_code(p),
                        "subj": subject(p),
                        "detail": f"Learning Outcomes skrivet som löpande text ({n} mål utan punktlista)",
                    })
    return findings


def check_sv_en_parity(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        sv_lo = extract_section(body, "Lärandemål")
        if not sv_lo:
            continue
        m = EN_LO_RE.search(body)
        if m:
            en_lo = m.group(1)
        elif EN_VERSION_RE.search(body):
            en_lo = ""
        else:
            continue
        sv_n = _count_outcomes(sv_lo)
        en_n = _count_outcomes(en_lo)
        if abs(sv_n - en_n) > PARITY_THRESHOLD:
            findings.append({
                "check": "sv-en-paritet",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"Svenska: {sv_n} mål, engelska: {en_n} mål (diff {abs(sv_n-en_n)})",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 16b — Förkunskapskrav refererar okänd HDa-kurs
# ─────────────────────────────────────────────────────────────────────────────
FORKUNSKAP_KURSNAMN_RE = re.compile(r'^kursnamn:\s*"?(.+?)"?\s*$', re.MULTILINE)
FORKUNSKAP_KURSEN_RE = re.compile(
    r"(?:^|\W)[Kk]urs(?:en|erna)?\s+([A-ZÅÄÖ][^,;.]{4,80}?)\s*,?\s+\d+(?:[,.]\d+)?\s*hp\b"
)
FORKUNSKAP_LINE_LEAD_RE = re.compile(
    r"^([A-ZÅÄÖ][^,;.]{4,80}?)\s*,\s+\d+(?:[,.]\d+)?\s*hp\b"
)
FORKUNSKAP_HP_RE = re.compile(r"\b\d+(?:[,.]\d+)?\s*hp\b", re.IGNORECASE)
FORKUNSKAP_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$", re.MULTILINE)
# Förstaord som indikerar att "titeln" inte är ett kursnamn utan tröskel/grad/verb.
FORKUNSKAP_STOPWORDS = {
    "och","samt","eller","inklusive","varav","inom","på","i","av","för","med",
    "minst","högst","antingen","grundläggande","kandidatexamen","magisterexamen",
    "masterexamen","lärarexamen","yrkesexamen","examen","behörighet","filosofie",
    "krävs","studenten","skall","ska","den","studerande","antagen","har","ha",
    "uppfylls","uppfyller","godkänd","godkänt","motsvarande","tillträde",
}


def _normalize_title(s: str) -> str:
    s = s.lower().replace("\xa0", " ")
    s = re.sub(r"[^\wåäö ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _build_vault_title_index(files: list[Path]) -> tuple[dict[str, set[str]], list[str]]:
    """Indexera samtliga kursnamn (active *och* vilande) från frontmatter.
    Returnerar (exakt-uppslag, lista över titlar ≥ 12 tecken för fuzzy-match)."""
    idx: dict[str, set[str]] = {}
    for p in files:
        raw = p.read_text(encoding="utf-8")
        fm = re.match(r"^---\n(.*?)\n---", raw, re.DOTALL)
        if not fm:
            continue
        m = FORKUNSKAP_KURSNAMN_RE.search(fm.group(1))
        if not m:
            continue
        title = m.group(1).strip().strip('"')
        norm = _normalize_title(title)
        if norm:
            idx.setdefault(norm, set()).add(course_code(p))
    long_titles = [t for t in idx if len(t) >= 12]
    return idx, long_titles


def check_forkunskap_okand_kurs(files: list[Path]) -> list[dict]:
    """Flagga förkunskapskrav som refererar en HDa-kurs vars kursnamn inte
    återfinns i vaulten (varken aktiv eller vilande). Sannolik indikation på
    att förkunskapsformuleringen är inaktuell och behöver revideras.

    Endast bullets som nämner ``hp`` granskas — gymnasiekurser (*Engelska 6*,
    *Matematik 2b* osv.) saknar hp och hoppas över per design. Två
    extraktionsmönster används för att hålla precisionen hög:

    1. ``kursen X, N hp`` (eller ``kurs X, N hp``) — explicit kursreferens.
    2. Bullet som börjar med ``X, N hp`` där X startar med versal.

    Titel-startord på en stopplista (*krävs, studenten, kandidatexamen, …*)
    förkastas eftersom de inte utgör kursnamn."""
    title_index, long_titles = _build_vault_title_index(files)
    # Om QA-cachen av nedlagda kursplaner finns låter vi den auktoritativa
    # ``nedlagd-förkunskapskrav``-checken hantera de fynd vi *bekräftat* — då
    # ska vi inte också rapportera samma kandidat som "troligen nedlagd",
    # det blir bara dubbletter i analysfilerna.
    try:
        from checks_nedlagda import load_index as _load_nedlagda
        nedlagda_index = _load_nedlagda()
    except Exception:
        nedlagda_index = None

    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        sec = extract_section(body, "Förkunskapskrav").strip()
        if not sec:
            continue
        reported: set[str] = set()
        for b in FORKUNSKAP_BULLET_RE.finditer(sec):
            line = b.group(1).strip()
            if not FORKUNSKAP_HP_RE.search(line):
                continue
            candidates: set[str] = set()
            for m in FORKUNSKAP_KURSEN_RE.finditer(line):
                candidates.add(m.group(1).strip())
            for m in FORKUNSKAP_LINE_LEAD_RE.finditer(line):
                candidates.add(m.group(1).strip())
            for title in candidates:
                first = title.split(maxsplit=1)[0].lower()
                if first in FORKUNSKAP_STOPWORDS or len(title) < 8:
                    continue
                norm = _normalize_title(title)
                if norm in title_index:
                    continue
                if any(vt in norm or norm in vt for vt in long_titles):
                    continue
                if title in reported:
                    continue
                # Bekräftat nedlagd → låt den hårda checken hantera fyndet.
                if nedlagda_index is not None and nedlagda_index.lookup_name(
                    title, subject=subject(p)
                ):
                    continue
                reported.add(title)
                findings.append({
                    "check": "förkunskap-okand-kurs",
                    "code": course_code(p),
                    "subj": subject(p),
                    "detail": f"Refererad kurs hittas ej i vaulten (troligen nedlagd): {title!r}",
                })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 18-19 — Övrigt
# ─────────────────────────────────────────────────────────────────────────────
OVRIGT_BOILERPLATE_RE = re.compile(r"pedagogiskt stöd från Högskolan Dalarna")


def check_ovrigt(files: list[Path]) -> list[dict]:
    """Två kontroller på `## Övrigt`-sektionen:

    1. ``övrigt-saknas`` — ingen Övrigt-sektion finns.
    2. ``övrigt-utan-boilerplate`` — sektionen finns men saknar standardfrasen
       om riktat pedagogiskt stöd från Högskolan Dalarna. Den frasen är central
       för studenter med funktionsnedsättning som behöver anpassad examination.
    """
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        sec = extract_section(body, "Övrigt").strip()
        if not sec:
            findings.append({
                "check": "övrigt-saknas",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Ingen Övrigt-sektion i kursplanen",
            })
            continue
        if not OVRIGT_BOILERPLATE_RE.search(sec):
            snippet = " ".join(sec.split())[:120]
            findings.append({
                "check": "övrigt-utan-boilerplate",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"Saknar standardfras om pedagogiskt stöd: {snippet}…",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 12-15 — Förkunskapskrav
# ─────────────────────────────────────────────────────────────────────────────
EN_PREREQ_RE = re.compile(
    r"^### Prerequisites\s*\n(.+?)(?=^#{2,3}\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
def _extract_en_prerequisites(body: str) -> str | None:
    """Returnera engelska Prerequisites-sektionen om English Version finns,
    annars None. Tom sträng betyder att rubriken finns men saknar innehåll."""
    if not EN_VERSION_RE.search(body):
        return None
    m = EN_PREREQ_RE.search(body)
    return m.group(1).strip() if m else ""


def check_forkunskap(files: list[Path]) -> list[dict]:
    """Kvalitetskontroll av förkunskapskravssektionen. Flaggar två mönster:

    1. ``förkunskap-saknas`` — varken svensk eller engelsk sektion finns.
    2. ``förkunskap-bara-engelska`` — engelska finns men svenska saknas
       (vanligaste tecknet på en luckig svensk källsida).
    """
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        sv = extract_section(body, "Förkunskapskrav").strip()
        en = _extract_en_prerequisites(body)

        if not sv:
            if en:
                findings.append({
                    "check": "förkunskap-bara-engelska",
                    "code": course_code(p),
                    "subj": subject(p),
                    "detail": f"Engelska Prerequisites finns ({len(en)} tecken) men svenska saknas",
                })
            else:
                findings.append({
                    "check": "förkunskap-saknas",
                    "code": course_code(p),
                    "subj": subject(p),
                    "detail": "Ingen förkunskapssektion i kursplanen",
                })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Rapport
# ─────────────────────────────────────────────────────────────────────────────

CHECK_LABELS = {
    "dubblerat-ord":         "Dubblerat ord",
    "känd-felstavning":      "Känd felstavning",
    "stavning-sv":           "Stavfel (svenska)",
    "stavning-en":           "Stavfel (engelska)",
    "introfras-fore-fras":   "Introfras före frasning",
    "frasning-avviker":      "Frasning avviker",
    "betygsskala-inkonsekvent": "Betygsskala inkonsekvent",
    "betyg-saknar-punktlista": "Betyg saknar punktlista",
    "övrigt-saknas":          "Övrigt saknas",
    "övrigt-utan-boilerplate": "Övrigt utan pedagogiskt-stöd-fras",
    "examinationsformer-utan-punktlista": "Examinationsformer utan punktlista",
    "omfång-få-mål":         "För få lärandemål",
    "omfång-många-mål":      "För många lärandemål",
    "långt-lärandemål":      "Långt lärandemål",
    "bloom-låg-avancerad":   "Bloom-nivå låg (avancerad kurs)",
    "bloom-hög-grund":       "Bloom-nivå hög (grundkurs)",
    "bloom-okant-verb":      "Bloom okänt verb",
    "sv-en-paritet":         "Paritetsskillnad sv/en",
    "lo-saknar-bullets-sv":  "Lärandemål saknar punktlista (sv)",
    "lo-saknar-bullets-en":  "Lärandemål saknar punktlista (en)",
    "förkunskap-saknas":     "Förkunskapskrav saknas",
    "förkunskap-bara-engelska": "Förkunskapskrav endast på engelska",
    "förkunskap-okand-kurs": "Förkunskapskrav refererar troligen nedlagd kurs",
    "nedlagd-förkunskapskrav": "Förkunskapskrav refererar bekräftat nedlagd kurs",
}


def main():
    parser = argparse.ArgumentParser(description="Kvalitetskontroll kursplaner")
    parser.add_argument("--out", metavar="FIL", help="Spara rapport till FIL.md")
    parser.add_argument("--skip-hunspell", action="store_true",
                        help="Hoppa över hunspell-körningar (snabbare)")
    args = parser.parse_args()

    files = load_files()
    print(f"Läser {len(files)} kursplansfiler…", file=sys.stderr)

    all_findings = []

    steps = [
        ("Dubblerade ord",           check_dup_words),
        ("Kända felstavningar",      check_known_typos),
        ("Introfras",                check_introfras),
        ("Frasningskonsistens",      check_frasning),
        ("Betygsskala",              check_betygsskala),
        ("Betyg-punktlista",         check_betyg_punktlista),
        ("Examinationsformer-format", check_examinationsformer_format),
        ("Omfång lärandemål",        check_omfang),
        ("Långa bullets",            check_long_bullets),
        ("Bloom-taxonomi",           check_bloom),
        ("Paritet sv/en",            check_sv_en_parity),
        ("Lärandemål-punktlista",    check_lo_bullets),
        ("Förkunskapskrav",          check_forkunskap),
        ("Förkunskap-okänd-kurs",    check_forkunskap_okand_kurs),
        ("Övrigt",                   check_ovrigt),
    ]

    # Bekräftat-nedlagda-check körs bara om QA-cachen är populerad.
    try:
        from checks_nedlagda import check_nedlagda_prereqs_kurs, load_index
        if len(load_index()) > 0:
            steps.append(("Förkunskap-bekräftat-nedlagd", check_nedlagda_prereqs_kurs))
    except ImportError:
        pass

    if not args.skip_hunspell:
        steps.insert(2, ("Hunspell svenska", check_hunspell_sv))
        steps.insert(3, ("Hunspell engelska", check_hunspell_en))

    for label, fn in steps:
        print(f"  {label}…", file=sys.stderr)
        found = fn(files)
        all_findings.extend(found)
        print(f"    → {len(found)} fynd", file=sys.stderr)

    report = build_report("QA-rapport kursplaner", all_findings, files, CHECK_LABELS)

    print(report)

    if args.out:
        out_path = Path(args.out)
        if not out_path.suffix:
            out_path = out_path.with_suffix(".md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"\nRapport sparad till {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
