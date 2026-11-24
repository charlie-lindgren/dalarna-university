# The new site

A rebuild of the Högskolan Dalarna site on Astro. It reads the vault in
`../vault-dalarna-university/` and writes a static site. It never writes to the vault, and it
shows plan text exactly as scraped.

Until cutover the live site is still Quartz. This one is published beside it as a preview at
`/dalarna-university/next/`, by the same workflow (`.github/workflows/deploy.yml`).

## Commands

Run these from `site/`.

| Command | What it does |
|---|---|
| `npm install` | Install dependencies (once) |
| `npm run dev` | Local preview at `http://localhost:4321/dalarna-university/`. Runs in the background; stop it with `npx astro dev stop` |
| `npm run build` | Build to `dist/` and index the plans for full-text search |
| `npm run check:links` | After a build: every internal link must lead somewhere |
| `node scripts/check-fidelity.ts` | After a build: every plan's text must equal the vault's, word for word |
| `npm run report` | What the vault index contains: counts, and links that do not resolve |
| `npx astro check` | Type-check |

The search field's full-text results come from the last build, also in the local preview. Run
`npm run build` once to get them there.

## What is where

| Path | Holds |
|---|---|
| `src/lib/vault.ts` | Reads the vault once per build: every note's kind, address, links, facts and quality notes |
| `src/lib/markdown.ts` | Vault markdown to HTML: wikilinks, callouts, and links written with Quartz paths |
| `src/lib/plan.ts` | A course or programme plan, shaped for its page |
| `src/lib/quality.ts`, `quality-math.ts`, `heat.ts` | The numbers and colours behind Kvalitet |
| `src/lib/graph.ts` | The graph's layout, computed at build time |
| `src/lib/ui.ts` | Every word the site itself says, in Swedish and English |
| `src/lib/checks.ts`, `src/lib/analysis-en.ts`, `src/translations/analys/` | The quality checks and analysis notes in English |
| `src/pages/` | One file per kind of page: Sök (`index.astro`), `bladdra/`, `graf/`, `kvalitet/`, `kurs/`, `program/`; `[...path].astro` takes the rest |
| `src/components/`, `src/layouts/` | The shell (menu, language and appearance switches) and the plan page |
| `src/scripts/` | What runs in the browser. Every page reads fine without it |
| `src/styles/` | `base.css` is the house design language; `site.css` the shell; one file per page type |

## Addresses

| Address | Page |
|---|---|
| `/` | Sök |
| `/bladdra/` | Bläddra: school, subject and course in three columns |
| `/graf/` | The graph |
| `/kvalitet/` | The quality dashboard |
| `/kurs/<kod>/`, `/program/<kod>/` | A course plan, a programme plan |
| `/amne/<namn>/`, `/institution/<inst>/`, `/kvalitet/<inst>/<kontroll>/` | The vault's own list and analysis notes |

A code that exists under two institutions carries the institution: `/kurs/GIE3HX-iit/`.
Codes lose Å, Ä and Ö in addresses only: `FÖ1041` is at `/kurs/FO1041/`.

The base path comes from `SITE_BASE` (default `/dalarna-university`).

## Interface language

The menu has a SV | EN switch. It changes the site's own words only: menus, headings, labels,
counts. Plan text, course names and analysis notes stay as the vault has them.

Every page carries both languages, so switching needs no reload and no second set of pages.
`<html data-ui>` says which one shows; `?ui=en` on any address opens it in English.

To add or change a string, edit `src/lib/ui.ts` and use it in one of three ways:

| Where | How |
|---|---|
| Text in a template | `<T k="menu.sok" />`, or `<T sv="…" en="…" />` for text built from data |
| An attribute (`aria-label`, `placeholder`, `title`) | `{...attrs({ "aria-label": "menu.label" })}`. Add `{ lang: true }` as a second argument when the element holds no Swedish text of its own, so a screen reader says the label in the right language |
| A script | `t(key, uiLang())` or one of the `say.*` sentences, drawn again on the `uichange` event |

### Check names, problem labels and the analysis texts

The quality checks' names and problem labels have their English in `src/lib/checks.ts`. The
hand-written parts of the analysis notes (Syfte, Metod, Datakälla, Rekommendationer, and the
opening of each school's overview) have theirs in `src/translations/analys/`, one file per
check. The findings tables are not translated, only their labels; detail texts quote the plans
and stay Swedish.

Each English section carries a fingerprint of the Swedish it was translated from
(`<!-- sv 1a2b3c4d -->`). When the Swedish in the vault changes, that section is shown in
Swedish in English mode too, and the build prints a warning, so an English text never stands
for a Swedish one it was not made from.

| Command | What it does |
|---|---|
| `node scripts/translations.ts` | The state of every section, and any check name or problem label without English |
| `node scripts/translations.ts --stamp` | Fingerprint new sections (written with a bare `<!-- sv -->`) |
| `node scripts/translations.ts --stamp introfras` | After bringing one file's English up to date: fingerprint all its sections again |
