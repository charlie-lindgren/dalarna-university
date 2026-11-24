// Behaviour every page shares: the interface language switch, and "/" for search.
import { reduceMotion, store } from "./util"

declare global {
  interface Window {
    /** Defined inline in layouts/Page.astro. */
    applyUiLanguage?: (lang: string) => void
  }
}

// ── Interface language ──────────────────────────────────────────────
// Both languages are in the page and CSS shows one, so changing is instant. What scripts
// have written (search results, the dashboard's sentences, the graph's names) is written
// again by each of them when "uichange" fires.
const root = document.documentElement
const choices = [...document.querySelectorAll<HTMLButtonElement>("[data-ui-choice]")]
const mark = () => choices.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.uiChoice === (root.dataset.ui ?? "sv"))))
mark()
for (const b of choices) {
  b.addEventListener("click", (e) => {
    const lang = b.dataset.uiChoice === "en" ? "en" : "sv"
    if (root.dataset.ui === lang) return
    const apply = () => {
      root.dataset.ui = lang
      window.applyUiLanguage?.(lang)
      mark()
      document.dispatchEvent(new CustomEvent("uichange"))
    }
    store.set("ui", lang === "en" ? "en" : null)
    // A link that carried ?ui= would otherwise bring the old language back on reload.
    const url = new URL(location.href)
    if (url.searchParams.has("ui")) {
      url.searchParams.delete("ui")
      history.replaceState(history.state, "", url)
    }
    // One cross-fade of the whole page, as for the appearance; none for a keyboard press.
    // (A fade the browser gives up on still makes the change; it is no error.)
    if (e.detail !== 0 && document.startViewTransition && !reduceMotion()) document.startViewTransition(apply).ready.catch(() => {})
    else apply()
  })
}

// ── "/" goes to search from anywhere. On the search page, search.ts focuses the field. ──
document.addEventListener("keydown", (e) => {
  const t = e.target as HTMLElement
  if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return
  if (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable) return
  if (document.querySelector("[data-search]")) return
  const home = document.querySelector<HTMLAnchorElement>('.sitemenu a[data-menu="sok"]')
  if (!home) return
  e.preventDefault()
  location.href = home.href
})
