#!/usr/bin/env python3
"""
identify_ej_aktiv.py — Identifierar och taggar kursplaner som inte längre finns
på du.se som "ej aktiv".

Arbetsflöde:
  1. Hämtar nuvarande ämnen + kurslistor från du.se (via samma upptäcktslogik
     som scrape_hda_kursplaner.py — men utan per-kurs-skrap).
  2. Jämför mot kursplansfiler i vault-dalarna-university/01 Kursplaner/<AMNE>/.
  3. För kurser som finns i vault men inte längre på du.se:
       - Lägger till `ej-aktiv` i tags + cssclasses
       - Pekar `up:` till "Ej Aktiv <Ämne> MOC"
  4. För kurser som åter finns på du.se men har ej-aktiv-flagga:
       - Tar bort flaggan + återställer `up:` till "<Ämne> MOC"
  5. Skapar/uppdaterar "Ej Aktiv <Ämne> MOC.md" per ämne med orphans.

Användning:
    python3 qa/identify_ej_aktiv.py                          # dry-run
    python3 qa/identify_ej_aktiv.py --apply                  # skriv ändringar
    python3 qa/identify_ej_aktiv.py --institution IIT        # bara IIT
    python3 qa/identify_ej_aktiv.py --subject DTA            # bara Datateknik
    python3 qa/identify_ej_aktiv.py --no-network --codes-file codes.txt
                                                              # läs koder från fil
                                                              # (en per rad: SUBJ CODE)

Beroenden: requests, beautifulsoup4 (för scraper-importen).
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scrape_hda_kursplaner import (  # noqa: E402
    INSTITUTIONS,
    REQUEST_DELAY,
    discover_subjects_for_institution,
    discover_courses_for_subject,
)

VAULT_KURSPLANER = ROOT / "vault-dalarna-university" / "01 Kursplaner"

BOLD   = "\033[1m"
GREEN  = "\033[0;32m"
YELLOW = "\033[0;33m"
RED    = "\033[0;31m"
CYAN   = "\033[0;36m"
RESET  = "\033[0m"

COURSE_CODE_RE = re.compile(r"^[A-ZÅÄÖ0-9]{4,8}$")


# ─────────────────────────────────────────────────────────────────────────────
# Frontmatter helpers
# ─────────────────────────────────────────────────────────────────────────────

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str, str] | None:
    """Returnerar (fm_dict, fm_block, body) eller None."""
    m = FM_RE.match(text)
    if not m:
        return None
    fm_block = m.group(1)
    body = text[m.end():]
    fm = {}
    for line in fm_block.split("\n"):
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm, fm_block, body


def parse_list_field(value: str) -> list[str]:
    """Parsar `[a, b, c]` eller `a` → list[str]."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1]
        return [p.strip() for p in inner.split(",") if p.strip()]
    if value:
        return [value]
    return []


def serialize_list_field(items: list[str]) -> str:
    return "[" + ", ".join(items) + "]"


def update_fm_field(fm_block: str, key: str, new_value: str | None) -> str:
    """Skriver/lägger till/raderar en frontmatter-rad. new_value=None → radera."""
    pattern = re.compile(rf"^{re.escape(key)}:.*$", re.MULTILINE)
    if new_value is None:
        return pattern.sub("", fm_block).rstrip("\n") + "\n"
    new_line = f"{key}: {new_value}"
    if pattern.search(fm_block):
        return pattern.sub(new_line, fm_block)
    # append at end
    return fm_block.rstrip("\n") + "\n" + new_line


# ─────────────────────────────────────────────────────────────────────────────
# Vault-skanning
# ─────────────────────────────────────────────────────────────────────────────

def list_vault_codes_per_subject() -> dict[str, dict[str, Path]]:
    """Returnerar {subj_code -> {course_code -> path}} från vault-katalogerna."""
    result: dict[str, dict[str, Path]] = defaultdict(dict)
    if not VAULT_KURSPLANER.exists():
        return result
    for subj_dir in VAULT_KURSPLANER.iterdir():
        if not subj_dir.is_dir():
            continue
        subj_code = subj_dir.name
        for f in subj_dir.glob("*.md"):
            if "MOC" in f.name:
                continue
            stem = f.stem
            if COURSE_CODE_RE.match(stem):
                result[subj_code][stem] = f
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Tagga / avtagga
# ─────────────────────────────────────────────────────────────────────────────

def tag_orphan(path: Path, subject_name: str, apply: bool) -> bool:
    """Tagga en kursplansfil som ej-aktiv. Returnerar True om filen ändrades."""
    text = path.read_text(encoding="utf-8")
    parsed = parse_frontmatter(text)
    if not parsed:
        return False
    _, fm_block, body = parsed

    new_fm = fm_block

    # tags
    tags_m = re.search(r"^tags:\s*(.+)$", new_fm, re.MULTILINE)
    if tags_m:
        tags = parse_list_field(tags_m.group(1))
        if "ej-aktiv" not in tags:
            tags.append("ej-aktiv")
            new_fm = update_fm_field(new_fm, "tags", serialize_list_field(tags))
    else:
        new_fm = update_fm_field(new_fm, "tags", "[ej-aktiv]")

    # cssclasses
    css_m = re.search(r"^cssclasses:\s*(.+)$", new_fm, re.MULTILINE)
    if css_m:
        css = parse_list_field(css_m.group(1))
        if "ej-aktiv" not in css:
            css.append("ej-aktiv")
            new_fm = update_fm_field(new_fm, "cssclasses", serialize_list_field(css))
    else:
        new_fm = update_fm_field(new_fm, "cssclasses", "[ej-aktiv]")

    # up:
    new_up = f'"[[Ej Aktiv {subject_name} MOC]]"'
    new_fm = update_fm_field(new_fm, "up", new_up)

    new_text = "---\n" + new_fm.rstrip("\n") + "\n---\n" + body
    if new_text == text:
        return False
    if apply:
        path.write_text(new_text, encoding="utf-8")
    return True


def untag_orphan(path: Path, subject_name: str, apply: bool) -> bool:
    """Ta bort ej-aktiv-flagga från en kursplansfil. Returnerar True om ändrad."""
    text = path.read_text(encoding="utf-8")
    parsed = parse_frontmatter(text)
    if not parsed:
        return False
    _, fm_block, body = parsed

    new_fm = fm_block
    changed = False

    tags_m = re.search(r"^tags:\s*(.+)$", new_fm, re.MULTILINE)
    if tags_m:
        tags = parse_list_field(tags_m.group(1))
        if "ej-aktiv" in tags:
            tags = [t for t in tags if t != "ej-aktiv"]
            new_fm = update_fm_field(new_fm, "tags", serialize_list_field(tags))
            changed = True

    css_m = re.search(r"^cssclasses:\s*(.+)$", new_fm, re.MULTILINE)
    if css_m:
        css = parse_list_field(css_m.group(1))
        if "ej-aktiv" in css:
            css = [c for c in css if c != "ej-aktiv"]
            if css:
                new_fm = update_fm_field(new_fm, "cssclasses", serialize_list_field(css))
            else:
                new_fm = update_fm_field(new_fm, "cssclasses", None)
            changed = True

    up_m = re.search(r'^up:\s*"\[\[Ej Aktiv .+? MOC\]\]"', new_fm, re.MULTILINE)
    if up_m:
        new_fm = update_fm_field(new_fm, "up", f'"[[{subject_name} MOC]]"')
        changed = True

    if not changed:
        return False
    new_text = "---\n" + new_fm.rstrip("\n") + "\n---\n" + body
    if apply:
        path.write_text(new_text, encoding="utf-8")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Ej-aktiv MOC
# ─────────────────────────────────────────────────────────────────────────────

def build_ej_aktiv_moc(subject_name: str, subject_code: str, inst_code: str,
                       orphan_paths: list[Path]) -> str:
    lines = [
        "---",
        "cssclasses: [ej-aktiv]",
        f"aliases: [Ej Aktiv {subject_name}]",
        f"tags: [MOC, ej-aktiv, {subject_code}, {inst_code}]",
        f'up: "[[{subject_name} MOC]]"',
        "---",
        "",
        f"# Ej Aktiv — {subject_name}",
        "",
        f"> Kurser inom {subject_name} som inte längre syns i du.se:s kursutbud.",
        "> Möjligen avvecklade, vilande eller omklassificerade.",
        "",
        f"## Kurser ({len(orphan_paths)} st)",
        "",
    ]
    for p in sorted(orphan_paths, key=lambda x: x.stem):
        # Försök hämta kursnamnet från filen
        course_name = ""
        try:
            text = p.read_text(encoding="utf-8")
            for line in text.split("\n"):
                if line.startswith("kursnamn:"):
                    course_name = line.split(":", 1)[1].strip().strip('"')
                    break
        except Exception:
            pass
        if course_name:
            lines.append(f"- [[{p.stem}]] — {course_name}")
        else:
            lines.append(f"- [[{p.stem}]]")
    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Discovery (network)
# ─────────────────────────────────────────────────────────────────────────────

def discover_current_codes(
    only_institutions: set[str] | None,
    only_subjects: set[str] | None,
    quiet: bool,
) -> tuple[dict[str, set[str]], dict[str, dict]]:
    """Returnerar (codes_per_subject, subject_info_per_subject)."""
    codes_per_subject: dict[str, set[str]] = {}
    subject_info: dict[str, dict] = {}

    for inst_code, inst in INSTITUTIONS.items():
        if only_institutions and inst_code not in only_institutions:
            continue
        if not quiet:
            print(f"\n  {CYAN}Institution {inst_code}{RESET}")
        subjects = discover_subjects_for_institution(inst_code, inst)
        for s in subjects:
            subj_code = s.get("code", "")
            if not subj_code:
                continue
            if only_subjects and subj_code not in only_subjects:
                continue
            subject_info[subj_code] = s
            try:
                courses = discover_courses_for_subject(s)
            except Exception as e:
                print(f"  {RED}✗ {subj_code}: {e}{RESET}", file=sys.stderr)
                continue
            codes_per_subject[subj_code] = {c["code"] for c in courses}
            if not quiet:
                print(f"    {subj_code:6s} {s['name']:40s} {len(courses)} aktiva kurser")
            time.sleep(REQUEST_DELAY)
    return codes_per_subject, subject_info


# ─────────────────────────────────────────────────────────────────────────────
# Huvud
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Markera kursplaner som inte längre finns på du.se som ej aktiv."
    )
    parser.add_argument("--apply", action="store_true",
                        help="Skriv ändringar (annars dry-run).")
    parser.add_argument("--institution", "-i", action="append",
                        help="Begränsa till specifik institution (IIT/IHV/IKS/ISLL).")
    parser.add_argument("--subject", "-s", action="append",
                        help="Begränsa till specifikt ämne (kod, t.ex. DTA).")
    parser.add_argument("--quiet", "-q", action="store_true")
    args = parser.parse_args()

    only_institutions = set(i.upper() for i in args.institution) if args.institution else None
    only_subjects = set(s.upper() for s in args.subject) if args.subject else None

    print(f"{BOLD}{CYAN}Identifiera ej-aktiva kursplaner{RESET}")
    if not args.apply:
        print(f"  {YELLOW}DRY-RUN — inga filer skrivs{RESET}")
    print(f"  Hämtar nuvarande kurslistor från du.se …")

    codes_per_subject, subject_info = discover_current_codes(
        only_institutions, only_subjects, args.quiet
    )

    print(f"\n{BOLD}Jämför mot vault …{RESET}")
    vault_codes = list_vault_codes_per_subject()

    total_orphans   = 0
    total_reactivated = 0
    total_moc_writes  = 0

    for subj_code, current_codes in codes_per_subject.items():
        info = subject_info.get(subj_code, {})
        subj_name = info.get("name") or subj_code
        inst_code = info.get("institution", "")
        vault_for_subj = vault_codes.get(subj_code, {})

        orphans = sorted(c for c in vault_for_subj if c not in current_codes)
        reactivated = []

        # Re-activate any previously-tagged orphans that now exist in du.se
        for code in current_codes:
            path = vault_for_subj.get(code)
            if not path:
                continue
            if untag_orphan(path, subj_name, args.apply):
                reactivated.append(code)

        # Tag new orphans
        orphan_paths = [vault_for_subj[c] for c in orphans]
        tagged = []
        for code, p in zip(orphans, orphan_paths):
            if tag_orphan(p, subj_name, args.apply):
                tagged.append(code)

        moc_path = VAULT_KURSPLANER / subj_code / f"Ej Aktiv {subj_name} MOC.md"
        if orphan_paths:
            moc_text = build_ej_aktiv_moc(subj_name, subj_code, inst_code, orphan_paths)
            existing = moc_path.read_text(encoding="utf-8") if moc_path.exists() else ""
            if existing != moc_text:
                if args.apply:
                    moc_path.parent.mkdir(parents=True, exist_ok=True)
                    moc_path.write_text(moc_text, encoding="utf-8")
                total_moc_writes += 1
        elif moc_path.exists():
            if args.apply:
                moc_path.unlink()
            total_moc_writes += 1

        if orphans or reactivated:
            label = f"{subj_code} ({subj_name})"
            print(f"  {label:50s}  "
                  f"{RED}+{len(orphans)} orphans{RESET}  "
                  f"{GREEN}-{len(reactivated)} reactivated{RESET}")
            for c in orphans[:5]:
                print(f"      orphan: {c}")
            if len(orphans) > 5:
                print(f"      … och {len(orphans) - 5} till")

        total_orphans += len(orphans)
        total_reactivated += len(reactivated)

    print(f"\n{BOLD}Sammanfattning{RESET}")
    print(f"  Orphans (ej aktiva): {total_orphans}")
    print(f"  Återaktiverade:      {total_reactivated}")
    print(f"  MOC-skrivningar:     {total_moc_writes}")
    if not args.apply and (total_orphans or total_reactivated or total_moc_writes):
        print(f"\n  Kör igen med {BOLD}--apply{RESET} för att skriva ändringarna.")


if __name__ == "__main__":
    main()
