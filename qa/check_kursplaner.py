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
  5.  Frasningskonsistens lärandemål (introfras)
  6.  Betygsskala — A–F-avvikare + inkonsekvent delskalor
  7.  Examinationsformer — rena prosabeskrivningar saknar kod/bullet
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

ROOT = Path(__file__).resolve().parent.parent / "vault-dalarna-university" / "01 Kursplaner"


def load_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.md") if "MOC" not in p.name)


# ─────────────────────────────────────────────────────────────────────────────
# Check 5 — Frasningskonsistens (introfras lärandemål)
# ─────────────────────────────────────────────────────────────────────────────
GOLD_INTRO = re.compile(
    r"efter\s+godkänd\s+kurs\s+ska\s+studenten\s+kunna\s*:",
    re.IGNORECASE,
)
GOLD_NO_COLON = re.compile(
    r"efter\s+godkänd\s+kurs\s+ska\s+studenten\s+kunna(?!\s*:)",
    re.IGNORECASE,
)
DELKURS_EXEMPT = re.compile(
    r"efter\s+avslutad\s+delkurs\s+ska\s+den\s+studerande\s+kunna\s*:",
    re.IGNORECASE,
)


def check_framing(files: list[Path]) -> list[dict]:
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
        if GOLD_INTRO.search(lo_section):
            continue
        if DELKURS_EXEMPT.search(lo_section):
            continue
        if GOLD_NO_COLON.search(lo_section):
            findings.append({
                "check": "introfras-kolon",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Saknar kolon: `Efter godkänd kurs ska studenten kunna`",
            })
        else:
            snippet = lo_section[:120].replace("\n", " ").strip()
            findings.append({
                "check": "introfras-avviker",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"Avvikande introfras: {snippet}…",
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
        if AF_RE.search(betyg_section):
            findings.append({
                "check": "betygsskala-AF",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Avvikande betygsskala: A–F istället för U/G/VG eller U/3/4/5",
            })
        if MIXED_SCALE_RE.search(betyg_section) and course_code(p) not in MIXED_SCALE_EXEMPT:
            findings.append({
                "check": "betygsskala-inkonsekvent",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Inkonsekvent delskalor: kursnivå U,3,4,5 men delmoment i U,G,VG",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 7 — Examinationsformer utan strukturerad lista
# ─────────────────────────────────────────────────────────────────────────────
EXAM_CODE_RE = re.compile(r"\b(TEN|LAB|INL|SEM|PRO|MUN|UPP|OPP|HEM|KON)\b")
BULLET_RE = re.compile(r"^\s*[-*]", re.MULTILINE)


def check_exam_structure(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        exam_section = extract_section(body, "Examinationsformer")
        if not exam_section:
            continue
        has_code = EXAM_CODE_RE.search(exam_section)
        has_bullets = BULLET_RE.search(exam_section)
        if not has_code and not has_bullets:
            findings.append({
                "check": "exam-ingen-struktur",
                "code": course_code(p),
                "subj": subject(p),
                "detail": "Examinationsformer saknar examinationskod (TEN/LAB/INL…) och bullets",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 8 — Omfång lärandemål
# ─────────────────────────────────────────────────────────────────────────────
LO_BULLET_RE = re.compile(r"^\s*[-*]\s+.+", re.MULTILINE)
LO_MIN = 4
LO_MAX = 12


def check_omfang(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        lo_section = extract_section(body, "Lärandemål")
        if not lo_section:
            continue
        bullets = LO_BULLET_RE.findall(lo_section)
        n = len(bullets)
        if n < LO_MIN:
            findings.append({
                "check": "omfång-få-mål",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"{n} lärandemål (minimum rekommenderat: {LO_MIN})",
            })
        elif n > LO_MAX:
            findings.append({
                "check": "omfång-många-mål",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"{n} lärandemål (maximum rekommenderat: {LO_MAX})",
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
PARITY_THRESHOLD = 2
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
    "introfras-kolon":       "Introfras saknar kolon",
    "introfras-avviker":     "Introfras avviker",
    "betygsskala-AF":        "Betygsskala A–F",
    "betygsskala-inkonsekvent": "Betygsskala inkonsekvent",
    "exam-ingen-struktur":   "Examinationsformer – ingen struktur",
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
        ("Frasningskonsistens",      check_framing),
        ("Betygsskala",              check_betygsskala),
        ("Examinationsformer",       check_exam_structure),
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
