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

export async function registerClient(payload) {
  const response = await fetch(`${API_URL}/auth/register-client`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.error || `Error ${response.status} al registrarse`)
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

export class AuthError extends Error {}

async function authFetch(path, options = {}) {
  const token = getToken()
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  if (response.status === 401) {
    logout()
    throw new AuthError('Tu sesión expiró, iniciá sesión de nuevo')
  }

  if (response.status === 204) {
    return null
  }

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.error || `Error ${response.status}`)
  }

  return data
}

function withQuery(path, params = {}) {
  const query = Object.entries(params)
    .filter(([, value]) => value !== undefined && value !== null && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&')

  return query ? `${path}?${query}` : path
}

// Clientes
export const listClients = () => authFetch('/clients')
export const createClient = (data) =>
  authFetch('/clients', { method: 'POST', body: JSON.stringify(data) })
export const updateClient = (id, data) =>
  authFetch(`/clients/${id}`, { method: 'PUT', body: JSON.stringify(data) })
export const deleteClient = (id) => authFetch(`/clients/${id}`, { method: 'DELETE' })

// Mascotas
export const listPets = (params) => authFetch(withQuery('/pets', params))
export const createPet = (data) =>
  authFetch('/pets', { method: 'POST', body: JSON.stringify(data) })
export const updatePet = (id, data) =>
  authFetch(`/pets/${id}`, { method: 'PUT', body: JSON.stringify(data) })
export const deletePet = (id) => authFetch(`/pets/${id}`, { method: 'DELETE' })

// Citas
export const listAppointments = (params) => authFetch(withQuery('/appointments', params))
export const createAppointment = (data) =>
  authFetch('/appointments', { method: 'POST', body: JSON.stringify(data) })
export const updateAppointment = (id, data) =>
  authFetch(`/appointments/${id}`, { method: 'PUT', body: JSON.stringify(data) })
export const deleteAppointment = (id) =>
  authFetch(`/appointments/${id}`, { method: 'DELETE' })
