// The graph's colours. The values are the ones the Quartz graph uses
// (quartz/components/graphColors.ts), so the new graph wears the same hues.
//
// Each institution has its own hue, about a quarter turn of the colour wheel from the next.
// Within an institution four steps mark the hierarchy, from vivid to pale:
//   moc      the institution itself
//   subject  a subject
//   program  a programme plan
//   course   a course plan

export interface InstitutionTiers {
  moc: string
  subject: string
  program: string
  course: string
}

export const INSTITUTIONS = ["IIT", "IHV", "IKS", "ISLL"] as const

export const INSTITUTION_PALETTE: Record<(typeof INSTITUTIONS)[number], InstitutionTiers> = {
  IIT: { moc: "#0d57c2", subject: "#3b7fd9", program: "#7eaae6", course: "#b6cff0" }, // royal blue
  IHV: { moc: "#0e8c5a", subject: "#2cb077", program: "#6ed5a3", course: "#a7e8c8" }, // emerald
  IKS: { moc: "#d65a1c", subject: "#ef8534", program: "#f5b073", course: "#f9cfa8" }, // orange
  ISLL: { moc: "#a3268f", subject: "#cd4cbf", program: "#e08bd6", course: "#efbce9" }, // magenta
}

/** The node in the middle, which belongs to no institution. */
export const STRUCTURAL_GOLD = "#d4a843"
