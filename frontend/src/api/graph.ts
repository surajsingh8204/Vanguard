import { api, unwrapData, type ApiEnvelope } from './client'

export type GraphSummary = {
  metadata: {
    node_count: number
    edge_count: number
    community_count: number
    centrality_labels: string[]
    top_influencers: unknown[]
    top_insights: unknown[]
  }
  labels: {
    communities: number
    centrality: number
    influencers: number
  }
  statistics: {
    node_count?: number
    edge_count?: number
  }
  communities?: Record<string, number[]>
  centrality?: {
    degree?: Record<string, number>
    pagerank?: Record<string, number>
    betweenness?: Record<string, number>
  }
  influencers?: Influencer[]
  influence_mappings?: Array<{
    source: string
    targets: Array<{ id: number; label: string; weight: number }>
  }>
  diagnostics?: Array<{
    cluster_a: string
    cluster_b: string
    semantic_similarity: number
    temporal_overlap: number
    final_score: number
  }>
  warnings: unknown[]
}

export type Influencer = {
  id: string
  label: string
  score: number
  volume: number
  volume_score?: number
  pagerank_score?: number
  betweenness_score?: number
}

export type GraphNetwork = {
  nodes: {
    items: Array<{ id: number; label: string }>
    page: number
    limit: number
    total: number
    pages: number
  }
  edges: {
    items: Array<{ source: number; target: number; weight: number }>
    page: number
    limit: number
    total: number
    pages: number
  }
}

export async function getGraphSummary() {
  const { data } = await api.get<ApiEnvelope<GraphSummary>>('/graphs/summary')
  return unwrapData(data)
}

export async function getGraphNetwork(params?: {
  page?: number
  limit?: number
  cluster?: number
}) {
  const { data } = await api.get<ApiEnvelope<GraphNetwork>>('/graphs/network', {
    params,
  })
  return unwrapData(data)
}
