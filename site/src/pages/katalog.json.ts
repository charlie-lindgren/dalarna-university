// The catalogue the search field and the browser fetch: every plan's code, names and credits.
import type { APIRoute } from "astro"
import { catalogue } from "../lib/site-data"

export const GET: APIRoute = () => new Response(JSON.stringify(catalogue()), { headers: { "Content-Type": "application/json" } })
