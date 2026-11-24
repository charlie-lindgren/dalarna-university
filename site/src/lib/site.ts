// Site-wide constants and the one place that knows about the base path.

/** Base path without a trailing slash: "" at a domain root, "/dalarna-university" on Pages. */
export const base = import.meta.env.BASE_URL.replace(/\/$/, "")

/** Turn a site path ("/kurs/GDT2JM/") into an href that works under the base path. */
export function link(url: string): string {
  return base + url
}

export const SITE_NAME = "Högskolan Dalarna"
