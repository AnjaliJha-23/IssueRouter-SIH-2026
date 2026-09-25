/**
 * api/client.js — Centralized Axios and Fetch API client for IssueRouter backend.
 * Reads backend API base URL from import.meta.env.VITE_API_URL.
 */
import axios from 'axios'

// Derive backend API base URL from Vite environment variable
const envApiUrl = import.meta.env.VITE_API_URL
export const API_BASE_URL = (envApiUrl && envApiUrl.trim() ? envApiUrl.trim() : 'http://localhost:8000').replace(/\/+$/, '')

/**
 * Resolve any endpoint path to full backend URL while avoiding double '/api/api/'.
 * Examples:
 *   resolveApiUrl('/api/challenges/') -> 'http://localhost:8000/api/challenges/'
 *   resolveApiUrl('/stats/overview')  -> 'http://localhost:8000/api/stats/overview'
 *   resolveApiUrl('https://example.com/api') -> 'https://example.com/api'
 */
export function resolveApiUrl(inputUrl) {
  if (!inputUrl) return ''
  if (inputUrl.startsWith('http://') || inputUrl.startsWith('https://')) {
    return inputUrl
  }

  const cleanPath = inputUrl.startsWith('/') ? inputUrl : `/${inputUrl}`
  if (cleanPath.startsWith('/api/') || cleanPath === '/api') {
    return `${API_BASE_URL}${cleanPath}`
  }
  return `${API_BASE_URL}/api${cleanPath}`
}

/**
 * Centralized Axios client instance.
 * Default baseURL is `${API_BASE_URL}/api`.
 */
const client = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor — attach auth token and normalize paths
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }

  // If request URL already includes /api, strip it so baseURL=/api does not produce /api/api
  if (config.url) {
    if (config.url.startsWith('/api/')) {
      config.url = config.url.substring(4)
    } else if (config.url === '/api') {
      config.url = '/'
    }
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

/**
 * Centralized fetch helper with authentication and base URL resolution.
 */
export async function authFetch(inputUrl, options = {}) {
  const token = localStorage.getItem('token')
  const isFormData = options.body instanceof FormData
  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  }

  const targetUrl = resolveApiUrl(inputUrl)
  return fetch(targetUrl, { ...options, headers })
}

/**
 * Helper to resolve media/static evidence upload URLs.
 */
export function getMediaUrl(url) {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  const cleanPath = url.startsWith('/') ? url : `/${url}`
  return `${API_BASE_URL}${cleanPath}`
}

export default client

