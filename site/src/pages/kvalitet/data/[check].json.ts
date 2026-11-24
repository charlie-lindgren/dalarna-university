// One check's notes, with the plans they sit in. The dashboard fetches this when the reader
// opens that check, so the page itself stays light.
import type { APIRoute } from "astro"
import { checkDetail, qualityOverview } from "../../../lib/quality"

export function getStaticPaths() {
  return qualityOverview().checks.map((c) => ({ params: { check: c.slug } }))
}

export const GET: APIRoute = async ({ params }) =>
  new Response(JSON.stringify(await checkDetail(params.check!)), { headers: { "Content-Type": "application/json" } })
