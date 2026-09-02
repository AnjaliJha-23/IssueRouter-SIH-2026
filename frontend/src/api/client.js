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

// Response interceptor — normalise errors
client.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err?.response?.data?.detail ?? err?.message ?? 'Unknown error'
    console.error('[API Error]', msg)
    return Promise.reject(new Error(msg))
  }
)

export default client
