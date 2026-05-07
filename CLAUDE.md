# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A Quartz 4 static site and Obsidian vault synthesizing the entire course and programme structure of Högskolan Dalarna (Dalarna University). It covers all four institutions (IIT, IHV, IKS, ISLL) with both course plans (kursplaner) and programme plans (utbildningsplaner).

This is **not a software project** — it is a structured knowledge base for navigating the university's educational offerings.

## Repository structure

```text
vault-dalarna-university/   Obsidian vault — living knowledge base
  00 Dashboard/             Overview and navigation hub
  01 IIT/                   Institution: Information & Engineering
    IIT MOC.md              Institution map of content
    Kursplaner/             Subject MOCs + course-code subfolders (DTA, BYA, …)
    Utbildningsplaner/      Programme files
  02 IHV/                   Institution: Health & Welfare
  03 IKS/                   Institution: Culture & Society
  04 ISLL/                  Institution: Language, Literature & Learning
  05 Analys/                Cross-cutting quality analyses (auto-populated)
  Templates/                Obsidian templates
content -> vault-dalarna-university  Symlink for Quartz site build
quartz/                     Quartz 4 static site engine
quartz.config.ts            Site configuration
quartz.layout.ts            Page layout configuration
qa/                         Quality-control pipeline (Python)
  check_kursplaner.py       Run all 11 checks against course plans
  check_utbildningsplaner.py Reduced check set for programme plans
  checks_common.py          Shared helpers + 4 reusable language checks
  diff_rapporter.py         Compare two QA reports — resolved vs new findings
  populate_analysfiler.py   Fill 03 Analys/ from latest report (also writes .xlsx alongside)
  prune_analysfiler.py      Remove resolved rows from 03 Analys/
  identify_ej_aktiv.py      Tag courses no longer in du.se as ej-aktiv (orphan detector)
  rapporter/                Timestamped course-plan QA reports
  rapporter-utb/            Timestamped programme-plan QA reports
hda.sh                      Interactive menu for the full workflow
```

### Dandyflower MOC pattern

MOCs (Maps of Content) use a dandyflower pattern: seeds spread outward from a central MOC without tangling across other seeds. The hierarchy is:

```text
Dalarna Dashboard
├── IIT MOC
│   ├── Kursplaner/  (subject MOCs → course files)
│   └── Utbildningsplaner/  (programme files)
├── IHV MOC
│   ├── Kursplaner/
│   └── Utbildningsplaner/
├── IKS MOC
│   ├── Kursplaner/
│   └── Utbildningsplaner/
└── ISLL MOC
    ├── Kursplaner/
    └── Utbildningsplaner/
```

Each file has an `up:` frontmatter key pointing to its parent MOC.

## Quartz site

Build and preview:

```bash
npm ci
npx quartz build           # build to public/
npx quartz build --serve   # local preview at localhost:8080
```

Deploy is automatic via GitHub Actions on push to main.

## Course plan scraping

Scrape all course plans from du.se:

```bash
python3 scrape_hda_kursplaner.py                     # dry-run (discover all)
python3 scrape_hda_kursplaner.py --apply              # write files
python3 scrape_hda_kursplaner.py --institution IIT    # only IIT
python3 scrape_hda_kursplaner.py --subject DTA        # only Datateknik
python3 scrape_hda_kursplaner.py --list-institutions  # list institutions
python3 scrape_hda_kursplaner.py --list-subjects      # list all subjects
python3 scrape_hda_kursplaner.py --list-courses       # list all courses
python3 scrape_hda_kursplaner.py GIK29B GDT34Z        # specific courses
```

Requires: `requests`, `beautifulsoup4`.

## Programme plan scraping

Scrape all programme plans from du.se:

```bash
python3 scrape_hda_utbildningsplaner.py               # dry-run
python3 scrape_hda_utbildningsplaner.py --apply        # write files
python3 scrape_hda_utbildningsplaner.py --list-programmes  # list all programmes
python3 scrape_hda_utbildningsplaner.py LGGYA HMILA    # specific programmes
```

Requires: `requests`, `beautifulsoup4`.

## Quality-control pipeline

Cross-cutting kvalitetsgranskning of all course and programme plans, mirroring the UKU repo's pipeline but scaled to all four institutions.

```bash
./hda.sh                                          # interactive menu
python3 qa/check_kursplaner.py --out qa/rapporter/rapport.md           # course plans
python3 qa/check_utbildningsplaner.py --out qa/rapporter-utb/rapport.md # programme plans
python3 qa/diff_rapporter.py --latest2            # what was resolved / what's new
python3 qa/populate_analysfiler.py                # fill 03 Analys/ from latest report
python3 qa/prune_analysfiler.py --dry-run         # remove resolved rows
```

Course-plan checks (11): duplicated words, known typos, hunspell sv/en, learning-outcome intro phrasing, grading scale, examination structure, learning-outcome count + length, Bloom verb level for advanced courses, Swedish/English parity. Programme-plan checks (4): duplicated words, known typos, hunspell sv/en. Hunspell requires `hunspell` + `sv_SE`/`en_US` dictionaries; without them, run with `--skip-hunspell`.

The `vault-dalarna-university/03 Analys/` files are the editorial layer — `populate_analysfiler.py` writes the `> [!example]-` callout block from the latest QA report, while the surrounding prose (Syfte / Metod / Observationer / Rekommendationer) is curated by hand.

## Ej-aktiv detection

`qa/identify_ej_aktiv.py` rediscovers the current du.se course offering per subject (using the same logic as the kursplan scraper, without per-course scraping) and compares it to the vault. Course files in the vault whose codes are no longer on du.se are tagged `ej-aktiv` (in both `tags:` and `cssclasses:`) and re-pointed via `up:` to a generated `Ej Aktiv {Subject} MOC.md`. Re-emerged courses are auto-untagged. The graph view colors `ej-aktiv` nodes in warm red so they stand out.

## Four institutions

| Abbrev | Swedish name | English name |
|--------|-------------|-------------|
| IIT | Institutionen för Information och Teknik | School of Information and Engineering |
| IHV | Institutionen för Hälsa och Välfärd | School of Health and Welfare |
| IKS | Institutionen för Kultur och Samhälle | School of Culture and Society |
| ISLL | Institutionen för Språk, Litteratur och Lärande | School of Language, Literature and Learning |
