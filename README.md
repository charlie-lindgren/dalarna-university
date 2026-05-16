# Högskolan Dalarna — Utbildningsöversikt

A Quartz 4 static site and Obsidian vault synthesizing the entire course and
programme structure of Högskolan Dalarna (Dalarna University). It covers all
four institutions (IIT, IHV, IKS, ISLL) with both course plans (kursplaner)
and programme plans (utbildningsplaner), plus a per-institution quality
assessment layer.

This is **not a software project** — it is a structured knowledge base for
navigating the university's educational offerings.

## Repository structure

```text
vault-dalarna-university/   Obsidian vault — living knowledge base
  00 Dashboard/             Overview and navigation hub
  01 IIT/                   Institutionen för information och teknik
    IIT MOC.md              Institution map of content
    Kursplaner/             Subject MOCs + course-code subfolders (DTA, BYA, …)
    Utbildningsplaner/      Programme files
    Analys/                 Per-institution quality analyses
  02 IHV/                   Institutionen för hälsa och välfärd
  03 IKS/                   Institutionen för kultur och samhälle
  04 ISLL/                  Institutionen för språk, litteratur och lärande
  Templates/                Obsidian templates
content -> vault-dalarna-university   Symlink for Quartz site build
quartz/                     Quartz 4 static site engine
qa/                         Quality-control pipeline (Python)
scripts/                    Scrapers (course + programme plans)
hda.sh                      Interactive menu for the full workflow
```

## Workflow via `./hda.sh`

The interactive menu (`./hda.sh`) is the primary entry point. It is split into
two sections: **Skrapa & bygg** and **Kvalitetsgranskning**.

### Phase 1 — Data ingestion (scraping)

1. **Scrape ALL course plans** (menu `1`)
   - Crawls all of du.se per institution → subject → course.
   - `--discover-stray` picks up orphan codes (e.g. GIK289-class).
   - Writes/updates files under `0X {INST}/Kursplaner/<SUBJECT>/` and each
     institution's MOC.

2. **Scrape programme plans** (menu `3`)
   - Pulls every programme plan into `0X {INST}/Utbildningsplaner/`.

3. **Identify vilande courses** (menu `4`)
   - Compares vault against current du.se offerings.
   - Tags courses with no scheduled occasion as `vilande` and refreshes
     `0X {INST}/Analys/Vilande kursplaner.md/.xlsx` per institution.

> Menu item `2` scrapes only course plans (no stray detection) for quick
> incremental runs.

### Phase 2 — Quality assessment (QA)

4. **QA of course plans** (menu `7`)
   - Runs 11 language/structure checks across all course plans.
   - Writes a timestamped report to
     `qa/rapporter/rapport-YYYY-MM-DD-HHMM.md`.

5. **QA of programme plans** (menu `8`)
   - Runs 4 reduced checks against programme plans.
   - Writes to `qa/rapporter-utb/`.

6. **Diff vs previous report** (menu `9`)
   - Shows resolved findings and new findings since the last run.

### Phase 3 — Editorial workflow

7. **Populate analysis files** (menu `10`)
   - Reads the latest report, classifies every finding to its institution by
     mapping the course code to its location in the vault.
   - Writes a callout table and `.xlsx` into each
     `0X {INST}/Analys/<analysis>.md`.
   - Curated prose (Syfte / Metod / Observationer / Rekommendationer) is
     left untouched.

8. **Manual review** (in Obsidian)
   - Walk each institution's Analys folder, fill in
     Observationer/Rekommendationer.
   - Fix findings by editing the underlying course plans directly.

9. **Prune resolved findings** (menu `11`)
   - After a fresh QA run, removes callout rows whose course code is no
     longer in the report.
   - Large deletions (≥50%) require per-institution confirmation.

### Phase 4 — Publish

10. **Build the site** (menu `5`) or **Build + serve** (menu `6`)
    - `5` produces `public/` for deploy (GitHub Actions takes over on push to
      `main`).
    - `6` starts a local preview at `localhost:8080`.

### Typical loop

```text
1 → 3 → 4 → 7 → 10 → (manual editing) → 9 → 11 → 5
```

First-time setup on a fresh checkout: `1`, `3`, `4`, `7`, `10`, `5`.
Subsequent cycles: QA → populate → manual editing → prune → build.

## Direct command-line usage

The menu wraps these scripts; you can also invoke them directly.

### Course-plan scraping

```bash
python3 scripts/scrape_hda_kursplaner.py                       # dry-run
python3 scripts/scrape_hda_kursplaner.py --apply               # write files
python3 scripts/scrape_hda_kursplaner.py --apply --discover-stray
python3 scripts/scrape_hda_kursplaner.py --institution IIT     # only IIT
python3 scripts/scrape_hda_kursplaner.py --subject DTA         # only Datateknik
python3 scripts/scrape_hda_kursplaner.py GIK29B GDT34Z         # specific courses
python3 scripts/scrape_hda_kursplaner.py --list-institutions
python3 scripts/scrape_hda_kursplaner.py --list-subjects
python3 scripts/scrape_hda_kursplaner.py --list-courses
```

Requires: `requests`, `beautifulsoup4`.

### Programme-plan scraping

```bash
python3 scripts/scrape_hda_utbildningsplaner.py                # dry-run
python3 scripts/scrape_hda_utbildningsplaner.py --apply        # write files
python3 scripts/scrape_hda_utbildningsplaner.py --list-programmes
python3 scripts/scrape_hda_utbildningsplaner.py LGGYA HMILA    # specific programmes
```

### QA pipeline

```bash
python3 qa/check_kursplaner.py --out qa/rapporter/rapport.md
python3 qa/check_utbildningsplaner.py --out qa/rapporter-utb/rapport.md
python3 qa/diff_rapporter.py --latest2
python3 qa/populate_analysfiler.py        # fill per-institution Analys files
python3 qa/prune_analysfiler.py --dry-run # remove resolved rows
python3 qa/identify_ej_aktiv.py --apply   # tag vilande courses
```

Course-plan checks (11): duplicated words, known typos, hunspell sv/en,
learning-outcome intro phrasing, grading scale, examination structure,
learning-outcome count + length, Bloom verb level for advanced courses,
Swedish/English parity. Programme-plan checks (4): duplicated words, known
typos, hunspell sv/en. Hunspell requires `hunspell` plus `sv_SE`/`en_US`
dictionaries; without them, run with `--skip-hunspell`.

### Quartz site

```bash
npm ci
npx quartz build              # build to public/
npx quartz build --serve      # local preview at localhost:8080
```

Deploy is automatic via GitHub Actions on push to `main`.

## Information architecture

### Dandyflower MOC pattern

MOCs (Maps of Content) use a dandyflower pattern: seeds spread outward from a
central MOC without tangling across other seeds.

```text
Dalarna Dashboard
├── IIT MOC
│   ├── Kursplaner/        (subject MOCs → course files)
│   ├── Utbildningsplaner/ (programme files)
│   └── Analys/            (per-institution quality analyses)
├── IHV MOC
│   ├── Kursplaner/
│   ├── Utbildningsplaner/
│   └── Analys/
├── IKS MOC
│   ├── …
└── ISLL MOC
    └── …
```

Each file has an `up:` frontmatter key pointing to its parent MOC.

### Per-institution Analys layer

Each institution owns its own Analys folder. The nine analysis files mirror
across institutions:

- `Stavfel och språkbruk.md`
- `Introfras.md`
- `Frasningskonsistens.md`
- `Omfång på lärandemål.md`
- `Bloom-taxonomi.md`
- `Examinationsformer.md`
- `Betygsskalor.md`
- `Samstämmighet svenska och engelska.md`
- `Vilande kursplaner.md`

`populate_analysfiler.py` writes the `> [!example]-` callout block from the
latest QA report into each institution's copy; surrounding prose
(Syfte / Metod / Datakälla / Resultat / Observationer / Rekommendationer) is
curated by hand.

Findings are routed to the correct institution by mapping the course code to
its location in the vault (`0X {INST}/Kursplaner/<SUBJECT>/<CODE>.md`). The
`institution:` frontmatter field acts as a tiebreaker when the same code
appears under more than one institution.

## Ej-aktiv detection

`qa/identify_ej_aktiv.py` rediscovers the current du.se offering per subject
and compares it to the vault. Course files whose codes no longer appear on
du.se are tagged `vilande` (in both `tags:` and `cssclasses:`) and re-pointed
via `up:` to a generated `Ej Aktiv {Subject} MOC.md`. Re-emerged courses are
auto-untagged. The graph view colours `vilande` nodes in warm red so they
stand out.

## Four institutions

| Abbrev | Swedish name | English name |
|--------|-------------|-------------|
| IIT | Institutionen för Information och Teknik | School of Information and Engineering |
| IHV | Institutionen för Hälsa och Välfärd | School of Health and Welfare |
| IKS | Institutionen för Kultur och Samhälle | School of Culture and Society |
| ISLL | Institutionen för Språk, Litteratur och Lärande | School of Language, Literature and Learning |
