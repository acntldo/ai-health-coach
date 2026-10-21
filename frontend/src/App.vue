<script setup>
import { computed, onBeforeUnmount, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import LeafLogo from './components/LeafLogo.vue'
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

    <!-- a tab bar on phones, a slim icon rail on computers -->
    <nav class="tabs" aria-label="Main">
      <LeafLogo class="rail-logo" />
      <router-link to="/" aria-label="Chat" title="Chat">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M5 4.5h14a2.5 2.5 0 0 1 2.5 2.5v8a2.5 2.5 0 0 1-2.5 2.5h-6.5L8 21v-3.5H5A2.5 2.5 0 0 1 2.5 15V7A2.5 2.5 0 0 1 5 4.5Z"
          />
        </svg>
        <span>Chat</span>
      </router-link>
      <router-link to="/history" aria-label="History" title="History">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 7v5l3 2" />
        </svg>
        <span>History</span>
      </router-link>
    </nav>

    <span class="float-toggle"><ThemeToggle /></span>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  max-width: 640px;
  margin: 0 auto;
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
  box-shadow: var(--shadow);
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
.rail-logo,
.screen-title,
.float-toggle {
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

/* computers: a floating icon rail, the screen title and total up top, the toggle in the corner.
   the right-hand column keeps the corner toggle clear of the content */
@media (min-width: 900px) {
  .app {
    display: grid;
    grid-template-columns: 64px minmax(0, 1fr) 52px;
    grid-template-rows: auto minmax(0, 1fr);
    gap: 12px 20px;
    max-width: none;
    margin: 0;
    padding: 16px;
  }

  .top {
    grid-column: 2;
    grid-row: 1;
    align-items: center;
    padding: 4px;
    background: transparent;
    color: var(--ink);
    border-radius: 0;
    box-shadow: none;
  }

  .brand,
  .top-toggle {
    display: none;
  }

  .screen-title {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
  }

  .total {
    display: flex;
    align-items: baseline;
    gap: 8px;
    padding: 8px 18px;
    background: var(--accent);
    color: var(--accent-ink);
    border-radius: 999px;
    box-shadow: var(--shadow);
  }

  .total-number {
    display: inline;
    font-size: 1.5rem;
  }

  .page {
    grid-column: 2;
    grid-row: 2;
  }

  .tabs {
    grid-column: 1;
    grid-row: 1 / -1;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 16px 0;
    background: var(--card);
    border: 0;
    border-radius: 24px;
    box-shadow: var(--shadow);
  }

  .rail-logo {
    display: block;
    width: 36px;
    height: 36px;
    margin-bottom: 14px;
  }

  .tabs a {
    flex: none;
    justify-content: center;
    width: 44px;
    height: 44px;
    padding: 0;
    border-radius: 50%;
  }

  .tabs a span {
    display: none; /* icons only, the names show as tooltips */
  }

  .tabs a:hover {
    background: color-mix(in srgb, currentColor 10%, transparent);
  }

  .tabs a.router-link-exact-active {
    background: var(--accent-soft);
  }

  .float-toggle {
    display: block;
    position: fixed;
    right: 20px;
    bottom: 20px;
    z-index: 10;
    color: var(--ink);
  }

  .float-toggle :deep(.toggle) {
    width: 44px;
    height: 44px;
    background: var(--card);
    box-shadow: var(--shadow);
    -webkit-backdrop-filter: blur(20px);
    backdrop-filter: blur(20px);
  }
}
</style>