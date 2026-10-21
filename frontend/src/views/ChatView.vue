<script setup>
import { nextTick, onMounted, ref } from 'vue'

import { getMessages, sendMessage } from '../api'
import ConfidenceBadge from '../components/ConfidenceBadge.vue'
import LeafLogo from '../components/LeafLogo.vue'
import { store } from '../store'
import { formatTime, parseServerTime, todayString } from '../utils/dates'

const messages = ref([]) // { key, role, text, entries, time }
const input = ref('')
const sending = ref(false)
const loading = ref(true)
const showGreeting = ref(false)
const error = ref('')
const listEl = ref(null)
let nextKey = 0

function addMessage(role, text, entries = [], time = new Date()) {
  messages.value.push({ key: nextKey++, role, text, entries, time })
}

async function scrollToBottom() {
  await nextTick()
  if (listEl.value) listEl.value.scrollTop = listEl.value.scrollHeight
}

onMounted(async () => {
  try {
    for (const m of await getMessages()) addMessage(m.role, m.text, [], parseServerTime(m.created_at))
  } catch {
    error.value = "Couldn't load your earlier conversation."
  } finally {
    // the greeting only shows when there is no saved conversation
    showGreeting.value = messages.value.length === 0
    loading.value = false
    scrollToBottom()
  }
})

async function send() {
  const text = input.value.trim()
  if (!text || sending.value) return

  error.value = ''
  sending.value = true
  const key = nextKey
  addMessage('user', text)
  input.value = ''
  scrollToBottom()

  try {
    // the date is read now, so a tab left open past midnight still logs to the right day
    const data = await sendMessage(text, todayString())
    addMessage('coach', data.reply, data.entries)
    store.todayTotal = data.day_total
  } catch (err) {
    // nothing was saved, so the bubble goes away and the text returns to the box
    messages.value = messages.value.filter((m) => m.key !== key)
    input.value = text
    error.value = err.message
  } finally {
    sending.value = false
    scrollToBottom()
  }
}
</script>

<template>
  <section class="chat">
    <div ref="listEl" class="messages" role="log" aria-live="polite">
      <p v-if="loading" class="hint">Loading…</p>

      <div v-if="showGreeting" class="row coach">
        <LeafLogo class="avatar" />
        <div class="col">
          <div class="bubble coach"><p>Hi! Tell me what you ate and I'll estimate the calories.</p></div>
        </div>
      </div>

      <div v-for="m in messages" :key="m.key" class="row" :class="m.role">
        <LeafLogo v-if="m.role === 'coach'" class="avatar" />
        <div class="col">
          <div class="bubble" :class="m.role">
            <p>{{ m.text }}</p>
            <ul v-if="m.entries.length" class="foods">
              <li v-for="e in m.entries" :key="e.id">
                <div class="food-main">
                  <span class="food-name">{{ e.name }}</span>
                  <span class="food-kcal">{{ e.calories }} kcal</span>
                </div>
                <div class="food-meta">
                  <span v-if="e.serving">{{ e.serving }}</span>
                  <ConfidenceBadge :level="e.confidence" />
                </div>
              </li>
            </ul>
          </div>
          <span class="time">{{ formatTime(m.time) }}</span>
        </div>
      </div>

      <div v-if="sending" class="row coach">
        <LeafLogo class="avatar" />
        <div class="col">
          <div class="bubble coach typing"><p>Thinking…</p></div>
        </div>
      </div>
    </div>

    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <form class="composer" @submit.prevent="send">
      <input
        v-model="input"
        type="text"
        placeholder="e.g. I had rice and chicken adobo"
        maxlength="500"
        aria-label="Message"
        autocomplete="off"
      />
      <button type="submit" class="send" :disabled="sending || !input.trim()" aria-label="Send">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7" /></svg>
      </button>
    </form>
    <p class="note">
      Estimates only, not medical advice. Messages are processed by Google Gemini, so please
      don't share personal information.
    </p>
  </section>
</template>

<style scoped>
.chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  max-width: 760px; /* a readable column on wide screens */
  margin: 0 auto;
}

.messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.hint {
  margin: 0;
  color: var(--muted);
  text-align: center;
}

.row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  max-width: 88%;
}

.row.user {
  align-self: flex-end;
}

.row.coach {
  align-self: flex-start;
}

.avatar {
  flex: none;
  width: 30px;
  height: 30px;
}

.col {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.row.user .col {
  align-items: flex-end;
}

.bubble {
  padding: 10px 16px;
  border-radius: 20px;
}

.bubble p {
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.bubble.user {
  background: var(--accent);
  color: var(--accent-ink);
  border-bottom-right-radius: 6px;
}

.bubble.coach {
  background: var(--card);
  box-shadow: var(--shadow);
  border-top-left-radius: 6px;
  -webkit-backdrop-filter: blur(16px);
  backdrop-filter: blur(16px);
}

.typing {
  color: var(--muted);
}

.time {
  padding: 0 6px;
  font-size: 0.6875rem;
  color: var(--muted);
}

.foods {
  list-style: none;
  margin: 10px 0 0;
  padding: 0;
}

.foods li {
  padding: 8px 0;
  border-top: 1px solid var(--line);
}

.food-main {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.food-name {
  font-weight: 600;
  overflow-wrap: anywhere;
}

.food-kcal {
  white-space: nowrap;
}

.food-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
  font-size: 0.85rem;
  color: var(--muted);
}

.error {
  margin: 0;
  padding: 8px 20px;
  font-size: 0.9rem;
  color: var(--danger);
}

/* a floating card, the ring shows when the box has focus */
.composer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 16px;
  padding: 6px 6px 6px 18px;
  background: var(--card);
  border-radius: 26px;
  box-shadow: var(--shadow);
  -webkit-backdrop-filter: blur(20px);
  backdrop-filter: blur(20px);
}

.composer:focus-within {
  box-shadow:
    var(--shadow),
    0 0 0 2px var(--accent);
}

/* 1rem keeps iphones from zooming in when the box is tapped */
.composer input {
  flex: 1;
  min-width: 0;
  padding: 10px 0;
  font-size: 1rem;
  color: var(--ink);
  background: transparent;
  border: 0;
  outline: 0;
}

.send {
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  color: var(--accent-ink);
  background: var(--accent);
  border: 0;
  border-radius: 50%;
  cursor: pointer;
}

.send:disabled {
  opacity: 0.35;
  cursor: default;
}

.send svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2.4;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.note {
  margin: 0;
  padding: 8px 20px 12px;
  font-size: 0.75rem;
  color: var(--muted);
  text-align: center;
}
</style>