// The search field on the home page: results as you type, arrows to move, Enter to open.
// Two sources answer. The catalogue (every code and name) answers at once. The full-text
// index of the plans' own words (Pagefind, built with the site) answers a moment later and
// is listed underneath.
import { loadCatalogue, type Entry } from "./catalogue"

interface TextHit {
  url: string
  meta: { title?: string }
  excerpt: string
  sub_results?: { title: string; url: string; excerpt: string; locations?: number[]; anchor?: { id?: string } }[]
}
interface Pagefind {
  options(o: Record<string, unknown>): Promise<void>
  init(): Promise<void>
  debouncedSearch(q: string, o?: Record<string, unknown>, ms?: number): Promise<{ results: { id: string; data(): Promise<TextHit> }[] } | null>
}

const fold = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
const el = <K extends keyof HTMLElementTagNameMap>(tag: K, className?: string, text?: string) => {
  const node = document.createElement(tag)
  if (className) node.className = className
  if (text !== undefined) node.textContent = text
  return node
}

const box = document.querySelector<HTMLElement>("[data-search]")
if (box) {
  const input = box.querySelector("input")!
  const list = box.querySelector<HTMLElement>('[role="listbox"]')!
  const note = box.querySelector<HTMLElement>(".hitnote")!
  const base = box.dataset.base ?? ""
  const LIMIT = 8
  // On a tie, the wider thing first: a subject leads to all its plans.
  const ORDER = { subject: 0, programme: 1, course: 2 }
  let index: { e: Entry; code: string; name: string; en: string; all: string }[] = []
  let byUrl = new Map<string, Entry>()
  let hits: typeof index = []
  let active = -1
  /** Counts for the line under the results. */
  let found = 0
  let inText: number | null = null

  // Every result, from either source, in the order shown.
  const options = () => [...list.querySelectorAll<HTMLAnchorElement>(".hit")]
  const setActive = (i: number, scroll: boolean) => {
    active = i
    options().forEach((h, j) => {
      h.setAttribute("aria-selected", String(j === i))
      if (j === i) {
        input.setAttribute("aria-activedescendant", h.id)
        if (scroll) h.scrollIntoView({ block: "nearest" })
      }
    })
    if (i < 0) input.removeAttribute("aria-activedescendant")
  }
  const point = (a: HTMLAnchorElement) => a.addEventListener("pointermove", () => {
    const i = options().indexOf(a)
    if (active !== i) setActive(i, false)
  })

  // ── Full text ──
  // Fetched on the first keystroke. If the index is not there (a local preview that has
  // never been built), the field simply answers from the catalogue alone.
  let engine: Promise<Pagefind | null> | null = null
  const fullText = () =>
    (engine ??= import(/* @vite-ignore */ `${base}/pagefind/pagefind.js`)
      .then(async (pf: Pagefind) => {
        await pf.options({ baseUrl: `${base}/`, excerptLength: 14 })
        await pf.init()
        return pf
      })
      .catch(() => null))
  const TEXT_LIMIT = 6

  /** Where a text hit should open: at the section the words are in, in the language they are in. */
  const landing = (hit: TextHit) => {
    const best = (hit.sub_results ?? []).filter((s) => s.url.includes("#h-")).sort((a, b) => (b.locations?.length ?? 0) - (a.locations?.length ?? 0))[0]
    if (!best) return { href: hit.url, section: "", excerpt: hit.excerpt }
    const [page, id] = best.url.split("#")
    const [, lang, row] = id.match(/^h-(sv|en)--(.+)$/) ?? []
    if (!row) return { href: hit.url, section: "", excerpt: hit.excerpt }
    // The link opens the plan in the language the words are in: an English section is only
    // on screen in the English view. (Programme plans have one language and take no view.)
    const view = page.includes("/kurs/") ? `?lang=${lang}` : ""
    // Pagefind's excerpt starts with the section's own heading; the heading is shown beside it already.
    const excerpt = best.excerpt.startsWith(best.title) ? best.excerpt.slice(best.title.length).replace(/^[.\s]+/, "") : best.excerpt
    return { href: `${page}${view}#${row}`, section: best.title, excerpt }
  }

  const sayCounts = () => {
    const q = input.value.trim()
    note.hidden = !q
    if (!q) return
    const text = inText === null ? "" : inText === 0 ? "" : ` ${inText.toLocaleString("sv-SE")} ${inText === 1 ? "plan" : "planer"} nämner det i texten.`
    note.textContent = !index.length
      ? "Hämtar katalogen…"
      : found === 0 && !inText
        ? inText === null
          ? "Söker i planernas text…"
          : `Inget matchar ”${q}”. Prova en kurskod, till exempel GDT2JM, eller en del av ett namn.`
        : found === 0
          ? `Ingen kod och inget namn matchar.${text}`
          : (found > hits.length ? `Visar ${hits.length} av ${found.toLocaleString("sv-SE")} träffar på kod och namn.` : `${found} ${found === 1 ? "träff" : "träffar"} på kod och namn.`) + text
  }

  const searchText = async (raw: string) => {
    list.querySelector(".textgroup")?.remove()
    inText = null
    if (raw.length < 2) return
    const pf = await fullText()
    if (!pf) return void ((inText = 0), sayCounts())
    const answer = await pf.debouncedSearch(raw, {}, 140)
    if (!answer || input.value.trim() !== raw) return // the reader has typed on
    const shown = new Set(hits.map((x) => base + x.e.url))
    const loaded = await Promise.all(answer.results.slice(0, TEXT_LIMIT + shown.size).map((r) => r.data()))
    if (input.value.trim() !== raw) return
    const data = loaded.filter((d) => !shown.has(d.url)).slice(0, TEXT_LIMIT)
    // Plans already listed above by code or name are not counted a second time.
    inText = answer.results.length - loaded.filter((d) => shown.has(d.url)).length
    list.querySelector(".textgroup")?.remove()
    if (data.length) {
      const group = el("div", "textgroup")
      group.setAttribute("role", "group")
      group.setAttribute("aria-label", "I planernas text")
      group.append(el("p", "grouplabel", "I planernas text"))
      data.forEach((d, i) => {
        const entry = byUrl.get(d.url.slice(base.length))
        const to = landing(d)
        const a = el("a", "hit text")
        a.id = `texthit-${i}`
        a.href = to.href
        a.setAttribute("role", "option")
        a.setAttribute("aria-selected", "false")
        const top = el("span", "line")
        top.append(el("span", "code num", entry?.code ?? ""), el("span", "name", entry?.name ?? d.meta.title ?? ""))
        const meta = el("span", "meta num")
        if (entry?.vilande) meta.append(el("span", "dot"), "Vilande")
        else meta.textContent = entry?.kind === "programme" ? "Program" : (entry?.credits ?? "")
        top.append(meta)
        const quote = el("span", "quote")
        if (to.section) quote.append(el("span", "where", to.section))
        const words = el("span")
        words.innerHTML = to.excerpt // Pagefind's own excerpt: escaped text with <mark> around the match
        quote.append(words)
        a.append(top, quote)
        point(a)
        group.append(a)
      })
      list.append(group)
      list.hidden = false
      input.setAttribute("aria-expanded", "true")
      if (active < 0) setActive(0, false)
    }
    sayCounts()
  }

  // An exact code first, then names that start with the query, then looser matches.
  const rank = (q: string, x: (typeof index)[number]) => {
    if (x.code === q || x.name === q) return 0
    if (x.code && x.code.startsWith(q)) return 1
    if (x.name.startsWith(q)) return 2
    if (x.name.includes(" " + q)) return 3
    if (x.en.startsWith(q) || x.en.includes(" " + q)) return 4
    if (x.code.includes(q)) return 5
    if (x.name.includes(q)) return 6
    if (x.en.includes(q)) return 7
    return 8 // every word matched somewhere, but not the phrase
  }

  const run = () => {
    const raw = input.value.trim()
    const q = fold(raw)
    list.replaceChildren()
    if (!q) {
      list.hidden = note.hidden = true
      input.setAttribute("aria-expanded", "false")
      hits = []
      found = 0
      inText = null
      return setActive(-1, false)
    }
    const words = q.split(/\s+/)
    const matched = index
      .filter((x) => words.every((w) => x.all.includes(w)))
      .map((x) => ({ x, r: rank(q, x) }))
      .sort((a, b) => a.r - b.r || Number(a.x.e.vilande) - Number(b.x.e.vilande) || ORDER[a.x.e.kind] - ORDER[b.x.e.kind] || a.x.e.name.localeCompare(b.x.e.name, "sv"))
    hits = matched.slice(0, LIMIT).map((f) => f.x)
    found = matched.length

    hits.forEach((x, i) => {
      const a = el("a", "hit")
      a.id = `hit-${i}`
      a.href = base + x.e.url
      a.setAttribute("role", "option")
      a.append(el("span", "code num", x.e.code))
      // The matched part of the name is set in weight, not colour.
      const name = el("span", "name")
      const at = x.name.indexOf(q)
      if (at >= 0 && x.name.length === x.e.name.length) name.append(x.e.name.slice(0, at), el("b", "", x.e.name.slice(at, at + q.length)), x.e.name.slice(at + q.length))
      else name.textContent = x.e.name
      a.append(name)
      const meta = el("span", "meta num")
      if (x.e.vilande) meta.append(el("span", "dot"), "Vilande")
      else meta.textContent = x.e.kind === "course" ? x.e.credits : x.e.kind === "programme" ? "Program" : "Ämne"
      a.append(meta)
      point(a)
      list.append(a)
    })
    list.hidden = hits.length === 0
    input.setAttribute("aria-expanded", String(hits.length > 0))
    setActive(hits.length ? 0 : -1, false)
    sayCounts()
    searchText(raw)
  }

  loadCatalogue(box.dataset.catalogue!).then((entries) => {
    index = entries.map((e) => {
      const code = fold(e.code), name = fold(e.name), en = fold(e.en)
      return { e, code, name, en, all: `${code} ${name} ${en}` }
    })
    byUrl = new Map(entries.map((e) => [e.url, e]))
    if (input.value) run()
  })

  input.addEventListener("input", run)
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      const n = options().length
      if (!n) return
      e.preventDefault()
      setActive((active + (e.key === "ArrowDown" ? 1 : -1) + n) % n, true)
    } else if (e.key === "Enter" && active >= 0) {
      e.preventDefault()
      const hit = options()[active]
      if (!hit) return
      if (e.metaKey || e.ctrlKey) window.open(hit.href, "_blank")
      else location.href = hit.href
    } else if (e.key === "Escape" && input.value) {
      e.preventDefault()
      input.value = ""
      run()
    }
  })
  // "/" from anywhere on the page goes to the field.
  document.addEventListener("keydown", (e) => {
    const t = e.target as HTMLElement
    if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable) return
    e.preventDefault()
    input.focus()
  })
  // With a mouse and keyboard the field is ready at once. On a phone it waits for a tap, so
  // the keyboard does not cover the page unasked.
  if (matchMedia("(hover: hover) and (pointer: fine)").matches) input.focus({ preventScroll: true })
  // Coming back with Back, the browser restores what was typed; show its results again.
  addEventListener("pageshow", () => input.value && run())
}
