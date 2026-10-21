<script setup>
import { computed } from 'vue'

import { theme, toggleTheme } from '../theme'

const label = computed(() => (theme.mode === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'))
</script>

<template>
  <button type="button" class="toggle" :aria-label="label" :title="label" @click="toggleTheme">
    <!-- sun while dark, moon while light: the icon shows what a click switches to -->
    <svg v-if="theme.mode === 'dark'" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
    <svg v-else viewBox="0 0 24 24" aria-hidden="true">
      <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z" />
    </svg>
  </button>
</template>

<style scoped>
.toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  color: inherit;
  background: color-mix(in srgb, currentColor 16%, transparent);
  border: 0;
  border-radius: 50%;
  cursor: pointer;
}

.toggle svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>