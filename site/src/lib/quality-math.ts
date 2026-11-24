// The numbers behind the quality dashboard, as plain data and plain functions, so the page
// (at build time) and the script (in the browser) count in exactly the same way.

import { LOCALE, num, say, t, type Lang } from "./ui"
import { checkName } from "./checks"

export const INSTS = ["IIT", "IHV", "IKS", "ISLL"] as const
export type InstCode = (typeof INSTS)[number]
export type Scope = InstCode | "alla"
export type PlanKind = "course" | "programme"

/** [active, vilande] */
export type Pair = [number, number]

export interface Group {
  title: string
  inst: InstCode
  /** A subject's course plans, an institution's programme plans, or its course plans that
   *  belong to no subject in the vault. Only a subject's title is the vault's own word. */
  kind: "subject" | "programmes" | "loose"
  plans: Pair
}

export interface CheckSummary {
  slug: string
  area: string
  /** The kinds of plan this check is run on; its share is counted against those only. */
  kinds: PlanKind[]
  /** Per institution: plans with a note [active, vilande], and notes [active, vilande]. */
  m: Record<InstCode, { plans: Pair; notes: Pair }>
}

export interface Overview {
  totals: Record<InstCode, Record<PlanKind, Pair>>
  /** Plans with at least one note of any kind, and all notes. */
  any: Record<InstCode, { plans: Pair; notes: Pair }>
  checks: CheckSummary[]
  groups: Group[]
}

/** One check's notes, fetched when the reader opens it. */
export interface CheckDetail {
  problems: string[]
  /** [code, name, group index, vilande 0|1, site path] */
  plans: [string, string, number, 0 | 1, string][]
  /** [plan index, problem index, detail as HTML] */
  notes: [number, number, string][]
  /** What the check is for and what to do, from the analysis notes; the English is null
   *  where no up-to-date translation exists. */
  about: Record<InstCode, { purpose: string | null; advice: string | null; purposeEn: string | null; adviceEn: string | null; url: string | null }>
}

const sum = (p: Pair, vilande: boolean) => p[0] + (vilande ? p[1] : 0)
const scopeOf = (scope: Scope) => (scope === "alla" ? INSTS : [scope])

export interface Cell {
  /** Plans with at least one note. */
  hit: number
  /** Plans the check applies to. */
  of: number
  notes: number
  share: number
}

/** One cell of the heat table. `check` null is the "at least one note of any kind" row. */
export function cell(o: Overview, check: CheckSummary | null, scope: Scope, vilande: boolean): Cell {
  let hit = 0, of = 0, notes = 0
  for (const inst of scopeOf(scope)) {
    const m = check ? check.m[inst] : o.any[inst]
    hit += sum(m.plans, vilande)
    notes += sum(m.notes, vilande)
    for (const kind of check ? check.kinds : (["course", "programme"] as PlanKind[])) of += sum(o.totals[inst][kind], vilande)
  }
  return { hit, of, notes, share: of ? hit / of : 0 }
}

export const percent = (share: number) => (share > 0 && share < 0.005 ? "<1" : String(Math.round(share * 100)))
/** "81 %" in Swedish, "81%" in English. */
export const pct = (share: number, lang: Lang) => (lang === "en" ? `${percent(share)}%` : `${percent(share)} %`)

/** What a check is run on: "kursplaner", "utbildningsplaner" or "planer". With vilande plans
 *  left out it says so: "aktiva kursplaner". (No programme plan is vilande, so those need no word.) */
export const planWord = (check: CheckSummary | null, vilande: boolean, lang: Lang) => {
  const kind = !check || check.kinds.length > 1 ? "any" : check.kinds[0]
  const word =
    lang === "en"
      ? { any: "syllabi", course: "course syllabi", programme: "programme syllabi" }[kind]
      : { any: "planer", course: "kursplaner", programme: "utbildningsplaner" }[kind]
  return !vilande && kind !== "programme" ? `${lang === "en" ? "active" : "aktiva"} ${word}` : word
}

/** The line under the page title: the figure, and the rest of its sentence. */
export function headline(o: Overview, vilande: boolean, lang: Lang): [string, string] {
  const c = cell(o, null, "alla", vilande)
  const each = (c.notes / Math.max(1, c.of)).toLocaleString(LOCALE[lang], { maximumFractionDigits: 1 })
  return lang === "en"
    ? [pct(c.share, lang), ` of ${vilande ? "all syllabi, dormant ones included," : "the active syllabi"} have at least one note, ${each} per syllabus on average.`]
    : [pct(c.share, lang), ` av ${vilande ? "alla planer, vilande inräknade," : "de aktiva planerna"} har minst en notering, i snitt ${each} per plan.`]
}

/** "581 noteringar i 560 av 752 kursplaner (74 %)." */
export function sentence(c: Cell, check: CheckSummary | null, vilande: boolean, lang: Lang): string {
  const what = planWord(check, vilande, lang)
  if (!c.hit) return lang === "en" ? `No notes among ${num(c.of, lang)} ${what}.` : `Inga noteringar bland ${num(c.of, lang)} ${what}.`
  return lang === "en"
    ? `${say.notes(c.notes, lang)} in ${say.of(c.hit, c.of, lang)} ${what} (${pct(c.share, lang)}).`
    : `${say.notes(c.notes, lang)} i ${say.of(c.hit, c.of, lang)} ${what} (${pct(c.share, lang)}).`
}

/** What one cell of the table says, for a screen reader. `check` null is the "any note" row. */
export function cellLabel(o: Overview, check: CheckSummary | null, scope: Scope, vilande: boolean, lang: Lang): string {
  const c = cell(o, check, scope, vilande)
  const where = scope === "alla" ? t("q.allSchools", lang).toLowerCase() : scope
  return `${check ? checkName(check.area, lang) : t("q.any", lang)}, ${where}: ${pct(c.share, lang)}, ${say.of(c.hit, c.of, lang)} ${planWord(check, vilande, lang)}`
}
