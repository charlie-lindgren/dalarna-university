// Stage report: what the vault index contains and which links do not resolve.
// Run from site/:  node scripts/report.ts
import { getVault } from "../src/lib/vault.ts"

const v = getVault()
const count = <T,>(items: T[], key: (item: T) => string) => {
  const m = new Map<string, number>()
  for (const item of items) m.set(key(item), (m.get(key(item)) ?? 0) + 1)
  return [...m].sort((a, b) => b[1] - a[1])
}

console.log(`Published notes: ${v.docs.length}   drafts skipped: ${v.drafts.length}   assets: ${v.assets.length}`)
console.log(`Last scrape: ${v.scrapeDate}`)
console.log("\nBy kind")
for (const [k, n] of count(v.docs, (d) => d.kind)) console.log(`  ${String(n).padStart(5)}  ${k}`)

const plans = v.docs.filter((d) => d.plan)
console.log("\nPlans by status")
for (const [k, n] of count(plans, (d) => `${d.kind} / ${d.status}`)) console.log(`  ${String(n).padStart(5)}  ${k}`)

const noFacts = plans.filter((d) => d.plan!.facts.length === 0)
const extra = plans.filter((d) => d.plan!.leadExtra !== null)
console.log(`\nPlans with facts parsed from the lead block: ${plans.length - noFacts.length} of ${plans.length}`)
for (const d of noFacts.slice(0, 10)) console.log(`  no facts: ${d.file}`)
console.log(`Plans with other text in the lead block (kept as markdown): ${extra.length}`)
for (const [k, n] of count(extra, (d) => d.plan!.leadExtra!.split("\n")[0].slice(0, 60))) console.log(`  ${String(n).padStart(5)}  ${k}`)
for (const [k, n] of count(plans.flatMap((d) => d.plan!.facts), (f) => f.label)) console.log(`  ${String(n).padStart(5)}  fact: ${k}`)
console.log(`Courses with an English version: ${plans.filter((d) => d.kind === "course" && d.plan!.en).length}`)

const findings = plans.flatMap((d) => d.findings)
console.log(`\nQuality findings: ${findings.length} in ${plans.filter((d) => d.findings.length).length} plans`)
for (const [k, n] of count(findings, (f) => f.area)) console.log(`  ${String(n).padStart(5)}  ${k}`)

const suffixed = v.docs.filter((d) => /-(iit|ihv|iks|isll)\/$/.test(d.url) && d.kind !== "analysis")
console.log(`\nPages that carry the institution in the URL (same name under two institutions): ${suffixed.length}`)
for (const d of suffixed) console.log(`  ${d.url}   ${d.file}`)

const links = v.docs.reduce((n, d) => n + d.links.length, 0)
console.log(`\nResolved links between notes: ${links}`)
for (const reason of ["unresolved", "draft"] as const) {
  const issues = v.issues.filter((i) => i.reason === reason)
  console.log(`Links to ${reason === "draft" ? "unpublished drafts" : "nothing"}: ${issues.length}`)
  for (const [k, n] of count(issues, (i) => i.target).slice(0, 15)) console.log(`  ${String(n).padStart(5)}  ${k}`)
}
const orphans = v.docs.filter((d) => d.backlinks.length === 0 && d.kind !== "home")
console.log(`\nNotes nothing links to: ${orphans.length}`)
for (const d of orphans.slice(0, 15)) console.log(`  ${d.file}`)
