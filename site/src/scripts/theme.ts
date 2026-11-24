// Appearance: Light, Dark, or Match macOS. The stored choice is applied before first paint
// by the inline script in the layout's <head>; this wires the switch itself.
import { reduceMotion, store } from "./util"

const buttons = [...document.querySelectorAll<HTMLButtonElement>("[data-theme-choice]")]
const mark = (choice: string) => buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.themeChoice === choice)))

mark(store.get("theme") ?? "auto")
for (const b of buttons) {
  b.addEventListener("click", () => {
    const choice = b.dataset.themeChoice!
    const apply = () => {
      if (choice === "auto") delete document.documentElement.dataset.theme
      else document.documentElement.dataset.theme = choice
      // The browser's own chrome follows: the forced colour, or each scheme's own again.
      for (const m of document.querySelectorAll<HTMLMetaElement>('meta[name="theme-color"]')) {
        const own = m.media.includes("dark") ? "dark" : "light"
        m.content = m.dataset[choice === "auto" ? own : choice] ?? m.content
      }
      mark(choice)
      document.dispatchEvent(new CustomEvent("themechange"))
    }
    store.set("theme", choice === "auto" ? null : choice)
    // One cross-fade of the whole page; glass gradients cannot animate property by property.
    if (document.startViewTransition && !reduceMotion()) document.startViewTransition(apply).ready.catch(() => {})
    else apply()
  })
}
