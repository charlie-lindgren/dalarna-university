#!/usr/bin/env python3
"""
Kvalitetskontroll av alla utbildningsplaner i
vault-dalarna-university/02 Utbildningsplaner/.

Reducerad checkuppsättning jämfört med kursplaner — utbildningsplaner saknar
strukturen ## Lärandemål / ## Examinationsformer / ## Betyg, så bara språk-
och stavningskontroller körs:

  1. Dubblerade ord
  2. Kända felstavningar
  3. Hunspell stavning svenska (sv_SE)
  4. Hunspell stavning engelska (en_US) — om en English Version-sektion finns

Körning:
    python3 qa/check_utbildningsplaner.py
    python3 qa/check_utbildningsplaner.py --out qa/rapporter-utb/rapport.md
    python3 qa/check_utbildningsplaner.py --skip-hunspell
"""

import argparse
import sys
from pathlib import Path

from checks_common import (
    build_report,
    check_dup_words,
    check_hunspell_en,
    check_hunspell_sv,
    check_known_typos,
)

VAULT = Path(__file__).resolve().parent.parent / "vault-dalarna-university"
INST_DIRS = ["01 IIT", "02 IHV", "03 IKS", "04 ISLL"]


def load_files() -> list[Path]:
    files: list[Path] = []
    for inst in INST_DIRS:
        utb = VAULT / inst / "Utbildningsplaner"
        if utb.exists():
            files.extend(p for p in utb.rglob("*.md") if "MOC" not in p.name)
    return sorted(files)


CHECK_LABELS = {
    "dubblerat-ord":     "Dubblerat ord",
    "känd-felstavning":  "Känd felstavning",
    "stavning-sv":       "Stavfel (svenska)",
    "stavning-en":       "Stavfel (engelska)",
}


def main():
    parser = argparse.ArgumentParser(description="Kvalitetskontroll utbildningsplaner")
    parser.add_argument("--out", metavar="FIL", help="Spara rapport till FIL.md")
    parser.add_argument("--skip-hunspell", action="store_true",
                        help="Hoppa över hunspell-körningar (snabbare)")
    args = parser.parse_args()

    files = load_files()
    print(f"Läser {len(files)} utbildningsplansfiler…", file=sys.stderr)

    all_findings = []

    steps = [
        ("Dubblerade ord",      check_dup_words),
        ("Kända felstavningar", check_known_typos),
    ]
    if not args.skip_hunspell:
        steps.append(("Hunspell svenska",  check_hunspell_sv))
        steps.append(("Hunspell engelska", check_hunspell_en))

    for label, fn in steps:
        print(f"  {label}…", file=sys.stderr)
        found = fn(files)
        all_findings.extend(found)
        print(f"    → {len(found)} fynd", file=sys.stderr)

    report = build_report("QA-rapport utbildningsplaner", all_findings, files, CHECK_LABELS)

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
