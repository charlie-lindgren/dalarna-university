#!/usr/bin/env python3
"""
populate_analysfiler.py — Fyll varje analysfil i vault-dalarna-university/03 Analys/
med fynd från senaste QA-rapporten.

Idempotent: hittar callout-blocket `> [!example]- ... fynd ...` i analysfilen,
och ersätter det med ett nytt block byggt från rapporten. All övrig prosa
(syfte, metod, observationer, rekommendationer) lämnas orörd.

Användning:
    python3 qa/populate_analysfiler.py [--rapport <fil>] [--dry-run]

--rapport   Använd specifik rapport i stället för den senaste.
--dry-run   Visa vad som skulle skrivas, ändra inga filer.
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT    = Path(__file__).resolve().parent.parent
VAULT_ANALYS = REPO_ROOT / "vault-dalarna-university" / "03 Analys"
RAPPORT_DIR  = Path(__file__).resolve().parent / "rapporter"

# Analysfil → (rapport-sektionsprefix → "Problem"-etikett i analystabellen)
ANALYS_FILES: dict[str, dict[str, str]] = {
    "Frasningskonsistens lärandemål.md": {
        "Introfras saknas":      "Introfras saknas",
        "Introfras saknar kolon": "Saknar kolon",
        "Introfras avviker":     "Avvikande formulering",
    },
    "Stavfel och språkbruk.md": {
        "Dubblerat ord":      "Dubblerat ord",
        "Känd felstavning":   "Felstavning",
        "Stavfel (svenska)":  "Felstavning",
        "Stavfel (engelska)": "Felstavning (en)",
    },
    "Betygsskalor.md": {
        "Betygsskala A–F":          "A–F-skala",
        "Betygsskala inkonsekvent": "Inkonsekvent delskalor",
    },
    "Examinationsformer.md": {
        "Examinationsformer – ingen struktur": "Saknar struktur",
    },
    "Omfång på lärandemål.md": {
        "För få lärandemål":   "För få mål",
        "För många lärandemål": "För många mål",
        "Långt lärandemål":    "Långt mål",
    },
    "Bloom-taxonomi.md": {
        "Bloom-nivå låg (avancerad kurs)": "Låg Bloom-nivå",
    },
    "Samstämmighet svenska och engelska.md": {
        "Paritetsskillnad sv/en": "Paritetsskillnad",
    },
}

KURSPLAN_URL = "https://www.du.se/sv/utbildning/kurser/kursplan/?code={code}"

# ─────────────────────────────────────────────────────────────────────────────
# Rapportparsning
# ─────────────────────────────────────────────────────────────────────────────
SECTION_RE = re.compile(r"^##\s+(.+?)\s*\(\d+")
ROW_RE = re.compile(r"^\|\s*([A-ZÅÄÖ0-9][A-Z0-9]{2,8})\s*\|\s*([A-ZÅÄÖ0-9]+)\s*\|(.+?)\|?\s*$")


def parse_rapport(path: Path) -> list[tuple[str, str, str, str]]:
    rows = []
    current_section = "Okänd"
    for line in path.read_text(encoding="utf-8").splitlines():
        m_sec = SECTION_RE.match(line)
        if m_sec:
            current_section = m_sec.group(1).strip()
            continue
        m_row = ROW_RE.match(line)
        if m_row:
            code = m_row.group(1).strip()
            subj = m_row.group(2).strip()
            detail = m_row.group(3).strip().rstrip("|").strip()
            if code.lower() in ("kod", "---"):
                continue
            rows.append((current_section, code, subj, detail))
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Callout-byggare
# ─────────────────────────────────────────────────────────────────────────────

def build_callout(rows: list[tuple[str, str, str]]) -> list[str]:
    """rows = [(code, subj, problem_label, detail), ...] -> callout lines."""
    n = len(rows)
    lines = [
        f"> [!example]- {n} fynd — klicka för att expandera",
        ">",
        "> | Kursplan | Ämne | Problem | Detalj |",
        "> | --- | --- | --- | --- |",
    ]
    for code, subj, problem, detail in rows:
        url = KURSPLAN_URL.format(code=code)
        lines.append(f"> | [{code}]({url}) | {subj} | {problem} | {detail} |")
    return lines


# ─────────────────────────────────────────────────────────────────────────────
# Filersättning
# ─────────────────────────────────────────────────────────────────────────────
CALLOUT_START_RE = re.compile(r"^>\s*\[!example\]")


def replace_callout(text: str, new_callout_lines: list[str]) -> str | None:
    """Replace the first `> [!example]…` callout block in text with the new lines.

    Block boundary: starts at the [!example] line; ends at the first line that
    does not start with `>` (blank line, prose, heading, etc.).
    Returns the new text, or None if no callout was found.
    """
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if CALLOUT_START_RE.match(line):
            start = i
            break
    if start is None:
        return None

    end = start + 1
    while end < len(lines) and lines[end].startswith(">"):
        end += 1

    new_lines = lines[:start] + new_callout_lines + lines[end:]
    return "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")


# ─────────────────────────────────────────────────────────────────────────────
# Färger
# ─────────────────────────────────────────────────────────────────────────────
BOLD   = "\033[1m"
GREEN  = "\033[0;32m"
YELLOW = "\033[0;33m"
CYAN   = "\033[0;36m"
RESET  = "\033[0m"


# ─────────────────────────────────────────────────────────────────────────────
# Huvud
# ─────────────────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args

    rapport_path = None
    if "--rapport" in args:
        idx = args.index("--rapport")
        rapport_path = Path(args[idx + 1])
    else:
        rapporter = sorted(RAPPORT_DIR.glob("rapport-*.md"))
        if not rapporter:
            print("Fel: Ingen rapport hittad i qa/rapporter/.", file=sys.stderr)
            sys.exit(1)
        rapport_path = rapporter[-1]

    print(f"\n{CYAN}{BOLD}Populera analysfilerna{RESET}")
    print(f"  Rapport: {rapport_path.name}")
    if dry_run:
        print(f"  {YELLOW}DRY-RUN — inga filer skrivs{RESET}")
    print()

    rapport_rows = parse_rapport(rapport_path)

    by_section: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for sec, code, subj, detail in rapport_rows:
        by_section[sec].append((code, subj, detail))

    for filename, section_map in ANALYS_FILES.items():
        analys_path = VAULT_ANALYS / filename
        if not analys_path.exists():
            print(f"  {filename:<50}  {YELLOW}saknas — hoppar över{RESET}")
            continue

        rows: list[tuple[str, str, str, str]] = []
        for section_label, problem_label in section_map.items():
            for code, subj, detail in by_section.get(section_label, []):
                rows.append((code, subj, problem_label, detail))

        rows.sort(key=lambda r: (r[1], r[0]))  # sort by subj, then code

        callout_lines = build_callout(rows)

        original = analys_path.read_text(encoding="utf-8")
        new_text = replace_callout(original, callout_lines)

        if new_text is None:
            print(f"  {filename:<50}  {YELLOW}inget callout-block hittades — hoppar över{RESET}")
            continue

        if new_text == original:
            print(f"  {filename:<50}  {len(rows):>4} fynd  (oförändrad)")
            continue

        verb = "skulle skrivas" if dry_run else "skrev"
        print(f"  {filename:<50}  {len(rows):>4} fynd  {GREEN}{verb}{RESET}")

        if not dry_run:
            analys_path.write_text(new_text, encoding="utf-8")

    print()


if __name__ == "__main__":
    main()
