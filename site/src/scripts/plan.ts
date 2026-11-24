// Behaviour of a plan page: the three language views, the section list that follows the
// reader, jump links that glide, and the toolbar that turns to glass once it sticks.
// The page reads fine without any of this; the script only adds to it.
import { glide } from "./glide"
import { reduceMotion, shown, store } from "./util"

type View = "sv" | "en" | "both"
const isView = (v: string | null | undefined): v is View => v === "sv" || v === "en" || v === "both"
const html = document.documentElement
const plan = document.querySelector<HTMLElement>(".plan")

// ── Svenska, English or Båda ────────────────────────────────────────
// The view lives on <html data-view>, set before first paint by the inline script in the
// page's <head>, so a reader who prefers English never sees Swedish flash by first.
function views(root: HTMLElement) {
  const seg = root.querySelector<HTMLElement>(".seg[data-view-switch]")
  if (!seg) return
  const thumb = seg.querySelector<HTMLElement>(".thumb")!
  const buttons = [...seg.querySelectorAll<HTMLButtonElement>("button")]
  const bar = seg.closest<HTMLElement>(".bar")
  const head = root.querySelector<HTMLElement>(".sheet-in > header")
  const content = root.querySelector<HTMLElement>(".sheet-in")
  const box = root.querySelector<HTMLElement>('[data-flip="box"]')
  const moved = () => [...root.querySelectorAll<HTMLElement>("[data-flip]")].filter(shown)
  let running: Animation[] = []

  const place = () => {
    const on = buttons.find((b) => b.getAttribute("aria-pressed") === "true")
    if (!on || !on.offsetWidth) return
    thumb.style.width = `${on.offsetWidth}px`
    thumb.style.transform = `translateX(${on.offsetLeft}px)`
  }

  // What the reader is looking at, so it can be put back in the same place once the view
  // has changed.
  //   While any of the title block is in view, nothing is held: the page stays where it is
  //   and the text below simply follows. (Holding a section heading there made the page
  //   scroll by however much the title block grew or shrank, which read as a stray jump.)
  //   Further down, a heading in the upper part of the window is the anchor: the eye is on
  //   it or just below it.
  //   With no heading in sight the reader is deep inside one long section, and that
  //   section's top is the anchor.
  const readingPlace = () => {
    const line = (bar?.getBoundingClientRect().bottom ?? 0) + 1
    if (head && head.getBoundingClientRect().bottom > line) return null
    const rows = [...root.querySelectorAll<HTMLElement>(".row")]
    const visible = rows.filter(shown)
    const tops = visible.map((r) => r.getBoundingClientRect().top)
    const aim = innerHeight / 3
    let el: HTMLElement | undefined
    let best = Infinity
    visible.forEach((r, i) => {
      if (tops[i] < line || tops[i] > innerHeight * 0.7) return
      const d = Math.abs(tops[i] - aim)
      if (d < best) [best, el] = [d, r]
    })
    el ??= visible.find((r, i) => tops[i] < line && r.getBoundingClientRect().bottom > line)
    return el ? { rows, at: rows.indexOf(el), offset: el.getBoundingClientRect().top } : null
  }

  // Everything that depends on the view but is not plain CSS.
  const sync = (value: View) => {
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.value === value)))
    place()
    // A note group whose section is not in this view keeps its label but loses the link.
    for (const a of root.querySelectorAll<HTMLAnchorElement>("a[data-jump]")) {
      const dead = !shown(document.getElementById(decodeURIComponent(a.hash.slice(1))))
      a.toggleAttribute("data-dead", dead)
      if (dead) a.tabIndex = -1
      else a.removeAttribute("tabindex")
    }
  }

  const set = (value: View, animate: boolean) => {
    // First: where things are now, mid-flight positions included.
    const els = animate ? moved() : []
    const first = els.map((el) => el.getBoundingClientRect())
    running.forEach((a) => a.cancel())
    running = []
    const reading = readingPlace()

    html.dataset.view = value
    if (!animate) seg.classList.remove("ready")
    sync(value)
    if (!animate) requestAnimationFrame(() => requestAnimationFrame(() => seg.classList.add("ready")))

    if (reading) {
      // The same section if this view has it, otherwise the nearest one after or before it.
      const { rows, at, offset } = reading
      const el = [...rows.slice(at), ...rows.slice(0, at).reverse()].find(shown)
      if (el) scrollBy({ top: el.getBoundingClientRect().top - offset, behavior: "instant" })
    }
    document.dispatchEvent(new CustomEvent("viewchange"))
    if (!animate) return

    // Last, and play the difference. Only transform, clip-path and opacity move: the text is
    // already in its new layout and is never re-wrapped mid-flight.
    const last = els.map((el) => el.getBoundingClientRect())
    const bi = box ? els.indexOf(box) : -1
    const grow = bi >= 0 ? last[bi].width - first[bi].width : 0
    // Opening out on the drawer curve; closing in faster.
    const timing = grow >= 0 ? { duration: 280, easing: "cubic-bezier(0.32, 0.72, 0, 1)" } : { duration: 200, easing: "cubic-bezier(0.23, 1, 0.32, 1)" }
    const still = reduceMotion()
    if (!still) {
      els.forEach((el, i) => {
        if (el === box) {
          const sx = first[i].width / last[i].width
          if (Math.abs(sx - 1) > 0.002) running.push(el.animate([{ transform: `scaleX(${sx})` }, { transform: "none" }], timing))
        } else {
          const dx = first[i].left - last[i].left
          if (Math.abs(dx) > 0.5) running.push(el.animate([{ transform: `translateX(${dx}px)` }, { transform: "none" }], timing))
        }
      })
    }
    if (content) {
      const frames =
        !still && grow > 1
          ? [{ opacity: 0.3, clipPath: `inset(0 ${grow}px 0 0)` }, { opacity: 1, clipPath: "inset(0 0 0 0)" }]
          : [{ opacity: 0.35 }, { opacity: 1 }]
      running.push(content.animate(frames, { duration: Math.max(timing.duration, 180), easing: timing.easing }))
    }
  }

  sync(isView(html.dataset.view) ? html.dataset.view : "sv")
  requestAnimationFrame(() => requestAnimationFrame(() => seg.classList.add("ready")))

  for (const b of buttons) {
    b.addEventListener("click", (e) => {
      const value = b.dataset.value
      if (!isView(value) || html.dataset.view === value) return
      // A keyboard press changes the view at once; a pointer press gets the motion.
      set(value, e.detail !== 0)
      // The choice carries to the next plan, and the address carries it to a colleague.
      store.set("plan-view", value)
      const url = new URL(location.href)
      url.searchParams.set("lang", value)
      history.replaceState(null, "", url)
    })
  }
  addEventListener("resize", place)
}

// ── Toolbar: glass once content scrolls under it ────────────────────
// CSS does this with scroll-state queries where the browser has them; this covers the rest.
function stuck(root: HTMLElement) {
  if (CSS.supports("container-type: scroll-state")) return
  for (const bar of root.querySelectorAll<HTMLElement>(".bar")) {
    const top = parseFloat(getComputedStyle(bar).top) || 0
    new IntersectionObserver(
      ([e]) => bar.classList.toggle("is-stuck", e.intersectionRatio < 1 && e.boundingClientRect.top <= top + 1),
      { threshold: [1], rootMargin: `-${top + 1}px 0px 0px 0px` },
    ).observe(bar)
  }
}

// ── Section list: follows the reader ────────────────────────────────
function sections(root: HTMLElement) {
  const lists = [...root.querySelectorAll<HTMLElement>("[data-spy]")]
  const links = lists.flatMap((l) => [...l.querySelectorAll<HTMLAnchorElement>('a[href^="#"]')])
  const jumps = [...root.querySelectorAll<HTMLAnchorElement>('a[data-jump][href^="#"]')]
  if (!links.length && !jumps.length) return
  const targetOf = (hash: string) => document.getElementById(decodeURIComponent(hash.slice(1)))
  // One entry per section, however many lists show it (the sidebar and the narrow-screen menu).
  const hashes = [...new Set(links.map((a) => a.hash))]

  // The browser's own tracking (scroll-target-group) picks the wrong link when a section is
  // only a line or two long, and plan sections often are. So the rule is spelled out here:
  // the current section is the last one whose heading has passed a line near the top.
  // A link the reader pressed stays marked until they scroll by hand, which also covers the
  // last sections of a page, which can never reach that line.
  let pinned: string | null = null
  let marked: string | null = null
  const mark = (hash: string) => {
    if (hash === marked) return
    marked = hash
    for (const l of links) {
      const on = l.hash === hash
      l.classList.toggle("target-current", on)
      if (on) l.setAttribute("aria-current", "true")
      else l.removeAttribute("aria-current")
    }
  }
  const compute = () => {
    if (pinned) return mark(pinned)
    const targets = hashes.map(targetOf).map((t) => (shown(t) ? t : null))
    const first = targets.find(Boolean)
    if (!first) return
    const line = (parseFloat(getComputedStyle(first).scrollMarginTop) || 0) + innerHeight * 0.12
    let current = hashes[targets.indexOf(first)]
    targets.forEach((t, i) => {
      if (t && t.getBoundingClientRect().top <= line) current = hashes[i]
    })
    mark(current)
  }
  let queued = false
  addEventListener(
    "scroll",
    () => {
      if (queued) return
      queued = true
      requestAnimationFrame(() => {
        queued = false
        compute()
      })
    },
    { passive: true },
  )
  const unpin = () => {
    pinned = null
  }
  for (const type of ["wheel", "touchmove", "keydown"]) addEventListener(type, unpin, { passive: true })
  addEventListener("resize", compute)
  // A change of view shows and hides sections, so the current one has to be found again.
  document.addEventListener("viewchange", () => {
    pinned = null
    marked = null
    compute()
  })
  compute()

  let stopGlide: (() => void) | null = null
  let startedOnPress = false
  const go = (a: HTMLAnchorElement, animate: boolean) => {
    const target = targetOf(a.hash)
    if (!shown(target)) return
    stopGlide?.()
    const menu = a.closest<HTMLElement>("[popover]")
    if (menu?.matches(":popover-open")) menu.hidePopover()
    history.replaceState(null, "", a.hash)
    // Light the pressed link at once, with no fade, and hold it there.
    if (hashes.includes(a.hash)) {
      pinned = a.hash
      mark(a.hash)
    }
    if (!animate || reduceMotion()) {
      target.scrollIntoView({ behavior: "instant", block: "start" })
      target.focus({ preventScroll: true })
      return
    }
    stopGlide = glide(target, () => {
      stopGlide = null
      target.focus({ preventScroll: true })
    })
  }
  for (const a of [...links, ...jumps]) {
    // A mouse starts moving on the press itself. Touch waits for the tap, so a swipe is not a jump.
    a.addEventListener("pointerdown", (e) => {
      if (e.pointerType !== "mouse" || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey) return
      startedOnPress = true
      go(a, true)
    })
    a.addEventListener("click", (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey) return
      e.preventDefault()
      if (startedOnPress) startedOnPress = false
      else go(a, e.detail !== 0) // detail 0 is the keyboard: jump, do not animate
    })
  }
}

if (plan) {
  // The view first, so the section list starts from what is actually on screen.
  views(plan)
  stuck(plan)
  sections(plan)
}
