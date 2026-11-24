// The Excel files the QA pipeline writes beside each analysis page, served next to that page.
import fs from "node:fs"
import type { APIRoute } from "astro"
import { getVault } from "../../../lib/vault"

export function getStaticPaths() {
  return getVault()
    .assets.filter((a) => a.url.startsWith("/kvalitet/") && a.url.endsWith(".xlsx"))
    .map((a) => {
      const [, , inst, name] = a.url.split("/")
      return { params: { inst, file: name.replace(/\.xlsx$/, "") }, props: { src: a.path } }
    })
}

export const GET: APIRoute = ({ props }) =>
  new Response(fs.readFileSync(props.src as string), {
    headers: {
      "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    },
  })
