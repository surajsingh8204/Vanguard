import { api, unwrapData, type ApiEnvelope } from './client'

export type InfluenceEntry = [
  string,
  {
    label: string
    score: number
    volume: number
    volume_score?: number
    pagerank_score?: number
    betweenness_score?: number
  },
]

export type DashboardSummary = {
  pipeline_status: {
    timestamp?: string
    documents_processed?: number
    cluster_count?: number
    subcluster_count?: number
    embedding_model?: string
    vector_index_size?: number
    pipeline_version?: string
    status?: string
  }
  executive_brief: {
    title?: string | null
    summary?: string | null
    highlights?: string[]
    priority_narratives?: string[]
    emerging_risks?: Array<string | { narrative: string; warning_score?: number }>
    strategic_observations?: string[]
  }
  strategic_context: {
    summary?: unknown
  }
  impact_reports?: Array<{ source: string; impacts: string[] }>
  intelligence_briefs?: unknown[]
  cluster_statistics?: Record<string, { label: string; size: number }>
  top_narratives: InfluenceEntry[]
  top_influencers: InfluenceEntry[]
  early_warnings: unknown[]
  forecast_summary: unknown[]
  system_statistics: {
    narrative_count: number
    warning_count: number
    forecast_count: number
    timeline_points: number
    influence_count: number
  }
}

export async function getDashboardSummary() {
  const { data } = await api.get<ApiEnvelope<DashboardSummary>>('/dashboard/')
  return unwrapData(data)
}
