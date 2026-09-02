/**
 * hooks/useStats.js — Fetches all analytics stats in parallel.
 */
import { useState, useEffect } from 'react'
import { fetchAllStats } from '../api/stats'

/**
 * @returns {{ stats, loading, error }}
 * stats = { overview, velocity, deptLoad, locations, priorityLoad }
 */
export default function useStats() {
  const [stats, setStats]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetchAllStats()
      .then((data) => { if (!cancelled) { setStats(data); setLoading(false) } })
      .catch((err)  => { if (!cancelled) { setError(err.message); setLoading(false) } })
    return () => { cancelled = true }
  }, [])

  return { stats, loading, error }
}
