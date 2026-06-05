// Shared graph color scheme — Högskolan Dalarna
// Imported by both the runtime graph renderer (scripts/graph.inline.ts) and the
// build-time Graph component (Graph.tsx) so the on-screen colors and the legend
// can never drift apart.
//
// Each of the four institutions gets its own hue family. Within an institution,
// four luminance steps mark hierarchy (vivid → pale):
//   moc      — top-level institution MOC node
//   subject  — subject MOC (darkest content tier)
//   program  — utbildningsplan (mid tier)
//   course   — kursplan (lightest leaf)
// Hues are placed ~90° apart for max separation.

export type InstitutionTiers = {
  moc: string
  subject: string
  program: string
  course: string
}

export const INSTITUTION_PALETTE: Record<string, InstitutionTiers> = {
  IIT: { moc: "#0d57c2", subject: "#3b7fd9", program: "#7eaae6", course: "#b6cff0" }, // royal blue (~215°)
  IHV: { moc: "#0e8c5a", subject: "#2cb077", program: "#6ed5a3", course: "#a7e8c8" }, // emerald   (~150°)
  IKS: { moc: "#d65a1c", subject: "#ef8534", program: "#f5b073", course: "#f9cfa8" }, // orange    (~25°)
  ISLL: { moc: "#a3268f", subject: "#cd4cbf", program: "#e08bd6", course: "#efbce9" }, // magenta  (~315°)
}

export const INSTITUTIONS = ["IIT", "IHV", "IKS", "ISLL"] as const

export const STRUCTURAL_GOLD = "#d4a843" // Dashboard, Analys MOC — cross-institution structure
export const ANALYS_PURPLE = "#7e3aed" // Analys leaf pages — vivid violet in the hue gap between IIT and ISLL
export const EJ_AKTIV_RED = "#c0392b" // not-running courses
export const VILANDE_RED = "#c0392b" // vilande courses
export const TVARFAK_AMBER = "#f59e0b" // cross-faculty programmes that legitimately float

// Human-readable names for the institutions, used in the legend.
export const INSTITUTION_LABELS: Record<(typeof INSTITUTIONS)[number], string> = {
  IIT: "IIT — Information & Teknik",
  IHV: "IHV — Hälsa & Välfärd",
  IKS: "IKS — Kultur & Samhälle",
  ISLL: "ISLL — Språk, Litteratur & Lärande",
}

// Compact legend entries for the cross-cutting (non-institutional) categories.
// Struktur (gold) and Tvärfakultet (amber) are intentionally omitted — they add
// noise without helping the typical visitor read the graph.
export const SPECIAL_LEGEND: { color: string; label: string }[] = [
  { color: ANALYS_PURPLE, label: "Analys" },
  { color: EJ_AKTIV_RED, label: "Ej aktiv / Vilande" },
]
