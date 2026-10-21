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

    <nav class="tabs" aria-label="Main">
      <router-link to="/">Chat</router-link>
      <router-link to="/history">History</router-link>
    </nav>

    <main class="page">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100dvh;
}

.top {
  flex: none;
  padding: 12px 16px;
  background: var(--accent);
  color: var(--accent-ink);
}

.top-inner {
  max-width: 640px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  font-weight: 600;
}

.total {
  text-align: right;
  line-height: 1.1;
}

.total-number {
  display: block;
  font-size: 1.75rem;
  font-weight: 700;
}

.total-label {
  font-size: 0.75rem;
  opacity: 0.85;
}

.tabs {
  flex: none;
  display: flex;
  background: var(--surface);
  border-bottom: 1px solid var(--line);
}

.tabs a {
  flex: 1;
  padding: 12px;
  text-align: center;
  color: var(--muted);
  text-decoration: none;
  border-bottom: 3px solid transparent;
}

.tabs a.router-link-exact-active {
  color: var(--ink);
  font-weight: 600;
  border-bottom-color: var(--accent);
}

.page {
  flex: 1;
  min-height: 0; /* lets a screen scroll inside the page instead of growing it */
  width: 100%;
  max-width: 640px;
  margin: 0 auto;
}
</style>