// A plan, shaped for its page: facts, sections, and quality notes placed on the section
// they concern. A course plan has an English version, whose sections are paired with the
// Swedish ones; a programme plan is Swedish only, with numbered sections.
import { getVault, slugify, INSTITUTION_NAMES, type Doc, type Inst } from "./vault"
import { renderMarkdown } from "./markdown"

/** Swedish H2 and its English H3 counterpart, in reading order. */
const PAIRS: [string, string][] = [
  ["Lärandemål", "Learning Outcomes"],
  ["Innehåll", "Course Content"],
  ["Examinationsformer", "Assessment"],
  ["Arbetsformer", "Forms of Study"],
  ["Betyg", "Grades"],
  ["Förkunskapskrav", "Prerequisites"],
]

/** Which section of a course plan a quality check is about. Checks not listed concern the whole plan. */
const AREA_SECTION: Record<string, string> = {
  Betygsrapportering: "Betyg",
  Betygsskalor: "Betyg",
  Examinationsformer: "Examinationsformer",
  Frasningskonsistens: "Lärandemål",
  Introfras: "Lärandemål",
  "Omfång på lärandemål": "Lärandemål",
  "Bloom-taxonomi": "Lärandemål",
  Förkunskapskrav: "Förkunskapskrav",
  Övrigt: "Övrigt",
}
/** In a programme plan both checks read the course list, "3. Programmets kurser". */
const PROGRAMME_AREAS = ["Programkurser olänkade", "Nedlagda kursreferenser"]
const concerns = (kind: Doc["kind"], area: string, title: string) =>
  kind === "course" ? AREA_SECTION[area] === title : PROGRAMME_AREAS.includes(area) && /programmets kurser/i.test(title)

export interface Note {
  area: string
  /** The dashboard, opened at this check for the plan's institution (with vilande plans
   *  counted when the plan itself is vilande, so that it is in the list). */
  areaUrl: string
  problem: string
  detailHtml: string
}

export interface Section {
  id: string
  /** Shared by a Swedish section and its English counterpart, so one can find the other. */
  key: string
  title: string
  html: string
  notes: Note[]
  /** Set where a section of a Swedish plan is written in English ("6. Summary in English"). */
  lang?: "en"
}

export interface Row {
  key: string
  sv: Section | null
  en: Section | null
  notes: Note[]
}

export interface PlanView {
  doc: Doc
  kind: "course" | "programme"
  code: string
  title: string
  titleEn: string | null
  inst: Inst
  instName: string
  status: Doc["status"]
  facts: { label: string; value: string }[]
  sourceUrl: string | null
  /** Anything else in the plan's lead block (a callout on five programmes), as HTML. */
  leadHtml: string | null
  notes: Note[]
  generalNotes: Note[]
  /** Whether the plan has an English version at all. */
  hasEnglish: boolean
  rows: Row[]
  /** Programmes that include this course. */
  programmes: Doc[]
}

function split(markdown: string, level: 2 | 3): { title: string; body: string }[] {
  const heading = level === 2 ? /^## +(.+?)\s*$/ : /^### +(.+?)\s*$/
  const out: { title: string; lines: string[] }[] = []
  for (const line of markdown.split(/\r?\n/)) {
    const m = line.match(heading)
    if (m) out.push({ title: m[1], lines: [] })
    else if (out.length) out[out.length - 1].lines.push(line)
    else if (line.trim()) out.push({ title: "", lines: [line] })
  }
  return out.map((s) => ({ title: s.title, body: s.lines.join("\n") }))
}

export async function planView(doc: Doc): Promise<PlanView> {
  const vault = getVault()
  if ((doc.kind !== "course" && doc.kind !== "programme") || !doc.plan || !doc.inst) throw new Error(`Not a plan: ${doc.file}`)
  const kind = doc.kind
  const fact = (label: string) => doc.plan!.facts.find((f) => f.label === label)?.value ?? null

  const notes: Note[] = []
  for (const f of doc.findings) {
    const html = await renderMarkdown(f.detail, doc)
    notes.push({
      area: f.area,
      areaUrl: `/kvalitet/#${doc.inst.toLowerCase()}/${slugify(f.area)}${doc.status === "active" ? "" : "/med-vilande"}`,
      problem: f.problem,
      detailHtml: html.replace(/^<p>/, "").replace(/<\/p>\s*$/, ""),
    })
  }

  const enKey = new Map(PAIRS.map(([s, e]) => [e, s]))
  const build = async (lang: "sv" | "en") => {
    const parts = split(lang === "sv" ? doc.plan!.sv : (doc.plan!.en ?? ""), lang === "sv" ? 2 : 3)
    const out: Section[] = []
    // A heading can occur twice in one plan (two "Modules" sections, for one). Ids and keys
    // stay unique so no section can shadow another.
    const seen = new Map<string, number>()
    for (const p of parts) {
      const n = (seen.get(p.title) ?? 0) + 1
      seen.set(p.title, n)
      const suffix = n > 1 ? `-${n}` : ""
      const key = (lang === "sv" ? p.title : (enKey.get(p.title) ?? `en:${p.title}`)) + suffix
      out.push({
        id: `${lang}-${slugify(p.title) || "inledning"}${suffix}`,
        key,
        title: p.title,
        // Sections are rendered one at a time, so two can produce the same heading id
        // ("delkurser" in Lärandemål and again in Examinationsformer). Nothing links to
        // these inner headings, so the ids are dropped.
        html: (await renderMarkdown(p.body, doc)).replace(/<(h[1-6]) id="[^"]*"/g, "<$1"),
        notes: lang === "sv" ? notes.filter((n) => concerns(kind, n.area, p.title)) : [],
        ...(lang === "sv" && /summary in english/i.test(p.title) ? { lang: "en" as const } : {}),
      })
    }
    return out
  }
  const sv = await build("sv")
  const en = await build("en")

  // Rows for side-by-side reading: Swedish order first, then English sections with no counterpart.
  const rows: Row[] = sv.map((s) => ({
    key: s.key,
    sv: s,
    en: en.find((e) => e.key === s.key) ?? null,
    notes: s.notes,
  }))
  // An English section with no Swedish counterpart goes right after the English section
  // before it, so the English column still reads in its own order.
  en.forEach((e, i) => {
    if (rows.some((r) => r.en === e)) return
    const after = i === 0 ? -1 : rows.findIndex((r) => r.en === en[i - 1])
    rows.splice(after + 1, 0, { key: e.key, sv: null, en: e, notes: [] })
  })

  const placed = new Set(sv.flatMap((s) => s.notes))
  const facts = (
    kind === "course"
      ? [
          { label: "Poäng", value: fact("Poäng") },
          { label: "Nivå", value: fact("Nivå") },
          { label: "Huvudområde", value: fact("Kursen kan ingå i följande huvudområde(n)") },
          { label: "Ämne", value: fact("Ämnestillhörighet") },
          { label: "Fastställd", value: fact("Fastställd") },
          { label: "Reviderad", value: fact("Reviderad") },
        ]
      : [
          { label: "Programansvarig", value: fact("Programansvarig") },
          { label: "Fastställd", value: fact("Fastställd") },
          { label: "Reviderad", value: fact("Reviderad") },
        ]
  ).filter((f): f is { label: string; value: string } => Boolean(f.value))

  return {
    doc,
    kind,
    code: doc.code!,
    title: doc.title,
    titleEn: fact("Course Name"),
    inst: doc.inst,
    instName: INSTITUTION_NAMES[doc.inst],
    status: doc.status,
    facts,
    sourceUrl: doc.plan.sourceUrl,
    leadHtml: doc.plan.leadExtra ? await renderMarkdown(doc.plan.leadExtra, doc) : null,
    notes,
    generalNotes: notes.filter((n) => !placed.has(n)),
    hasEnglish: en.length > 0,
    rows,
    programmes: doc.backlinks
      .map((f) => vault.byFile.get(f)!)
      .filter((d) => d.kind === "programme")
      .sort((a, b) => a.title.localeCompare(b.title, "sv")),
  }
}

export const noteCount = (n: number) => `${n} ${n === 1 ? "kvalitetsnotering" : "kvalitetsnoteringar"}`
