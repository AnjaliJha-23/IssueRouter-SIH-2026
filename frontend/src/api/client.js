/**
 * api/client.js — Axios base client for IssueRouter backend.
 * All API calls go through /api which Vite proxies to http://localhost:8000.
 */
import axios from 'axios'

// Respect VITE_API_URL when deploying against separate backend hosts (e.g. Azure App Service / Vercel)
// In local development or single-host deployments, defaults to relative '/api'
const rawApiUrl = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) || ''
const apiBase = rawApiUrl.endsWith('/') ? rawApiUrl.slice(0, -1) : rawApiUrl
export const API_BASE_URL = apiBase
export const API_PREFIX = apiBase ? `${apiBase}/api` : '/api'

const client = axios.create({
  baseURL: API_PREFIX,
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor — attach auth token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// Response interceptor — normalise errors
client.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err?.response?.data?.detail ?? err?.message ?? 'Unknown error'
    console.error('[API Error]', msg)
    return Promise.reject(new Error(msg))
  }
)

export function getAuthHeaders(extraHeaders = {}) {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...extraHeaders,
  }
}

export async function authFetch(inputUrl, options = {}) {
  const token = localStorage.getItem('token')
  const isFormData = options.body instanceof FormData
  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  }

  try {
    const res = await fetch(inputUrl, { ...options, headers })
    return res
  } catch (err) {
    if (API_BASE_URL && inputUrl.startsWith('/api/')) {
      const remoteUrl = `${API_BASE_URL}${inputUrl}`
      return fetch(remoteUrl, { ...options, headers })
    }
    if (!API_BASE_URL && inputUrl.startsWith('/api/')) {
      return fetch(inputUrl, { ...options, headers })
    }
    throw err
  }
}

export function getMediaUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  return url.startsWith('/') ? url : `/${url}`
}

export default client
