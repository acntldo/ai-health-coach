<script setup>
import { computed, onBeforeUnmount, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import ThemeToggle from './components/ThemeToggle.vue'
import { refreshTodayTotal, store } from './store'

const route = useRoute()
const screenTitle = computed(() => (route.path === '/history' ? 'History' : 'Chat'))

// refresh when the tab comes back into view, so the total is right after midnight too
function onVisible() {
  if (document.visibilityState === 'visible') refreshTodayTotal()
}

onMounted(() => {
  refreshTodayTotal()
  document.addEventListener('visibilitychange', onVisible)
})
onBeforeUnmount(() => document.removeEventListener('visibilitychange', onVisible))
</script>

<template>
  <div class="app">
    <header class="top">
      <div class="top-left">
        <span class="brand">AI Health Coach</span>
        <span class="screen-title">{{ screenTitle }}</span>
        <span class="top-toggle"><ThemeToggle /></span>
      </div>
      <div class="total" aria-live="polite">
        <span class="total-number">{{ store.todayTotal }}</span>
        <span class="total-label">kcal today</span>
      </div>
    </header>

    <main class="page">
      <router-view />
    </main>

    <!-- a tab bar on phones, a sidebar on computers -->
    <nav class="tabs" aria-label="Main">
      <div class="side-brand">
        <svg class="logo" viewBox="0 0 64 64" aria-hidden="true">
          <rect width="64" height="64" rx="14" fill="#2f6f4f" />
          <path d="M18 46C18 30 28 18 46 18C46 36 36 46 18 46Z" fill="#fff" />
          <path d="M18 46L34 30" stroke="#2f6f4f" stroke-width="3" stroke-linecap="round" fill="none" />
        </svg>
        <span>AI Health Coach</span>
      </div>
      <router-link to="/">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M5 4.5h14a2.5 2.5 0 0 1 2.5 2.5v8a2.5 2.5 0 0 1-2.5 2.5h-6.5L8 21v-3.5H5A2.5 2.5 0 0 1 2.5 15V7A2.5 2.5 0 0 1 5 4.5Z"
          />
        </svg>
        <span>Chat</span>
      </router-link>
      <router-link to="/history">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7v5l3 2" />
        </svg>
        <span>History</span>
      </router-link>
      <span class="side-toggle"><ThemeToggle /></span>
    </nav>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  max-width: 640px;
  margin: 0 auto;
  background: var(--bg);
}

.top {
  flex: none;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: calc(12px + env(safe-area-inset-top)) 20px 16px;
  background: var(--accent);
  color: var(--accent-ink);
  border-radius: 0 0 22px 22px;
}

.top-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand {
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}

/* these belong to the computer layout */
.screen-title,
.side-brand,
.side-toggle {
  display: none;
}

.total {
  text-align: right;
  line-height: 1.05;
}

.total-number {
  display: block;
  font-size: 2.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

.total-label {
  font-size: 0.75rem;
  opacity: 0.85;
}

.page {
  flex: 1;
  min-height: 0; /* lets a screen scroll inside the page instead of growing it */
  width: 100%;
}

/* frosted bar like the iphone tab bar */
.tabs {
  flex: none;
  display: flex;
  padding-bottom: env(safe-area-inset-bottom);
  background: var(--bar-bg);
  border-top: 0.5px solid var(--line);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  backdrop-filter: saturate(180%) blur(20px);
}

.tabs a {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 8px 0 6px;
  color: var(--muted);
  font-size: 0.6875rem;
  font-weight: 500;
  text-decoration: none;
}

.tabs a.router-link-exact-active {
  color: var(--accent-text);
}

.tabs a svg {
  width: 26px;
  height: 26px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* computers: a sidebar on the left, the total in a bar across the top of the content */
@media (min-width: 900px) {
  .app {
    display: grid;
    grid-template-columns: 248px minmax(0, 1fr);
    grid-template-rows: auto minmax(0, 1fr);
    max-width: none;
    margin: 0;
  }

  .top {
    grid-column: 2;
    grid-row: 1;
    align-items: center;
    padding: 14px 28px;
    border-radius: 0;
  }

  .brand,
  .top-toggle {
    display: none;
  }

  .screen-title {
    display: block;
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -0.02em;
  }

  .total {
    display: flex;
    align-items: baseline;
    gap: 8px;
  }

  .total-number {
    font-size: 1.75rem;
  }

  .page {
    grid-column: 2;
    grid-row: 2;
  }

  .tabs {
    grid-column: 1;
    grid-row: 1 / -1;
    flex-direction: column;
    gap: 2px;
    padding: 20px 12px 16px;
    border-top: 0;
    border-right: 0.5px solid var(--line);
  }

  .side-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 12px 20px;
    font-weight: 600;
    letter-spacing: -0.01em;
  }

  .logo {
    width: 30px;
    height: 30px;
    flex: none;
  }

  .tabs a {
    flex-direction: row;
    justify-content: flex-start;
    gap: 10px;
    padding: 9px 12px;
    border-radius: 9px;
    font-size: 0.95rem;
  }

  .tabs a:hover {
    background: color-mix(in srgb, currentColor 8%, transparent);
  }

  .tabs a.router-link-exact-active {
    background: var(--accent-soft);
  }

  .tabs a svg {
    width: 22px;
    height: 22px;
  }

  .side-toggle {
    display: block;
    margin: auto 0 0 12px;
    color: var(--muted);
  }
}
</style>