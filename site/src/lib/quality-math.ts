// The numbers behind the quality dashboard, as plain data and plain functions, so the page
// (at build time) and the script (in the browser) count in exactly the same way.

export const INSTS = ["IIT", "IHV", "IKS", "ISLL"] as const
export type InstCode = (typeof INSTS)[number]
export type Scope = InstCode | "alla"
export type PlanKind = "course" | "programme"

/** [active, vilande] */
export type Pair = [number, number]

export interface Group {
  title: string
  inst: InstCode
  /** A subject's course plans, or an institution's programme plans. */
  kind: "subject" | "programmes"
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
  about: Record<InstCode, { purpose: string | null; advice: string | null; url: string | null }>
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

const sv = (n: number) => n.toLocaleString("sv-SE")
export const percent = (share: number) => (share > 0 && share < 0.005 ? "<1" : String(Math.round(share * 100)))

/** "kursplaner", "utbildningsplaner" or "planer", by what a check is run on. With vilande plans
 *  left out it says so: "aktiva kursplaner". (No programme plan is vilande, so those need no word.) */
export const planWord = (check: CheckSummary | null, vilande: boolean) => {
  const word = !check || check.kinds.length > 1 ? "planer" : check.kinds[0] === "course" ? "kursplaner" : "utbildningsplaner"
  return !vilande && word !== "utbildningsplaner" ? `aktiva ${word}` : word
}

/** The line under the page title: the figure, and the rest of its sentence. */
export function headline(o: Overview, vilande: boolean): [string, string] {
  const c = cell(o, null, "alla", vilande)
  const each = (c.notes / Math.max(1, c.of)).toLocaleString("sv-SE", { maximumFractionDigits: 1 })
  return [`${percent(c.share)} %`, ` av ${vilande ? "alla planer, vilande inräknade," : "de aktiva planerna"} har minst en notering, i snitt ${each} per plan.`]
}

/** "581 noteringar i 560 av 752 kursplaner (74 %)." */
export function sentence(c: Cell, check: CheckSummary | null, vilande: boolean): string {
  const what = planWord(check, vilande)
  if (!c.hit) return `Inga noteringar bland ${sv(c.of)} ${what}.`
  return `${sv(c.notes)} ${c.notes === 1 ? "notering" : "noteringar"} i ${sv(c.hit)} av ${sv(c.of)} ${what} (${percent(c.share)} %).`
}
