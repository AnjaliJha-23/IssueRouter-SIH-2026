/**
 * api/client.js — Axios base client for IssueRouter backend.
 * All API calls go through /api which Vite proxies to http://localhost:8000.
 */
import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
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
    if (inputUrl.startsWith('http://localhost:8000/api/')) {
      const relativeUrl = inputUrl.replace('http://localhost:8000', '')
      return fetch(relativeUrl, { ...options, headers })
    }
    if (inputUrl.startsWith('/api/')) {
      const directUrl = `http://localhost:8000${inputUrl}`
      return fetch(directUrl, { ...options, headers })
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
