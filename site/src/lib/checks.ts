// The quality checks' own words in English: the check names (Område) and the problem labels
// (Problem) that the QA pipeline writes into the vault. The vault keeps the Swedish; the site
// shows these when the interface is English. A name missing here simply stays Swedish, and
// `npm run report` lists it.
//
// Glossary, as in ui.ts: kursplan = course syllabus, utbildningsplan = programme syllabus,
// grundnivå = first cycle, avancerad nivå = second cycle, lärandemål = learning outcome.
import type { Lang } from "./ui"

export const CHECK_EN: Record<string, string> = {
  Betygsrapportering: "Grade reporting",
  Betygsskalor: "Grading scales",
  "Bloom-taxonomi": "Bloom's taxonomy",
  Examinationsformer: "Forms of assessment",
  Frasningskonsistens: "Consistent wording",
  Förkunskapskrav: "Prerequisites",
  Introfras: "Introductory phrase",
  "Nedlagda kursreferenser": "Discontinued courses listed",
  "Omfång på lärandemål": "Number and length of outcomes",
  "Programkurser olänkade": "Unlinked programme courses",
  "Samstämmighet svenska och engelska": "Swedish and English agreement",
  "Stavfel och språkbruk": "Spelling and language",
  "Vilande kursplaner": "Dormant course syllabi",
  Övrigt: "Other information",
}

export const PROBLEM_EN: Record<string, string> = {
  "Saknar punktlista": "Not a bulleted list",
  "Saknar punktlista (sv)": "Not a bulleted list (Swedish)",
  "Saknar punktlista (en)": "Not a bulleted list (English)",
  "Inkonsekvent delskalor": "Inconsistent component scales",
  "Hög verbnivå för grundkurs": "High verb level for a first-cycle course",
  "Låg verbnivå för avancerad kurs": "Low verb level for a second-cycle course",
  "Okänt ledande verb": "Unknown leading verb",
  "Avviker från referensformen": "Differs from the reference wording",
  "Refererar bekräftat nedlagd kurs": "Refers to a course confirmed as discontinued",
  "Refererar troligen nedlagd kurs": "Refers to a course probably discontinued",
  "Prosa/rubrik före frasning": "Text or heading before the phrase",
  "Programmet listar nedlagd kurs": "Lists a discontinued course",
  "För få mål": "Too few outcomes",
  "För många mål": "Too many outcomes",
  "Långt mål": "Long outcome",
  "Kursnamnet finns varken aktivt eller nedlagt": "Course name not found, active or discontinued",
  "Programtext avviker från kursplanens namn": "Differs from the syllabus's course name",
  Paritetsskillnad: "Different number of outcomes",
  "Dubblerat ord": "Repeated word",
  Felstavning: "Misspelling",
  "Felstavning (en)": "Misspelling (English)",
  "Saknar standardfras om pedagogiskt stöd": "Standard text on study support missing",
  "Sektion saknas": "Section missing",
  "Ingen aktiv kursomgång": "No course offering scheduled",
}

/** A check's name in the interface language. */
export const checkName = (area: string, lang: Lang) => (lang === "en" ? (CHECK_EN[area] ?? area) : area)
/** A problem label in the interface language. */
export const problemName = (problem: string, lang: Lang) => (lang === "en" ? (PROBLEM_EN[problem] ?? problem) : problem)
