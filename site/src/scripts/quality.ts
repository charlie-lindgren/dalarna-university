// The quality dashboard. The heat table is the map; choosing a cell opens that check at
// that institution: what it is for, what its notes concern, where they sit, and the plans.
// The overview is embedded in the page; one check's notes are fetched when it is opened.
import { cell, headline, percent, planWord, sentence, INSTS, type CheckDetail, type InstCode, type Overview, type Scope } from "../lib/quality-math"
import { heat } from "../lib/heat"
import { glide } from "./glide"
import { segmented } from "./segmented"
import { reduceMotion } from "./util"

const sv = (n: number) => n.toLocaleString("sv-SE")
const el = <K extends keyof HTMLElementTagNameMap>(tag: K, className?: string, text?: string) => {
  const node = document.createElement(tag)
  if (className) node.className = className
  if (text !== undefined) node.textContent = text
  return node
}
const CHEVRON = '<svg class="chev" viewBox="0 0 12 12" aria-hidden="true"><path d="m2 4 4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>'

const root = document.querySelector<HTMLElement>("[data-q]")
if (root) {
  const o: Overview = JSON.parse(document.getElementById("q-data")!.textContent!)
  const names: Record<InstCode, string> = JSON.parse(root.dataset.names!)
  const base = root.dataset.base ?? ""
  const checkOf = (slug: string) => o.checks.find((c) => c.slug === slug)!
  const isScope = (s: string): s is Scope => s === "alla" || (INSTS as readonly string[]).includes(s)

  const cells = [...root.querySelectorAll<HTMLAnchorElement>("a.cell")]
  const anyCells = [...root.querySelectorAll<HTMLElement>("[data-any]")]
  const grid = [...root.querySelectorAll<HTMLElement>("tr[data-row]")].map((r) => [...r.querySelectorAll<HTMLAnchorElement>("a.cell")])
  const figures = root.querySelector<HTMLElement>("[data-q-figures]")!
  const select = root.querySelector<HTMLSelectElement>("[data-q-check]")!
  const detail = root.querySelector<HTMLElement>("[data-q-detail]")!
  const scopeLine = root.querySelector<HTMLElement>("[data-q-scope]")!
  const sum = root.querySelector<HTMLElement>("[data-q-sum]")!
  const aboutBox = root.querySelector<HTMLElement>("[data-q-about]")!
  const problemBox = root.querySelector<HTMLElement>("[data-q-problems]")!
  const groupBox = root.querySelector<HTMLElement>("[data-q-groups]")!
  const tip = root.querySelector<HTMLElement>("[data-tip]")!
  // Below this width the detail sits under the table, so choosing a cell has to take you there.
  const stacked = matchMedia("(max-width: 1080px)")

  // Counted on active plans unless the reader asks for all: plans that are not offered are
  // the least urgent to put right.
  const state = { scope: "alla" as Scope, check: o.checks[0].slug, vilande: false, problem: null as number | null }
  /** What the reader has opened, kept across redraws of the same check. */
  const open = new Set<number>()
  let adviceOpen = false
  let showAll = false

  // ── The heat table ──
  const describe = (check: ReturnType<typeof checkOf> | null, scope: Scope) => {
    const c = cell(o, check, scope, state.vilande)
    return `${check?.area ?? "Minst en notering"}, ${scope === "alla" ? "alla institutioner" : scope}: ${percent(c.share)} %, ${c.hit} av ${c.of} ${planWord(check, state.vilande)}`
  }
  const paint = () => {
    for (const a of cells) {
      const check = checkOf(a.dataset.check!)
      const c = cell(o, check, a.dataset.scope as Scope, state.vilande)
      a.style.cssText = heat(c.share)
      a.querySelector(".n")!.textContent = percent(c.share)
      a.setAttribute("aria-label", describe(check, a.dataset.scope as Scope))
    }
    for (const s of anyCells) {
      const c = cell(o, null, s.dataset.any as Scope, state.vilande)
      s.style.cssText = heat(c.share)
      s.querySelector(".n")!.textContent = percent(c.share)
      s.setAttribute("aria-label", describe(null, s.dataset.any as Scope))
    }
    const [figure, rest] = headline(o, state.vilande)
    figures.replaceChildren(el("b", "", figure), rest)
  }
  const mark = () => {
    for (const a of cells) {
      const on = a.dataset.check === state.check && a.dataset.scope === state.scope
      a.parentElement!.setAttribute("aria-selected", String(on))
      a.tabIndex = on ? 0 : -1
    }
    root.querySelectorAll<HTMLElement>("[data-row]").forEach((r) => r.toggleAttribute("data-on", r.dataset.row === state.check))
    root.querySelectorAll<HTMLElement>("[data-col]").forEach((h) => h.toggleAttribute("data-on", h.dataset.col === state.scope))
    select.value = state.check
    seg.set(state.scope)
    basis.set(state.vilande ? "alla" : "aktiva")
  }

  // ── The chosen cell, opened up ──
  const fetched = new Map<string, Promise<CheckDetail>>()
  const load = (slug: string) => {
    let p = fetched.get(slug)
    if (!p) fetched.set(slug, (p = fetch(`${root.dataset.detail}${slug}.json`).then((r) => r.json() as Promise<CheckDetail>)))
    return p
  }
  let drawing = 0

  const inScope = (d: CheckDetail, plan: number) => {
    const [, , group, vilande] = d.plans[plan]
    return (state.scope === "alla" || o.groups[group].inst === state.scope) && (state.vilande || vilande === 0)
  }

  const drawAbout = (d: CheckDetail) => {
    const a = d.about[state.scope === "alla" ? (INSTS.find((i) => d.about[i].purpose) ?? INSTS[0]) : state.scope]
    aboutBox.replaceChildren()
    if (a.purpose) {
      const purpose = el("div", "prose")
      purpose.innerHTML = a.purpose
      aboutBox.append(purpose)
    }
    if (a.advice) {
      const advice = el("details", "disc advice")
      advice.open = adviceOpen
      advice.innerHTML = `<summary>${CHEVRON}Rekommendationer</summary>`
      const body = el("div", "prose")
      body.innerHTML = a.advice
      advice.append(body)
      advice.addEventListener("toggle", () => (adviceOpen = advice.open))
      aboutBox.append(advice)
    }
    const more = el("p", "more")
    const pages = (state.scope === "alla" ? [...INSTS] : [state.scope]).filter((i) => d.about[i].url)
    if (pages.length) more.append(state.scope === "alla" ? "Hela analysen per institution" : "")
    for (const i of pages) {
      const a = el("a", "pill", state.scope === "alla" ? i : `Hela analysen för ${i}`)
      a.href = base + d.about[i].url
      more.append(a)
    }
    if (pages.length) aboutBox.append(more)
  }

  const drawProblems = (d: CheckDetail) => {
    problemBox.replaceChildren()
    const counts = d.problems.map(() => 0)
    for (const [plan, problem] of d.notes) if (inScope(d, plan)) counts[problem]++
    const total = counts.reduce((a, b) => a + b, 0)
    if (!total) return
    problemBox.append(el("h3", "", "Vad noteringarna gäller"))
    if (d.problems.length === 1) {
      const p = el("p", "one")
      p.append("Alla noteringar gäller samma sak: ", el("b", "", d.problems[0]), ".")
      return void problemBox.append(p)
    }
    const top = Math.max(...counts)
    const list = el("div", "probs")
    d.problems
      .map((label, i) => ({ label, i, n: counts[i] }))
      .filter((x) => x.n > 0)
      .sort((a, b) => b.n - a.n)
      .forEach(({ label, i, n }) => {
        const b = el("button", "prob")
        b.type = "button"
        b.setAttribute("aria-pressed", String(state.problem === i))
        const track = el("span", "track")
        const bar = el("i", "bar")
        bar.style.setProperty("--w", String(n / top))
        track.append(bar, el("span", "val num", sv(n)))
        b.append(el("span", "lab", label), track)
        // Choosing a kind of note narrows the list below to the plans that have it.
        b.addEventListener("click", () => {
          state.problem = state.problem === i ? null : i
          drawProblems(d)
          drawGroups(d)
        })
        list.append(b)
      })
    problemBox.append(list, el("p", "caption", state.problem === null ? "Välj en rad för att bara se de planerna nedan." : `Visar bara planer med ”${d.problems[state.problem]}”. Välj raden igen för att se alla.`))
  }

  const drawGroups = (d: CheckDetail) => {
    groupBox.replaceChildren()
    // Which plans in each group have a note, under the current institution, status and kind of note.
    const hits = new Map<number, Set<number>>()
    for (const [plan, problem] of d.notes) {
      if (!inScope(d, plan) || (state.problem !== null && problem !== state.problem)) continue
      const g = d.plans[plan][2]
      if (!hits.has(g)) hits.set(g, new Set())
      hits.get(g)!.add(plan)
    }
    const rows = [...hits]
      .map(([g, plans]) => ({ g, group: o.groups[g], plans: [...plans], total: o.groups[g].plans[0] + (state.vilande ? o.groups[g].plans[1] : 0) }))
      .sort((a, b) => b.plans.length - a.plans.length || a.group.title.localeCompare(b.group.title, "sv"))
    if (!rows.length) return void groupBox.append(el("p", "empty", "Inga noteringar här."))

    const head = el("div", "grouphead")
    const legend = el("p", "legend")
    legend.append(el("i", "sw a"), "Planer med notering", el("i", "sw r"), "Övriga planer")
    head.append(el("h3", "", "Var noteringarna finns"), legend)
    groupBox.append(head)

    const LIMIT = 12
    const widest = Math.max(...rows.map((r) => r.total))
    const multi = d.problems.length > 1
    const list = el("div", "groups")
    for (const r of showAll || rows.length <= LIMIT + 2 ? rows : rows.slice(0, LIMIT)) {
      const item = el("details", "disc grp")
      item.dataset.inst = r.group.inst
      const summary = el("summary")
      summary.innerHTML = CHEVRON
      const title = el("span", "gt")
      if (state.scope === "alla") title.append(el("span", "idot"))
      title.append(el("span", "gname", r.group.title))
      // The dot alone would leave the institution to colour; the abbreviation says it.
      if (state.scope === "alla") title.append(el("span", "ginst", r.group.inst))
      // One bar per group: its length is the group's size, the filled part the plans with a note.
      const bar = el("span", "gbar")
      bar.style.setProperty("--w", String(r.total / widest))
      const hit = el("i", "a")
      hit.style.flex = String(r.plans.length)
      bar.append(hit)
      if (r.total > r.plans.length) {
        const rest = el("i", "r")
        rest.style.flex = String(r.total - r.plans.length)
        bar.append(rest)
      }
      summary.append(title, bar, el("span", "gcount num", `${sv(r.plans.length)} av ${sv(r.total)}`))
      const body = el("div", "plans")
      // The plans are only built when the group is opened: some groups hold a hundred.
      const fill = () => {
        if (body.childElementCount) return
        for (const p of r.plans.sort((a, b) => d.plans[a][1].localeCompare(d.plans[b][1], "sv"))) {
          const [code, name, , vilande, url] = d.plans[p]
          const row = el("div", "p")
          const a = el("a")
          a.href = base + url
          a.append(el("span", "code num", code), el("span", "pn", name))
          if (vilande) {
            const st = el("span", "st")
            st.append(el("span", "dot"), "Vilande")
            a.append(st)
          }
          const notes = el("ul", "pnotes")
          for (const [plan, problem, html] of d.notes) {
            if (plan !== p || (state.problem !== null && problem !== state.problem)) continue
            const li = el("li")
            if (multi) li.append(el("b", "", d.problems[problem]))
            const text = el("span")
            text.innerHTML = html // rendered from the vault at build time, like the plan pages
            li.append(text)
            notes.append(li)
          }
          row.append(a, notes)
          body.append(row)
        }
      }
      item.addEventListener("toggle", () => {
        if (item.open) {
          fill()
          open.add(r.g)
        } else open.delete(r.g)
      })
      item.append(summary, body)
      if (open.has(r.g)) {
        fill()
        item.open = true
      }
      list.append(item)
    }
    groupBox.append(list)
    if (!showAll && rows.length > LIMIT + 2) {
      const more = el("button", "pill showall", `Visa alla ${rows.length}`)
      more.type = "button"
      more.addEventListener("click", () => {
        showAll = true
        drawGroups(d)
      })
      groupBox.append(more)
    }
  }

  const draw = async () => {
    const check = checkOf(state.check)
    scopeLine.replaceChildren()
    if (state.scope === "alla") scopeLine.textContent = "Alla institutioner"
    else {
      scopeLine.dataset.inst = state.scope
      scopeLine.append(el("span", "idot"), names[state.scope])
    }
    // The headline comes from the embedded overview, so it changes at once.
    sum.textContent = sentence(cell(o, check, state.scope, state.vilande), check, state.vilande)
    const mine = ++drawing
    if (!fetched.has(state.check)) groupBox.replaceChildren(el("p", "empty", "Hämtar noteringarna…"))
    const d = await load(state.check)
    if (mine !== drawing) return // the reader has already moved on
    drawAbout(d)
    drawProblems(d)
    drawGroups(d)
  }

  // ── Choosing ──
  const remember = () =>
    history.replaceState(history.state, "", `${location.pathname}${location.search}#${state.scope.toLowerCase()}/${state.check}${state.vilande ? "/med-vilande" : ""}`)

  const choose = (next: Partial<Pick<typeof state, "scope" | "check" | "vilande">>, how: { reveal?: boolean; silent?: boolean } = {}) => {
    const checkChanged = next.check !== undefined && next.check !== state.check
    const scopeChanged = next.scope !== undefined && next.scope !== state.scope
    const vilandeChanged = next.vilande !== undefined && next.vilande !== state.vilande
    Object.assign(state, next)
    if (checkChanged) {
      state.problem = null
      open.clear()
    }
    if (checkChanged || scopeChanged) showAll = false
    if (vilandeChanged) paint()
    mark()
    if (!how.silent) remember()
    draw()
    if (how.reveal && stacked.matches) {
      if (reduceMotion()) detail.scrollIntoView({ behavior: "instant", block: "start" })
      else glide(detail, () => {})
    }
  }

  const seg = segmented(root.querySelector<HTMLElement>("[data-q-inst]")!, (value) => isScope(value) && choose({ scope: value }))
  select.addEventListener("change", () => choose({ check: select.value }))
  const basis = segmented(root.querySelector<HTMLElement>("[data-q-basis]")!, (value) => choose({ vilande: value === "alla" }))

  for (const a of cells) {
    a.addEventListener("click", (e) => {
      // A modified click still opens the institution's own analysis page in a new tab.
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return
      e.preventDefault()
      choose({ check: a.dataset.check!, scope: a.dataset.scope as Scope }, { reveal: e.detail !== 0 })
    })
    // The table is one stop in the Tab order; the arrow keys move within it.
    a.addEventListener("focus", () => cells.forEach((c) => (c.tabIndex = c === a ? 0 : -1)))
    a.addEventListener("keydown", (e) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return
      if (e.key === " ") {
        e.preventDefault()
        return a.click()
      }
      const r = grid.findIndex((row) => row.includes(a))
      const c = grid[r].indexOf(a)
      const next =
        e.key === "ArrowRight" ? grid[r][c + 1] : e.key === "ArrowLeft" ? grid[r][c - 1] : e.key === "ArrowDown" ? grid[r + 1]?.[c] : e.key === "ArrowUp" ? grid[r - 1]?.[c] : e.key === "Home" ? grid[r][0] : e.key === "End" ? grid[r][grid[r].length - 1] : undefined
      // At an edge there is nothing to move to, and the key keeps its usual job of scrolling.
      if (!next || next === a) return
      e.preventDefault()
      next.focus()
    })
  }

  // ── Tooltip on the table: a short wait the first time, then instant between cells ──
  let timer = 0
  let warm = false
  const hide = () => {
    clearTimeout(timer)
    tip.classList.remove("show")
    timer = window.setTimeout(() => (warm = false), 400)
  }
  for (const c of [...cells, ...anyCells]) {
    c.addEventListener("pointerenter", (e) => {
      if (e.pointerType !== "mouse") return
      const check = c.dataset.check ? checkOf(c.dataset.check) : null
      const scope = (c.dataset.scope ?? c.dataset.any) as Scope
      const n = cell(o, check, scope, state.vilande)
      tip.replaceChildren(
        el("b", "num", `${sv(n.hit)} av ${sv(n.of)} ${planWord(check, state.vilande)}`),
        el("span", "", `${check?.area ?? "Minst en notering"}, ${scope === "alla" ? "alla institutioner" : scope}`),
        el("span", "num", `${sv(n.notes)} ${n.notes === 1 ? "notering" : "noteringar"}`),
      )
      const box = c.getBoundingClientRect()
      tip.style.left = `${Math.max(8, Math.min(box.left, innerWidth - tip.offsetWidth - 8))}px`
      tip.style.top = `${box.bottom + 8}px`
      clearTimeout(timer)
      tip.classList.toggle("instant", warm)
      if (warm) tip.classList.add("show")
      else timer = window.setTimeout(() => (tip.classList.add("show"), (warm = true)), 280)
    })
    c.addEventListener("pointerleave", hide)
  }
  addEventListener("scroll", hide, { passive: true })

  // ── Start: from the address if it names a place (#iks/betygsskalor, or …/med-vilande) ──
  const fromAddress = () => {
    const [scope, check, status] = location.hash.slice(1).split("/")
    const s = scope?.toUpperCase() === "ALLA" ? "alla" : scope?.toUpperCase()
    const next: Parameters<typeof choose>[0] = {}
    if (s && isScope(s)) next.scope = s
    if (check && o.checks.some((c) => c.slug === check)) next.check = check
    if (scope) next.vilande = status === "med-vilande"
    return next
  }
  choose(fromAddress(), { silent: true })
  addEventListener("hashchange", () => choose(fromAddress(), { silent: true }))
}
