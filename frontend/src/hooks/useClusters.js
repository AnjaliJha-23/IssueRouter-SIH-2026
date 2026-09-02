/**
 * hooks/useClusters.js — Fetches clusters from the API with loading/error states.
 */
import { useState, useEffect, useCallback } from 'react'
import { fetchClusters } from '../api/clusters'

/**
 * @param {Object} filters - { status, department, priority, search }
 * @returns {{ clusters, loading, error, refetch }}
 */
export default function useClusters(filters = {}) {
  const [clusters, setClusters] = useState([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // Strip empty / falsy values so we don't send ?status=&department= etc.
      const params = Object.fromEntries(
        Object.entries(filters).filter(([, v]) => v !== '' && v !== null && v !== undefined)
      )
      const data = await fetchClusters({ limit: 500, ...params })
      setClusters(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [JSON.stringify(filters)]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { load() }, [load])

  return { clusters, loading, error, refetch: load }
}
