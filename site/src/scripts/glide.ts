// A jump to a place on the page, as a glide.
// Not the browser's smooth scroll, which eases in (it reads as a delay) and lands hard.
// This moves at once and eases out on a long tail, re-reads the target every frame, and
// hands over to the reader the moment they scroll, touch or type.

const html = document.documentElement

export function glide(target: HTMLElement, done: () => void): () => void {
  const margin = parseFloat(getComputedStyle(target).scrollMarginTop) || 0
  const dest = () => Math.max(0, Math.min(target.getBoundingClientRect().top + scrollY - margin, html.scrollHeight - innerHeight))
  const from = scrollY
  const duration = Math.min(900, Math.max(450, Math.abs(dest() - from) * 0.35))
  const t0 = performance.now()
  const prev = html.style.scrollBehavior
  html.style.scrollBehavior = "auto"
  let raf = 0
  const ac = new AbortController()
  const stop = () => {
    cancelAnimationFrame(raf)
    ac.abort()
    html.style.scrollBehavior = prev
    done()
  }
  // Any input from the reader takes over at once.
  for (const type of ["wheel", "touchstart", "keydown"]) addEventListener(type, stop, { signal: ac.signal, passive: true })
  const step = () => {
    // Read the clock here: a frame's own timestamp can predate the press.
    const p = Math.min(1, Math.max(0, (performance.now() - t0) / duration))
    scrollTo(0, from + (dest() - from) * (1 - Math.pow(1 - p, 5)))
    if (p < 1) raf = requestAnimationFrame(step)
    else stop()
  }
  raf = requestAnimationFrame(step)
  return stop
}
