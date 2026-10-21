<script setup>
import { onBeforeUnmount, onMounted } from 'vue'

import { refreshTodayTotal, store } from './store'

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
      <div class="top-inner">
        <span class="brand">AI Health Coach</span>
        <div class="total" aria-live="polite">
          <span class="total-number">{{ store.todayTotal }}</span>
          <span class="total-label">kcal today</span>
        </div>
      </div>
    </header>

    <main class="page">
      <router-view />
    </main>

    <nav class="tabs" aria-label="Main">
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
  padding: calc(12px + env(safe-area-inset-top)) 20px 16px;
  background: var(--accent);
  color: var(--accent-ink);
  border-radius: 0 0 22px 22px;
}

.top-inner {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.brand {
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  opacity: 0.95;
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

.tabs svg {
  width: 26px;
  height: 26px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* on a computer the app sits in a rounded window in the middle of the screen */
@media (min-width: 700px) {
  .app {
    height: min(calc(100dvh - 48px), 880px);
    margin: 24px auto;
    overflow: hidden;
    border: 1px solid var(--line);
    border-radius: 28px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.14);
  }
}
</style>