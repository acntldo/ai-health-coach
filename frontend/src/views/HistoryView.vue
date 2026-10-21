<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { deleteEntry, getDay, getDays } from '../api'
import ConfidenceBadge from '../components/ConfidenceBadge.vue'
import { refreshTodayTotal } from '../store'
import { formatDay, shiftDay, todayString } from '../utils/dates'

// read when the screen opens. the screen is rebuilt every time the tab is visited
const today = todayString()
const selected = ref(today)
const entries = ref([])
const total = ref(0)
const pastDays = ref([])
const daysLoaded = ref(false)
const loading = ref(true)
const error = ref('')
const confirmingId = ref(null)
let confirmTimer = null

const isToday = computed(() => selected.value === today)
// the back arrow stops at the earliest day that has food
const oldest = computed(() =>
  pastDays.value.length ? pastDays.value[pastDays.value.length - 1].day : today,
)
const canGoBack = computed(() => !daysLoaded.value || selected.value > oldest.value)

async function loadDay() {
  const day = selected.value
  loading.value = true
  error.value = ''
  try {
    const data = await getDay(day)
    // ignore the answer if the user already moved to another day
    if (day !== selected.value) return
    entries.value = data.entries
    total.value = data.total
  } catch (err) {
    if (day === selected.value) error.value = err.message
  } finally {
    if (day === selected.value) loading.value = false
  }
}

async function loadPastDays() {
  try {
    pastDays.value = await getDays()
    daysLoaded.value = true
  } catch {
    // the list is a shortcut, the arrows still work without it
  }
}

function go(offset) {
  if (offset < 0 && !canGoBack.value) return
  if (offset > 0 && isToday.value) return // no future days
  selected.value = shiftDay(selected.value, offset)
}

function cancelConfirm() {
  clearTimeout(confirmTimer)
  confirmingId.value = null
}

async function onDelete(entry) {
  if (confirmingId.value !== entry.id) {
    // the first tap asks for confirmation, and it expires after a few seconds
    cancelConfirm()
    confirmingId.value = entry.id
    confirmTimer = setTimeout(() => (confirmingId.value = null), 3000)
    return
  }
  cancelConfirm()
  try {
    await deleteEntry(entry.id)
  } catch (err) {
    error.value = err.message
    return
  }
  await Promise.all([loadDay(), loadPastDays()])
  refreshTodayTotal() // keeps the header right if today's food changed
}

watch(selected, () => {
  cancelConfirm()
  entries.value = [] // so the previous day's food doesn't show under the new date
  total.value = 0
  loadDay()
})

onMounted(() => {
  loadDay()
  loadPastDays()
})
onBeforeUnmount(cancelConfirm)
</script>

<template>
  <section class="history">
    <div class="day-nav">
      <button type="button" aria-label="Previous day" :disabled="!canGoBack" @click="go(-1)">‹</button>
      <div class="day-title">
        <strong>{{ isToday ? 'Today' : formatDay(selected) }}</strong>
        <span v-if="isToday">{{ formatDay(selected) }}</span>
      </div>
      <button type="button" aria-label="Next day" :disabled="isToday" @click="go(1)">›</button>
    </div>

    <div class="day-total"><span class="number">{{ total }}</span> kcal</div>

    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <p v-else-if="loading && !entries.length" class="notice">Loading…</p>
    <p v-else-if="!entries.length" class="notice">Nothing logged for this day.</p>
    <ul v-else class="entries">
      <li v-for="e in entries" :key="e.id">
        <div class="entry-main">
          <span class="entry-name">{{ e.name }}</span>
          <span class="entry-kcal">{{ e.calories }} kcal</span>
        </div>
        <div class="entry-meta">
          <span v-if="e.serving">
            {{ e.serving }}<template v-if="e.grams"> · {{ Math.round(e.grams) }} g</template>
          </span>
          <ConfidenceBadge :level="e.confidence" />
        </div>
        <p v-if="e.usda_description" class="entry-source">USDA: {{ e.usda_description }}</p>
        <button
          type="button"
          class="delete"
          :class="{ confirm: confirmingId === e.id }"
          @click="onDelete(e)"
        >
          {{ confirmingId === e.id ? 'Tap again to delete' : 'Delete' }}
        </button>
      </li>
    </ul>

    <div v-if="pastDays.length" class="past">
      <h2>All days</h2>
      <ul>
        <li v-for="d in pastDays" :key="d.day">
          <button type="button" :class="{ active: d.day === selected }" @click="selected = d.day">
            <span>{{ d.day === today ? 'Today' : formatDay(d.day) }}</span>
            <span>{{ d.total }} kcal</span>
          </button>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.history {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
}

.day-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.day-nav button {
  width: 44px;
  height: 44px;
  font-size: 1.5rem;
  color: var(--accent);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 50%;
  cursor: pointer;
}

.day-nav button:disabled {
  opacity: 0.35;
  cursor: default;
}

.day-title {
  text-align: center;
  line-height: 1.3;
}

.day-title span {
  display: block;
  font-size: 0.85rem;
  color: var(--muted);
}

.day-total {
  margin: 20px 0;
  text-align: center;
  color: var(--muted);
}

.day-total .number {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--accent);
}

.notice {
  margin: 0;
  padding: 24px 0;
  text-align: center;
  color: var(--muted);
}

.notice.error {
  color: var(--danger);
}

.entries,
.past ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.entries {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
}

.entries li {
  padding: 12px 14px;
}

.entries li + li {
  border-top: 1px solid var(--line);
}

.entry-main {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.entry-name {
  font-weight: 600;
  overflow-wrap: anywhere;
}

.entry-kcal {
  white-space: nowrap;
}

.entry-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
  font-size: 0.85rem;
  color: var(--muted);
}

.entry-source {
  margin: 4px 0 0;
  font-size: 0.8rem;
  color: var(--muted);
  overflow-wrap: anywhere;
}

.delete {
  margin-top: 8px;
  padding: 6px 12px;
  font-size: 0.85rem;
  color: var(--muted);
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 8px;
  cursor: pointer;
}

.delete.confirm {
  color: var(--danger);
  border-color: var(--danger);
  font-weight: 600;
}

.past {
  margin-top: 28px;
}

.past h2 {
  margin: 0 0 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.past li + li {
  margin-top: 6px;
}

.past button {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: 10px 14px;
  color: var(--ink);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  cursor: pointer;
}

.past button.active {
  background: var(--accent-soft);
  border-color: var(--accent);
}
</style>