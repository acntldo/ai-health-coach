// local date as YYYY-MM-DD. toISOString() gives the utc date,
// which is wrong in the early morning for anyone ahead of utc
export function toDateString(date = new Date()) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function todayString() {
  return toDateString()
}

// "2026-10-18" -> "Sun, Oct 18". the T00:00:00 makes js read it as local time
export function formatDay(dateString) {
  return new Date(`${dateString}T00:00:00`).toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
}

export function shiftDay(dateString, offset) {
  const date = new Date(`${dateString}T00:00:00`)
  date.setDate(date.getDate() + offset)
  return toDateString(date)
}


// the server sends utc times without a zone suffix, so one is added before parsing.
// without it the browser would read them as local time and show the wrong hour
export function parseServerTime(value) {
  return new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(value) ? value : `${value}Z`)
}

// "2:32 PM", in the viewer's own language and time zone
export function formatTime(date) {
  return date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
}