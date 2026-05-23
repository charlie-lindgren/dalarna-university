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
  14. Förkunskapskrav — osannolikt kort innehåll
  15. Förkunskapskrav — stor sv/en-längdskillnad
  16. Betyg — sektionen saknar punktlista (rapportering i löpande text)
  17. Innehåll — sektionen är ett enda stycke trots flera meningar
  18. Innehåll — sektionen är en stub/platshållare (< 80 tecken)
  19. Innehåll — modulrubrik utan hp-angivelse
  20. Övrigt — sektionen saknas helt
  21. Övrigt — saknar standardfras om pedagogiskt stöd
  22. Terminologi — blandar 'studenten' och 'den studerande'
  23. Terminologi — blandar 'ska' och 'skall'
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
            files.extend(p for p in kp.rglob("*.md") if "MOC" not in p.name)
    return sorted(files)


# ─────────────────────────────────────────────────────────────────────────────
# Check 5a — Introfras (rubriken följs direkt av en *Efter ...*-fras)
# Check 5b — Frasningskonsistens (introfras matchar referensformen)
# ─────────────────────────────────────────────────────────────────────────────
GOLD_INTRO_TEXT = "Efter godkänd kurs ska studenten kunna:"
DELKURS_INTRO_TEXT = "Efter avslutad delkurs ska den studerande kunna:"

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
MIXED_SCALE_RE = re.compile(r"\bU\s*[,/]\s*3\b.*?\bU\s*[,/]\s*[GV]", re.DOTALL | re.IGNORECASE)
MIXED_SCALE_EXEMPT: set[str] = {
    "GBY2ME", "GBY2NG", "GBY2V5",
    "BFY227", "FY1018",
    "EG3019", "GEG2UE",
}


def check_betygsskala(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        betyg_section = extract_section(body, "Betyg")
        if not betyg_section:
            continue
        if MIXED_SCALE_RE.search(betyg_section) and course_code(p) not in MIXED_SCALE_EXEMPT:
            findings.append({
                "check": "betygsskala-inkonsekvent",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Inkonsekvent delskalor: kursnivå U,3,4,5 men delmoment i U,G,VG",
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
# Check 17 — Innehåll utan styckeindelning
# ─────────────────────────────────────────────────────────────────────────────
SENTENCE_END_RE = re.compile(r"[.!?](?=\s+[A-ZÅÄÖ]|\s*$)")
INNEHALL_RUNON_MIN_SENTENCES = 4
INNEHALL_RUNON_MIN_CHARS = 400


INNEHALL_STUB_MAX_CHARS = 80
INNEHALL_MODUL_RE = re.compile(r"\b[MmDd](?:odul|elkurs)\s+\d+\b")
HP_MENTION_RE = re.compile(r"\b\d+(?:[,.]\d+)?\s*hp\b|högskolepoäng\b", re.IGNORECASE)


def check_innehall_stub(files: list[Path]) -> list[dict]:
    """Flagga kursplaner vars `## Innehåll`-sektion är så kort att den ser ut
    som en platshållartext (t.ex. *"Innehåll saknas."* eller *"Kursen består
    av tre delkurser."* utan beskrivning av delkurserna)."""
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        sec = extract_section(body, "Innehåll").strip()
        if not sec or len(sec) >= INNEHALL_STUB_MAX_CHARS:
            continue
        findings.append({
            "check": "innehåll-stub",
            "code": course_code(p),
            "subj": subject(p),
            "detail": f"Osannolikt kort ({len(sec)} tecken): {sec!r}",
        })
    return findings


def check_innehall_modul_utan_hp(files: list[Path]) -> list[dict]:
    """Flagga kursplaner där `## Innehåll` refererar till moduler eller
    delkurser men ingen hp-angivelse finns i sektionen. Modulrubriker utan hp
    gör det svårt att se hur kursens totala hp-summa fördelar sig."""
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        sec = extract_section(body, "Innehåll").strip()
        if not sec:
            continue
        m = INNEHALL_MODUL_RE.search(sec)
        if not m:
            continue
        if HP_MENTION_RE.search(sec):
            continue
        findings.append({
            "check": "innehåll-modul-utan-hp",
            "code": course_code(p),
            "subj": subject(p),
            "detail": f"Modulrubrik utan hp-angivelse: {m.group(0)!r}",
        })
    return findings


def check_innehall_styckeindelning(files: list[Path]) -> list[dict]:
    """Flagga kursplaner vars `## Innehåll`-sektion består av ett enda långt
    stycke (ingen blankrad mellan logiska avsnitt) men ändå innehåller flera
    meningar. Konventionen är att längre innehållsbeskrivningar styckeindelas
    så att läsbarheten håller; en monolitisk textmassa skymmer strukturen."""
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        sec = extract_section(body, "Innehåll").strip()
        if not sec:
            continue
        paragraphs = [pp for pp in re.split(r"\n\s*\n", sec) if pp.strip()]
        if len(paragraphs) > 1:
            continue
        txt = paragraphs[0]
        sentences = len(SENTENCE_END_RE.findall(txt))
        if sentences >= INNEHALL_RUNON_MIN_SENTENCES and len(txt) >= INNEHALL_RUNON_MIN_CHARS:
            snippet = " ".join(txt.split())[:120]
            findings.append({
                "check": "innehåll-ostyckat",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"{sentences} meningar i ett stycke ({len(txt)} tecken): {snippet}…",
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
# Check 20 — Terminologi-blandning
# ─────────────────────────────────────────────────────────────────────────────
STUDENTEN_RE = re.compile(r"\bstudenten\b")
DEN_STUDERANDE_RE = re.compile(r"\bden studerande\b")
SKA_RE = re.compile(r"\bska\b")
SKALL_RE = re.compile(r"\bskall\b")


def _strip_to_swedish(raw: str) -> str:
    body = strip_frontmatter(raw)
    return re.sub(r"\n## English Version.+", "", body, flags=re.DOTALL)


def check_terminologi(files: list[Path]) -> list[dict]:
    """Flagga kursplaner som blandar olika varianter av samma term inom den
    svenska delen. Två blandningar fångas:

    1. ``terminologi-studenten-blandning`` — *studenten* och *den studerande*
       förekommer båda. Stilguider rekommenderar att man väljer en.
    2. ``terminologi-ska-skall-blandning`` — *ska* och *skall* förekommer båda;
       *skall* är ålderdomligt och bör harmoniseras till *ska*.
    """
    findings = []
    for p in files:
        sv = _strip_to_swedish(p.read_text(encoding="utf-8"))
        if STUDENTEN_RE.search(sv) and DEN_STUDERANDE_RE.search(sv):
            findings.append({
                "check": "terminologi-studenten-blandning",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Blandar 'studenten' och 'den studerande' i samma kursplan",
            })
        if SKA_RE.search(sv) and SKALL_RE.search(sv):
            findings.append({
                "check": "terminologi-ska-skall-blandning",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Blandar 'ska' och 'skall' i samma kursplan",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 12-15 — Förkunskapskrav
# ─────────────────────────────────────────────────────────────────────────────
EN_PREREQ_RE = re.compile(
    r"^### Prerequisites\s*\n(.+?)(?=^#{2,3}\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
FORKUNSKAP_TUNN_MIN_CHARS = 25
FORKUNSKAP_PARITY_MIN_CHARS = 30
FORKUNSKAP_PARITY_RATIO = 2.0


def _extract_en_prerequisites(body: str) -> str | None:
    """Returnera engelska Prerequisites-sektionen om English Version finns,
    annars None. Tom sträng betyder att rubriken finns men saknar innehåll."""
    if not EN_VERSION_RE.search(body):
        return None
    m = EN_PREREQ_RE.search(body)
    return m.group(1).strip() if m else ""


def check_forkunskap(files: list[Path]) -> list[dict]:
    """Kvalitetskontroll av förkunskapskravssektionen. Flaggar fyra mönster:

    1. ``förkunskap-saknas`` — varken svensk eller engelsk sektion finns.
    2. ``förkunskap-bara-engelska`` — engelska finns men svenska saknas
       (vanligaste tecknet på en luckig svensk källsida).
    3. ``förkunskap-tunn`` — svensk text är osannolikt kort (< 25 tecken),
       t.ex. ``- Lärarexamen`` utan ämnesangivelse.
    4. ``förkunskap-paritet`` — svensk och engelsk text skiljer sig mer än 2×
       i längd (båda måste vara över 30 tecken för att räknas).
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
            continue

        if len(sv) < FORKUNSKAP_TUNN_MIN_CHARS:
            findings.append({
                "check": "förkunskap-tunn",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"Osannolikt kort ({len(sv)} tecken): {sv!r}",
            })

        if en and len(sv) >= FORKUNSKAP_PARITY_MIN_CHARS and len(en) >= FORKUNSKAP_PARITY_MIN_CHARS:
            ratio = max(len(sv), len(en)) / min(len(sv), len(en))
            if ratio >= FORKUNSKAP_PARITY_RATIO:
                findings.append({
                    "check": "förkunskap-paritet",
                    "code": course_code(p),
                    "subj": subject(p),
                    "detail": f"Längdskillnad sv {len(sv)} tecken vs en {len(en)} tecken (×{ratio:.1f})",
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
    "innehåll-ostyckat":      "Innehåll ostyckat",
    "innehåll-stub":          "Innehåll stub/platshållare",
    "innehåll-modul-utan-hp": "Innehåll modul utan hp",
    "övrigt-saknas":          "Övrigt saknas",
    "övrigt-utan-boilerplate": "Övrigt utan pedagogiskt-stöd-fras",
    "terminologi-studenten-blandning": "Blandar studenten/den studerande",
    "terminologi-ska-skall-blandning": "Blandar ska/skall",
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
    "förkunskap-tunn":       "Förkunskapskrav osannolikt kort",
    "förkunskap-paritet":    "Förkunskapskrav paritet sv/en",
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
        ("Innehåll-styckeindelning", check_innehall_styckeindelning),
        ("Innehåll-stub",            check_innehall_stub),
        ("Innehåll-modul-utan-hp",   check_innehall_modul_utan_hp),
        ("Övrigt",                   check_ovrigt),
        ("Terminologi",              check_terminologi),
    ]

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
