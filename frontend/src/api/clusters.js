/**
 * api/clusters.js — Cluster-related API calls.
 */
import client from './client'

/**
 * Fetch all clusters with optional server-side filters.
 * @param {Object} params - { status, department, priority, search, skip, limit }
 */
export const fetchClusters = (params = {}) =>
  client.get('/clusters', { params }).then((r) => r.data)

/**
 * Fetch a single cluster by ID (includes sample_tweets).
 */
export const fetchCluster = (clusterId) =>
  client.get(`/clusters/${clusterId}`).then((r) => r.data)

/**
 * Update the status of a cluster.
 * @param {string} clusterId
 * @param {string} status - 'pending' | 'inprogress' | 'resolved'
 */
export const updateClusterStatus = (clusterId, status) =>
  client.patch(`/clusters/${clusterId}/status`, { status }).then((r) => r.data)
