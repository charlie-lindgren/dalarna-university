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


PROGRAMME_COURSE_RE = re.compile(r"\[\[([A-ZÅÄÖ0-9]{4,8})(?:\|[^\]]*)?\]\]")
PROGRAMME_NAME_RE = re.compile(r'^programnamn:\s*"?([^"\n]+?)"?\s*$', re.MULTILINE)
PROGRAMME_INST_RE = re.compile(r'^institution:\s*"?([^"\n]+?)"?\s*$', re.MULTILINE)


def parse_programme(p: Path) -> dict | None:
    """Returnerar programkod, namn, institution och uppsättning kurskoder
    listade i programmets kursförteckning."""
    raw = p.read_text(encoding="utf-8")
    fm = FM_RE.match(raw)
    if not fm:
        return None
    fm_text = fm.group(1)
    body = raw[fm.end():]
    m_name = PROGRAMME_NAME_RE.search(fm_text)
    m_inst = PROGRAMME_INST_RE.search(fm_text)
    if not (m_name and m_inst):
        return None
    courses = set(PROGRAMME_COURSE_RE.findall(body))
    return {
        "code": p.stem,
        "name": m_name.group(1).strip(),
        "inst": m_inst.group(1).strip(),
        "courses": courses,
    }


def collect() -> tuple[dict, dict]:
    """Returnerar:
       agg[(inst, huvudområde)] = {
           "courses_by_subject": {subj_kod: {"name": ..., "courses": [...]}},
           "programmes": [{code, name, course_overlap}, ...],
       }
       cross_inst[huvudområde] = set(institutioner)
    """
    # course_code -> {"inst", "huvudomr": [...], "subj_kod", "subj_namn"}
    course_index: dict[str, dict] = {}
    files = [
        p for p in VAULT.glob("0[1-4]*/Kursplaner/*/*.md") if "MOC" not in p.name
    ]
    for p in files:
        info = parse_kursplan(p)
        if not info:
            continue
        course_index[info["code"]] = info

    # Build aggregation by (inst, huvudområde)
    agg: dict[tuple[str, str], dict] = defaultdict(
        lambda: {
            "courses_by_subject": defaultdict(lambda: {"name": "", "courses": []}),
            "courses_in_huvud": set(),
            "programmes": [],
        }
    )
    cross_inst: dict[str, set[str]] = defaultdict(set)

    for info in course_index.values():
        for h in info["huvudomr"]:
            key = (info["inst"], h)
            sub_entry = agg[key]["courses_by_subject"][info["subj_kod"]]
            sub_entry["name"] = info["subj_namn"] or info["subj_kod"]
            sub_entry["courses"].append(info["code"])
            agg[key]["courses_in_huvud"].add(info["code"])
            cross_inst[h].add(info["inst"])

    # Walk programmes; for each, see which (inst, huvudområde) buckets it
    # touches by intersection of course sets.
    prog_files = list(VAULT.glob("0[1-4]*/Utbildningsplaner/*.md"))
    for pp in prog_files:
        prog = parse_programme(pp)
        if not prog:
            continue
        # Only consider course overlaps for huvudområden in the SAME institution
        # (we never bridge institutions in the graph).
        for (inst, h), bucket in agg.items():
            if inst != prog["inst"]:
                continue
            overlap = prog["courses"] & bucket["courses_in_huvud"]
            if not overlap:
                continue
            bucket["programmes"].append({
                "code": prog["code"],
                "name": prog["name"],
                "overlap": len(overlap),
            })

    return agg, cross_inst


def moc_filename(huvudomrade: str, inst: str, spans_multiple: bool) -> str:
    base = f"Huvudområde - {huvudomrade}"
    if spans_multiple:
        base += f" ({inst})"
    return f"{base} MOC.md"


def render_moc(
    huvudomrade: str,
    inst: str,
    bucket: dict,
    spans_multiple: bool,
) -> str:
    """Bygg markdown-innehållet för en huvudområdes-MOC.

    Huvudområdes-MOC:en sätter inga graf-edges till institutions-MOC:en
    (``up:`` är ren textsträng) eller till ämnes-MOC:ar — endast till
    programmen som faktiskt inkluderar kurser med detta huvudområde. På så
    sätt klustrar sig huvudområdet visuellt med "sina" program istället för
    att hänga av institutionshubben."""
    courses_by_subject = bucket["courses_by_subject"]
    programmes = bucket["programmes"]
    total_courses = sum(len(s["courses"]) for s in courses_by_subject.values())
    n_subjects = len(courses_by_subject)

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
        "## Program",
        "",
    ]
    if programmes:
        sorted_programmes = sorted(programmes, key=lambda x: (-x["overlap"], x["name"]))
        for prog in sorted_programmes:
            lines.append(
                f"- [[{prog['code']}|{prog['code']}]] — {prog['name']} "
                f"({prog['overlap']} kurs"
                + ("er" if prog["overlap"] != 1 else "")
                + ")"
            )
    else:
        lines.append("_Inga program inkluderar kurser i detta huvudområde._")
    lines.append("")

    # Ämneslistan visas som ren text (inga graf-edges från huvudområde
    # till ämne) — den är informativ för läsaren men huvudområdet ska
    # bara koppla till program i graf-vyn.
    lines.append("## Ämnen (informativt)")
    lines.append("")
    sorted_subjects = sorted(
        courses_by_subject.items(),
        key=lambda kv: (-len(kv[1]["courses"]), kv[1]["name"]),
    )
    for subj_kod, data in sorted_subjects:
        n = len(data["courses"])
        href = data["name"] + " MOC"
        lines.append(
            f'- <a class="no-graph" href="{href}">{data["name"]}</a> '
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
    for (inst, huvudomrade), bucket in sorted(agg.items()):
        inst_dir = VAULT / INST_DIR_NAME[inst] / "Huvudområden"
        spans_multiple = huvudomrade in spans
        filename = moc_filename(huvudomrade, inst, spans_multiple)
        out_path = inst_dir / filename
        content = render_moc(huvudomrade, inst, bucket, spans_multiple)

        if args.apply:
            inst_dir.mkdir(parents=True, exist_ok=True)
            existing = out_path.read_text(encoding="utf-8") if out_path.exists() else None
            if existing != content:
                out_path.write_text(content, encoding="utf-8")
                written += 1
        per_inst_count[inst] += 1

        n_courses = sum(len(s["courses"]) for s in bucket["courses_by_subject"].values())
        n_subjects = len(bucket["courses_by_subject"])
        per_inst_entries[inst].append(
            (huvudomrade, filename[:-3], n_courses, n_subjects)
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
