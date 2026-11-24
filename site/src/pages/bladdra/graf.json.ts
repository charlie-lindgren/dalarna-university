// The graph: every node with its place, and the links between them.
import type { APIRoute } from "astro"
import { graphData } from "../../lib/graph"

export const GET: APIRoute = () => new Response(JSON.stringify(graphData()), { headers: { "Content-Type": "application/json" } })
