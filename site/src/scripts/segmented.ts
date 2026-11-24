// A segmented control with a sliding thumb (.seg in base.css). The thumb slides for a
// pointer press and jumps for a keyboard press.

export function segmented(seg: HTMLElement, onChange: (value: string) => void) {
  const thumb = seg.querySelector<HTMLElement>(".thumb")!
  const buttons = [...seg.querySelectorAll<HTMLButtonElement>("button")]
  const place = () => {
    const on = buttons.find((b) => b.getAttribute("aria-pressed") === "true")
    if (!on || !on.offsetWidth) return
    thumb.style.width = `${on.offsetWidth}px`
    thumb.style.transform = `translateX(${on.offsetLeft}px)`
  }
  /** Set the value from outside (no callback). The thumb jumps: nothing here was pressed. */
  const set = (value: string, slide = false) => {
    if (buttons.find((b) => b.getAttribute("aria-pressed") === "true")?.dataset.value === value) return
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.value === value)))
    if (!slide) seg.classList.remove("ready")
    place()
    if (!slide) requestAnimationFrame(() => requestAnimationFrame(() => seg.classList.add("ready")))
  }
  for (const b of buttons)
    b.addEventListener("click", (e) => {
      if (b.getAttribute("aria-pressed") === "true") return
      set(b.dataset.value!, e.detail !== 0)
      onChange(b.dataset.value!)
    })
  addEventListener("resize", place)
  place()
  requestAnimationFrame(() => requestAnimationFrame(() => seg.classList.add("ready")))
  return { set }
}
