// Bläddra: institution, then subject, then course plans.
// On a wide window the three columns sit side by side and a choice only changes what the
// next column shows. On a phone each column is a screen: a choice pushes the next one in,
// and the browser's Back, the on-screen back button and a swipe all lead back out.
import { loadCatalogue, type Entry } from "./catalogue"

const el = <K extends keyof HTMLElementTagNameMap>(tag: K, className?: string, text?: string) => {
  const node = document.createElement(tag)
  if (className) node.className = className
  if (text !== undefined) node.textContent = text
  return node
}

const box = document.querySelector<HTMLElement>("[data-browser]")
if (box) {
  const cols = box.querySelector<HTMLElement>(".cols")!
  const panes = [...cols.querySelectorAll<HTMLElement>(".pane")]
  const tabs = [...box.querySelectorAll<HTMLButtonElement>('[role="tab"]')]
  const panels = [...box.querySelectorAll<HTMLElement>('[role="tabpanel"]')]
  const drills = [...box.querySelectorAll<HTMLAnchorElement>("a[data-subject]")]
  const courses = box.querySelector<HTMLElement>("[data-courses]")!
  const heading = box.querySelector<HTMLElement>("[data-subject-title]")!
  const toggle = box.querySelector<HTMLButtonElement>("[data-vilande]")!
  const base = box.dataset.base ?? ""
  const narrow = matchMedia("(max-width: 820px)")
  let entries: Entry[] = []
  let subject: HTMLAnchorElement | null = null
  let showVilande = true
  /** Which screen a phone is on: 0 institutions, 1 subjects, 2 course plans. */
  let depth = 0
  /** Set while a swipe back is being squared with the browser's history. */
  let landing: number | null = null

  const currentTab = () => tabs.find((t) => t.getAttribute("aria-selected") === "true") ?? tabs[0]
  const panelOf = (tab: HTMLButtonElement) => panels.find((p) => p.id === tab.getAttribute("aria-controls"))!
  const depthOf = (hash: string) => {
    const [inst, slug] = hash.slice(1).split("/")
    return !inst ? 0 : slug ? 2 : 1
  }
  /** The address for a screen: nothing, #iks, or #iks/historia. */
  const hashFor = (d: number) => {
    const inst = currentTab().dataset.inst!.toLowerCase()
    return d <= 0 ? "" : d === 1 || !subject ? `#${inst}` : `#${inst}/${subject.dataset.slug}`
  }
  // The graph view opens at the same place: the link to it carries the current address.
  const graphLink = document.querySelector<HTMLAnchorElement>('[data-view-link="graf"]')
  const address = (hash: string) => {
    if (graphLink) graphLink.hash = hash
    return location.pathname + location.search + hash
  }
  const pushed = () => (history.state?.b as number | undefined) ?? 0

  // ── What each column shows ──
  const render = () => {
    courses.replaceChildren()
    toggle.hidden = !subject
    if (!subject) return void courses.append(el("p", "empty", "Välj ett ämne för att se dess kursplaner."))
    if (!entries.length) return void courses.append(el("p", "empty", "Hämtar kursplaner…"))
    const mine = entries
      .filter((e) => e.kind === "course" && e.subject === subject!.dataset.subject)
      .sort((a, b) => Number(a.vilande) - Number(b.vilande) || a.name.localeCompare(b.name, "sv"))
    const vilande = mine.filter((e) => e.vilande).length
    toggle.hidden = vilande === 0
    toggle.textContent = `Vilande (${vilande})`
    const listed = showVilande ? mine : mine.filter((e) => !e.vilande)
    if (!listed.length) return void courses.append(el("p", "empty", "Inga aktiva kursplaner i det här ämnet."))
    for (const e of listed) {
      const a = el("a", "item")
      a.href = base + e.url
      const grow = el("span", "grow")
      grow.append(el("span", "t", e.name))
      const m = el("span", "m num")
      if (e.vilande) m.append(el("span", "dot"), "Vilande")
      else m.textContent = e.credits
      a.append(el("span", "code num", e.code), grow, m)
      courses.append(a)
    }
    courses.scrollTop = 0
  }
  const selectSubject = (a: HTMLAnchorElement | null) => {
    subject = a
    drills.forEach((d) => (d === a ? d.setAttribute("aria-current", "true") : d.removeAttribute("aria-current")))
    heading.textContent = a ? a.querySelector(".t")!.textContent : "Kursplaner"
    render()
  }
  const selectInst = (tab: HTMLButtonElement) => {
    tabs.forEach((t) => {
      t.setAttribute("aria-selected", String(t === tab))
      t.tabIndex = t === tab ? 0 : -1
    })
    panels.forEach((p) => (p.hidden = p !== panelOf(tab)))
  }
  /** Make the columns show what an address names. A wide window always has a subject open. */
  const apply = (hash: string) => {
    const [inst, slug] = hash.slice(1).split("/")
    const tab = tabs.find((t) => t.dataset.inst!.toLowerCase() === inst) ?? (inst ? tabs[0] : currentTab())
    selectInst(tab)
    const panel = panelOf(tab)
    const named = slug ? panel.querySelector<HTMLAnchorElement>(`a[data-slug="${CSS.escape(slug)}"]`) : null
    const kept = subject && panel.contains(subject) ? subject : null
    selectSubject(named ?? (narrow.matches ? null : (kept ?? panel.querySelector<HTMLAnchorElement>("a[data-subject]"))))
  }

  // ── A phone's three screens ──
  // The screen in view is the only one that takes focus and reads aloud; the others are inert.
  const settle = (current: HTMLElement) => {
    panes.forEach((p) => p.toggleAttribute("inert", narrow.matches && p !== current))
    if (!narrow.matches) return
    const d = panes.indexOf(current)
    if (d === depth) return
    if (d < depth) {
      // The reader swiped back. Step the browser's history back with them, as far as the
      // entries this page added reach, so Back afterwards goes where they expect.
      const steps = Math.min(depth - d, pushed())
      depth = d
      if (steps > 0) {
        landing = d
        history.go(-steps)
      } else history.replaceState(history.state, "", address(hashFor(d)))
    } else {
      depth = d
      history.replaceState(history.state, "", address(hashFor(d)))
    }
  }
  const show = (d: number, animate: boolean) => {
    if (!narrow.matches) return
    // "auto" defers to the stylesheet, which scrolls smoothly unless the reader asked for less motion.
    cols.scrollTo({ left: d * cols.clientWidth, behavior: animate ? "auto" : "instant" })
    if (!animate) settle(panes[d])
  }
  // Whichever signal says the columns came to rest, the screen in view is read from where
  // they actually are. (The event's own target can be a step behind right after the page
  // has jumped to a deep link, and acting on it marked the visible screen inert.)
  const inView = () => panes[Math.round(cols.scrollLeft / Math.max(1, cols.clientWidth))] ?? panes[0]
  if ("onscrollsnapchange" in HTMLElement.prototype) cols.addEventListener("scrollsnapchange", () => settle(inView()))
  else {
    const io = new IntersectionObserver((seen) => seen.some((s) => s.intersectionRatio === 1) && settle(inView()), { root: cols, threshold: 1 })
    panes.forEach((p) => io.observe(p))
  }

  /** The reader chose something. A phone moves to the next screen and gains a history entry. */
  const drill = (d: number, animate: boolean) => {
    if (!narrow.matches) return void history.replaceState(history.state, "", address(hashFor(2)))
    history.pushState({ b: pushed() + 1 }, "", address(hashFor(d)))
    depth = d
    show(d, animate)
  }
  /** The on-screen back button. */
  const up = (animate: boolean) => {
    if (pushed() > 0) return history.back()
    // Arrived here by a link straight to this screen: there is no entry of ours to go back to.
    const d = Math.max(0, depth - 1)
    history.replaceState(history.state, "", address(hashFor(d)))
    depth = d
    show(d, animate)
  }
  // Back and Forward, and links to a place on this page, all arrive here.
  addEventListener("hashchange", () => {
    apply(location.hash)
    if (!narrow.matches) return
    if (landing !== null) {
      // A swipe already put the right screen in view; only the address may need correcting.
      if (depthOf(location.hash) !== landing) history.replaceState(history.state, "", address(hashFor(landing)))
      landing = null
      return
    }
    const d = depthOf(location.hash)
    const back = d < depth
    depth = d
    show(d, back) // going back glides; going forward is already where the reader meant to be
  })

  for (const tab of tabs) {
    tab.addEventListener("click", (e) => {
      const changed = tab.getAttribute("aria-selected") !== "true"
      selectInst(tab)
      if (changed) selectSubject(narrow.matches ? null : panelOf(tab).querySelector<HTMLAnchorElement>("a[data-subject]"))
      narrow.matches ? drill(1, e.detail !== 0) : drill(2, false)
    })
    // A vertical tab list: the arrow keys move between institutions, and the choice follows.
    tab.addEventListener("keydown", (e) => {
      const i = tabs.indexOf(tab)
      const next = e.key === "ArrowDown" ? tabs[(i + 1) % tabs.length] : e.key === "ArrowUp" ? tabs[(i - 1 + tabs.length) % tabs.length] : e.key === "Home" ? tabs[0] : e.key === "End" ? tabs[tabs.length - 1] : null
      if (!next || e.metaKey || e.ctrlKey || e.altKey) return
      e.preventDefault()
      selectInst(next)
      selectSubject(narrow.matches ? null : panelOf(next).querySelector<HTMLAnchorElement>("a[data-subject]"))
      next.focus()
      history.replaceState(history.state, "", address(hashFor(narrow.matches ? depth : 2)))
    })
  }
  for (const a of drills)
    a.addEventListener("click", (e) => {
      // A modified click still opens the subject's own page in a new tab.
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return
      e.preventDefault()
      selectSubject(a)
      drill(2, e.detail !== 0)
    })
  for (const b of box.querySelectorAll<HTMLButtonElement>("[data-back]")) b.addEventListener("click", (e) => up(e.detail !== 0))
  toggle.addEventListener("click", () => {
    showVilande = !showVilande
    toggle.setAttribute("aria-pressed", String(showVilande))
    render()
  })

  // Start from the address if it names a place; otherwise from the first institution.
  const start = () => {
    apply(location.hash)
    if (graphLink) graphLink.hash = location.hash
    depth = narrow.matches ? depthOf(location.hash) : 0
    if (narrow.matches) show(depth, false)
    else panes.forEach((p) => p.removeAttribute("inert"))
  }
  narrow.addEventListener("change", start)
  start()
  loadCatalogue(box.dataset.catalogue!).then((all) => {
    entries = all
    render()
  })
}
