/**
 * api/stats.js — Analytics & stats API calls.
 */
import client from './client'

export const fetchOverview     = ()            => client.get('/stats/overview').then((r) => r.data)
export const fetchVelocity     = ()            => client.get('/stats/velocity').then((r) => r.data)
export const fetchDeptLoad     = ()            => client.get('/stats/dept-load').then((r) => r.data)
export const fetchLocations    = (top = 15)    => client.get('/stats/locations', { params: { top } }).then((r) => r.data)
export const fetchPriorityLoad = ()            => client.get('/stats/priority-load').then((r) => r.data)

/** Fetch all stats in one parallel call — used by Analytics page. */
export const fetchAllStats = () =>
  Promise.all([
    fetchOverview(),
    fetchVelocity(),
    fetchDeptLoad(),
    fetchLocations(10),
    fetchPriorityLoad(),
  ]).then(([overview, velocity, deptLoad, locations, priorityLoad]) => ({
    overview, velocity, deptLoad, locations, priorityLoad,
  }))
