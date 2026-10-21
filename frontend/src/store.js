import { reactive } from 'vue'

import { getDay } from './api'
import { todayString } from './utils/dates'

// shared so the total in the header updates when the chat or history changes it
export const store = reactive({ todayTotal: 0 })

export async function refreshTodayTotal() {
  try {
    store.todayTotal = (await getDay(todayString())).total
  } catch {
    // keep the last value if the api can't be reached
  }
}