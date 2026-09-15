const API_URL = import.meta.env.VITE_API_URL
const TOKEN_KEY = 'vet_token'
const USER_KEY = 'vet_user'

export async function getHealth() {
  const response = await fetch(`${API_URL}/health`)

  if (!response.ok) {
    throw new Error(`Error ${response.status} al consultar /health`)
  }

  return response.json()
}

export async function login(email, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.error || `Error ${response.status} al iniciar sesión`)
  }

  setSession(data.access_token, data.user)
  return data
}

export function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY)
  return raw ? JSON.parse(raw) : null
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}
