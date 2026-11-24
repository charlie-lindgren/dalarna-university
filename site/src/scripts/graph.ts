// Graf. The layout arrives ready-made (lib/graph.ts computes it when the site
// is built); this draws it on a canvas and makes it something you can move around in:
// zoom and pan, point at a node to see what it is and what it connects to, click to open it.
import "d3-transition"
import { quadtree, type Quadtree } from "d3-quadtree"
import { select } from "d3-selection"
import { zoom, zoomIdentity, type ZoomTransform } from "d3-zoom"
import { INSTITUTION_PALETTE, INSTITUTIONS, STRUCTURAL_GOLD } from "../lib/graph-colors"
import { instShort, say, t as txt, uiLang } from "../lib/ui"
import { reduceMotion } from "./util"

interface N {
  i: number
  x: number
  y: number
  r: number
  /** 0 home, 1 institution, 2 subject, 3 programme, 4 course */
  tier: number
  inst: number
  vilande: boolean
  /** A programme with no link inside its own institution: it reads other institutions' courses. */
  lone: boolean
  code: string
  title: string
  path: string
  near: N[]
  /** What the node travels out from when the graph opens: a course from its subject, a
   *  subject or programme from its institution, an institution from the middle. */
  hub: N | null
  /** For a subject: how far its flower of courses reaches. Its name sits just below that. */
  reach: number
}

const FONT = '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif'
const codeSlug = (code: string) => code.normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^A-Za-z0-9]+/g, "")
const easeOut = (p: number) => 1 - Math.pow(1 - Math.min(1, Math.max(0, p)), 4)

const stage = document.querySelector<HTMLElement>("[data-graph]")
if (stage) start(stage)

async function start(stage: HTMLElement) {
  const canvas = stage.querySelector("canvas")!
  const ctx = canvas.getContext("2d")!
  const base = stage.dataset.base ?? ""
  const tip = stage.querySelector<HTMLElement>("[data-tip]")!
  const hint = stage.querySelector<HTMLElement>("[data-hint]")!
  const card = stage.querySelector<HTMLElement>("[data-card]")!
  const raw: { n: [number, number, number, number, number, number, string, string, string, number][]; l: [number, number][] } = await fetch(stage.dataset.src!).then((r) => r.json())

  // ── The graph ──
  const nodes: N[] = raw.n.map(([x, y, r, tier, inst, flags, code, title, path, reach], i) => ({
    i, x, y, r, tier, inst, code, title, reach,
    vilande: (flags & 1) === 1,
    lone: (flags & 2) === 2,
    path: path || `/${tier === 3 ? "program" : "kurs"}/${codeSlug(code)}/`,
    near: [],
    hub: null,
  }))
  const links = raw.l.map(([a, b]) => [nodes[a], nodes[b]] as [N, N])
  for (const [a, b] of links) {
    a.near.push(b)
    b.near.push(a)
  }
  const home = nodes.find((n) => n.tier === 0)!
  const hubs = nodes.filter((n) => n.tier === 1)
  // The home node sits in the middle of the four institutions, joined to each by a stem:
  // the hierarchy the site is built on, even though the notes themselves do not link it.
  home.x = hubs.reduce((s, n) => s + n.x, 0) / hubs.length
  home.y = hubs.reduce((s, n) => s + n.y, 0) / hubs.length
  for (const n of nodes) {
    const institution = hubs.find((h) => h.inst === n.inst) ?? home
    n.hub = n.tier === 0 ? null : n.tier === 1 ? home : n.tier === 4 ? (n.near.find((m) => m.tier === 2) ?? institution) : institution
  }
  // Links from a programme to the courses it reads cross the flowers, so they are drawn
  // more lightly than the spokes of a flower until a programme is pointed at.
  const spokes = links.filter(([a, b]) => a.tier !== 3 && b.tier !== 3)
  const reads = links.filter(([a, b]) => a.tier === 3 || b.tier === 3)
  /** What a node is called. The university and its schools go by their names in the
   *  interface language; a subject or a plan keeps the name it has in the vault. */
  const short = (n: N) => (n.tier === 0 ? txt("site.name", uiLang()) : n.tier === 1 ? instShort(INSTITUTIONS[n.inst], uiLang()) : n.title)
  // Hubs are drawn last, so they sit on top of the plans around them.
  const drawOrder = [...nodes].sort((a, b) => b.tier - a.tier)
  const subjectsBySize = nodes.filter((n) => n.tier === 2).sort((a, b) => b.reach - a.reach)
  const programmes = nodes.filter((n) => n.tier === 3)

  // ── State ──
  let t: ZoomTransform = zoomIdentity
  let hover: N | null = null
  let picked: N | null = null
  let only = -1
  let showVilande = true
  let touched = false
  /** False while the page is still putting the first view in place. */
  let settled = false
  let bloom = 1
  let W = 0, H = 0, dpr = 1
  const X = new Float32Array(nodes.length)
  const Y = new Float32Array(nodes.length)
  let tree: Quadtree<N>

  /** A node's radius in graph units. Zooming in enlarges nodes more slowly than the space
   *  between them, so a close view shows separate points with room for their names. */
  const rad = (n: N) => Math.max(n.r * (t.k > 1 ? Math.pow(t.k, -0.45) : 1), 1.5 / t.k)
  // What is not highlighted steps back, but stays readable.
  const BACK = { node: 0.45, label: 0.66, link: 0.75 }
  const ASIDE = { node: 0.32, label: 0.55, link: 0.4 }
  const shown = (n: N) => showVilande || !n.vilande
  const faded = (n: N) => only >= 0 && n.tier !== 0 && n.inst !== only

  /** Where each node is drawn. While the graph opens, the institutions move out from the
   *  middle, then their subjects and programmes, then each subject's courses unfold. */
  const place = () => {
    const e1 = easeOut(bloom / 0.42)
    const e2 = easeOut((bloom - 0.14) / 0.56)
    const e3 = easeOut((bloom - 0.4) / 0.6)
    const at = (n: N, e: number, from: N) => {
      X[n.i] = X[from.i] + (n.x - from.x) * e
      Y[n.i] = Y[from.i] + (n.y - from.y) * e
    }
    X[home.i] = home.x
    Y[home.i] = home.y
    if (bloom >= 1) {
      for (const n of nodes) {
        X[n.i] = n.x
        Y[n.i] = n.y
      }
      return
    }
    // Outermost last, so each node starts from where its hub has got to.
    for (const n of hubs) at(n, e1, home)
    for (const n of nodes) if (n.tier === 2 || n.tier === 3) at(n, e2, n.hub!)
    for (const n of nodes) if (n.tier === 4) at(n, n.hub!.tier === 2 ? e3 : e2, n.hub!)
  }
  const index = () => (tree = quadtree<N>().x((n) => n.x).y((n) => n.y).addAll(nodes.filter(shown)))

  // ── Colours: the institution hues are the graph's own; inks and surfaces follow the theme ──
  let C = { ink: "", ink2: "", tint: "", halo: "", link: "", vilande: "" }
  const readColours = () => {
    const cs = getComputedStyle(document.documentElement)
    const forced = document.documentElement.dataset.theme
    const dark = forced ? forced === "dark" : matchMedia("(prefers-color-scheme: dark)").matches
    C = {
      ink: cs.getPropertyValue("--ink").trim(),
      ink2: cs.getPropertyValue("--ink-2").trim(),
      tint: cs.getPropertyValue("--tint").trim(),
      halo: dark ? "rgba(31, 33, 40, 0.86)" : "rgba(255, 255, 255, 0.86)",
      link: dark ? "rgba(255, 255, 255, 0.13)" : "rgba(40, 48, 80, 0.13)",
      // Vilande plans recede to a neutral grey: there are many, and they are context.
      vilande: dark ? "rgba(168, 172, 188, 0.22)" : "rgba(112, 118, 140, 0.34)",
    }
  }
  const fill = (n: N) => {
    if (n.tier === 0) return STRUCTURAL_GOLD
    if (n.vilande) return C.vilande
    const p = INSTITUTION_PALETTE[INSTITUTIONS[n.inst]]
    return n.tier === 1 ? p.moc : n.tier === 2 ? p.subject : n.tier === 3 ? p.program : p.course
  }

  // ── Drawing ──
  const widths = new Map<string, number>()
  const measure = (text: string, font: string) => {
    const key = font + text
    let w = widths.get(key)
    if (w === undefined) {
      ctx.font = font
      widths.set(key, (w = ctx.measureText(text).width))
    }
    return w
  }
  let queued = 0
  const schedule = () => (queued ||= requestAnimationFrame(draw))

  function draw() {
    queued = 0
    const k = t.k
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.clearRect(0, 0, W, H)
    ctx.save()
    ctx.translate(t.x, t.y)
    ctx.scale(k, k)
    const focus = hover ?? picked
    const lit = focus ? new Set<N>([focus, ...focus.near]) : null
    const x0 = -t.x / k - 40, y0 = -t.y / k - 40, x1 = (W - t.x) / k + 40, y1 = (H - t.y) / k + 40
    const out = (n: N) => X[n.i] < x0 || X[n.i] > x1 || Y[n.i] < y0 || Y[n.i] > y1

    // Links: the spokes of each flower and the stems to the hubs, then (lighter) what each
    // programme reads, then the pointed-at node's own links over them all in the tint.
    ctx.lineWidth = 0.9 / k
    ctx.strokeStyle = C.link
    for (const [set, weight] of [[spokes, 1], [reads, 0.55]] as const)
      for (const aside of [false, true]) {
        ctx.globalAlpha = weight * (aside ? ASIDE.link : 1) * (lit ? BACK.link : 1)
        ctx.beginPath()
        for (const [a, b] of set) {
          if (!shown(a) || !shown(b) || (faded(a) || faded(b)) !== aside || (out(a) && out(b))) continue
          ctx.moveTo(X[a.i], Y[a.i])
          ctx.lineTo(X[b.i], Y[b.i])
        }
        if (set === spokes)
          for (const h of hubs) {
            if (faded(h) !== aside) continue
            ctx.moveTo(X[home.i], Y[home.i])
            ctx.lineTo(X[h.i], Y[h.i])
          }
        ctx.stroke()
      }
    if (focus) {
      ctx.globalAlpha = 0.9
      ctx.strokeStyle = C.tint
      ctx.lineWidth = 1.3 / k
      ctx.beginPath()
      for (const n of focus.near) {
        if (!shown(n)) continue
        ctx.moveTo(X[focus.i], Y[focus.i])
        ctx.lineTo(X[n.i], Y[n.i])
      }
      ctx.stroke()
    }

    // Nodes. A programme is a diamond, so it can be told from the courses around it.
    const shape = (n: N, r: number) => {
      const x = X[n.i], y = Y[n.i]
      ctx.beginPath()
      if (n.tier === 3) {
        const d = r * 1.25
        ctx.moveTo(x, y - d)
        ctx.lineTo(x + d, y)
        ctx.lineTo(x, y + d)
        ctx.lineTo(x - d, y)
        ctx.closePath()
      } else ctx.arc(x, y, r, 0, 6.2832)
    }
    let plansInView = 0
    for (const n of drawOrder) {
      if (!shown(n) || out(n)) continue
      if (n.tier >= 3) plansInView++
      ctx.globalAlpha = lit ? (lit.has(n) ? 1 : BACK.node) : faded(n) ? ASIDE.node : 1
      shape(n, rad(n))
      if (n.lone) {
        // An outline, not a filled shape: this programme stands apart from its institution's courses.
        ctx.lineWidth = 1.6 / k
        ctx.strokeStyle = fill(n)
        ctx.stroke()
      } else {
        ctx.fillStyle = fill(n)
        ctx.fill()
      }
    }
    if (focus && shown(focus)) {
      ctx.strokeStyle = C.tint
      // What a plan connects to is spread over several flowers, so each of those is ringed and
      // stands out without the rest going dark. A subject's courses are its own flower, which
      // the tint spokes already show.
      if (focus.tier >= 3) {
        ctx.globalAlpha = 0.9
        ctx.lineWidth = 1.1 / k
        for (const n of focus.near) {
          if (!shown(n) || out(n)) continue
          shape(n, rad(n) + 1.6 / k)
          ctx.stroke()
        }
      }
      ctx.globalAlpha = 1
      ctx.lineWidth = 2 / k
      shape(focus, rad(focus) + 3 / k)
      ctx.stroke()
    }
    ctx.restore()

    // Labels, in screen space, most important first. One is only drawn where it does not
    // run into a label already there, so the picture stays readable at every zoom.
    const boxes: [number, number, number, number][] = []
    ctx.textAlign = "center"
    ctx.textBaseline = "top"
    ctx.lineJoin = "round"
    const label = (n: N, text: string, size: number, weight: number, colour: string, alpha: number) => {
      const sx = X[n.i] * k + t.x
      const sy = Y[n.i] * k + t.y
      // Only nodes that are themselves in view are named.
      if (sx < 0 || sx > W || sy < -10 || sy > H) return
      const font = `${weight} ${size}px ${FONT}`
      const w = measure(text, font) + 8
      const h = size * 1.35
      // A name near the edge is nudged inward so it is never cut off.
      const cx = W > w + 8 ? Math.min(Math.max(sx, w / 2 + 4), W - w / 2 - 4) : sx
      const bx = cx - w / 2
      // A subject is named under its whole flower; once the flower fills a good part of the
      // window, under its own hub instead, where there is room by then. Anything else is
      // named under itself.
      const below = n.tier === 2 && n.reach * k <= 170 ? Math.max(n.reach, rad(n)) : rad(n) * (n.tier === 3 ? 1.25 : 1)
      const by = sy + below * k + 4
      for (const b of boxes) if (bx < b[0] + b[2] && bx + w > b[0] && by < b[1] + b[3] && by + h > b[1]) return
      boxes.push([bx, by, w, h])
      ctx.font = font
      ctx.globalAlpha = alpha
      ctx.lineWidth = 3.5
      ctx.strokeStyle = C.halo
      ctx.strokeText(text, cx, by)
      ctx.fillStyle = colour
      ctx.fillText(text, cx, by)
    }
    const arrive = Math.min(1, Math.max(0, (bloom - 0.7) / 0.3))
    const strength = (n: N) => arrive * (lit ? (lit.has(n) ? 1 : BACK.label) : faded(n) ? ASIDE.label : 1)
    if (focus && shown(focus)) {
      // Under the mouse the tooltip already names the node; a tapped or linked-to node is named here.
      if (focus !== hover) label(focus, focus.tier >= 3 ? `${focus.code} ${focus.title}` : short(focus), 12, 600, C.ink, arrive)
      for (const n of [...focus.near].filter(shown).sort((a, b) => a.tier - b.tier || b.r - a.r).slice(0, 16)) label(n, n.tier >= 3 ? n.title : short(n), 11, 500, C.ink, arrive)
    }
    // On a narrow screen the four full names cannot sit side by side, so the institutions
    // go by the abbreviations the legend uses.
    for (const n of hubs) label(n, W < 560 ? INSTITUTIONS[n.inst] : short(n), 14, 600, C.ink, strength(n))
    label(home, short(home), 12, 600, C.ink, arrive)
    // A flower is named once it is large enough on screen to be worth naming.
    for (const n of subjectsBySize) if (n.reach * k >= 12) label(n, n.title, 12, 500, C.ink, strength(n))
    // Programmes are named once the view is close enough for their names to sit between the
    // flowers; course plans only once few enough are in view for theirs to fit.
    if (k >= 0.62) for (const n of programmes) if (shown(n)) label(n, n.title, 11, 500, C.ink2, strength(n))
    if (plansInView <= 150)
      for (const n of drawOrder) {
        if (n.tier !== 4 || !shown(n)) continue
        label(n, `${n.code} ${n.title}`, 11, 400, C.ink2, strength(n))
      }
    ctx.globalAlpha = 1
  }

  // ── Size, zoom and pan ──
  const sel = select(canvas)
  const zoomer = zoom<HTMLCanvasElement, unknown>()
    .on("start", (e) => e.sourceEvent?.type === "mousedown" && canvas.classList.add("dragging"))
    .on("zoom", (e) => {
      t = e.transform
      if (e.sourceEvent) {
        touched = true
        hideTip()
      }
      // The hint has done its job once the reader has moved the view in any way.
      if (settled) hint.classList.add("gone")
      schedule()
    })
    .on("end", () => canvas.classList.remove("dragging"))
  sel.call(zoomer).on("dblclick.zoom", null)

  const frame = (members: N[]) => {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity
    for (const n of members) {
      x0 = Math.min(x0, n.x - n.r)
      y0 = Math.min(y0, n.y - n.r)
      x1 = Math.max(x1, n.x + n.r)
      y1 = Math.max(y1, n.y + n.r)
    }
    // Room for the controls along the bottom and for labels under the lowest nodes.
    const pad = Math.min(56, W * 0.06)
    const k = Math.min((W - pad * 2) / Math.max(1, x1 - x0), (H - pad * 2 - 24) / Math.max(1, y1 - y0), 6)
    return zoomIdentity.translate(W / 2, (H - 24) / 2).scale(k).translate(-(x0 + x1) / 2, -(y0 + y1) / 2)
  }
  const go = (to: ZoomTransform, animate: boolean) => {
    if (animate && !reduceMotion()) sel.transition().duration(420).ease((p) => 1 - Math.pow(1 - p, 3)).call(zoomer.transform, to)
    else sel.call(zoomer.transform, to)
  }
  const everything = () => frame(nodes.filter(shown))
  const resize = () => {
    const box = stage.getBoundingClientRect()
    W = box.width
    H = box.height
    dpr = Math.min(2, devicePixelRatio || 1)
    canvas.width = Math.round(W * dpr)
    canvas.height = Math.round(H * dpr)
    zoomer.scaleExtent([everything().k * 0.6, 10])
    if (!touched) sel.call(zoomer.transform, only >= 0 ? frame(nodes.filter((n) => n.inst === only && shown(n))) : everything())
    else draw()
  }

  // ── Pointing and opening ──
  const at = (px: number, py: number) => {
    const [gx, gy] = t.invert([px, py])
    const n = tree.find(gx, gy, 16 + 8 / t.k)
    return n && Math.hypot(n.x - gx, n.y - gy) <= rad(n) + 6 / t.k ? n : null
  }
  const describe = (n: N): [string, string] => {
    const l = uiLang()
    if (n.tier === 4) return [n.title, say.graphCourse(n.code, n.vilande, l)]
    if (n.tier === 3) return [n.title, say.graphProgramme(n.code, n.lone ? null : n.near.length, l)]
    if (n.tier === 2) return [n.title, say.graphSubject(n.near.filter((m) => m.tier === 4).length, l)]
    if (n.tier === 1) return [short(n), say.graphSchool(nodes.filter((m) => m.inst === n.inst && m.tier === 2).length, nodes.filter((m) => m.inst === n.inst && m.tier === 4).length, l)]
    return [short(n), txt("graph.toSearch", l)]
  }
  let timer = 0
  let warm = false
  function hideTip() {
    clearTimeout(timer)
    tip.classList.remove("show")
    timer = window.setTimeout(() => (warm = false), 400)
  }
  const showTip = (n: N, px: number, py: number) => {
    const [title, sub] = describe(n)
    const b = document.createElement("b")
    b.textContent = title
    const s = document.createElement("span")
    s.textContent = sub
    tip.replaceChildren(b, s)
    const box = stage.getBoundingClientRect()
    tip.style.left = `${Math.min(box.left + px + 14, innerWidth - tip.offsetWidth - 10)}px`
    tip.style.top = `${box.top + py + 16}px`
    clearTimeout(timer)
    tip.classList.toggle("instant", warm)
    if (warm) tip.classList.add("show")
    // A short wait the first time, then instant while moving from node to node.
    else timer = window.setTimeout(() => (tip.classList.add("show"), (warm = true)), 260)
  }
  let pointer = "mouse"
  canvas.addEventListener("pointerdown", (e) => (pointer = e.pointerType))
  canvas.addEventListener("pointermove", (e) => {
    if (e.pointerType !== "mouse" || e.buttons || bloom < 1) return
    const n = at(e.offsetX, e.offsetY)
    canvas.classList.toggle("over", !!n)
    if (n) showTip(n, e.offsetX, e.offsetY)
    else hideTip()
    if (n !== hover) {
      hover = n
      schedule()
    }
  })
  canvas.addEventListener("pointerleave", () => {
    hideTip()
    if (hover) {
      hover = null
      schedule()
    }
  })
  const pick = (n: N | null) => {
    picked = n
    card.hidden = !n
    if (n) {
      const [title, sub] = describe(n)
      card.querySelector("[data-card-title]")!.textContent = title
      card.querySelector("[data-card-sub]")!.textContent = sub
      card.querySelector<HTMLAnchorElement>("[data-card-link]")!.href = base + n.path
    }
    schedule()
  }
  canvas.addEventListener("click", (e) => {
    const n = at(e.offsetX, e.offsetY)
    // A mouse click opens the node. A finger has no hover, so a tap first shows what the
    // node is, with a button to open it.
    if (!n) return pick(null)
    if (pointer !== "mouse") return pick(n)
    if (e.metaKey || e.ctrlKey) window.open(base + n.path, "_blank")
    else location.href = base + n.path
  })

  // ── Controls ──
  const columns = document.querySelector<HTMLAnchorElement>('.sitemenu a[data-menu="bladdra"]')
  const onlyButtons = [...stage.querySelectorAll<HTMLButtonElement>("[data-only]")]
  const setOnly = (inst: number, animate: boolean) => {
    only = inst
    onlyButtons.forEach((b, i) => b.setAttribute("aria-pressed", String(i === inst)))
    // Bläddra, from the menu, opens at the same institution.
    if (columns) columns.hash = inst >= 0 ? INSTITUTIONS[inst].toLowerCase() : ""
    touched = false
    go(inst >= 0 ? frame(nodes.filter((n) => n.inst === inst && shown(n))) : everything(), animate)
    schedule()
  }
  onlyButtons.forEach((b, i) => b.addEventListener("click", (e) => setOnly(only === i ? -1 : i, e.detail !== 0)))
  const vilandeButton = stage.querySelector<HTMLButtonElement>("[data-vilande]")!
  vilandeButton.addEventListener("click", () => {
    showVilande = !showVilande
    vilandeButton.setAttribute("aria-pressed", String(showVilande))
    index()
    if (picked && !shown(picked)) pick(null)
    schedule()
  })
  for (const b of stage.querySelectorAll<HTMLButtonElement>("[data-zoom]"))
    b.addEventListener("click", (e) => {
      const animate = e.detail !== 0 && !reduceMotion()
      if (b.dataset.zoom === "fit") {
        touched = false
        return go(only >= 0 ? frame(nodes.filter((n) => n.inst === only && shown(n))) : everything(), animate)
      }
      const by = b.dataset.zoom === "in" ? 1.6 : 1 / 1.6
      if (animate) sel.transition().duration(220).ease((p) => 1 - Math.pow(1 - p, 3)).call(zoomer.scaleBy, by)
      else sel.call(zoomer.scaleBy, by)
    })

  // The appearance switch, or the system changing scheme: same picture, new inks.
  const recolour = () => {
    readColours()
    schedule()
  }
  document.addEventListener("themechange", recolour)
  // Another interface language: the names drawn on the canvas, and the card if one is open.
  document.addEventListener("uichange", () => {
    if (picked) pick(picked)
    schedule()
  })
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", recolour)

  // ── Start ──
  readColours()
  index()
  place()
  new ResizeObserver(resize).observe(stage)
  resize()

  setTimeout(() => (settled = true), 1800)
  // An address can name a place (#iks, or #iks/historia when coming from Bläddra).
  const [instName, slug] = location.hash.slice(1).split("/")
  const inst = INSTITUTIONS.findIndex((i) => i.toLowerCase() === instName)
  if (inst >= 0) {
    const subject = slug ? nodes.find((n) => n.tier === 2 && n.inst === inst && n.path.endsWith(`/${slug}`)) : null
    setOnly(inst, false)
    if (subject) {
      picked = subject
      touched = true
      go(frame([subject, ...subject.near.filter((m) => m.tier === 4)]), false)
    }
    return
  }
  // Otherwise, once per visit, the graph opens out from the middle: the institutions first,
  // then everything they hold.
  let seen = false
  try {
    seen = sessionStorage.getItem("graf-opened") === "1"
    sessionStorage.setItem("graf-opened", "1")
  } catch {
    // no storage: the opening simply plays each time
  }
  if (seen || reduceMotion()) return
  const t0 = performance.now()
  const open = () => {
    bloom = Math.min(1, (performance.now() - t0) / 1400)
    place()
    draw()
    if (bloom < 1) requestAnimationFrame(open)
  }
  bloom = 0
  open()
}
