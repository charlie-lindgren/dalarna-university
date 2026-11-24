// What the home page and the browser need from the vault: the four institutions with their
// subjects and programmes, a few totals, and the compact catalogue the pages fetch.
import { getVault, parentOf, codeSlug, INSTITUTIONS, type Doc, type Inst } from "./vault"

const credits = (d: Doc) => String(d.fm.hp ?? "").replace(/\s*högskolepoäng/, " hp").trim()

export interface InstitutionView {
  inst: Inst
  courses: number
  programmes: { code: string; title: string; url: string }[]
  subjects: { title: string; url: string; slug: string; count: number }[]
  /** Quality notes in the institution's active plans: the count the dashboard opens with. */
  notes: number
}

export function siteData() {
  const v = getVault()
  const plans = v.docs.filter((d) => d.plan)
  const courses = plans.filter((d) => d.kind === "course")
  const subjectOf = new Map(courses.map((d) => [d, parentOf(d)]))

  const institutions: InstitutionView[] = INSTITUTIONS.map((inst) => {
    const mine = v.docs.filter((d) => d.inst === inst)
    const own = courses.filter((d) => d.inst === inst)
    return {
      inst,
      courses: own.length,
      programmes: mine
        .filter((d) => d.kind === "programme")
        .map((d) => ({ code: d.code!, title: d.title, url: d.url }))
        .sort((a, b) => a.title.localeCompare(b.title, "sv")),
      subjects: mine
        .filter((d) => d.kind === "subject")
        .map((s) => ({ title: s.title, url: s.url, slug: s.url.split("/")[2], count: own.filter((c) => subjectOf.get(c) === s).length }))
        .sort((a, b) => a.title.localeCompare(b.title, "sv")),
      notes: mine.filter((d) => d.status === "active").reduce((n, d) => n + d.findings.length, 0),
    }
  })

  const [y, m, day] = (v.scrapeDate ?? "").split("-").map(Number)
  const when = new Date(Date.UTC(y || 1970, (m || 1) - 1, day || 1))
  return {
    institutions,
    plans: plans.length,
    subjects: v.docs.filter((d) => d.kind === "subject").length,
    /** When the plans were last fetched from du.se: "24 november 2026" and "24 November 2026". */
    scrapeDate: {
      sv: y ? when.toLocaleDateString("sv-SE", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }) : "",
      en: y ? when.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }) : "",
    },
  }
}

/** The catalogue as the pages fetch it: rows, not objects, to keep one file for 2,000 plans small.
 *  scripts/catalogue.ts is the other half and must match this shape.
 *    s  subjects    [title, url, institution]
 *    c  courses     [code, name, English name, credits, vilande 0|1, subject index, institution index, url?]
 *    p  programmes  [code, name, institution index, url?]
 *  A url is only given when it is not the plain /kurs/<code>/ or /program/<code>/. */
export function catalogue() {
  const v = getVault()
  const subjects = v.docs.filter((d) => d.kind === "subject")
  const at = new Map(subjects.map((s, i) => [s, i]))
  const inst = (d: Doc) => INSTITUTIONS.indexOf(d.inst!)
  const odd = (d: Doc, prefix: string) => (d.url === `/${prefix}/${codeSlug(d.code!)}/` ? [] : [d.url])
  return {
    s: subjects.map((s) => [s.title, s.url, s.inst]),
    c: v.docs
      .filter((d) => d.kind === "course")
      .map((d) => [d.code, d.title, String(d.fm.course_name ?? ""), credits(d), d.status === "active" ? 0 : 1, at.get(parentOf(d)!) ?? -1, inst(d), ...odd(d, "kurs")]),
    p: v.docs.filter((d) => d.kind === "programme").map((d) => [d.code, d.title, inst(d), ...odd(d, "program")]),
  }
}
