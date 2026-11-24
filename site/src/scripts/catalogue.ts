// Fetches the catalogue once per page and unpacks its rows. The shape is set by
// catalogue() in lib/site-data.ts.

export interface Entry {
  kind: "course" | "programme" | "subject"
  code: string
  name: string
  /** English name; courses only. */
  en: string
  /** Site path without the base. A subject leads into the browser, opened at that subject. */
  url: string
  credits: string
  vilande: boolean
  /** The subject page a course belongs to, as the browser knows it. */
  subject: string
}

const INSTITUTIONS = ["IIT", "IHV", "IKS", "ISLL"]
const codeSlug = (code: string) => code.normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^A-Za-z0-9]+/g, "")

let pending: Promise<Entry[]> | null = null

export function loadCatalogue(url: string): Promise<Entry[]> {
  return (pending ??= fetch(url)
    .then((r) => r.json())
    .then((raw: { s: [string, string, string][]; c: (string | number)[][]; p: (string | number)[][] }) => {
      const entries: Entry[] = []
      for (const [name, url, inst] of raw.s)
        entries.push({ kind: "subject", code: "", name, en: "", url: `/bladdra/#${inst.toLowerCase()}/${url.split("/")[2]}`, credits: "", vilande: false, subject: url })
      for (const [code, name, en, credits, vilande, subject, , url] of raw.c as [string, string, string, string, number, number, number, string?][])
        entries.push({ kind: "course", code, name, en, url: url ?? `/kurs/${codeSlug(code)}/`, credits, vilande: vilande === 1, subject: raw.s[subject]?.[1] ?? "" })
      for (const [code, name, , url] of raw.p as [string, string, number, string?][])
        entries.push({ kind: "programme", code, name, en: "", url: url ?? `/program/${codeSlug(code)}/`, credits: "", vilande: false, subject: "" })
      return entries
    }))
}

export { INSTITUTIONS }
