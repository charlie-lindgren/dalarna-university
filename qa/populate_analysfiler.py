#!/usr/bin/env python3
"""
populate_analysfiler.py — Fyll varje analysfil i vault-dalarna-university/05 Analys/
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

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

REPO_ROOT    = Path(__file__).resolve().parent.parent
VAULT_ANALYS = REPO_ROOT / "vault-dalarna-university" / "05 Analys"
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
        "Betygsmoduler hp ≠ kurs hp": "HP-summa stämmer ej",
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

DOWNLOAD_ICON_SVG = (
    '<svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
    '<polyline points="7 10 12 15 17 10"/>'
    '<line x1="12" y1="15" x2="12" y2="3"/>'
    '</svg>'
)


def build_callout(rows: list[tuple[str, str, str, str]], xlsx_filename: str) -> list[str]:
    """rows = [(code, subj, problem_label, detail), ...] -> callout + download link lines."""
    n = len(rows)
    href = xlsx_filename.replace(" ", "-")  # Quartz slugifies non-md asset names the same way
    lines = [
        f'<a class="download-xlsx" href="{href}" download>'
        f'{DOWNLOAD_ICON_SVG}'
        f'<span>Ladda ner som Excel-fil ({n} rader)</span>'
        f'</a>',
        "",
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
# Excel-export
# ─────────────────────────────────────────────────────────────────────────────
HEADER_FILL = PatternFill("solid", fgColor="8B1A1A")
HEADER_FONT = Font(bold=True, color="FFFFFF")
LINK_FONT   = Font(color="0563C1", underline="single")


def build_xlsx(rows: list[tuple[str, str, str, str]], output_path: Path, sheet_title: str) -> None:
    """Write rows to an .xlsx file with a hyperlinked Kursplan column."""
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_title[:31]  # Excel max sheet title length

    headers = ["Kursplan", "Ämne", "Problem", "Detalj", "Länk"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="left", vertical="center")

    for code, subj, problem, detail in rows:
        url = KURSPLAN_URL.format(code=code)
        ws.append([code, subj, problem, detail, url])
        row_idx = ws.max_row
        kod_cell = ws.cell(row=row_idx, column=1)
        kod_cell.hyperlink = url
        kod_cell.font = LINK_FONT
        link_cell = ws.cell(row=row_idx, column=5)
        link_cell.hyperlink = url
        link_cell.font = LINK_FONT

    widths = [12, 8, 28, 70, 70]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = "A2"
    if ws.max_row >= 2:
        ws.auto_filter.ref = ws.dimensions

    wb.save(output_path)


# ─────────────────────────────────────────────────────────────────────────────
# Filersättning
# ─────────────────────────────────────────────────────────────────────────────
CALLOUT_START_RE = re.compile(r"^>\s*\[!example\]")


def replace_callout(text: str, new_block_lines: list[str]) -> str | None:
    """Replace the first `> [!example]…` callout block (and any directly preceding
    .xlsx download link) with new_block_lines.

    Block boundary: starts at the [!example] line by default. If the line(s)
    immediately above (allowing one blank line) contain `.xlsx`, the block start
    is moved up to include them — so the script is idempotent across re-runs.
    Block end: first line after the callout that does not start with `>`.
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

    block_start = start
    j = start - 1
    while j >= 0 and lines[j].strip() == "":
        j -= 1
    if j >= 0 and ".xlsx" in lines[j]:
        block_start = j

    new_lines = lines[:block_start] + new_block_lines + lines[end:]
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
        # Pick the most recently modified report. Match both timestamped
        # (`rapport-YYYY-MM-DD-HHMM.md`) and bare (`rapport.md`) forms — the
        # latter is the default output of `qa/check_kursplaner.py --out …`
        # so it's often the freshest one.
        rapporter = list(RAPPORT_DIR.glob("rapport*.md"))
        if not rapporter:
            print("Fel: Ingen rapport hittad i qa/rapporter/.", file=sys.stderr)
            sys.exit(1)
        rapport_path = max(rapporter, key=lambda p: p.stat().st_mtime)

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

        xlsx_filename = analys_path.stem + ".xlsx"
        xlsx_path = analys_path.with_suffix(".xlsx")

        callout_lines = build_callout(rows, xlsx_filename)

        original = analys_path.read_text(encoding="utf-8")
        new_text = replace_callout(original, callout_lines)

        if new_text is None:
            print(f"  {filename:<50}  {YELLOW}inget callout-block hittades — hoppar över{RESET}")
            continue

        md_changed = new_text != original
        verb = "skulle skrivas" if dry_run else "skrev"

        if md_changed:
            print(f"  {filename:<50}  {len(rows):>4} fynd  {GREEN}{verb} md{RESET}")
            if not dry_run:
                analys_path.write_text(new_text, encoding="utf-8")
        else:
            print(f"  {filename:<50}  {len(rows):>4} fynd  (md oförändrad)")

        if not dry_run:
            build_xlsx(rows, xlsx_path, sheet_title=analys_path.stem)
            print(f"    └─ {GREEN}{verb}{RESET}  {xlsx_filename}  ({len(rows)} rader)")

    print()


if __name__ == "__main__":
    main()
