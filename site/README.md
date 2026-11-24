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
| `src/pages/` | One file per kind of page: Sök (`index.astro`), `bladdra/`, `kvalitet/`, `kurs/`, `program/`; `[...path].astro` takes the rest |
| `src/components/`, `src/layouts/` | The shell (menu, appearance switch) and the plan page |
| `src/scripts/` | What runs in the browser. Every page reads fine without it |
| `src/styles/` | `base.css` is the house design language; `site.css` the shell; one file per page type |

## Addresses

| Address | Page |
|---|---|
| `/` | Sök |
| `/bladdra/`, `/bladdra/graf/` | Bläddra, as columns or as a graph |
| `/kvalitet/` | The quality dashboard |
| `/kurs/<kod>/`, `/program/<kod>/` | A course plan, a programme plan |
| `/amne/<namn>/`, `/institution/<inst>/`, `/kvalitet/<inst>/<kontroll>/` | The vault's own list and analysis notes |

A code that exists under two institutions carries the institution: `/kurs/GIE3HX-iit/`.
Codes lose Å, Ä and Ö in addresses only: `FÖ1041` is at `/kurs/FO1041/`.

The base path comes from `SITE_BASE` (default `/dalarna-university`).
