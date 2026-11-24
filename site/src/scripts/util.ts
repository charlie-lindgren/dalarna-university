// Small helpers the page scripts share.

export const reduceMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches

/** True when the element is rendered (not inside something with display: none). */
export const shown = (el: Element | null): el is HTMLElement => !!el && el.getClientRects().length > 0

/** localStorage that never throws: storage can be blocked, and the page must still work. */
export const store = {
  get(key: string): string | null {
    try {
      return localStorage.getItem(key)
    } catch {
      return null
    }
  },
  set(key: string, value: string | null) {
    try {
      if (value === null) localStorage.removeItem(key)
      else localStorage.setItem(key, value)
    } catch {
      // The choice then lasts for this page view only.
    }
  },
}
