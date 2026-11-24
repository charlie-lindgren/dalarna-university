// Behaviour every designed page shares. Small on purpose.

// "/" goes to search from anywhere. On the search page itself, search.ts focuses the field.
document.addEventListener("keydown", (e) => {
  const t = e.target as HTMLElement
  if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return
  if (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable) return
  if (document.querySelector("[data-search]")) return
  const home = document.querySelector<HTMLAnchorElement>('.sitemenu a[data-menu="sok"]')
  if (!home) return
  e.preventDefault()
  location.href = home.href
})
