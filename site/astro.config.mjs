// @ts-check
import { defineConfig } from "astro/config"

// SITE_BASE lets the same build serve from a sub-path: "/dalarna-university" on GitHub Pages,
// "/dalarna-university/next" for the preview beside the live Quartz site.
export default defineConfig({
  site: "https://charlie-lindgren.github.io",
  base: process.env.SITE_BASE ?? "/dalarna-university",
  trailingSlash: "always",
  build: { format: "directory" },
  // Astro's own toolbar only shows in local preview, where it sat on top of the page.
  devToolbar: { enabled: false },
})
