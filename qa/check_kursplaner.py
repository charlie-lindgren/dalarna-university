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
  5b. Frasningskonsistens (gold standard + tom rad)
  6.  Betygsskala — inkonsekvent delskalor
  7.  Examinationsformer — hp-summa i Betyg matchar inte kursens hp
  8.  Omfång lärandemål — för få (< 4) eller för många (> 12)
  9.  Långa bullets (> 25 ord)
  10. Bloom-taxonomi — avancerade kurser med enbart låga nivåer
  11. Svenska/engelska paritet — stor skillnad i antal lärandemål
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
# Check 5a — Introfras (existens)
# Check 5b — Frasningskonsistens (gold-standard match + tom rad före punktlista)
# ─────────────────────────────────────────────────────────────────────────────
GOLD_INTRO_TEXT = "Efter godkänd kurs ska studenten kunna:"
GOLD_INTRO_RE = re.compile(re.escape(GOLD_INTRO_TEXT))
# Lös regex för att avgöra om en introfras alls existerar (något i stil med
# "Efter ... kunna" eller "studenten ska ..."). Räcker för att skilja "ingen
# introfras alls" från "introfras som avviker från gold standard".
ANY_INTRO_RE = re.compile(
    r"(?:efter\b.{0,80}\bkunna|studenten\s+(?:ska(?:ll)?|skall)\b.{0,80}\bkunna|"
    r"kursens\s+\S+\s+m[åa]l\b|m[åa]let\s+med\s+kursen\b)",
    re.IGNORECASE | re.DOTALL,
)
DELKURS_EXEMPT_RE = re.compile(
    r"efter\s+avslutad\s+delkurs\s+ska\s+den\s+studerande\s+kunna\s*:",
    re.IGNORECASE,
)


def _first_bullet_match(text: str) -> re.Match | None:
    return LO_BULLET_RE.search(text)


def check_introfras(files: list[Path]) -> list[dict]:
    """Finns en introfras före lärandemålen alls?"""
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        lo_section = extract_section(body, "Lärandemål")
        if not lo_section:
            findings.append({
                "check": "introfras-saknas",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Saknar ## Lärandemål-sektion",
            })
            continue
        first_bullet = _first_bullet_match(lo_section)
        if first_bullet is None:
            findings.append({
                "check": "introfras-saknas",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Saknar punktlista med lärandemål",
            })
            continue
        before = lo_section[: first_bullet.start()]
        if not ANY_INTRO_RE.search(before):
            findings.append({
                "check": "introfras-saknas",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Saknar introfras före lärandemålen",
            })
    return findings


def check_frasning(files: list[Path]) -> list[dict]:
    """Matchar introfrasen exakt 'Efter godkänd kurs ska studenten kunna:' och
    finns en tom rad mellan frasen och första punktlistan?"""
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        lo_section = extract_section(body, "Lärandemål")
        if not lo_section:
            continue
        if DELKURS_EXEMPT_RE.search(lo_section):
            continue
        first_bullet = _first_bullet_match(lo_section)
        if first_bullet is None:
            continue
        before = lo_section[: first_bullet.start()]
        if not ANY_INTRO_RE.search(before):
            # Existens-fallet hanteras av check_introfras.
            continue
        m_gold = GOLD_INTRO_RE.search(before)
        if not m_gold:
            snippet = before.strip().replace("\n", " ")[:120]
            findings.append({
                "check": "frasning-avviker",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"Avviker från gold standard: {snippet}…",
            })
            continue
        between = before[m_gold.end():]
        # Kräv minst en tom rad (\n\n) mellan introfrasen och första bulleten.
        if "\n\n" not in between:
            findings.append({
                "check": "frasning-utan-blankrad",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Saknar tom rad mellan introfras och lärandemål",
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
# Check 7 — hp-summa i Betyg matchar inte kursens hp
# ─────────────────────────────────────────────────────────────────────────────
COMPONENT_HP_RE = re.compile(r"[-*].*?(\d+(?:[,.]\d+)?)\s*hp", re.IGNORECASE)
TOTAL_HP_RE = re.compile(r"^hp:\s*(\d+(?:[,.]\d+)?)", re.MULTILINE)
BETYG_SECTION_RE = re.compile(
    r"^## Betyg\s*\n(.+?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
)


def check_hp_sum(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        raw = p.read_text(encoding="utf-8")
        m_hp = TOTAL_HP_RE.search(raw)
        if not m_hp:
            continue
        course_hp = float(m_hp.group(1).replace(",", "."))
        body = strip_frontmatter(raw)
        m_betyg = BETYG_SECTION_RE.search(body)
        if not m_betyg:
            continue
        components = COMPONENT_HP_RE.findall(m_betyg.group(1))
        if not components:
            continue
        comp_sum = sum(float(x.replace(",", ".")) for x in components)
        if abs(comp_sum - course_hp) > 0.1:
            findings.append({
                "check": "betyg-hp-summa",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"Betygsmoduler summerar till {comp_sum} hp, kursäns hp är {course_hp} hp",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 8 — Omfång lärandemål
# ─────────────────────────────────────────────────────────────────────────────
LO_BULLET_RE = re.compile(r"^\s*[-*]\s+.+", re.MULTILINE)


def lo_bounds(hp: float) -> tuple[int, int]:
    """Rimligt antal lärandemål skalat efter kursens hp."""
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
# Check 10 — Bloom (avancerade kurser med enbart låga nivåer)
# ─────────────────────────────────────────────────────────────────────────────
BLOOM_LOW = {
    "redogöra", "beskriva", "definiera", "namnge", "identifiera", "lista",
    "återge", "ange", "förklara", "sammanfatta", "tolka", "klassificera",
    "jämföra", "känna", "förstå",
}
BLOOM_HIGH = {
    "analysera", "utvärdera", "bedöma", "kritiskt", "granska", "värdera",
    "motivera", "argumentera", "skapa", "utforma", "konstruera", "designa",
    "utveckla", "planera", "genomföra", "lösa", "tillämpa", "implementera",
    "integrera", "syntetisera", "föreslå", "reflektera", "diskutera",
}


def check_bloom(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        code = course_code(p)
        if not code.startswith(("A", "G2")):
            continue
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        lo_section = extract_section(body, "Lärandemål")
        if not lo_section:
            continue
        words = set(re.findall(r"\b\w+\b", lo_section.lower()))
        has_high = bool(words & BLOOM_HIGH)
        has_low = bool(words & BLOOM_LOW)
        if has_low and not has_high:
            findings.append({
                "check": "bloom-låg-avancerad",
                "code": code,
                "subj": subject(p),
                "detail": "Avancerad kurs utan höga Bloom-verb (analysera/utvärdera/skapa…)",
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


def check_sv_en_parity(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        sv_lo = extract_section(body, "Lärandemål")
        m = EN_LO_RE.search(body)
        en_lo = m.group(1) if m else ""
        if not sv_lo or not en_lo:
            continue
        sv_n = len(LO_BULLET_RE.findall(sv_lo))
        en_n = len(LO_BULLET_RE.findall(en_lo))
        if abs(sv_n - en_n) > PARITY_THRESHOLD:
            findings.append({
                "check": "sv-en-paritet",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"Svenska: {sv_n} mål, engelska: {en_n} mål (diff {abs(sv_n-en_n)})",
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
    "introfras-saknas":      "Introfras saknas",
    "frasning-avviker":      "Frasning avviker",
    "frasning-utan-blankrad": "Frasning utan blankrad",
    "betygsskala-inkonsekvent": "Betygsskala inkonsekvent",
    "omfång-få-mål":         "För få lärandemål",
    "omfång-många-mål":      "För många lärandemål",
    "långt-lärandemål":      "Långt lärandemål",
    "bloom-låg-avancerad":   "Bloom-nivå låg (avancerad kurs)",
    "sv-en-paritet":         "Paritetsskillnad sv/en",
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
        ("Omfång lärandemål",        check_omfang),
        ("Långa bullets",            check_long_bullets),
        ("Bloom-taxonomi",           check_bloom),
        ("Paritet sv/en",            check_sv_en_parity),
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
