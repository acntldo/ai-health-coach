<script setup>
import { computed } from 'vue'

const props = defineProps({ level: { type: String, required: true } })

// words as well as color, so the meaning doesn't depend on seeing the color
const labels = { high: 'High confidence', medium: 'Medium confidence', low: 'Rough estimate' }
const label = computed(() => labels[props.level] ?? props.level)
</script>

<template>
  <span class="badge" :class="level">{{ label }}</span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.high {
  background: var(--high-bg);
  color: var(--high-ink);
}

.medium {
  background: var(--medium-bg);
  color: var(--medium-ink);
}

.low {
  background: var(--low-bg);
  color: var(--low-ink);
}
</style>