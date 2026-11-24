// English versions of the analysis notes' hand-written prose (Syfte, Metod, Datakälla,
// Rekommendationer, and the opening of each school's overview).
//
// The vault keeps the Swedish and stays untouched; the English lives in
// src/translations/analys/, one file per check. Each English section carries a fingerprint of
// the Swedish text it was translated from (<!-- sv 1a2b3c4d -->). If the Swedish has changed
// since, that section is shown in Swedish in English mode too, and the build says so: a
// translation is never shown for a text it was not made from.
//
// `node scripts/translations.ts` lists the state of every section; see site/README.md.
import fs from "node:fs"
import path from "node:path"
import crypto from "node:crypto"
import matter from "gray-matter"
import { getVault, INSTITUTIONS, type Doc, type Inst } from "./vault.ts"
import { instName } from "./ui.ts"

export const DIR = path.join(process.cwd(), "src", "translations", "analys")

/** The analysis notes' section headings, in English. */
export const HEADING_EN: Record<string, string> = {
  Syfte: "Purpose",
  Metod: "Method",
  Datakälla: "Data source",
  Rekommendationer: "Recommendations",
  Analyser: "Analyses",
  "Problematiska kursplaner": "Flagged course syllabi",
  "Problematiska utbildningsplaner": "Flagged programme syllabi",
}
const SV_OF = Object.fromEntries(Object.entries(HEADING_EN).map(([sv, en]) => [en, sv]))
/** The overview's opening paragraph, which has no heading of its own. */
export const INTRO = "Intro"

/** The fingerprint of a Swedish text: whitespace does not count, every other character does. */
export const fingerprint = (sv: string) => crypto.createHash("sha256").update(sv.replace(/\s+/g, " ").trim()).digest("hex").slice(0, 8)

export interface Section {
  /** The heading as written: "Syfte", or "" for the text before the first heading. */
  heading: string
  body: string
}

/** A note's body in sections, split at its H2 headings. The H1 is left out. */
export function sections(body: string): Section[] {
  const parts = body.replace(/^\s*# .*\r?\n/, "").split(/^## +/m)
  const out: Section[] = [{ heading: "", body: parts[0].trim() }]
  for (const p of parts.slice(1)) {
    const nl = p.indexOf("\n")
    out.push({ heading: (nl < 0 ? p : p.slice(0, nl)).trim(), body: nl < 0 ? "" : p.slice(nl + 1).trim() })
  }
  return out
}

export interface Translated {
  /** The Swedish heading this answers to. */
  sv: string
  heading: string
  /** null when the section has not been stamped with a fingerprint yet. */
  stamp: string | null
  body: string
}
export interface TranslationFile {
  file: string
  /** The check's Swedish name (Område), or null for the overview file. */
  check: string | null
  sections: Translated[]
}

let cache: Map<string, TranslationFile> | undefined
/** Every translation file, by its name without .md ("introfras", "_oversikt"). */
export function translationFiles(): Map<string, TranslationFile> {
  if (cache) return cache
  cache = new Map()
  if (!fs.existsSync(DIR)) return cache
  for (const name of fs.readdirSync(DIR).filter((f) => f.endsWith(".md")).sort()) {
    const file = path.join(DIR, name)
    const { data, content } = matter(fs.readFileSync(file, "utf8"))
    const out: Translated[] = []
    for (const s of sections(content).slice(1)) {
      const m = s.body.match(/^<!--\s*sv(?:\s+([0-9a-f]{8}))?\s*-->\s*/)
      out.push({ sv: SV_OF[s.heading] ?? s.heading, heading: s.heading, stamp: m?.[1] ?? null, body: m ? s.body.slice(m[0].length).trim() : s.body })
    }
    cache.set(name.replace(/\.md$/, ""), { file, check: typeof data.check === "string" ? data.check : null, sections: out })
  }
  return cache
}

const warned = new Set<string>()
function warn(what: string) {
  if (warned.has(what)) return
  warned.add(what)
  console.warn(`[translations] ${what}: shown in Swedish. Run node scripts/translations.ts`)
}

/** The English for one section of a check's analysis note, or null (no translation, or the
 *  Swedish has changed since it was made). */
export function englishSection(check: string, svHeading: string, svBody: string): string | null {
  const file = [...translationFiles().values()].find((f) => f.check === check)
  const t = file?.sections.find((s) => s.sv === svHeading)
  if (!t) return null
  if (t.stamp !== fingerprint(svBody)) {
    warn(`${check} / ${svHeading} ${t.stamp ? "has changed in the vault since it was translated" : "has no fingerprint yet"}`)
    return null
  }
  return t.body
}

/** The overview's opening paragraph is the same for every school bar the school's name, so it
 *  is compared with those taken out. */
export const genericIntro = (sv: string, inst: Inst) => sv.split(instName(inst, "sv")).join("{name}").split(inst).join("{code}")

/** The English opening of a school's analysis overview, or null. */
export function englishIntro(svIntro: string, inst: Inst): string | null {
  const t = translationFiles().get("_oversikt")?.sections.find((s) => s.heading === INTRO)
  if (!t) return null
  if (t.stamp !== fingerprint(genericIntro(svIntro, inst))) {
    warn(`The analysis overview's opening (${inst}) ${t.stamp ? "has changed in the vault since it was translated" : "has no fingerprint yet"}`)
    return null
  }
  return t.body.split("{name}").join(instName(inst, "en")).split("{code}").join(inst)
}

/** Each check's analysis note in the vault. They are the same for every school, so the first
 *  school's is the reference. */
export function analysisNotes(): Map<string, Doc> {
  const out = new Map<string, Doc>()
  for (const inst of INSTITUTIONS)
    for (const d of getVault().docs)
      if (d.kind === "analysis" && d.inst === inst && !out.has(d.title)) out.set(d.title, d)
  return out
}

// ── The pipeline's own words inside an analysis note ──
// The findings table, its title and the download link are written by the QA pipeline and can
// run to hundreds of rows, so they are not repeated per language. Only their labels are given
// an English twin, shown by the same rule as every other interface text.
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
/** Both languages of a label, one shown at a time (see site.css). */
export const both = (sv: string, en: string) => (sv === en ? sv : `<span data-l="sv">${sv}</span><span data-l="en" lang="en">${esc(en)}</span>`)

const COLUMN_EN: Record<string, string> = {
  Kursplan: "Syllabus",
  Utbildningsplan: "Programme syllabus",
  Sida: "Page",
  Ämne: "Subject",
  Institution: "School",
  Fastställd: "Established",
  Reviderad: "Revised",
  Detalj: "Detail",
  Förslag: "Suggestion",
}

/** Give the labels in a rendered analysis note their English twins: column headings, problem
 *  labels, check names in links, the "page" links, the table's title and the download link.
 *  Everything else, including every detail cell, stays exactly as written. */
export function bilingualLabels(html: string, checks: Record<string, string>, problems: Record<string, string>): string {
  return html
    .replace(/<th([^>]*)>([^<]+)<\/th>/g, (m, a, t) => (COLUMN_EN[t] ? `<th${a}>${both(t, COLUMN_EN[t])}</th>` : m))
    .replace(/<td([^>]*)>([^<]+)<\/td>/g, (m, a, t) => (problems[t] ? `<td${a}>${both(t, problems[t])}</td>` : m))
    .replace(/(<a class="internal"[^>]*>)([^<]+)(<\/a>)/g, (m, open, t, close) => (checks[t] ? open + both(t, checks[t]) + close : m))
    .replace(/(<a class="no-graph"[^>]*>)sida(<\/a>)/g, (_, open, close) => open + both("sida", "page") + close)
    .replace(/(<div class="callout-title-text">)((\d+) fynd \u2014 klicka för att expandera)(<\/div>)/g, (_, open, sv, n, close) =>
      open + both(sv, `${n} ${n === "1" ? "finding" : "findings"}, click to expand`) + close)
    .replace(/<span>(Ladda ner som Excel-fil \((\d+) rad(?:er)?\))<\/span>/g, (_, sv, n) =>
      `<span>${both(sv, `Download as an Excel file (${n} ${n === "1" ? "row" : "rows"})`)}</span>`)
}
