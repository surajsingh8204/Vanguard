import { api, unwrapData, type ApiEnvelope } from './client'

export type NarrativeSummary = {
  metadata: {
    cluster_count: number
    subcluster_count: number
    statistics: Record<string, { label: string; size: number }>
    sentiment: unknown
    top_insights: unknown[]
    warnings: unknown[]
  }
  cluster_labels: Record<string, string>
  subcluster_labels: Record<string, string | Record<string, string>>
  statistics: Record<string, { label: string; size: number }>
  sentiment: unknown
  top_insights: unknown[]
  warnings: unknown[]
}

export type ClusterPage = {
  items: Array<{ cluster: string; items: Array<Record<string, unknown>> }>
  page: number
  limit: number
  total: number
  pages: number
}

export async function getNarrativeSummary() {
  const { data } = await api.get<ApiEnvelope<NarrativeSummary>>('/narrative/summary')
  return unwrapData(data)
}

export async function getNarrativeClusters(params?: {
  page?: number
  limit?: number
  cluster?: string
}) {
  const { data } = await api.get<ApiEnvelope<ClusterPage>>('/narrative/clusters', {
    params,
  })
  return unwrapData(data)
}
