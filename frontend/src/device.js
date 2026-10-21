const KEY = 'device_id'
// same shape the backend accepts
const VALID_ID = /^[A-Za-z0-9-]{8,64}$/

let memoryId = null // used when storage is blocked, lost on refresh

function makeId() {
  if (crypto.randomUUID) return crypto.randomUUID()
  // older browsers
  return Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join('')
}

// anonymous id that tells one browser from another. it is not a login
export function getDeviceId() {
  try {
    let id = localStorage.getItem(KEY)
    if (!id || !VALID_ID.test(id)) {
      id = makeId()
      localStorage.setItem(KEY, id)
    }
    return id
  } catch {
    // private browsing can block storage
    memoryId = memoryId || makeId()
    return memoryId
  }
}