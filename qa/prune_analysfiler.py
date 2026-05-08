#!/usr/bin/env python3
"""
prune_analysfiler.py — Ta bort lösta fynd ur analysfilerna i
varje institutions Analys-mapp (vault-dalarna-university/0X {INST}/Analys/).

Jämför kurskodsuppsättningen i varje analyses callout-tabell mot den
senaste QA-rapporten. Rader vars kurskod inte längre finns i rapporten
(under relevanta sektioner) tas bort och callout-rubriken uppdateras.

Användning:
    python3 qa/prune_analysfiler.py [--rapport <fil>] [--dry-run]

--rapport   Använd specifik rapport i stället för den senaste.
--dry-run   Visa vad som skulle tas bort, skriv ingenting.
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT     = Path(__file__).resolve().parent.parent
VAULT         = REPO_ROOT / "vault-dalarna-university"
INST_DIR_NAME = {
    "IIT": "01 IIT",
    "IHV": "02 IHV",
    "IKS": "03 IKS",
    "ISLL": "04 ISLL",
}
RAPPORT_DIR   = Path(__file__).resolve().parent / "rapporter"


def institution_analys_dir(inst_code: str) -> Path:
    return VAULT / INST_DIR_NAME[inst_code] / "Analys"

# ─────────────────────────────────────────────────────────────────────────────
# Konfiguration: vilka rapport-sektioner som "äger" varje analysfil
# ─────────────────────────────────────────────────────────────────────────────
ANALYS_CONFIG: dict[str, list[str]] = {
    "Introfras.md": [
        "Introfras före frasning",
    ],
    "Frasningskonsistens.md": [
        "Frasning avviker",
    ],
    "Stavfel och språkbruk.md": [
        "Dubblerat ord",
        "Känd felstavning",
        "Stavfel (svenska)",
        "Stavfel (engelska)",
    ],
    "Betygsskalor.md": [
        "Betygsskala inkonsekvent",
    ],
    "Examinationsformer.md": [
        "Betygsmoduler hp ≠ kurs hp",
        "Examinationsformer utan punktlista",
    ],
    "Omfång på lärandemål.md": [
        "För få lärandemål",
        "För många lärandemål",
        "Långt lärandemål",
    ],
    "Bloom-taxonomi.md": [
        "Bloom-nivå låg (avancerad kurs)",
        "Bloom-nivå hög (grundkurs)",
        "Bloom okänt verb",
    ],
    "Samstämmighet svenska och engelska.md": [
        "Paritetsskillnad",
    ],
}

PRUNE_MANUAL_ONLY = {
    "Betygsskalor.md",
    "Bloom-taxonomi.md",
    "Samstämmighet svenska och engelska.md",
}

LARGE_DELETION_THRESHOLD = 0.5


SECTION_RE = re.compile(r"^##\s+(.+?)\s*\(\d+")
ROW_RE      = re.compile(r"^\|\s*([A-ZÅÄÖ0-9][A-Z0-9]{2,8})\s*\|")


def parse_rapport(path: Path) -> dict[str, set[str]]:
    by_section: dict[str, set[str]] = defaultdict(set)
    current = "Okänd"
    for line in path.read_text(encoding="utf-8").splitlines():
        m = SECTION_RE.match(line)
        if m:
            current = m.group(1).strip()
            continue
        m = ROW_RE.match(line)
        if m:
            code = m.group(1).strip()
            if code.lower() not in ("kod", "---"):
                by_section[current].add(code)
    return dict(by_section)


def codes_for_sections(rapport: dict[str, set[str]], section_prefixes: list[str]) -> set[str]:
    codes: set[str] = set()
    for sec_title, sec_codes in rapport.items():
        if any(sec_title.startswith(p) for p in section_prefixes):
            codes |= sec_codes
    return codes


CALLOUT_CODE_RE = re.compile(r'<a href="[^"]*">([A-Z][A-Z0-9]+)</a>|\[([A-Z][A-Z0-9]+)\]\(https?://[^\)]+\)')
CALLOUT_COUNT_RE = re.compile(r'^(>\s*\[!example\]-?\s*)(\d+)(.+)$')


def _row_code(line: str) -> str | None:
    m = CALLOUT_CODE_RE.search(line)
    if not m:
        return None
    return m.group(1) or m.group(2)


def prune_analys_file(
    path: Path,
    active_codes: set[str],
    dry_run: bool,
) -> tuple[int, int]:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

    new_lines = []
    rows_before = 0
    removed = []
    in_callout = False

    for line in lines:
        if re.match(r'>\s*\[!example\]', line):
            in_callout = True

        if in_callout:
            if not line.startswith(">") and line.strip() != "":
                in_callout = False

        if in_callout:
            code = _row_code(line)
            if code is not None:
                rows_before += 1
                if code not in active_codes:
                    removed.append(code)
                    continue

        new_lines.append(line)

    rows_removed = len(removed)
    if rows_removed == 0:
        return rows_before, 0

    updated = []
    for line in new_lines:
        m = CALLOUT_COUNT_RE.match(line.rstrip("\n"))
        if m:
            new_count = rows_before - rows_removed
            line = m.group(1) + str(new_count) + m.group(3) + "\n"
        updated.append(line)

    if not dry_run:
        path.write_text("".join(updated), encoding="utf-8")

    return rows_before, rows_removed


BOLD   = "\033[1m"
GREEN  = "\033[0;32m"
YELLOW = "\033[0;33m"
CYAN   = "\033[0;36m"
RESET  = "\033[0m"


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args

    rapport_path = None
    if "--rapport" in args:
        idx = args.index("--rapport")
        rapport_path = Path(args[idx + 1])
    else:
        # Pick the most recently modified report (matches both timestamped
        # `rapport-YYYY-MM-DD-HHMM.md` and bare `rapport.md`).
        rapporter = list(RAPPORT_DIR.glob("rapport*.md"))
        if not rapporter:
            print("Fel: Ingen rapport hittad i qa/rapporter/.", file=sys.stderr)
            sys.exit(1)
        rapport_path = max(rapporter, key=lambda p: p.stat().st_mtime)

    print(f"\n{CYAN}{BOLD}Rensa analysfilerna{RESET}")
    print(f"  Rapport: {rapport_path.name}")
    if dry_run:
        print(f"  {YELLOW}DRY-RUN — inga filer skrivs{RESET}")
    print()

    rapport = parse_rapport(rapport_path)

    total_removed = 0
    for filename, section_prefixes in ANALYS_CONFIG.items():
        if filename in PRUNE_MANUAL_ONLY:
            print(f"  {filename:<50} (manuellt kurerad — hoppas över)")
            continue

        active = codes_for_sections(rapport, section_prefixes)

        per_inst_results: list[tuple[str, Path, int, int]] = []
        for inst_code in INST_DIR_NAME:
            analys_path = institution_analys_dir(inst_code) / filename
            if not analys_path.exists():
                continue
            before, removed = prune_analys_file(analys_path, active, dry_run=True)
            per_inst_results.append((inst_code, analys_path, before, removed))

        if not per_inst_results:
            continue

        print(f"  {filename}")
        for inst_code, analys_path, before, removed in per_inst_results:
            if removed == 0:
                print(f"    {inst_code:<5} {before:>3}     ingen förändring")
                continue

            fraction = removed / before if before > 0 else 0
            status = f"{GREEN}{BOLD}−{removed} lösta{RESET}"
            if fraction >= LARGE_DELETION_THRESHOLD:
                status += f"  {YELLOW}({int(fraction*100)}% av rader — stor ändring){RESET}"

            print(f"    {inst_code:<5} {before:>3} → {before-removed:>3}  {status}")

            if not dry_run:
                if fraction >= LARGE_DELETION_THRESHOLD:
                    answer = input(
                        f"      Bekräfta borttagning av {removed} rader ur "
                        f"{inst_code}/{filename}? [j/N]: "
                    ).strip().lower()
                    if answer not in ("j", "ja", "y", "yes"):
                        print(f"      {YELLOW}Hoppas över.{RESET}")
                        continue
                prune_analys_file(analys_path, active, dry_run=False)
                total_removed += removed
            else:
                total_removed += removed

    print()
    if total_removed > 0:
        verb = "skulle tas bort" if dry_run else "togs bort"
        print(f"{GREEN}{BOLD}Totalt {total_removed} lösta rader {verb}.{RESET}")
    else:
        print(f"{YELLOW}Inga lösta fynd att ta bort.{RESET}")
    print()


if __name__ == "__main__":
    main()
