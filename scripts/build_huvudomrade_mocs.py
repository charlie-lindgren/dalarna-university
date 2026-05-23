#!/usr/bin/env python3
"""build_huvudomrade_mocs.py — Generera huvudområdes-MOC:ar per institution.

Skapar en MOC-fil per (institution, huvudområde)-par i mappen
``0X {INST}/Huvudområden/``. Varje MOC har:

- ``up:`` → institutionens MOC
- En kort metadata-rad (antal kurser, antal ämnen)
- En punktlista över ämnes-MOC:ar i samma institution som har kurser i
  huvudområdet

För att hålla institutionerna åtskilda i graph-vyn skapas separata MOC:ar
för huvudområden som spänner över flera institutioner — t.ex. ger
*Mikrodataanalys* en MOC i IIT och en i IKS, utan korsförbindelser.

``Ej huvudområde`` hoppas över — det är en placeholder och inte ett riktigt
huvudområde.

Körning:

    python3 scripts/build_huvudomrade_mocs.py            # dry-run
    python3 scripts/build_huvudomrade_mocs.py --apply    # skriv filerna
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent / "vault-dalarna-university"
INST_DIR_NAME = {"IIT": "01 IIT", "IHV": "02 IHV", "IKS": "03 IKS", "ISLL": "04 ISLL"}
INST_TO_CODE = {v: k for k, v in INST_DIR_NAME.items()}

SKIP_HUVUD = {"ej huvudområde"}

FM_FIELD_RE = re.compile(r'^(\w+):\s*"?(.+?)"?\s*$', re.MULTILINE)
FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
HUVUD_SPLIT_RE = re.compile(r"\s+\d+\s*")


def parse_kursplan(p: Path) -> dict | None:
    raw = p.read_text(encoding="utf-8")
    fm = FM_RE.match(raw)
    if not fm:
        return None
    fields = dict(FM_FIELD_RE.findall(fm.group(1)))
    inst = fields.get("institution", "").strip().strip('"')
    subj_kod = fields.get("amne_kod", "").strip().strip('"')
    subj_namn = fields.get("amne", "").strip().strip('"')
    kursnamn = fields.get("kursnamn", "").strip().strip('"')
    huvud_raw = fields.get("huvudomrade", "").strip().strip('"')
    if not (inst and subj_kod and huvud_raw):
        return None
    huvudomr = [
        h.strip() for h in HUVUD_SPLIT_RE.split(huvud_raw) if h.strip()
    ]
    huvudomr = [h for h in huvudomr if h.lower() not in SKIP_HUVUD]
    if not huvudomr:
        return None
    return {
        "path": p,
        "code": p.stem,
        "inst": inst,
        "subj_kod": subj_kod,
        "subj_namn": subj_namn,
        "kursnamn": kursnamn,
        "huvudomr": huvudomr,
    }


def collect() -> tuple[dict, dict]:
    """Returnerar:
       agg[(inst, huvudområde)] = {subj_kod: {"name": subj_namn, "courses": [...]}}
       cross_inst[huvudområde] = set(institutioner)
    """
    agg: dict[tuple[str, str], dict[str, dict]] = defaultdict(
        lambda: defaultdict(lambda: {"name": "", "courses": []})
    )
    cross_inst: dict[str, set[str]] = defaultdict(set)

    files = [
        p for p in VAULT.glob("0[1-4]*/Kursplaner/*/*.md") if "MOC" not in p.name
    ]
    for p in files:
        info = parse_kursplan(p)
        if not info:
            continue
        for h in info["huvudomr"]:
            entry = agg[(info["inst"], h)][info["subj_kod"]]
            entry["name"] = info["subj_namn"] or info["subj_kod"]
            entry["courses"].append(info["code"])
            cross_inst[h].add(info["inst"])
    return agg, cross_inst


def moc_filename(huvudomrade: str, inst: str, spans_multiple: bool) -> str:
    base = f"Huvudområde - {huvudomrade}"
    if spans_multiple:
        base += f" ({inst})"
    return f"{base} MOC.md"


def render_moc(
    huvudomrade: str,
    inst: str,
    subjects: dict[str, dict],
    spans_multiple: bool,
) -> str:
    """Bygg markdown-innehållet för en huvudområdes-MOC."""
    total_courses = sum(len(s["courses"]) for s in subjects.values())
    n_subjects = len(subjects)

    title_suffix = f" ({inst})" if spans_multiple else ""

    lines = [
        "---",
        "tags: [huvudområde, moc, " + inst.lower() + "]",
        # Plain string (utan ``[[ ]]``) — Quartz extraherar wikilinks från
        # frontmatter, men en ren textsträng räknas inte som en graf-edge.
        # Institutionshubben skulle annars drunkna i huvudområdes-länkar.
        f'up: "{inst} MOC"',
        f'huvudomrade: "{huvudomrade}"',
        f'institution: "{inst}"',
        "---",
        "",
        f"# {huvudomrade}{title_suffix}",
        "",
        f"Huvudområde inom **{inst}**. Omfattar {total_courses} kurs"
        + ("er" if total_courses != 1 else "")
        + f" fördelade på {n_subjects} ämne"
        + ("n" if n_subjects != 1 else "")
        + ".",
        "",
        "## Ämnen",
        "",
    ]
    # Sort by course-count desc, then subject name
    sorted_subjects = sorted(
        subjects.items(),
        key=lambda kv: (-len(kv[1]["courses"]), kv[1]["name"]),
    )
    for subj_kod, data in sorted_subjects:
        n = len(data["courses"])
        lines.append(
            f"- [[{data['name']} MOC|{data['name']}]] "
            f"({subj_kod}, {n} kurs"
            + ("er" if n != 1 else "")
            + ")"
        )
    lines.append("")
    return "\n".join(lines)


INSTITUTION_SECTION_HEADER = "## Huvudområden"
INSTITUTION_SECTION_RE = re.compile(
    r"\n##\s+Huvudområden.*?(?=\n##\s|\Z)", re.DOTALL
)


def patch_institution_moc(
    inst: str, huvudomraden: list[tuple[str, str, int, int]], apply: bool
) -> bool:
    """Lägg till eller uppdatera ``## Huvudområden``-sektionen i institutionens MOC.

    ``huvudomraden`` = lista av (display_namn, filnamn_utan_md, antal_kurser,
    antal_ämnen), sorterad efter visningsnamn.
    """
    inst_dir = VAULT / INST_DIR_NAME[inst]
    moc_path = inst_dir / f"{inst} MOC.md"
    if not moc_path.exists():
        return False

    lines = [
        INSTITUTION_SECTION_HEADER,
        "",
    ]
    for display, fname_stem, n_courses, n_subjects in huvudomraden:
        # ``class="no-graph"`` håller institutionshubben ren — länken navigerar
        # på sidan men räknas inte som en graf-edge från institutions-MOC:en.
        # Huvudområdes-MOC:arna sitter ändå i grafen via ``up:`` och sina egna
        # länkar till ämnes-MOC:ar i samma institution.
        href = f"Huvudområden/{fname_stem}"
        lines.append(
            f'- <a class="no-graph" href="{href}">{display}</a> '
            f"({n_courses} kurs"
            + ("er" if n_courses != 1 else "")
            + f", {n_subjects} ämne"
            + ("n" if n_subjects != 1 else "")
            + ")"
        )
    section = "\n" + "\n".join(lines) + "\n"

    existing = moc_path.read_text(encoding="utf-8")
    if INSTITUTION_SECTION_RE.search(existing):
        new_text = INSTITUTION_SECTION_RE.sub(section.rstrip(), existing, count=1)
        if not new_text.endswith("\n"):
            new_text += "\n"
    else:
        # Lägg in före ``## Kvalitetsanalys`` om den finns, annars i slutet.
        if "\n## Kvalitetsanalys" in existing:
            new_text = existing.replace(
                "\n## Kvalitetsanalys", section + "\n## Kvalitetsanalys", 1
            )
        else:
            new_text = existing.rstrip() + "\n" + section

    if new_text == existing:
        return False
    if apply:
        moc_path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Skriv filerna till disk")
    args = parser.parse_args()

    agg, cross_inst = collect()
    spans = {h for h, insts in cross_inst.items() if len(insts) > 1}

    print(f"Hittade {len(agg)} (institution × huvudområde)-par.")
    print(f"  Varav {len(spans)} huvudområden spänner över flera institutioner "
          f"(separata MOC:ar per institution).")
    print()

    per_inst_count: dict[str, int] = defaultdict(int)
    per_inst_entries: dict[str, list[tuple[str, str, int, int]]] = defaultdict(list)
    written = 0
    for (inst, huvudomrade), subjects in sorted(agg.items()):
        inst_dir = VAULT / INST_DIR_NAME[inst] / "Huvudområden"
        spans_multiple = huvudomrade in spans
        filename = moc_filename(huvudomrade, inst, spans_multiple)
        out_path = inst_dir / filename
        content = render_moc(huvudomrade, inst, subjects, spans_multiple)

        if args.apply:
            inst_dir.mkdir(parents=True, exist_ok=True)
            existing = out_path.read_text(encoding="utf-8") if out_path.exists() else None
            if existing != content:
                out_path.write_text(content, encoding="utf-8")
                written += 1
        per_inst_count[inst] += 1

        n_courses = sum(len(s["courses"]) for s in subjects.values())
        per_inst_entries[inst].append(
            (huvudomrade, filename[:-3], n_courses, len(subjects))
        )

    print("Per institution:")
    inst_patches = 0
    for inst in ("IIT", "IHV", "IKS", "ISLL"):
        print(f"  {inst}: {per_inst_count[inst]} MOC:ar")
        entries = sorted(per_inst_entries[inst], key=lambda e: e[0])
        if entries and patch_institution_moc(inst, entries, args.apply):
            inst_patches += 1

    if args.apply:
        print(f"\nSkrev {written} huvudområdes-MOC:ar (övriga var oförändrade).")
        print(f"Patchade {inst_patches} institutions-MOC:ar med ## Huvudområden-sektion.")
    else:
        print("\nDry-run — kör med --apply för att skriva filerna.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
