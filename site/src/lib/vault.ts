// The vault as data.
//
// Reads vault-dalarna-university/ once per build and exposes an index of every published
// note: what kind it is, where it lives on the new site, what it links to, and (for plans)
// its facts and quality findings. The site only reads the vault. It never writes to it, and
// it never cleans up plan text: values are passed on exactly as scraped.
//
// Classification follows the same frontmatter tags the QA pipeline uses (see `is_hub` in
// qa/checks_common.py), never file names.

import fs from "node:fs"
import path from "node:path"
import matter from "gray-matter"
import { instName } from "./ui.ts"

export const VAULT_DIR = path.resolve(
  process.env.VAULT_DIR ?? path.join(process.cwd(), "..", "vault-dalarna-university"),
)

export const INSTITUTIONS = ["IIT", "IHV", "IKS", "ISLL"] as const
export type Inst = (typeof INSTITUTIONS)[number]

/** The institutions' Swedish names. Both languages are in lib/ui.ts. */
export const INSTITUTION_NAMES = Object.fromEntries(INSTITUTIONS.map((i) => [i, instName(i, "sv")])) as Record<Inst, string>

export type Kind =
  | "home"
  | "institution"
  | "subject"
  | "course"
  | "programme"
  | "analysisHub"
  | "analysis"

export type Status = "active" | "vilande" | "ej-aktiv"

export interface Fact {
  label: string
  value: string
}

export interface Finding {
  area: string
  problem: string
  detail: string
}

export interface PlanParts {
  /** Facts from the lead block between the H1 and the first H2, in source order. */
  facts: Fact[]
  /** The du.se link in the lead block, when there is one. */
  sourceUrl: string | null
  /** Whatever else the lead block holds (a callout on five programmes), as markdown. */
  leadExtra: string | null
  /** Swedish body: everything from the first H2 up to `## English Version`. */
  sv: string
  /** English body: what follows `## English Version`, or null when the plan has none. */
  en: string | null
}

export interface Doc {
  /** Vault-relative path with forward slashes, NFC-normalised. */
  file: string
  /** File name without `.md`. */
  name: string
  kind: Kind
  inst: Inst | null
  tags: string[]
  fm: Record<string, unknown>
  /** Markdown after the frontmatter, with the per-plan analysis block removed. */
  body: string
  /** Site path without the base, always with leading and trailing slash. */
  url: string
  /** The path Quartz published this note under (no leading slash, no extension). */
  quartzSlug: string
  title: string
  /** Course or programme code, or the subject code for a subject hub. */
  code: string | null
  status: Status
  research: boolean
  findings: Finding[]
  plan: PlanParts | null
  /** Resolved outgoing links to other published notes (vault paths), deduplicated. */
  links: string[]
  backlinks: string[]
  /** The links the graph draws: as `links`, minus the ones the pipeline marks "no-graph"
   *  (navigation only, such as an institution's list of its programmes). */
  graph: string[]
}

export interface Asset {
  file: string
  /** Where the file is on disk, spelled as the file system has it. */
  path: string
  quartzSlug: string
  url: string
}

export interface LinkIssue {
  from: string
  target: string
  reason: "unresolved" | "draft"
}

export type Resolved =
  | { type: "doc"; doc: Doc }
  | { type: "asset"; asset: Asset }
  | { type: "draft"; file: string }
  | null

export interface Vault {
  docs: Doc[]
  byFile: Map<string, Doc>
  byUrl: Map<string, Doc>
  assets: Asset[]
  /** Notes with `draft: true`. Quartz does not publish them and neither does this site. */
  drafts: string[]
  issues: LinkIssue[]
  scrapeDate: string | null
  resolve(target: string, from?: Doc): Resolved
}

// ── Names and slugs ─────────────────────────────────────────────────

const nfc = (s: string) => s.normalize("NFC")
const stripMarks = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "")

/** Lower-case ASCII slug: "Vårdvetenskap inr omvårdnad" becomes "vardvetenskap-inr-omvardnad". */
export function slugify(s: string): string {
  return stripMarks(s)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
}

/** Codes keep their case but lose diacritics in URLs: "GFÖ3FJ" becomes "GFO3FJ". */
export function codeSlug(code: string): string {
  return stripMarks(code).replace(/[^A-Za-z0-9]+/g, "")
}

/** Quartz's own slug rule (quartz/util/path.ts `sluggify`), kept so old links can be mapped. */
export function quartzSlug(fileWithoutExt: string): string {
  return fileWithoutExt
    .split("/")
    .map((seg) =>
      seg
        .replace(/\s/g, "-")
        .replace(/&/g, "-and-")
        .replace(/%/g, "-percent")
        .replace(/\?/g, "")
        .replace(/#/g, ""),
    )
    .join("/")
}

// ── Reading ─────────────────────────────────────────────────────────

const SKIP_DIRS = new Set([".obsidian", "Templates", "private"])

function walk(dir: string, rel = ""): string[] {
  const out: string[] = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".") || SKIP_DIRS.has(entry.name)) continue
    const relPath = rel ? `${rel}/${entry.name}` : entry.name
    if (entry.isDirectory()) out.push(...walk(path.join(dir, entry.name), relPath))
    else out.push(relPath)
  }
  return out
}

function asTags(value: unknown): string[] {
  if (Array.isArray(value)) return value.map(String)
  if (typeof value === "string") return value.split(/[,\s]+/).filter(Boolean)
  return []
}

function instOf(file: string): Inst | null {
  const top = file.split("/")[0]
  return INSTITUTIONS.find((i) => top.endsWith(` ${i}`)) ?? null
}

function kindOf(tags: string[], file: string): Kind | null {
  const has = (t: string) => tags.includes(t)
  if (has("kursplan")) return "course"
  if (has("utbildningsplan")) return "programme"
  if (has("MOC") && has("institution")) return "institution"
  if (has("MOC") && has("amne")) return "subject"
  if (has("MOC") && has("analys")) return "analysisHub"
  if (has("analys")) return "analysis"
  if (has("dashboard")) return "home"
  // index.md only embeds the dashboard. It is the same page as home, not a page of its own.
  if (file === "index.md") return null
  return null
}

// ── Plan parsing ────────────────────────────────────────────────────

const ANALYS_BLOCK = /<!-- analys:start -->[\s\S]*?<!-- analys:end -->\r?\n?/

/** Split a markdown table row on pipes that are not escaped and not inside a code span. */
function splitRow(row: string): string[] {
  const cells: string[] = []
  let cell = ""
  let inCode = false
  for (let i = 0; i < row.length; i++) {
    const ch = row[i]
    if (ch === "\\" && row[i + 1] === "|") {
      cell += "|"
      i++
    } else if (ch === "`") {
      inCode = !inCode
      cell += ch
    } else if (ch === "|" && !inCode) {
      cells.push(cell.trim())
      cell = ""
    } else cell += ch
  }
  cells.push(cell.trim())
  // A row starts and ends with a pipe, which leaves an empty cell at each end.
  return cells.slice(1, -1)
}

function parseFindings(raw: string): Finding[] {
  const block = raw.match(ANALYS_BLOCK)?.[0]
  if (!block) return []
  const findings: Finding[] = []
  for (const line of block.split(/\r?\n/)) {
    const row = line.replace(/^>\s?/, "").trim()
    if (!row.startsWith("|")) continue
    const cells = splitRow(row)
    if (cells.length < 3) continue
    if (cells[0] === "Område" || /^:?-+:?$/.test(cells[0])) continue
    findings.push({ area: cells[0], problem: cells[1], detail: cells.slice(2).join(" | ") })
  }
  return findings
}

const FACT_LINE = /^\s*(?:[-*]\s+)?\*\*(.+?):\*\*\s*(.*)$/
const SOURCE_LINE = /^\s*\[[^\]]*\]\((https?:\/\/[^)\s]+)\)\s*$/

function parsePlan(body: string): PlanParts {
  const lines = body.split(/\r?\n/)
  const h1 = lines.findIndex((l) => /^# \S/.test(l))
  const firstH2 = lines.findIndex((l, i) => i > h1 && /^## \S/.test(l))
  const leadLines = lines.slice(h1 + 1, firstH2 === -1 ? lines.length : firstH2)
  const rest = firstH2 === -1 ? [] : lines.slice(firstH2)

  // Fact lines and the du.se link become data. Any other line is kept as markdown, in
  // order, so nothing in the lead block is ever dropped.
  const facts: Fact[] = []
  const extra: string[] = []
  let sourceUrl: string | null = null
  for (const line of leadLines) {
    const fact = line.match(FACT_LINE)
    const source = line.match(SOURCE_LINE)
    if (fact) facts.push({ label: fact[1].trim(), value: fact[2].trim() })
    else if (source && !sourceUrl) sourceUrl = source[1]
    else extra.push(line)
  }
  const leadExtra = extra.join("\n").trim()

  const enAt = rest.findIndex((l) => /^## English Version\s*$/.test(l))
  const sv = (enAt === -1 ? rest : rest.slice(0, enAt)).join("\n")
  const en = enAt === -1 ? null : rest.slice(enAt + 1).join("\n")

  return {
    facts,
    sourceUrl,
    leadExtra: leadExtra || null,
    sv,
    en: en && en.trim() ? en : null,
  }
}

// ── Link extraction ─────────────────────────────────────────────────

/** `[[target]]`, `[[target|alias]]`, `[[target#heading]]`, with `\|` as used inside tables. */
export const WIKILINK = /(!?)\[\[([^\]|#\\]+)(#[^\]|\\]*)?(?:\\?\|([^\]]+))?\]\]/g
const RAW_HREF = /<a\s[^>]*?href="([^"]+)"/g

export function isExternal(href: string): boolean {
  return /^[a-z][a-z0-9+.-]*:/i.test(href) || href.startsWith("//") || href.startsWith("#")
}

function linkTargets(markdown: string): string[] {
  const targets: string[] = []
  for (const m of markdown.matchAll(WIKILINK)) targets.push(m[2])
  for (const m of markdown.matchAll(RAW_HREF)) if (!isExternal(m[1])) targets.push(m[1])
  return targets
}

/** As linkTargets, but leaving out anchors with class "no-graph", as Quartz's link crawler does. */
function graphTargets(markdown: string): string[] {
  const targets: string[] = []
  for (const m of markdown.matchAll(WIKILINK)) targets.push(m[2])
  for (const m of markdown.matchAll(/<a\s([^>]*)>/g)) {
    const href = m[1].match(/href="([^"]+)"/)?.[1]
    if (href && !isExternal(href) && !/class="[^"]*\bno-graph\b/.test(m[1])) targets.push(href)
  }
  return targets
}

// ── The index ───────────────────────────────────────────────────────

function build(): Vault {
  // Names are compared in NFC form, but a file is opened by the name the file system gave:
  // Linux does not treat the two forms of "ä" as the same name, as macOS does.
  const onDisk = new Map(walk(VAULT_DIR).map((raw) => [nfc(raw), path.join(VAULT_DIR, raw)]))
  const files = [...onDisk.keys()].sort((a, b) => a.localeCompare(b, "sv"))
  const docs: Doc[] = []
  const drafts: string[] = []
  const assets: Asset[] = []
  let scrapeDate: string | null = null

  for (const file of files) {
    if (!file.endsWith(".md")) {
      const inst = instOf(file)
      const ext = path.extname(file)
      const base = slugify(path.basename(file, ext))
      // Analysis spreadsheets sit beside the analysis page they belong to.
      const dir = inst && file.includes("/Analys/") ? `/kvalitet/${inst.toLowerCase()}` : "/filer"
      assets.push({ file, path: onDisk.get(file)!, quartzSlug: quartzSlug(file), url: `${dir}/${base}${ext}` })
      continue
    }

    const raw = fs.readFileSync(onDisk.get(file)!, "utf8")
    const parsed = matter(raw)
    const fm = parsed.data as Record<string, unknown>
    if (fm.draft === true || fm.draft === "true") {
      drafts.push(file)
      continue
    }

    const tags = asTags(fm.tags)
    const kind = kindOf(tags, file)
    if (!kind) continue

    const name = path.basename(file, ".md")
    const inst = instOf(file)
    const isPlan = kind === "course" || kind === "programme"
    const body = parsed.content.replace(ANALYS_BLOCK, "")

    let code: string | null = null
    let title = name
    // The file name is the plan's code. Frontmatter agrees for every course, but two
    // programmes (DBIMA, DDCMA) both carry `programkod: ANA235`, and the hubs link by file name.
    if (kind === "course") {
      code = name
      title = String(fm.kursnamn ?? name)
    } else if (kind === "programme") {
      code = name
      title = String(fm.programnamn ?? name)
    } else if (kind === "subject") {
      code = tags.find((t) => !["MOC", "amne"].includes(t) && t !== inst) ?? null
    } else if (kind === "institution" && inst) {
      title = INSTITUTION_NAMES[inst]
    } else if (kind === "home") {
      title = "Högskolan Dalarna"
      scrapeDate = body.match(/scrape-date:start[\s\S]*?\*\*(\d{4}-\d{2}-\d{2})\*\*/)?.[1] ?? null
    }

    const i = inst?.toLowerCase()
    const url =
      kind === "home"
        ? "/"
        : kind === "institution"
          ? `/institution/${i}/`
          : kind === "subject"
            ? `/amne/${slugify(name)}/`
            : kind === "course"
              ? `/kurs/${codeSlug(code!)}/`
              : kind === "programme"
                ? `/program/${codeSlug(code!)}/`
                : kind === "analysisHub"
                  ? `/kvalitet/${i}/`
                  : `/kvalitet/${i}/${slugify(name)}/`

    docs.push({
      file,
      name,
      kind,
      inst,
      tags,
      fm,
      body,
      url,
      quartzSlug: quartzSlug(file.replace(/\.md$/, "")),
      title,
      code,
      status: tags.includes("ej-aktiv") ? "ej-aktiv" : tags.includes("vilande") ? "vilande" : "active",
      research: tags.includes("forskarutbildning"),
      findings: isPlan ? parseFindings(parsed.content) : [],
      plan: isPlan ? parsePlan(body) : null,
      links: [],
      backlinks: [],
      graph: [],
    })
  }

  // A code or subject name can exist under two institutions, with differing content. Those
  // pages keep one URL each by carrying the institution: /kurs/GIE3HX-iit/, /kurs/GIE3HX-iks/.
  const urlCount = new Map<string, number>()
  for (const d of docs) urlCount.set(d.url, (urlCount.get(d.url) ?? 0) + 1)
  for (const d of docs) {
    if ((urlCount.get(d.url) ?? 0) > 1 && d.inst) {
      d.url = d.url.replace(/\/$/, `-${d.inst.toLowerCase()}/`)
    }
  }

  const byFile = new Map(docs.map((d) => [d.file, d]))
  const byUrl = new Map<string, Doc>()
  for (const d of docs) {
    const clash = byUrl.get(d.url)
    if (clash) throw new Error(`Two notes map to ${d.url}: ${clash.file} and ${d.file}`)
    byUrl.set(d.url, d)
  }

  // Lookup tables for link targets. Keys are lower-cased; values keep every candidate so a
  // name that exists twice can be settled by the institution of the linking note.
  const add = <T>(map: Map<string, T[]>, key: string, value: T) => {
    const k = nfc(key).toLowerCase()
    const list = map.get(k)
    if (list) list.includes(value) || list.push(value)
    else map.set(k, [value])
  }
  const byPath = new Map<string, Doc[]>()
  const byName = new Map<string, Doc[]>()
  for (const d of docs) {
    add(byPath, d.file.replace(/\.md$/, ""), d)
    add(byPath, d.quartzSlug, d)
    add(byName, d.name, d)
    add(byName, quartzSlug(d.name), d)
    if (Array.isArray(d.fm.aliases)) for (const alias of d.fm.aliases) add(byName, String(alias), d)
  }
  const assetByPath = new Map<string, Asset>()
  for (const a of assets) {
    assetByPath.set(a.file.toLowerCase(), a)
    assetByPath.set(a.quartzSlug.toLowerCase(), a)
  }
  const draftKeys = new Map<string, string>()
  for (const f of drafts) {
    const noExt = f.replace(/\.md$/, "")
    draftKeys.set(noExt.toLowerCase(), f)
    draftKeys.set(quartzSlug(noExt).toLowerCase(), f)
    draftKeys.set(path.basename(noExt).toLowerCase(), f)
  }

  const pick = (candidates: Doc[] | undefined, from?: Doc): Doc | null => {
    if (!candidates?.length) return null
    if (candidates.length === 1) return candidates[0]
    return candidates.find((c) => c.inst === from?.inst) ?? candidates[0]
  }

  const resolve = (target: string, from?: Doc): Resolved => {
    let t = target
    try {
      t = decodeURI(t)
    } catch {
      // not URI-encoded; use it as written
    }
    t = nfc(t).split("#")[0].trim().replace(/^\.?\//, "").replace(/\/$/, "")
    if (!t) return from ? { type: "doc", doc: from } : null
    const key = t.replace(/\.md$/, "").toLowerCase()

    const asset = assetByPath.get(t.toLowerCase())
    if (asset) return { type: "asset", asset }
    if (key === "index") {
      const home = docs.find((d) => d.kind === "home")
      if (home) return { type: "doc", doc: home }
    }
    const doc = pick(byPath.get(key), from) ?? pick(byName.get(key), from)
    if (doc) return { type: "doc", doc }
    const draft = draftKeys.get(key)
    if (draft) return { type: "draft", file: draft }
    return null
  }

  // Outgoing links and backlinks. The analysis block is data, not prose, so its links are
  // not counted; plan pages link to their analysis areas through the findings instead.
  const issues: LinkIssue[] = []
  for (const d of docs) {
    const seen = new Set<string>()
    for (const target of linkTargets(d.body)) {
      const r = resolve(target, d)
      if (!r) issues.push({ from: d.file, target, reason: "unresolved" })
      else if (r.type === "draft") issues.push({ from: d.file, target, reason: "draft" })
      else if (r.type === "doc" && r.doc !== d && !seen.has(r.doc.file)) {
        seen.add(r.doc.file)
        d.links.push(r.doc.file)
      }
    }
    // `up:` is the note's parent hub. It counts as a link even when the body does not repeat it.
    const up = typeof d.fm.up === "string" ? d.fm.up.match(/\[\[([^\]|#]+)/)?.[1] : null
    if (up) {
      const r = resolve(up, d)
      if (r?.type === "doc" && r.doc !== d && !seen.has(r.doc.file)) d.links.push(r.doc.file)
    }
  }
  for (const d of docs) for (const f of d.links) byFile.get(f)?.backlinks.push(d.file)
  for (const d of docs) {
    const seen = new Set<string>()
    for (const target of graphTargets(d.body)) {
      const r = resolve(target, d)
      if (r?.type === "doc" && r.doc !== d && !seen.has(r.doc.file)) {
        seen.add(r.doc.file)
        d.graph.push(r.doc.file)
      }
    }
  }

  return { docs, byFile, byUrl, assets, drafts, issues, scrapeDate, resolve }
}

let cached: Vault | undefined

/** The vault index. Built on first use and shared by every page in the build. */
export function getVault(): Vault {
  return (cached ??= build())
}

/** The parent hub named by a note's `up:` frontmatter, when it resolves. */
export function parentOf(doc: Doc): Doc | null {
  const vault = getVault()
  const up = typeof doc.fm.up === "string" ? doc.fm.up : null
  if (!up) return null
  const target = up.match(/\[\[([^\]|#]+)/)?.[1] ?? up
  const r = vault.resolve(target, doc)
  return r?.type === "doc" && r.doc !== doc ? r.doc : null
}
