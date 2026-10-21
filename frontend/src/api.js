import { getDeviceId } from './device'

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, options = {}) {
  let res
  try {
    res = await fetch(path, {
      ...options,
      headers: { 'X-Device-ID': getDeviceId(), ...options.headers },
    })
  } catch {
    throw new ApiError("Couldn't reach the server. Check your connection and try again.", 0)
  }

  if (res.status === 204) return null // delete answers with no body
  const body = await res.json().catch(() => null)

  if (!res.ok) {
    // the backend sends {detail: "text"}, validation errors send a list instead
    const fallback =
      res.status >= 500
        ? "The server isn't responding. Please try again in a minute."
        : 'Something went wrong. Please try again.'
    throw new ApiError(typeof body?.detail === 'string' ? body.detail : fallback, res.status)
  }
  return body
}

export function sendMessage(message, day) {
  return request('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, day }),
  })
}

export const getMessages = () => request('/api/messages')
export const getDays = () => request('/api/days')
export const getDay = (day) => request(`/api/days/${day}`)
export const deleteEntry = (id) => request(`/api/entries/${id}`, { method: 'DELETE' })