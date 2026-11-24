// The quality notes, gathered for the dashboard: the overview the page embeds, and one
// file of detail per check that the page fetches when the reader opens that check.
import { getVault, parentOf, slugify, INSTITUTIONS, type Doc, type Inst } from "./vault"
import { renderMarkdown } from "./markdown"
import type { CheckDetail, CheckSummary, Group, Overview, Pair, PlanKind } from "./quality-math"

const pair = (): Pair => [0, 0]
const kindOf = (d: Doc): PlanKind => (d.kind === "course" ? "course" : "programme")

let cached: { overview: Overview; groupOf: Map<Doc, number> } | undefined

function gather() {
  if (cached) return cached
  const v = getVault()
  const plans = v.docs.filter((d) => d.plan)

  // Groups: each institution's subjects, then its programme plans as one group.
  const groups: Group[] = []
  const groupOf = new Map<Doc, number>()
  const bySubject = new Map<Doc, number>()
  for (const inst of INSTITUTIONS) {
    const subjects = v.docs.filter((d) => d.kind === "subject" && d.inst === inst).sort((a, b) => a.title.localeCompare(b.title, "sv"))
    for (const s of subjects) bySubject.set(s, groups.push({ title: s.title, inst, kind: "subject", plans: pair() }) - 1)
    const programmes = groups.push({ title: "Utbildningsplaner", inst, kind: "programmes", plans: pair() }) - 1
    let loose = -1 // course plans whose subject page is not in the vault
    for (const d of plans.filter((p) => p.inst === inst)) {
      let g = programmes
      if (d.kind === "course") {
        const subject = parentOf(d)
        g = (subject && bySubject.get(subject)) ?? (loose >= 0 ? loose : (loose = groups.push({ title: "Övriga kursplaner", inst, kind: "subject", plans: pair() }) - 1))
      }
      groupOf.set(d, g)
      groups[g].plans[d.status === "active" ? 0 : 1]++
    }
  }

  const totals = Object.fromEntries(INSTITUTIONS.map((i) => [i, { course: pair(), programme: pair() }])) as Overview["totals"]
  const any = Object.fromEntries(INSTITUTIONS.map((i) => [i, { plans: pair(), notes: pair() }])) as Overview["any"]
  const byArea = new Map<string, CheckSummary>()
  for (const d of plans) {
    const inst = d.inst as Inst
    const s = d.status === "active" ? 0 : 1
    totals[inst][kindOf(d)][s]++
    if (d.findings.length) any[inst].plans[s]++
    any[inst].notes[s] += d.findings.length
    for (const area of new Set(d.findings.map((f) => f.area))) {
      let c = byArea.get(area)
      if (!c) byArea.set(area, (c = { slug: slugify(area), area, kinds: [], m: Object.fromEntries(INSTITUTIONS.map((i) => [i, { plans: pair(), notes: pair() }])) as CheckSummary["m"] }))
      if (!c.kinds.includes(kindOf(d))) c.kinds.push(kindOf(d))
      c.m[inst].plans[s]++
      c.m[inst].notes[s] += d.findings.filter((f) => f.area === area).length
    }
  }
  // Within a block, the largest share comes first: of the active plans the check applies
  // to, which is what the dashboard opens with.
  const share = (c: CheckSummary) => {
    let hit = 0, of = 0
    for (const i of INSTITUTIONS) {
      hit += c.m[i].plans[0]
      for (const k of c.kinds) of += totals[i][k][0]
    }
    return hit / Math.max(1, of)
  }
  // Checks run on course plans come first, then those run only on programme plans, so the
  // table can show them as two blocks, each counted against its own kind of plan.
  const programmeOnly = (c: CheckSummary) => Number(c.kinds.length === 1 && c.kinds[0] === "programme")
  const checks = [...byArea.values()].sort((a, b) => programmeOnly(a) - programmeOnly(b) || share(b) - share(a))
  return (cached = { overview: { totals, any, checks, groups }, groupOf })
}

export const qualityOverview = () => gather().overview

/** A section of an analysis note, by its H2 heading. */
function section(body: string, heading: string): string | null {
  const parts = body.split(/^## +/m)
  const part = parts.find((p) => p.startsWith(heading))
  return part ? part.slice(part.indexOf("\n") + 1).trim() || null : null
}

const rendered = new Map<string, string>()

export async function checkDetail(slug: string): Promise<CheckDetail> {
  const v = getVault()
  const { overview, groupOf } = gather()
  const check = overview.checks.find((c) => c.slug === slug)
  if (!check) throw new Error(`No check ${slug}`)

  const problems: string[] = []
  const plans: CheckDetail["plans"] = []
  const notes: CheckDetail["notes"] = []
  const docs = v.docs.filter((d) => d.plan && d.findings.some((f) => f.area === check.area)).sort((a, b) => a.title.localeCompare(b.title, "sv"))
  for (const d of docs) {
    const at = plans.push([d.code!, d.title, groupOf.get(d)!, d.status === "active" ? 0 : 1, d.url]) - 1
    for (const f of d.findings.filter((f) => f.area === check.area)) {
      let p = problems.indexOf(f.problem)
      if (p < 0) p = problems.push(f.problem) - 1
      // The same detail text recurs across hundreds of plans; render each distinct one once.
      const key = `${d.inst}|${f.detail}`
      let html = rendered.get(key)
      if (html === undefined) rendered.set(key, (html = (await renderMarkdown(f.detail, d)).replace(/^<p>/, "").replace(/<\/p>\s*$/, "")))
      notes.push([at, p, html])
    }
  }

  // What the check is for and what to do about it, in the words of the analysis notes.
  const about = {} as CheckDetail["about"]
  for (const inst of INSTITUTIONS) {
    const page = v.byUrl.get(`/kvalitet/${inst.toLowerCase()}/${slug}/`)
    const purpose = page && section(page.body, "Syfte")
    const advice = page && section(page.body, "Rekommendationer")
    about[inst] = {
      purpose: purpose ? await renderMarkdown(purpose, page!) : null,
      advice: advice ? await renderMarkdown(advice, page!) : null,
      url: page?.url ?? null,
    }
  }
  return { problems, plans, notes, about }
}
