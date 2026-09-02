/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState } from 'react'
import { clusters as staticClusters } from '../data/Clusters'
import { enrichClusterWithAccountability } from '../data/accountability'
import { fetchClusters, updateClusterStatus } from '../api/clusters'

const IssueContext = createContext(null)

export function IssueProvider({ children }) {
    const [issues, setIssues] = useState(staticClusters.map(enrichClusterWithAccountability))
    const [assignments, setAssignments] = useState({})
    const [discarded, setDiscarded] = useState(new Set())

    useEffect(() => {
        fetchClusters({ limit: 500 })
            .then((data) => {
                if (data && data.length > 0) {
                    setIssues(
                        data.map((cluster) => {
                            const staticMatch = staticClusters.find(
                                (item) => item.cluster_id === cluster.cluster_id
                            )
                            return enrichClusterWithAccountability({
                                ...(staticMatch ?? {}),
                                ...cluster,
                            })
                        })
                    )
                }
            })
            .catch(() => {
                // Backend unavailable. Keep the seeded local data.
            })
    }, [])

    const assignOfficer = (clusterId, officer) => {
        const assignedAt = new Date()
        const dueAt = new Date(assignedAt.getTime() + 3 * 24 * 60 * 60 * 1000)

        setAssignments((prev) => ({
            ...prev,
            [clusterId]: {
                ...officer,
                assignedAt: assignedAt.toISOString(),
                dueAt: dueAt.toISOString(),
            },
        }))

        setIssues((prev) =>
            prev.map((cluster) =>
                cluster.cluster_id === clusterId
                    ? {
                        ...cluster,
                        status: 'inprogress',
                        assigned_at: assignedAt.toISOString(),
                        due_at: dueAt.toISOString(),
                    }
                    : cluster
            )
        )

        updateClusterStatus(clusterId, 'inprogress').catch(() => {
            // Optimistic UI already reflects the assignment.
        })
    }

    const resolveIssue = (clusterId) => {
        const resolvedAt = new Date().toISOString()

        setIssues((prev) =>
            prev.map((cluster) =>
                cluster.cluster_id === clusterId
                    ? { ...cluster, status: 'resolved', resolved_at: resolvedAt }
                    : cluster
            )
        )

        updateClusterStatus(clusterId, 'resolved').catch(() => {
            // Optimistic UI already reflects the resolution.
        })
    }

    const discardIssue = (clusterId) => {
        setDiscarded((prev) => new Set([...prev, clusterId]))
    }

    const value = {
        issues,
        assignments,
        discarded,
        assignOfficer,
        resolveIssue,
        discardIssue,
    }

    return <IssueContext.Provider value={value}>{children}</IssueContext.Provider>
}

export function useIssues() {
    return useContext(IssueContext)
}
