import { reactive } from 'vue'

const KEY = 'theme'
const systemDark = window.matchMedia('(prefers-color-scheme: dark)')

function saved() {
  try {
    const value = localStorage.getItem(KEY)
    return value === 'light' || value === 'dark' ? value : null
  } catch {
    return null // storage can be blocked in private browsing
  }
}

export const theme = reactive({ mode: saved() || (systemDark.matches ? 'dark' : 'light') })

function apply(mode) {
  theme.mode = mode
  document.documentElement.dataset.theme = mode
}

// until a choice is saved, the device setting decides
systemDark.addEventListener('change', (event) => {
  if (!saved()) apply(event.matches ? 'dark' : 'light')
})

export function initTheme() {
  apply(theme.mode)
}

export function toggleTheme() {
  const next = theme.mode === 'dark' ? 'light' : 'dark'
  apply(next)
  try {
    localStorage.setItem(KEY, next)
  } catch {
    // the choice just won't be remembered
  }
}