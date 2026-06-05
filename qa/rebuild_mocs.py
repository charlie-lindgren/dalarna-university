#!/usr/bin/env python3
"""rebuild_mocs.py — Bygg om alla MOC-filer från vault-tillstånd.

Skannar vault-dalarna-university/, läser frontmatter från varje kursplansfil
och bygger MOC-strukturen från grunden. Hanterar:

- Forskarämnen vs grundämnen utan namnkollisioner ("Forskarämne X" → distinkt
  MOC-fil)
- Migration av kurser i 5 forskarämnesfoldrar (ANALYTIC, ENERGIBM, MIKRODAT,
  VÅRDVETS, PEDAGARB) till nya forskarämnesnamnet
- Stale eller felaktigt placerade MOC-filer
- Institutions-MOC:erna med korrekta "Ämnen" / "Forskarutbildningsämnen"-sektioner

Kör ``--dry-run`` (default) för att se ändringarna; ``--apply`` för att skriva.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent / "scripts"))

from scrape_hda_kursplaner import (  # noqa: E402
    FORSKAR_PREFIX_TO_SUBJECT,
    INSTITUTIONS,
    INST_DIR_NAME,
    VAULT,
    build_institution_moc,
    build_subject_moc,
    institution_dir,
    kursplaner_dir,
    render_course_sections,
)

CODE_OK = re.compile(r"^[A-ZÅÄÖ]{2,4}[0-9A-Z]{3,5}$")
FORSKAR_CODES = {info[1] for info in FORSKAR_PREFIX_TO_SUBJECT.values()}


# ─────────────────────────────────────────────────────────────────────────────
# Frontmatter-hjälpare
# ─────────────────────────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fm = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            fm[key] = val
    return fm


def replace_frontmatter_field(text: str, key: str, new_value: str) -> str:
    """Bytar värdet för ``key:`` i frontmattern (eller infogar om saknas)."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    fm_body = text[4:end]
    pattern = re.compile(rf"^({re.escape(key)}:\s*).*$", re.MULTILINE)
    if pattern.search(fm_body):
        new_fm = pattern.sub(rf"\g<1>{new_value}", fm_body)
    else:
        new_fm = fm_body + f"\n{key}: {new_value}"
    return "---\n" + new_fm + "\n---\n" + text[end + 5 :]


# ─────────────────────────────────────────────────────────────────────────────
# Steg 1: Migrera forskarkurs-filer till "Forskarämne X"-namn
# ─────────────────────────────────────────────────────────────────────────────

def migrate_forskar_courses(apply: bool) -> int:
    """Uppdaterar amne + up i forskarkurs-filerna."""
    # Bygg lookup från subject_code → nya namnet
    code_to_name = {info[1]: info[0] for info in FORSKAR_PREFIX_TO_SUBJECT.values()}
    code_to_inst = {info[1]: info[2] for info in FORSKAR_PREFIX_TO_SUBJECT.values()}

    n_changes = 0
    for inst_code in INST_DIR_NAME:
        kp = kursplaner_dir(inst_code)
        if not kp.exists():
            continue
        for subj_code in FORSKAR_CODES:
            subj_dir = kp / subj_code
            if not subj_dir.exists():
                continue
            new_name = code_to_name[subj_code]
            for cf in subj_dir.glob("*.md"):
                if "MOC" in cf.name:
                    continue
                text = cf.read_text(encoding="utf-8")
                fm = parse_frontmatter(text)
                if not fm:
                    continue
                current_amne = fm.get("amne", "")
                current_up = fm.get("up", "")
                expected_up = f'"[[{new_name}]]"'
                if current_amne == new_name and current_up == expected_up:
                    continue
                new_text = text
                new_text = replace_frontmatter_field(new_text, "amne", f'"{new_name}"')
                new_text = replace_frontmatter_field(
                    new_text, "up", f'"[[{new_name}]]"'
                )
                if new_text != text:
                    n_changes += 1
                    if apply:
                        cf.write_text(new_text, encoding="utf-8")
                    print(f"  {'✓' if apply else 'skulle uppdatera'}: "
                          f"{cf.relative_to(VAULT)}  amne→{new_name!r}")
    return n_changes


# ─────────────────────────────────────────────────────────────────────────────
# Steg 2: Samla alla ämnen och kurser från vaulten
# ─────────────────────────────────────────────────────────────────────────────

def _course_is_vilande(text: str) -> bool:
    fm = parse_frontmatter(text) or {}
    tags = fm.get("tags", "")
    return "vilande" in tags


def _course_name(text: str) -> str:
    fm = parse_frontmatter(text) or {}
    return fm.get("kursnamn", "") or fm.get("course_name", "")


def collect_subjects_from_vault() -> dict[str, dict]:
    """Returnerar {(inst, subj_code) → {name, code, institution, type, courses, huvudomrade}}."""
    forskar_name_by_code = {info[1]: info[0] for info in FORSKAR_PREFIX_TO_SUBJECT.values()}
    subjects: dict[tuple[str, str], dict] = {}

    for inst_code in INST_DIR_NAME:
        kp = kursplaner_dir(inst_code)
        if not kp.exists():
            continue
        for subj_dir in sorted(kp.iterdir()):
            if not subj_dir.is_dir():
                continue
            subj_code = subj_dir.name
            courses: list[dict] = []
            subj_name = None
            huvudomrade = None
            for cf in subj_dir.glob("*.md"):
                if "MOC" in cf.name:
                    continue
                if not CODE_OK.match(cf.stem):
                    continue
                text = cf.read_text(encoding="utf-8")
                fm = parse_frontmatter(text) or {}
                if subj_name is None:
                    subj_name = fm.get("amne", "")
                if huvudomrade is None:
                    huvudomrade = fm.get("huvudomrade", "")
                courses.append({
                    "code": cf.stem,
                    "name": fm.get("kursnamn", "") or cf.stem,
                    "vilande": "vilande" in fm.get("tags", ""),
                })
            if not courses:
                continue
            stype = "research" if subj_code in FORSKAR_CODES else "subject"
            # Forskarämnen: använd det auktoritativa namnet från FORSKAR_PREFIX_TO_SUBJECT
            # istället för frontmatter-värdet (som kan vara från före migrationen).
            if stype == "research":
                subj_name = forskar_name_by_code.get(subj_code, subj_name or subj_code)
            subjects[(inst_code, subj_code)] = {
                "name": subj_name or subj_code,
                "code": subj_code,
                "institution": inst_code,
                "type": stype,
                "courses": courses,
                "huvudomrade": huvudomrade or "",
            }
    return subjects


# ─────────────────────────────────────────────────────────────────────────────
# Steg 3: Skriv subject-MOCs + institutions-MOCs
# ─────────────────────────────────────────────────────────────────────────────

def write_subject_mocs(subjects: dict, apply: bool) -> tuple[int, int]:
    """Skriv en MOC-fil per (inst, subj_code). Returnerar (written, removed_stale)."""
    written = 0
    expected_paths: set[Path] = set()

    for (inst_code, subj_code), info in subjects.items():
        moc_path = kursplaner_dir(inst_code) / f"{info['name']}.md"
        expected_paths.add(moc_path)
        new_text = build_subject_moc(info, info["courses"])
        if not new_text.endswith("\n"):
            new_text += "\n"
        if moc_path.exists() and moc_path.read_text(encoding="utf-8") == new_text:
            continue
        written += 1
        if apply:
            moc_path.write_text(new_text, encoding="utf-8")
        print(f"  {'✓' if apply else 'skulle skriva'}: {moc_path.relative_to(VAULT)} "
              f"({len(info['courses'])} kurser)")

    # Hitta MOC-filer i Kursplaner/ som inte längre motsvarar någon ämnesmapp
    removed = 0
    for inst_code in INST_DIR_NAME:
        kp = kursplaner_dir(inst_code)
        if not kp.exists():
            continue
        # Ämnes-hubbar ligger direkt under kp (kurser ligger i subkod-mappar).
        for moc in kp.glob("*.md"):
            if moc in expected_paths:
                continue
            if moc.stem.startswith(("Stray ", "Ej Aktiv ")):
                # Behandlas av identify_ej_aktiv.py — lämna ifred
                continue
            removed += 1
            if apply:
                moc.unlink()
            print(f"  {'✗' if apply else 'skulle ta bort'}: {moc.relative_to(VAULT)} "
                  f"(stale)")
    return written, removed


def write_institution_mocs(subjects: dict, apply: bool) -> int:
    """Skriv institutions-MOC:s baserat på samlade subjects."""
    inst_subjects: dict[str, list[dict]] = defaultdict(list)
    course_counts: dict[str, int] = {}
    for (inst_code, subj_code), info in subjects.items():
        inst_subjects[inst_code].append(info)
        course_counts[subj_code] = len(info["courses"])

    n_written = 0
    for inst_code in INST_DIR_NAME:
        subs = inst_subjects.get(inst_code, [])
        # Programmes: hämta från Utbildningsplaner-mappen
        programmes: list[dict] = []
        utb_dir = institution_dir(inst_code) / "Utbildningsplaner"
        if utb_dir.exists():
            for pf in sorted(utb_dir.glob("*.md")):
                if "MOC" in pf.stem:
                    continue
                text = pf.read_text(encoding="utf-8")
                fm = parse_frontmatter(text) or {}
                code = pf.stem  # filename is authoritative; programkod in frontmatter can be wrong
                name = fm.get("programnamn", "") or pf.stem
                programmes.append({"code": code, "name_sv": name})

        new_text = build_institution_moc(inst_code, subs, course_counts, programmes)
        if not new_text.endswith("\n"):
            new_text += "\n"

        moc_path = institution_dir(inst_code) / f"{inst_code}.md"
        if moc_path.exists() and moc_path.read_text(encoding="utf-8") == new_text:
            continue
        n_written += 1
        if apply:
            moc_path.write_text(new_text, encoding="utf-8")
        print(f"  {'✓' if apply else 'skulle skriva'}: {moc_path.relative_to(VAULT)} "
              f"({len(subs)} ämnen)")
    return n_written


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true",
                   help="Skriv ändringar till disk (annars dry-run).")
    p.add_argument("--skip-migration", action="store_true",
                   help="Hoppa över migration av forskarkurs-filer (bara MOC:s).")
    args = p.parse_args()

    mode = "SKRIVER" if args.apply else "DRY-RUN"
    print(f"=== rebuild_mocs.py — {mode} ===\n")

    if not args.skip_migration:
        print("Steg 1: Migrerar forskarkurs-filer till 'Forskarämne X'-namn ...")
        n = migrate_forskar_courses(args.apply)
        print(f"  → {n} kursfil(er) {'uppdaterade' if args.apply else 'skulle uppdateras'}\n")

    print("Steg 2: Samlar ämnen och kurser från vault ...")
    subjects = collect_subjects_from_vault()
    print(f"  → {len(subjects)} (institution, ämneskod)-kombinationer\n")

    print("Steg 3: Skriver ämnes-MOC:s ...")
    written, removed = write_subject_mocs(subjects, args.apply)
    print(f"  → {written} MOC:s {'skrivna' if args.apply else 'att skriva'}, "
          f"{removed} stale {'borttagna' if args.apply else 'att ta bort'}\n")

    print("Steg 4: Skriver institutions-MOC:s ...")
    n = write_institution_mocs(subjects, args.apply)
    print(f"  → {n} institutions-MOC:s {'skrivna' if args.apply else 'att skriva'}\n")

    if not args.apply:
        print("(Dry-run — inga filer ändrades. Kör med --apply för att skriva.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
