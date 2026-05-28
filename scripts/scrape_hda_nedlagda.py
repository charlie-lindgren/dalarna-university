#!/usr/bin/env python3
"""scrape_hda_nedlagda.py — Skrapa nedlagda kursplaner från du.se till QA-cache.

Hämtar samtliga kursplaner med ``status=discontinued`` via du.se:s sök-API och
sparar en slim metadata-fil per kurskod under ``qa/nedlagda-kursplaner/``.
Cachen är gitignored och visas inte på sajten — den används bara av QA-koden
för att t.ex. flagga utbildningsplaner som listar nedlagda kurser och vid
analys av förkunskapskrav.

Använd ``--apply`` för att skriva. Utan flaggan görs en dry-run. Nedlagda
kursplaner är persistenta — när en kurs väl är nedlagd återuppstår den inte
— så cachade poster hoppas alltid över utan omskrapning.
"""

from __future__ import annotations

import argparse
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Återanvänd hjälparna från den aktiva scrapern.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from scrape_hda_kursplaner import (  # noqa: E402
    SV_URL,
    _extract_code_from_href,
    extract_course_name,
    extract_metadata,
    fetch_page,
    parse_amnestillhorighet,
    parse_institution_from_meta,
)

REPO_ROOT = SCRIPT_DIR.parent
CACHE_DIR = REPO_ROOT / "qa" / "nedlagda-kursplaner"
SEARCH_URL = "https://www.du.se/sv/utbildning/kursplaner/Search/"


def discover_nedlagda_codes() -> set[str]:
    """Returnerar samtliga kurskoder med ``status=discontinued`` på du.se."""
    soup = fetch_page(
        SEARCH_URL,
        params={"searchtype": "code", "code": "%", "status": "discontinued"},
    )
    if soup is None:
        return set()
    codes: set[str] = set()
    for a in soup.select("table#coursesTable tbody a[href*='code=']"):
        code = _extract_code_from_href(a["href"])
        if code:
            codes.add(code)
    return codes


def scrape_nedlagd(code: str) -> dict | None:
    """Skrapar en enskild nedlagd kursplan utan att avbryta på nedlagd-text."""
    soup = fetch_page(SV_URL.format(code=code))
    if soup is None:
        return None
    name = extract_course_name(soup)
    if not (name or "").strip():
        return None
    meta = extract_metadata(soup)
    return {"code": code, "name": name, "metadata": meta}


def build_md(scraped: dict) -> str:
    code = scraped["code"]
    name = scraped["name"]
    meta = scraped["metadata"]
    am = parse_amnestillhorighet(meta)
    inst = parse_institution_from_meta(meta) or ""
    subject_name = am[0] if am else ""
    subject_code = am[1] if am else ""

    lines = [
        "---",
        f"kurskod: {code}",
        f'kursnamn: "{name}"',
    ]
    if subject_name:
        lines.append(f'amne: "{subject_name}"')
    if subject_code:
        lines.append(f"amneskod: {subject_code}")
    if inst:
        lines.append(f'institution: "{inst}"')
    if meta.get("Fastställd"):
        lines.append(f'faststalld: "{meta["Fastställd"]}"')
    if meta.get("Nedlagd"):
        lines.append(f'nedlagd: "{meta["Nedlagd"]}"')
    if meta.get("Nivå"):
        lines.append(f'niva: "{meta["Nivå"]}"')
    if meta.get("Poäng"):
        lines.append(f'poang: "{meta["Poäng"]}"')
    lines.append("tags: [kursplan, nedlagd]")
    lines.append("---")
    lines.append("")
    lines.append(f"# {code}")
    lines.append("")
    lines.append(f"**Kursnamn:** {name}")
    if subject_name:
        suffix = f" ({subject_code})" if subject_code else ""
        lines.append(f"**Ämne:** {subject_name}{suffix}")
    if inst:
        lines.append(f"**Institution:** {inst}")
    for key in ("Nivå", "Poäng", "Fastställd", "Nedlagd"):
        if meta.get(key):
            lines.append(f"**{key}:** {meta[key]}")
    return "\n".join(lines).rstrip() + "\n"


def _load_existing() -> set[str]:
    if not CACHE_DIR.exists():
        return set()
    return {p.stem for p in CACHE_DIR.glob("*.md")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "codes",
        nargs="*",
        help="Specifika koder att skrapa (annars alla nedlagda enligt du.se).",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Skriv filer (utan flaggan görs en dry-run).",
    )
    parser.add_argument(
        "--concurrency", type=int, default=6,
        help="Antal parallella förfrågningar (default: 6).",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Begränsa antal koder (för stickprov).",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Tystare loggning.",
    )
    args = parser.parse_args()

    if args.codes:
        all_codes = {c.upper() for c in args.codes}
        if not args.quiet:
            print(f"  {len(all_codes)} kod(er) från kommandoraden")
    else:
        if not args.quiet:
            print("Hämtar lista över nedlagda kursplaner från du.se …")
        all_codes = discover_nedlagda_codes()
        if not args.quiet:
            print(f"  {len(all_codes)} nedlagda kursplaner enligt du.se")

    existing = _load_existing() if not args.force else set()
    targets = sorted(all_codes - existing)
    if not args.quiet and existing:
        print(f"  {len(existing)} redan cachade — hoppar över "
              f"(använd --force för omskrivning)")

    if args.limit:
        targets = targets[: args.limit]
        if not args.quiet:
            print(f"  Begränsar till {len(targets)} (--limit)")

    if not targets:
        print("Inget att skrapa.")
        return 0

    mode = "SKRIVER" if args.apply else "DRY-RUN"
    print()
    print("╔══════════════════════════════════════════════════╗")
    print(f"║  HDa nedlagda-kursplaner — {mode:<22}║")
    print(f"║     {len(targets):>4} koder att bearbeta              ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    if args.apply:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    n_written = n_unchanged = n_empty = n_err = 0

    def _process(code: str) -> tuple[str, str]:
        try:
            scraped = scrape_nedlagd(code)
            if scraped is None:
                return code, "tom"
            md = build_md(scraped)
            path = CACHE_DIR / f"{code}.md"
            if path.exists():
                if path.read_text(encoding="utf-8") == md:
                    return code, "oförändrad"
            if args.apply:
                path.write_text(md, encoding="utf-8")
            return code, "skriven"
        except Exception as exc:  # pragma: no cover — defensiv
            return code, f"fel: {exc}"

    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {ex.submit(_process, c): c for c in targets}
        for i, fut in enumerate(as_completed(futures), 1):
            code, status = fut.result()
            if status.startswith("fel"):
                n_err += 1
                print(f"  ✗ {code}: {status}", file=sys.stderr)
            elif status == "tom":
                n_empty += 1
            elif status == "oförändrad":
                n_unchanged += 1
            else:
                n_written += 1
            if not args.quiet and (i % 100 == 0 or i == len(targets)):
                print(f"  [{i}/{len(targets)}] {n_written} skrivna, "
                      f"{n_unchanged} oförändrade, {n_empty} tomma, {n_err} fel")

    print()
    print(f"Klart: {n_written} skrivna, {n_unchanged} oförändrade, "
          f"{n_empty} tomma, {n_err} fel.")
    if not args.apply and n_written:
        print("Kör igen med --apply för att spara.")
    return 0 if n_err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
