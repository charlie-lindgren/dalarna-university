// The English versions of the analysis notes, against the Swedish in the vault.
//
//   node scripts/translations.ts                 the state of every section
//   node scripts/translations.ts --stamp         fingerprint the sections that have none yet
//   node scripts/translations.ts --stamp introfras
//                                                re-fingerprint every section of one file,
//                                                after its English has been brought up to date
//
// Also lists check names and problem labels in the vault that have no English yet.
// Run from site/.
import fs from "node:fs"
import { getVault, INSTITUTIONS } from "../src/lib/vault.ts"
import { analysisNotes, fingerprint, genericIntro, sections, translationFiles, INTRO } from "../src/lib/analysis-en.ts"
import { CHECK_EN, PROBLEM_EN } from "../src/lib/checks.ts"

const args = process.argv.slice(2)
const stamp = args.includes("--stamp")
const only = args.find((a) => !a.startsWith("--"))

const notes = analysisNotes()
const hub = getVault().docs.find((d) => d.kind === "analysisHub" && d.inst === INSTITUTIONS[0])
let problems = 0

for (const [name, file] of translationFiles()) {
  let text = fs.readFileSync(file.file, "utf8")
  const lines: string[] = []
  for (const t of file.sections) {
    let sv: string | undefined
    if (file.check === null && t.heading === INTRO && hub) sv = genericIntro(sections(hub.body)[0].body, INSTITUTIONS[0])
    else if (file.check) sv = sections(notes.get(file.check)?.body ?? "").find((s) => s.heading === t.sv)?.body
    if (sv === undefined) {
      lines.push(`  ${t.heading}: no Swedish section "${t.sv}" in the vault`)
      problems++
      continue
    }
    const now = fingerprint(sv)
    const restamp = stamp && (t.stamp === null || only === name)
    if (restamp) {
      // Rewrite this section's marker in place: the first marker after its heading.
      const at = text.indexOf(`## ${t.heading}`)
      text = text.slice(0, at) + text.slice(at).replace(/<!--\s*sv(?:\s+[0-9a-f]{8})?\s*-->/, `<!-- sv ${now} -->`)
      lines.push(`  ${t.heading}: stamped ${now}`)
    } else if (t.stamp === now) lines.push(`  ${t.heading}: up to date`)
    else {
      lines.push(`  ${t.heading}: ${t.stamp ? "OUT OF DATE, the Swedish has changed" : "no fingerprint yet (--stamp)"}`)
      problems++
    }
  }
  if (stamp) fs.writeFileSync(file.file, text)
  console.log(`${name}${file.check ? ` (${file.check})` : ""}\n${lines.join("\n")}`)
}

// Checks in the vault with no translation file at all.
const translated = new Set([...translationFiles().values()].map((f) => f.check))
for (const check of notes.keys()) if (!translated.has(check)) (console.log(`${check}: no English file`), problems++)

// Names the site shows that have no English.
const areas = new Set<string>(), labels = new Set<string>()
for (const d of getVault().docs) for (const f of d.findings) (areas.add(f.area), labels.add(f.problem))
for (const a of [...areas, ...notes.keys()]) if (!CHECK_EN[a]) (console.log(`Check name without English: ${a}`), problems++)
for (const p of labels) if (!PROBLEM_EN[p]) (console.log(`Problem label without English: ${p}`), problems++)

console.log(problems ? `\n${problems} to see to.` : "\nEverything has an up-to-date English version.")
