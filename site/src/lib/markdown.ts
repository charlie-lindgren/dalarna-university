// Vault markdown to HTML.
//
// Handles what Obsidian and the QA pipeline put in the notes: wikilinks, collapsible
// callouts, GFM tables, and raw <a href> links written with Quartz paths. Every internal
// link is resolved through the vault index, so it lands on the new URL. A target that does
// not resolve becomes plain text with class "unresolved", never a dead link.

import { unified } from "unified"
import remarkParse from "remark-parse"
import remarkGfm from "remark-gfm"
import remarkRehype from "remark-rehype"
import rehypeRaw from "rehype-raw"
import rehypeSlug from "rehype-slug"
import rehypeCallouts from "rehype-callouts"
import rehypeStringify from "rehype-stringify"
import { visit } from "unist-util-visit"
import type { Element, Root } from "hast"
import type { VFile } from "vfile"
import { getVault, isExternal, WIKILINK, type Doc } from "./vault"
import { link } from "./site"

const escapeHtml = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;")

/** Replace wikilinks in the source with resolved anchors, before the markdown is parsed. */
function resolveWikilinks(markdown: string, from: Doc): string {
  const vault = getVault()
  return markdown.replace(WIKILINK, (_all, _bang, target: string, _anchor, alias?: string) => {
    const text = escapeHtml((alias ?? target.split("/").pop() ?? target).trim())
    const r = vault.resolve(target, from)
    if (r?.type === "doc") return `<a class="internal" href="${link(r.doc.url)}">${text}</a>`
    if (r?.type === "asset") return `<a class="internal" href="${link(r.asset.url)}">${text}</a>`
    return `<span class="unresolved">${text}</span>`
  })
}

/** Resolve the raw relative hrefs the pipeline writes, and mark external links. */
function rehypeVaultLinks() {
  return (tree: Root, file: VFile) => {
    const vault = getVault()
    const from = file.data.from as Doc
    visit(tree, "element", (node: Element) => {
      if (node.tagName !== "a") return
      const href = node.properties?.href
      if (typeof href !== "string") return
      if (isExternal(href)) {
        if (/^https?:/i.test(href)) node.properties.rel = ["noopener"]
        return
      }
      // Wikilinks were resolved before parsing and already carry the base path.
      if (href.startsWith("/")) return
      const r = vault.resolve(href, from)
      if (r?.type === "doc") node.properties.href = link(r.doc.url)
      else if (r?.type === "asset") node.properties.href = link(r.asset.url)
      else {
        node.tagName = "span"
        node.properties = { className: ["unresolved"] }
      }
    })
  }
}

const processor = unified()
  .use(remarkParse)
  .use(remarkGfm)
  .use(remarkRehype, { allowDangerousHtml: true })
  .use(rehypeRaw)
  .use(rehypeCallouts, { theme: "obsidian" })
  .use(rehypeVaultLinks)
  .use(rehypeSlug)
  .use(rehypeStringify)

/** Render a piece of a note's markdown. `from` is the note it came from. */
export async function renderMarkdown(markdown: string, from: Doc): Promise<string> {
  const file = await processor.process({ value: resolveWikilinks(markdown, from), data: { from } })
  return String(file)
}

/** Drop the note's own H1, for pages where the template prints the title. */
export function withoutH1(markdown: string): string {
  return markdown.replace(/^\s*# .*\r?\n/, "")
}
