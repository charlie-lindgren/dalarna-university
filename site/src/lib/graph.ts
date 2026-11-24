// The graph of the university: institutions, subjects, programmes and course plans, laid out
// once when the site is built, so every visitor gets the same picture at once.
//
// What it keeps from the Quartz graph (quartz/components/scripts/graph.inline.ts): analysis
// notes are left out, only links inside an institution are drawn, and each institution has
// its own quarter. What it changes is how a quarter is filled. There, one force simulation
// pulled every course toward the centre and the result was hard to read. Here the layout is
// built in two steps, so that each subject is a flower of its own:
//
//   1. Per institution, the subjects (as discs sized for their courses) and the programmes
//      are packed around the institution's hub without overlapping. A programme is drawn
//      toward the subjects whose courses it reads, so it settles between them.
//   2. Each subject's courses are set around it in a sunflower spiral, active plans inside
//      and vilande plans on the rim.
import { forceCollide, forceLink, forceManyBody, forceSimulation, forceX, forceY, type SimulationNodeDatum } from "d3-force"
import { getVault, parentOf, codeSlug, INSTITUTIONS, type Doc, type Inst } from "./vault"

/** 0 home, 1 institution, 2 subject, 3 programme, 4 course */
export type Tier = 0 | 1 | 2 | 3 | 4

/** Distance between neighbouring courses in a flower is about 1.8 times this. */
const SPACING = 11.5
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5))
/** Room kept clear around each thing in a cluster: under a subject, for its name. */
const AROUND = { hub: 26, subject: 34, programme: 18 }
/** Clear space between the four clusters. */
const BETWEEN = 150

interface Item extends SimulationNodeDatum {
  doc: Doc
  kind: "hub" | "subject" | "programme"
  /** The radius the item takes up: a subject's whole flower, not just its hub. */
  R: number
}
interface Pull {
  source: Item
  target: Item
  distance: number
  strength: number
}

let cached: ReturnType<typeof compute> | undefined
export const graphData = () => (cached ??= compute())

function compute() {
  const v = getVault()
  const tierOf = (d: Doc): Tier | null =>
    d.kind === "home" ? 0 : d.kind === "institution" ? 1 : d.kind === "subject" ? 2 : d.kind === "programme" ? 3 : d.kind === "course" ? 4 : null
  const docs = v.docs.filter((d) => tierOf(d) !== null) // analysis notes are for the dashboard
  const at = new Map(docs.map((d, i) => [d.file, i]))

  // Only links inside one institution, as in Quartz: the clusters stay apart, and a programme
  // that reads another institution's courses does not tie two clusters together.
  const links: [number, number][] = []
  const seen = new Set<string>()
  docs.forEach((d, a) => {
    for (const file of d.graph) {
      const b = at.get(file)
      if (b === undefined || !d.inst || d.inst !== docs[b].inst) continue
      const key = a < b ? `${a}-${b}` : `${b}-${a}`
      if (seen.has(key)) continue
      seen.add(key)
      links.push([a, b])
    }
  })
  const degree = docs.map(() => 0)
  for (const [a, b] of links) {
    degree[a]++
    degree[b]++
  }

  // Which courses each subject holds, and which programme reads which course.
  const coursesOf = new Map<Doc, Doc[]>()
  const loose = new Map<Inst, Doc[]>() // courses whose subject page is not in the vault
  for (const d of docs) {
    if (d.kind !== "course") continue
    const subject = parentOf(d)
    if (subject?.kind === "subject" && subject.inst === d.inst) coursesOf.set(subject, [...(coursesOf.get(subject) ?? []), d])
    else loose.set(d.inst!, [...(loose.get(d.inst!) ?? []), d])
  }
  const subjectOf = new Map<Doc, Doc>()
  for (const [s, cs] of coursesOf) for (const c of cs) subjectOf.set(c, s)

  // Sizes. A hub is drawn larger the more it holds; a flower needs room for all its courses.
  const hubRadius = (courses: number) => Math.min(16, 8 + 0.7 * Math.sqrt(courses))
  const firstRing = (centre: number) => Math.ceil(((centre + 10) / SPACING) ** 2)
  const flower = (courses: number, centre: number) => SPACING * Math.sqrt(courses + firstRing(centre)) + 9
  const radius = (d: Doc, i: number) =>
    d.kind === "home" ? 14 : d.kind === "institution" ? 18 : d.kind === "subject" ? hubRadius(coursesOf.get(d)?.length ?? 0) : d.kind === "programme" ? 8 : 5 + 0.9 * Math.sqrt(degree[i])

  // ── Step 1: pack each institution's subjects and programmes around its hub ──
  const place = new Map<Doc, [number, number]>()
  const reach = new Map<Doc, number>() // a subject's flower radius, for its label and the page
  const clusters = INSTITUTIONS.map((inst) => {
    const mine = docs.filter((d) => d.inst === inst)
    const hubDoc = mine.find((d) => d.kind === "institution")!
    const strays = loose.get(inst)?.length ?? 0
    const hub: Item = { doc: hubDoc, kind: "hub", R: strays ? flower(strays, 18) : 18, fx: 0, fy: 0 }
    const subjects: Item[] = mine.filter((d) => d.kind === "subject").map((doc) => ({ doc, kind: "subject", R: flower(coursesOf.get(doc)?.length ?? 0, hubRadius(coursesOf.get(doc)?.length ?? 0)) }))
    const programmes: Item[] = mine.filter((d) => d.kind === "programme").map((doc) => ({ doc, kind: "programme", R: 8 }))
    const items = [hub, ...subjects, ...programmes]
    const itemOf = new Map(items.map((it) => [it.doc, it]))
    for (const s of subjects) reach.set(s.doc, s.R)
    reach.set(hubDoc, hub.R)

    // About how far out the cluster will reach, for the programmes that read no local course.
    const rim = Math.sqrt(items.reduce((a, it) => a + (it.R + AROUND[it.kind]) ** 2, 0)) * 1.05
    const pulls: Pull[] = subjects.map((s) => ({ source: s, target: hub, distance: hub.R + s.R + AROUND.hub, strength: 0.6 }))
    for (const p of programmes) {
      const read = new Map<Item, number>()
      for (const file of p.doc.graph) {
        const subject = subjectOf.get(v.byFile.get(file)!)
        const it = subject && itemOf.get(subject)
        if (it) read.set(it, (read.get(it) ?? 0) + 1)
      }
      const total = [...read.values()].reduce((a, b) => a + b, 0)
      // Toward each subject it reads from, in proportion; so it comes to rest between them.
      for (const [s, n] of read) pulls.push({ source: p, target: s, distance: s.R + AROUND.programme + 8, strength: 0.35 * (n / total) })
      if (!total) pulls.push({ source: p, target: hub, distance: rim, strength: 0.08 })
    }

    const simulation = forceSimulation(items)
      .force("pull", forceLink<Item, Pull>(pulls).distance((l) => l.distance).strength((l) => l.strength))
      .force("apart", forceCollide<Item>((it) => it.R + AROUND[it.kind]).iterations(4))
      .force("spread", forceManyBody<Item>().strength(-50).distanceMax(900))
      // Gathered more firmly from above and below than from the sides: a cluster comes out
      // wider than tall, which is the shape a window has.
      .force("x", forceX<Item>(0).strength(0.012))
      .force("y", forceY<Item>(0).strength(0.16))
      .stop()
    // d3-force starts from a fixed spiral and its own seeded random source, so the same
    // vault always gives the same picture.
    for (let i = 0; i < 700; i++) simulation.tick()

    const rx = Math.max(...items.map((it) => Math.abs(it.x!) + it.R + AROUND[it.kind]))
    const ry = Math.max(...items.map((it) => Math.abs(it.y!) + it.R + AROUND[it.kind]))
    return { inst, hubDoc, items, rx, ry, strays: loose.get(inst) ?? [] }
  })

  // The four clusters in their quarters, as before: IIT and IHV above, IKS and ISLL below.
  const [iit, ihv, iks, isll] = clusters
  const left = Math.max(iit.rx, iks.rx), right = Math.max(ihv.rx, isll.rx)
  const top = Math.max(iit.ry, ihv.ry), bottom = Math.max(iks.ry, isll.ry)
  const centre: Record<Inst, [number, number]> = {
    IIT: [-(BETWEEN / 2 + left), -(BETWEEN / 2 + top)],
    IHV: [BETWEEN / 2 + right, -(BETWEEN / 2 + top)],
    IKS: [-(BETWEEN / 2 + left), BETWEEN / 2 + bottom],
    ISLL: [BETWEEN / 2 + right, BETWEEN / 2 + bottom],
  }
  for (const c of clusters) for (const it of c.items) place.set(it.doc, [centre[c.inst][0] + it.x!, centre[c.inst][1] + it.y!])

  // ── Step 2: each subject's courses around it ──
  const spiral = (courses: Doc[], [cx, cy]: [number, number], first: number) => {
    // Active plans by name, then vilande ones: the grey rim of a flower is its dormant share.
    const ordered = [...courses].sort((a, b) => Number(a.status !== "active") - Number(b.status !== "active") || a.title.localeCompare(b.title, "sv"))
    ordered.forEach((d, i) => {
      const r = SPACING * Math.sqrt(i + first)
      const a = i * GOLDEN_ANGLE
      place.set(d, [cx + r * Math.cos(a), cy + r * Math.sin(a)])
    })
  }
  for (const [subject, courses] of coursesOf) spiral(courses, place.get(subject)!, firstRing(hubRadius(courses.length)))
  for (const c of clusters) if (c.strays.length) spiral(c.strays, place.get(c.hubDoc)!, firstRing(18))

  return {
    /** [x, y, radius, tier, institution index, flags (1 vilande, 2 reads only other institutions' courses), code, name, path, flower radius] */
    n: docs.map((d, i) => {
      const tier = tierOf(d)!
      const [x, y] = place.get(d) ?? [0, 0]
      const inst = d.inst ? INSTITUTIONS.indexOf(d.inst) : -1
      const flags = (d.status !== "active" ? 1 : 0) | (tier === 3 && degree[i] === 0 ? 2 : 0)
      const where = d.inst?.toLowerCase()
      // Hubs open in the browser at that place; plans open as themselves.
      const path =
        tier === 0 ? "/" : tier === 1 ? `/bladdra/#${where}` : tier === 2 ? `/bladdra/#${where}/${d.url.split("/")[2]}` : d.url === `/${tier === 3 ? "program" : "kurs"}/${codeSlug(d.code!)}/` ? "" : d.url
      return [Math.round(x), Math.round(y), Math.round(radius(d, i) * 10) / 10, tier, inst, flags, tier >= 3 ? d.code : "", d.title, path, Math.round(reach.get(d) ?? 0)]
    }),
    l: links,
  }
}
