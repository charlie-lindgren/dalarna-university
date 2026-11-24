// The colour of a heat-table cell: one hue, more is darker (lighter on a dark surface), with
// the number on it set in white or near-black, whichever reads better on that fill.
// Pure maths, so the page can colour the table at build time and the script can recolour it.

type RGB = [number, number, number]
const RAMP: Record<"light" | "dark", [string, string]> = {
  light: ["#E8EBF2", "#0B5BD3"],
  dark: ["#272B36", "#5AA2FF"],
}
const WHITE = "#ffffff"
const NEAR_BLACK = "#0b0d12"

const hex = (h: string): RGB => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255) as RGB
const toLinear = (c: number) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
const toGamma = (c: number) => (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055)

// Mixed in OKLab, where equal steps look equal, so 40 % reads as twice 20 %.
function toLab(rgb: RGB): RGB {
  const [r, g, b] = rgb.map(toLinear)
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
  return [0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s, 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s, 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s]
}
function toLinearRgb([L, a, b]: RGB): RGB {
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
  const m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
  const s = (L - 0.0894841775 * a - 1.291485548 * b) ** 3
  return [4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s]
}
const luminance = (linear: RGB) => 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
const contrast = (a: number, b: number) => (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)
const WHITE_L = 1
const BLACK_L = luminance(hex(NEAR_BLACK).map(toLinear) as RGB)

function step(mode: "light" | "dark", v: number) {
  const [from, to] = RAMP[mode].map((h) => toLab(hex(h)))
  const t = Math.min(1, Math.max(0, v))
  const linear = toLinearRgb(from.map((c, i) => c + (to[i] - c) * t) as RGB).map((c) => Math.min(1, Math.max(0, c))) as RGB
  const fill = "#" + linear.map((c) => Math.round(toGamma(c) * 255).toString(16).padStart(2, "0")).join("")
  const L = luminance(linear)
  return { fill, ink: contrast(L, WHITE_L) >= contrast(L, BLACK_L) ? WHITE : NEAR_BLACK }
}

/** Fill and text colour for a share between 0 and 1, for each theme, as a style string. */
export function heat(v: number): string {
  const light = step("light", v)
  const dark = step("dark", v)
  return `--l:${light.fill};--d:${dark.fill};--li:${light.ink};--di:${dark.ink}`
}

/** The two ends of each ramp, for the legend. */
export const HEAT_ENDS = RAMP
