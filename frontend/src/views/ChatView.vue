<script setup>
import { nextTick, onMounted, ref } from 'vue'

import { getMessages, sendMessage } from '../api'
import ConfidenceBadge from '../components/ConfidenceBadge.vue'
import { store } from '../store'
import { todayString } from '../utils/dates'

const messages = ref([]) // { key, role, text, entries }
const input = ref('')
const sending = ref(false)
const loading = ref(true)
const showGreeting = ref(false)
const error = ref('')
const listEl = ref(null)
let nextKey = 0

function addMessage(role, text, entries = []) {
  messages.value.push({ key: nextKey++, role, text, entries })
}

async function scrollToBottom() {
  await nextTick()
  if (listEl.value) listEl.value.scrollTop = listEl.value.scrollHeight
}

onMounted(async () => {
  try {
    for (const m of await getMessages()) addMessage(m.role, m.text)
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

      <div v-if="showGreeting" class="bubble coach">
        <p>Hi! Tell me what you ate and I'll estimate the calories.</p>
      </div>

      <div v-for="m in messages" :key="m.key" class="bubble" :class="m.role">
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

      <div v-if="sending" class="bubble coach typing"><p>Thinking…</p></div>
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
      <button type="submit" :disabled="sending || !input.trim()">Send</button>
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
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.hint {
  margin: 0;
  color: var(--muted);
  text-align: center;
}

.bubble {
  max-width: 88%;
  padding: 10px 14px;
  border-radius: 16px;
  background: var(--surface);
  border: 1px solid var(--line);
}

.bubble p {
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.bubble.user {
  align-self: flex-end;
  background: var(--accent);
  border-color: var(--accent);
  color: var(--accent-ink);
  border-bottom-right-radius: 4px;
}

.bubble.coach {
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}

.typing {
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
  padding: 8px 16px;
  font-size: 0.9rem;
  color: var(--danger);
}

.composer {
  display: flex;
  gap: 8px;
  padding: 12px 16px 6px;
  background: var(--surface);
  border-top: 1px solid var(--line);
}

/* 1rem keeps iphones from zooming in when the box is tapped */
.composer input {
  flex: 1;
  min-width: 0;
  padding: 12px 14px;
  font-size: 1rem;
  color: var(--ink);
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 999px;
}

.composer input:focus {
  outline: 2px solid var(--accent);
  border-color: transparent;
}

.composer button {
  padding: 0 20px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--accent-ink);
  background: var(--accent);
  border: 0;
  border-radius: 999px;
  cursor: pointer;
}

.composer button:disabled {
  opacity: 0.5;
  cursor: default;
}

.note {
  margin: 0;
  padding: 0 16px 10px;
  background: var(--surface);
  font-size: 0.75rem;
  color: var(--muted);
}
</style>