// After the build: every address the old Quartz site had keeps working.
//
// For each page Quartz published (notes, folder pages, tag pages, alias pages) this writes a
// small page at the same address that sends the reader on to the same thing here. The Excel
// files are copied to their old addresses too, since a download cannot be redirected. It also
// writes sitemap.xml for the new pages.
//
// GitHub Pages serves "…/01-IIT/Kursplaner/DTA/GDT2JM" from "GDT2JM.html" and a folder from
// its "index.html", exactly as it did for Quartz, so the files are named as Quartz named them.
// Run from site/ after `astro build` (npm run build does it).
import fs from "node:fs"
import path from "node:path"
import matter from "gray-matter"
import { getVault, parentOf, quartzSlug, INSTITUTIONS, type Doc } from "../src/lib/vault.ts"

const base = (process.env.SITE_BASE ?? "/dalarna-university").replace(/\/$/, "")
const ORIGIN = "https://charlie-lindgren.github.io"
const dist = path.join(process.cwd(), "dist")
const v = getVault()

/** Old address (a Quartz slug, without .html) → new address (a site path such as /kurs/GDT2JM/). */
const moves = new Map<string, string>()
const move = (slug: string, to: string) => {
  if (!moves.has(slug)) moves.set(slug, to)
}
const urlOf = (d: Doc) => (d.kind === "home" ? "/" : d.url)
const instDoc = (inst: string) => v.docs.find((d) => d.kind === "institution" && d.inst === inst)

// 1. Every note.
for (const d of v.docs) move(d.quartzSlug, urlOf(d))

// 2. Aliases: Quartz gave each alias in a note's frontmatter a page of its own at the top level.
for (const d of v.docs) {
  const { data } = matter(fs.readFileSync(path.join(process.env.VAULT_DIR ?? path.join(process.cwd(), "..", "vault-dalarna-university"), d.file), "utf8"))
  const aliases = Array.isArray(data.aliases) ? data.aliases : typeof data.aliases === "string" ? [data.aliases] : []
  for (const a of aliases) move(quartzSlug(String(a)), urlOf(d))
}

// 3. Folder pages: a school's folder goes to the school; any other folder to the page most of
//    its notes belong under (a subject's courses to the subject, analysis notes to the
//    school's overview of them).
const folders = new Map<string, Doc[]>()
for (const d of v.docs) {
  const dir = path.posix.dirname(d.file)
  if (dir === ".") continue
  for (let f = dir; f !== "."; f = path.posix.dirname(f)) if (!folders.has(f)) folders.set(f, [])
  folders.get(dir)!.push(d)
}
for (const [folder, docs] of [...folders].sort((a, b) => b[0].length - a[0].length)) {
  const depth = folder.split("/").length
  const inst = INSTITUTIONS.find((i) => folder.split("/")[0].endsWith(` ${i}`))
  let to: string | undefined
  if (depth === 1) to = inst ? instDoc(inst)?.url : "/"
  else {
    const votes = new Map<string, number>()
    for (const d of docs) {
      const p = parentOf(d)
      if (p) votes.set(urlOf(p), (votes.get(urlOf(p)) ?? 0) + 1)
    }
    to = [...votes].sort((a, b) => b[1] - a[1])[0]?.[0]
  }
  move(`${quartzSlug(folder)}/index`, to ?? (inst ? instDoc(inst)?.url : undefined) ?? "/")
}

// 4. Tag pages: a subject code goes to the subject, a school to the school, the rest home.
const tags = new Set<string>()
for (const d of v.docs) {
  const { data } = matter(fs.readFileSync(path.join(process.env.VAULT_DIR ?? path.join(process.cwd(), "..", "vault-dalarna-university"), d.file), "utf8"))
  for (const t of Array.isArray(data.tags) ? data.tags : []) tags.add(String(t))
}
move("tags/index", "/")
move("tags", "/")
for (const t of tags) {
  const subject = v.docs.find((d) => d.kind === "subject" && d.code === t)
  const school = INSTITUTIONS.includes(t as never) ? instDoc(t) : undefined
  move(`tags/${quartzSlug(t)}`, subject?.url ?? school?.url ?? "/")
}

// ── Write ──
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;")
const page = (to: string) => {
  const href = esc(base + to)
  return `<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<title>Sidan har flyttat</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="${esc(ORIGIN) + href}">
<meta http-equiv="refresh" content="0; url=${href}">
<script>location.replace(${JSON.stringify(base + to)})</script>
</head>
<body><p>Sidan har flyttat: <a href="${href}">${href}</a></p></body>
</html>
`
}
let written = 0, kept = 0
for (const [slug, to] of moves) {
  const file = path.join(dist, `${slug}.html`)
  // Never cover a page of this site (none share a name today, but the check is cheap).
  if (fs.existsSync(file)) {
    kept++
    continue
  }
  fs.mkdirSync(path.dirname(file), { recursive: true })
  fs.writeFileSync(file, page(to))
  written++
}
let copied = 0
for (const a of v.assets) {
  const from = path.join(dist, a.url)
  const to = path.join(dist, a.quartzSlug)
  if (!fs.existsSync(from) || fs.existsSync(to)) continue
  fs.mkdirSync(path.dirname(to), { recursive: true })
  fs.copyFileSync(from, to)
  copied++
}

// ── sitemap.xml: the pages of this site, not the redirects ──
const urls: string[] = []
const walk = (dir: string) => {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) walk(p)
    else if (e.name === "index.html") urls.push(path.relative(dist, path.dirname(p)).split(path.sep).join("/"))
  }
}
walk(dist)
const isRedirect = (rel: string) => moves.has(rel ? `${rel}/index` : "index")
const loc = (rel: string) => `${ORIGIN}${base}/${rel ? encodeURI(rel) + "/" : ""}`
const pages = urls.filter((u) => !isRedirect(u) && !u.startsWith("pagefind")).sort()
fs.writeFileSync(
  path.join(dist, "sitemap.xml"),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${pages.map((u) => `<url><loc>${loc(u)}</loc></url>`).join("\n")}\n</urlset>\n`,
)

console.log(`Old addresses: ${written} redirect pages written, ${kept} already pages of this site, ${copied} Excel files copied. Sitemap: ${pages.length} pages.`)
