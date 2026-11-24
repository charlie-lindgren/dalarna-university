// The interface in two languages.
//
// Only what the site itself says is here: menus, labels, counts and messages. Plan text,
// subject names, the names of the quality checks and the analysis notes are the vault's own
// words and are never translated. The English names of the university and its four schools
// are their official ones.
//
// Both languages are in every page. Which one shows is decided by <html data-ui="sv|en">,
// set before first paint (layouts/Page.astro). Templates render both through <T>; scripts
// ask t() and say.* at the moment they write text, and write again on a "uichange" event.
//
// This file is read by the build and by the browser, so it must not import anything that
// only exists in one of them.

export type Lang = "sv" | "en"
export type InstCode = "IIT" | "IHV" | "IKS" | "ISLL"

export const LOCALE: Record<Lang, string> = { sv: "sv-SE", en: "en-GB" }
export const num = (n: number, lang: Lang) => n.toLocaleString(LOCALE[lang])
/** The language the page is shown in. Browser only. */
export const uiLang = (): Lang => (document.documentElement.dataset.ui === "en" ? "en" : "sv")

// ── Names ───────────────────────────────────────────────────────────

const INSTITUTION: Record<InstCode, [string, string]> = {
  IIT: ["Institutionen för information och teknik", "School of Information and Engineering"],
  IHV: ["Institutionen för hälsa och välfärd", "School of Health and Welfare"],
  IKS: ["Institutionen för kultur och samhälle", "School of Culture and Society"],
  ISLL: ["Institutionen för språk, litteratur och lärande", "School of Language, Literature and Learning"],
}
export const instName = (inst: InstCode, lang: Lang) => INSTITUTION[inst][lang === "en" ? 1 : 0]
/** Without "Institutionen för" or "School of": "Information och teknik". */
export const instShort = (inst: InstCode, lang: Lang) => {
  const s = instName(inst, lang).replace(/^Institutionen för |^School of /, "")
  return s[0].toUpperCase() + s.slice(1)
}

// ── Fixed texts: [svenska, English] ─────────────────────────────────

const S = {
  "site.name": ["Högskolan Dalarna", "Dalarna University"],
  "site.sub": ["Kursplaner och utbildningsplaner", "Course and programme syllabi"],

  "menu.label": ["Huvudmeny", "Main menu"],
  "menu.sok": ["Sök", "Search"],
  "menu.bladdra": ["Bläddra", "Browse"],
  "menu.graf": ["Graf", "Graph"],
  "menu.kvalitet": ["Kvalitet", "Quality"],
  "theme.label": ["Utseende", "Appearance"],
  "theme.light": ["Ljust", "Light"],
  "theme.dark": ["Mörkt", "Dark"],
  "theme.auto": ["Följ systemet", "Match the system"],
  "lang.label": ["Språk", "Language"],
  "crumbs.label": ["Brödsmulor", "Breadcrumbs"],

  schools: ["Institutioner", "Schools"],
  subjects: ["Ämnen", "Subjects"],
  subject: ["Ämne", "Subject"],
  programmes: ["Program", "Programmes"],
  programme: ["Program", "Programme"],
  courses: ["Kursplaner", "Course syllabi"],
  course: ["Kursplan", "Course syllabus"],
  vilande: ["Vilande", "Dormant"],
  all: ["Alla", "All"],
  open: ["Öppna", "Open"],
  "open.duse": ["Öppna på du.se", "Open on du.se"],
  contents: ["Innehåll", "Contents"],
  "fetched.from": [", hämtade från ", ", fetched from "],

  // Sök
  "search.label": ["Sök kursplan, program eller ämne", "Search for a course syllabus, programme or subject"],
  "search.placeholder": ["Sök på kurskod eller namn", "Search by course code or name"],
  "search.hits": ["Träffar", "Results"],
  "search.loading": ["Hämtar katalogen…", "Loading the catalogue…"],
  "search.inText": ["I planernas text", "In the text of the syllabi"],
  "search.searchingText": ["Söker i planernas text…", "Searching the text of the syllabi…"],
  "search.noName": ["Ingen kod och inget namn matchar.", "No code or name matches."],

  // Bläddra
  "browse.h1": ["Bläddra bland kursplaner och program", "Browse course syllabi and programmes"],
  "browse.pane2": ["Ämnen och program", "Subjects and programmes"],
  "browse.back.schools": ["Tillbaka till Institutioner", "Back to Schools"],
  "browse.back.subjects": ["Tillbaka till Ämnen", "Back to Subjects"],
  "browse.quality": ["Kvalitetsgranskning", "Quality review"],
  "browse.pick": ["Välj ett ämne för att se dess kursplaner.", "Choose a subject to see its course syllabi."],
  "browse.loading": ["Hämtar kursplaner…", "Loading course syllabi…"],
  "browse.noActive": ["Inga aktiva kursplaner i det här ämnet.", "No active course syllabi in this subject."],

  // Graf
  "graph.h1": ["Graf över institutioner, ämnen, program och kursplaner", "Graph of schools, subjects, programmes and course syllabi"],
  "graph.canvas": [
    "Graf: varje institution med sina ämnen, program och kursplaner som punkter. Samma innehåll finns som listor under Bläddra.",
    "Graph: every school with its subjects, programmes and course syllabi as points. The same content is listed under Browse.",
  ],
  "graph.zoom": ["Zooma", "Zoom"],
  "graph.zoom.out": ["Zooma ut", "Zoom out"],
  "graph.zoom.in": ["Zooma in", "Zoom in"],
  "graph.zoom.fit": ["Visa hela grafen", "Show the whole graph"],
  "graph.show": ["Visa", "Show"],
  "graph.hint": [
    "Skrolla för att zooma, dra för att flytta. Peka på något för att se vad det hör ihop med.",
    "Scroll to zoom, drag to move. Point at something to see what it belongs with.",
  ],
  "graph.toSearch": ["Till sökningen", "To search"],

  // Kvalitet
  "q.h1": ["Kvalitetsgranskning", "Quality review"],
  "q.map": ["Andel planer med notering", "Share of syllabi with a note"],
  "q.basis": ["Räkna på", "Count"],
  "q.active": ["Aktiva planer", "Active syllabi"],
  "q.allPlans": ["Alla planer", "All syllabi"],
  "q.check": ["Kontroll", "Check"],
  "q.any": ["Minst en notering", "At least one note"],
  "q.block.course": ["Kontroller av kursplaner", "Checks of course syllabi"],
  "q.block.programme": ["Kontroller av utbildningsplaner", "Checks of programme syllabi"],
  "q.caption": [
    "Andelen är planer med minst en notering, av de planer kontrollen gäller. Välj en ruta för att se vad som ligger bakom.",
    "The share is syllabi with at least one note, out of the syllabi the check applies to. Choose a cell to see what lies behind it.",
  ],
  "q.school": ["Institution", "School"],
  "q.allSchools": ["Alla institutioner", "All schools"],
  "q.toTable": ["Till tabellen", "To the table"],
  "q.noscript": [
    "Utan skript visas inte planerna här. Varje ruta i tabellen leder i stället till institutionens analys av kontrollen.",
    "Without scripts the syllabi are not listed here. Each cell in the table leads to the school's analysis of the check instead.",
  ],
  "q.advice": ["Rekommendationer", "Recommendations"],
  "q.fullPer": ["Hela analysen per institution", "The full analysis, by school"],
  "q.what": ["Vad noteringarna gäller", "What the notes concern"],
  "q.same": ["Alla noteringar gäller samma sak: ", "All the notes concern the same thing: "],
  "q.pickRow": ["Välj en rad för att bara se de planerna nedan.", "Choose a row to see only those syllabi below."],
  "q.where": ["Var noteringarna finns", "Where the notes are"],
  "q.withNote": ["Planer med notering", "Syllabi with a note"],
  "q.others": ["Övriga planer", "Other syllabi"],
  "q.none": ["Inga noteringar här.", "No notes here."],
  "q.loading": ["Hämtar noteringarna…", "Loading the notes…"],
  "q.programmeGroup": ["Utbildningsplaner", "Programme syllabi"],
  "q.looseGroup": ["Övriga kursplaner", "Other course syllabi"],

  // A plan's page
  "view.label": ["Visa språk", "Show language"],
  "view.sv": ["Svenska", "Swedish"],
  "view.en": ["English", "English"],
  "view.both": ["Båda", "Both"],
  "plan.whole.course": ["Hela kursplanen", "The whole course syllabus"],
  "plan.whole.programme": ["Hela utbildningsplanen", "The whole programme syllabus"],
  "plan.missing.sv": ["Finns inte i den svenska versionen.", "Not in the Swedish version."],
  "plan.missing.en": ["Finns inte i den engelska versionen.", "Not in the English version."],
  "plan.partOf": ["Ingår i program", "Part of programmes"],
  "plan.hasNotes": ["har kvalitetsnoteringar", "has quality notes"],
  "fact.Poäng": ["Poäng", "Credits"],
  "fact.Nivå": ["Nivå", "Level"],
  "fact.Huvudområde": ["Huvudområde", "Main field of study"],
  "fact.Ämne": ["Ämne", "Subject"],
  "fact.Fastställd": ["Fastställd", "Established"],
  "fact.Reviderad": ["Reviderad", "Revised"],
  "fact.Programansvarig": ["Programansvarig", "Programme director"],

  // The vault's own list and analysis notes
  "doc.linksHere": ["Länkar hit", "Links here"],
} as const satisfies Record<string, readonly [string, string]>

export type Key = keyof typeof S
export const t = (key: Key, lang: Lang): string => S[key][lang === "en" ? 1 : 0]

// ── Texts with numbers or names in them ─────────────────────────────

const en = (lang: Lang) => lang === "en"
const one = (n: number, singular: string, plural: string) => (n === 1 ? singular : plural)

export const say = {
  /** "349 kursplaner, 19 program" */
  holds: (courses: number, programmes: number, l: Lang) =>
    en(l)
      ? `${num(courses, l)} ${one(courses, "course", "courses")}, ${programmes} ${one(programmes, "programme", "programmes")}`
      : `${num(courses, l)} ${one(courses, "kursplan", "kursplaner")}, ${programmes} program`,
  plans: (n: number, l: Lang) => (en(l) ? `${num(n, l)} ${one(n, "syllabus", "syllabi")}` : `${num(n, l)} ${one(n, "plan", "planer")}`),
  plansInSubjects: (n: number, subjects: number, l: Lang) =>
    en(l) ? `${num(n, l)} syllabi in ${subjects} subjects` : `${num(n, l)} planer i ${subjects} ämnen`,
  /** " den 24 november 2026." */
  onDate: (date: string, l: Lang) => (en(l) ? ` on ${date}.` : ` den ${date}.`),

  // Sök
  noMatch: (q: string, l: Lang) =>
    en(l)
      ? `Nothing matches “${q}”. Try a course code, such as GDT2JM, or part of a name.`
      : `Inget matchar ”${q}”. Prova en kurskod, till exempel GDT2JM, eller en del av ett namn.`,
  showing: (shown: number, found: number, l: Lang) =>
    en(l) ? `Showing ${shown} of ${num(found, l)} matches on code and name.` : `Visar ${shown} av ${num(found, l)} träffar på kod och namn.`,
  matches: (found: number, l: Lang) =>
    en(l) ? `${found} ${one(found, "match", "matches")} on code and name.` : `${found} ${one(found, "träff", "träffar")} på kod och namn.`,
  inText: (n: number, l: Lang) =>
    en(l) ? ` ${num(n, l)} ${one(n, "syllabus mentions", "syllabi mention")} it in the text.` : ` ${num(n, l)} ${one(n, "plan", "planer")} nämner det i texten.`,

  // Graf
  graphCourse: (code: string, vilande: boolean, l: Lang) =>
    en(l) ? `Course syllabus ${code}${vilande ? ", dormant" : ""}` : `Kursplan ${code}${vilande ? ", vilande" : ""}`,
  graphProgramme: (code: string, reads: number | null, l: Lang) =>
    reads === null
      ? en(l) ? `Programme syllabus ${code}, reads courses from other schools` : `Utbildningsplan ${code}, läser kurser från andra institutioner`
      : en(l) ? `Programme syllabus ${code}, ${reads} of the school's course syllabi` : `Utbildningsplan ${code}, ${reads} av institutionens kursplaner`,
  graphSubject: (courses: number, l: Lang) =>
    en(l) ? `Subject, ${courses} course ${one(courses, "syllabus", "syllabi")}` : `Ämne, ${courses} ${one(courses, "kursplan", "kursplaner")}`,
  graphSchool: (subjects: number, courses: number, l: Lang) =>
    en(l) ? `${subjects} subjects, ${num(courses, l)} course syllabi` : `${subjects} ämnen, ${num(courses, l)} kursplaner`,

  // Kvalitet
  checksLead: (checks: number, l: Lang) =>
    en(l)
      ? `Every course and programme syllabus is tested against ${checks} checks. This shows what share of the syllabi have a note, where the notes are and what they concern.`
      : `Varje kursplan och utbildningsplan prövas mot ${checks} kontroller. Här syns hur stor andel av planerna som har fått en notering, var noteringarna finns och vad de gäller.`,
  notes: (n: number, l: Lang) => (en(l) ? `${num(n, l)} ${one(n, "note", "notes")}` : `${num(n, l)} ${one(n, "notering", "noteringar")}`),
  of: (a: number, b: number, l: Lang) => `${num(a, l)} ${en(l) ? "of" : "av"} ${num(b, l)}`,
  fullFor: (inst: string, l: Lang) => (en(l) ? `The full analysis for ${inst}` : `Hela analysen för ${inst}`),
  onlyWith: (label: string, l: Lang) =>
    en(l) ? `Showing only syllabi with “${label}”. Choose the row again to see all.` : `Visar bara planer med ”${label}”. Välj raden igen för att se alla.`,
  showAll: (n: number, l: Lang) => (en(l) ? `Show all ${n}` : `Visa alla ${n}`),

  // A plan's page
  qualityNotes: (n: number, l: Lang) => (en(l) ? `${n} quality ${one(n, "note", "notes")}` : `${n} ${one(n, "kvalitetsnotering", "kvalitetsnoteringar")}`),
  status: (kind: "course" | "programme", status: "vilande" | "ej-aktiv", l: Lang) =>
    status === "ej-aktiv"
      ? en(l) ? "Not active" : "Ej aktiv"
      : en(l)
        ? `Dormant ${kind === "course" ? "course" : "programme"} syllabus`
        : `Vilande ${kind === "course" ? "kursplan" : "utbildningsplan"}`,
}

/** "7,5 hp" as the catalogue has it, or "7.5 credits". */
export function credits(raw: string, lang: Lang): string {
  if (lang === "sv" || !raw) return raw
  const n = raw.replace(/\s*hp$/, "").replace(",", ".")
  return `${n} ${n === "1" ? "credit" : "credits"}`
}

/** For a template: attributes that carry text (aria-label, placeholder, title). The Swedish
 *  text goes in the attribute, the English beside it, and a marker tells the page script
 *  which attributes to switch. Give a key, or the two texts.
 *
 *  An attribute has no language of its own: a screen reader says a label in the language of
 *  its element. So pass `{ lang: true }` on an element that holds no Swedish text itself (a
 *  button with an icon, a group of such buttons), and the page script marks it `lang="en"`
 *  while the interface is English. Leave it out where the element holds names or plan text. */
export function attrs(map: Record<string, Key | readonly [string, string]>, opts: { lang?: boolean } = {}): Record<string, string> {
  const out: Record<string, string> = {}
  for (const [name, value] of Object.entries(map)) {
    const [sv, english] = typeof value === "string" ? [t(value, "sv"), t(value, "en")] : value
    out[name] = sv
    out[`data-en-${name}`] = english
  }
  out["data-i18n"] = Object.keys(map).join(" ")
  if (opts.lang) out["data-i18n-lang"] = ""
  return out
}

/** For a script: the same for a label written at run time. Only for an element that holds no
 *  Swedish text of its own. */
export function spoken(el: Element, text: string, lang: Lang): void {
  el.setAttribute("aria-label", text)
  if (lang === "en") el.setAttribute("lang", "en")
  else el.removeAttribute("lang")
}
