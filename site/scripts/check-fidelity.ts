// Post-build check: the plan text on the site is the plan text in the vault.
// Every element that carries plan text is marked data-plan-text="sv" or "en". For each plan
// and each language, the words in those elements must equal the words in the vault source,
// in the same order. Nothing may be dropped, added or "cleaned up" on the way.
// Run from site/ after a build:  node scripts/check-fidelity.ts
import fs from "node:fs"
import path from "node:path"
import { unified } from "unified"
import remarkParse from "remark-parse"
import remarkGfm from "remark-gfm"
import rehypeParse from "rehype-parse"
import { SKIP, visit } from "unist-util-visit"
import { getVault } from "../src/lib/vault.ts"

const words = (s: string) => s.match(/[\p{L}\p{N}]+/gu) ?? []

const ENTITIES: Record<string, string> = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " " }
const decode = (s: string) =>
  s
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d)))
    .replace(/&([a-z]+);/gi, (all, name) => ENTITIES[name.toLowerCase()] ?? all)
// The vault side is read with the same markdown parser the site uses, so list markers and
// other syntax are told apart from text the same way. What this check then guards is
// everything after parsing: the splitting into sections, raw HTML, callouts, link rewriting.
const parser = unified().use(remarkParse).use(remarkGfm)
const fromMarkdown = (md: string) => {
  const parts: string[] = []
  visit(parser.parse(md.replace(/!?\[\[([^\]|]+\|)?([^\]]+)\]\]/g, "$2")), (node) => {
    if (node.type === "text" || node.type === "inlineCode" || node.type === "code") parts.push(node.value)
    else if (node.type === "html") parts.push(node.value.replace(/<[^>]+>/g, " "))
  })
  return words(decode(parts.join(" ")))
}

// The site side: the text of every element marked data-plan-text, per language, in page order.
const htmlParser = unified().use(rehypeParse)
const fromPage = (html: string, lang: "sv" | "en") => {
  const parts: string[] = []
  const collect = (node: any) => {
    if (node.type === "text") parts.push(node.value)
    else for (const child of node.children ?? []) collect(child)
  }
  visit(htmlParser.parse(html), "element", (node: any) => {
    if (node.properties?.dataPlanText !== lang) return
    collect(node)
    return SKIP
  })
  return words(parts.join(" "))
}

const vault = getVault()
const plans = vault.docs.filter((d) => d.plan)
let checked = 0
const bad: string[] = []
for (const d of plans) {
  const html = fs.readFileSync(path.join("dist", d.url, "index.html"), "utf8")
  for (const lang of ["sv", "en"] as const) {
    const source = lang === "sv" ? d.plan!.sv : d.plan!.en
    if (source === null) continue
    const got = fromPage(html, lang)
    const want = fromMarkdown(source)
    if (got.length !== want.length || got.some((w, i) => w !== want[i])) {
      const at = got.findIndex((w, i) => w !== want[i])
      const i = at === -1 ? Math.min(got.length, want.length) : at
      bad.push(`${d.file} (${lang})\n    site:  … ${got.slice(Math.max(0, i - 4), i + 6).join(" ")}\n    vault: … ${want.slice(Math.max(0, i - 4), i + 6).join(" ")}`)
    }
  }
  checked++
}
console.log(`${checked} plans compared word for word, Swedish and English; ${bad.length} texts differ`)
for (const b of bad.slice(0, 12)) console.log("  " + b)
process.exit(bad.length ? 1 : 0)
