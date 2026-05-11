#!/usr/bin/env python3
"""
populate_analysfiler.py — Fyll analysfilerna i
vault-dalarna-university/0X {INST}/Analys/ med fynd från senaste QA-rapporten.

Varje fynd klassas till en institution genom att slå upp kurskoden mot
kursplansfilernas placering i vaulten (med fallback till `institution:` i
frontmatter). Rapportens fynd partitioneras därefter per institution och
skrivs till varje institutions egna analysfiler.

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

REPO_ROOT     = Path(__file__).resolve().parent.parent
VAULT         = REPO_ROOT / "vault-dalarna-university"
INST_DIR_NAME = {
    "IIT": "01 IIT",
    "IHV": "02 IHV",
    "IKS": "03 IKS",
    "ISLL": "04 ISLL",
}
RAPPORT_DIR   = Path(__file__).resolve().parent / "rapporter"

COURSE_CODE_RE = re.compile(r"^[A-ZÅÄÖ0-9]{4,8}$")


def institution_analys_dir(inst_code: str) -> Path:
    return VAULT / INST_DIR_NAME[inst_code] / "Analys"


def build_code_to_institution_map() -> dict[str, str]:
    """Skanna vaulten och bygg `kurskod -> institutionskod` baserat på
    kursfilernas placering. Filplacering är auktoritativ; vid kollision
    läses `institution:` i frontmatter som tiebreaker."""
    mapping: dict[str, str] = {}
    for inst_code, dirname in INST_DIR_NAME.items():
        kp = VAULT / dirname / "Kursplaner"
        if not kp.exists():
            continue
        for md in kp.rglob("*.md"):
            if "MOC" in md.stem:
                continue
            stem = md.stem
            if not COURSE_CODE_RE.match(stem):
                continue
            if stem in mapping and mapping[stem] != inst_code:
                try:
                    text = md.read_text(encoding="utf-8", errors="replace")
                    m = re.search(r'^institution:\s*"?(\w+)"?', text, re.MULTILINE)
                    if m:
                        mapping[stem] = m.group(1)
                except Exception:
                    pass
            else:
                mapping[stem] = inst_code
    return mapping

# Analysfil → (rapport-sektionsprefix → "Problem"-etikett i analystabellen)
ANALYS_FILES: dict[str, dict[str, str]] = {
    "Introfras.md": {
        "Introfras före frasning": "Prosa/rubrik före frasning",
    },
    "Frasningskonsistens.md": {
        "Frasning avviker": "Avviker från referensformen",
    },
    "Stavfel och språkbruk.md": {
        "Dubblerat ord":      "Dubblerat ord",
        "Känd felstavning":   "Felstavning",
        "Stavfel (svenska)":  "Felstavning",
        "Stavfel (engelska)": "Felstavning (en)",
    },
    "Betygsskalor.md": {
        "Betygsskala inkonsekvent": "Inkonsekvent delskalor",
    },
    "Examinationsformer.md": {
        "Examinationsformer utan punktlista": "Saknar punktlista",
    },
    "Omfång på lärandemål.md": {
        "För få lärandemål":   "För få mål",
        "För många lärandemål": "För många mål",
        "Långt lärandemål":    "Långt mål",
    },
    "Bloom-taxonomi.md": {
        "Bloom-nivå låg (avancerad kurs)": "Låg verbnivå för avancerad kurs",
        "Bloom-nivå hög (grundkurs)":      "Hög verbnivå för grundkurs",
        "Bloom okänt verb":                "Okänt ledande verb",
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


def build_callout(
    rows: list[tuple[str, str, str, str]],
    xlsx_filename: str,
    inst_code: str | None = None,
) -> list[str]:
    """rows = [(code, subj, problem_label, detail), ...] -> callout + download link lines.

    With per-institution Analys folders, the same xlsx basename exists in 4 places
    (one per institution). Quartz's "shortest" link resolver sees multiple matches
    and falls back to vault-root → 404. We avoid that by writing the full
    institution-prefixed slug path so transformLink's suffix-match yields a unique hit.
    """
    n = len(rows)
    xlsx_slug = xlsx_filename.replace(" ", "-")  # Quartz slugifies asset names the same way
    if inst_code:
        # e.g. "01 IIT" → "01-IIT" (Quartz slug convention)
        inst_slug = INST_DIR_NAME[inst_code].replace(" ", "-")
        href = f"{inst_slug}/Analys/{xlsx_slug}"
    else:
        href = xlsx_slug
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
        # Escape `##` so Quartz doesn't render it as a heading/tag link inside
        # the table cell — the excerpt quotes raw kursplan markdown verbatim.
        cell_detail = detail.replace("##", r"\##")
        lines.append(f"> | [{code}]({url}) | {subj} | {problem} | {cell_detail} |")
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

    code_to_inst = build_code_to_institution_map()
    unmapped: set[str] = set()

    for filename, section_map in ANALYS_FILES.items():
        all_rows: list[tuple[str, str, str, str]] = []
        for section_label, problem_label in section_map.items():
            for code, subj, detail in by_section.get(section_label, []):
                all_rows.append((code, subj, problem_label, detail))

        all_rows.sort(key=lambda r: (r[1], r[0]))  # by subj, then code

        rows_by_inst: dict[str, list[tuple[str, str, str, str]]] = {
            inst: [] for inst in INST_DIR_NAME
        }
        for row in all_rows:
            code = row[0]
            inst = code_to_inst.get(code)
            if inst is None:
                unmapped.add(code)
                continue
            rows_by_inst.setdefault(inst, []).append(row)

        print(f"  {filename}")
        for inst_code in INST_DIR_NAME:
            analys_path = institution_analys_dir(inst_code) / filename
            rows = rows_by_inst.get(inst_code, [])

            if not analys_path.exists():
                print(f"    {inst_code:<5} {len(rows):>4} fynd  "
                      f"{YELLOW}saknar {filename} — hoppar över{RESET}")
                continue

            xlsx_filename = analys_path.stem + ".xlsx"
            xlsx_path = analys_path.with_suffix(".xlsx")
            callout_lines = build_callout(rows, xlsx_filename, inst_code=inst_code)

            original = analys_path.read_text(encoding="utf-8")
            new_text = replace_callout(original, callout_lines)

            if new_text is None:
                print(f"    {inst_code:<5} {len(rows):>4} fynd  "
                      f"{YELLOW}inget callout-block — hoppar över{RESET}")
                continue

            md_changed = new_text != original
            verb = "skulle skrivas" if dry_run else "skrev"

            if md_changed:
                print(f"    {inst_code:<5} {len(rows):>4} fynd  "
                      f"{GREEN}{verb} md{RESET}")
                if not dry_run:
                    analys_path.write_text(new_text, encoding="utf-8")
            else:
                print(f"    {inst_code:<5} {len(rows):>4} fynd  (md oförändrad)")

            if not dry_run:
                build_xlsx(rows, xlsx_path, sheet_title=analys_path.stem)

    if unmapped:
        print(f"\n  {YELLOW}{len(unmapped)} kurs(er) gick inte att klassa till institution"
              f" och hoppades över: {', '.join(sorted(unmapped))}{RESET}")

    print()


if __name__ == "__main__":
    main()
