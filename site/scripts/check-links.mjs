// Post-build check: every internal href in dist/ must point at a file that exists.
// Run from site/ after a build:  node scripts/check-links.mjs
import fs from "node:fs"
import path from "node:path"

const dist = path.resolve("dist")
const base = (process.env.SITE_BASE ?? "/dalarna-university").replace(/\/$/, "")

const pages = []
const walk = (dir) => {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) walk(p)
    else if (e.name.endsWith(".html")) pages.push(p)
  }
}
walk(dist)

let links = 0
let outside = 0
let unresolvedSpans = 0
const broken = new Map()
for (const page of pages) {
  const html = fs.readFileSync(page, "utf8")
  unresolvedSpans += (html.match(/class="unresolved"/g) ?? []).length
  for (const m of html.matchAll(/\s(?:href|src)="([^"]+)"/g)) {
    const href = m[1].replace(/&amp;/g, "&")
    if (/^[a-z][a-z0-9+.-]*:/i.test(href) || href.startsWith("//") || href.startsWith("#")) continue
    links++
    if (!href.startsWith(base + "/")) {
      outside++
      broken.set(href, (broken.get(href) ?? 0) + 1)
      continue
    }
    const rel = decodeURI(href.slice(base.length).split("#")[0].split("?")[0])
    const target = path.join(dist, rel.endsWith("/") ? rel + "index.html" : rel)
    if (!fs.existsSync(target)) broken.set(href, (broken.get(href) ?? 0) + 1)
  }
}

console.log(`${pages.length} pages, ${links} internal links checked`)
console.log(`Links shown as plain text because the target is not published: ${unresolvedSpans}`)
console.log(`Broken internal links: ${[...broken.values()].reduce((a, b) => a + b, 0)} (${outside} outside the base path)`)
for (const [href, n] of [...broken].sort((a, b) => b[1] - a[1]).slice(0, 20)) console.log(`  ${String(n).padStart(5)}  ${href}`)
process.exit(broken.size ? 1 : 0)
