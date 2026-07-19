import { api, unwrapData, type ApiEnvelope } from './client'

export type EvaluationSummary = {
  metadata: {
    coherence_count: number
    purity_count: number
    label_audit_count: number
    status: string
    temporal_buckets?: number
    narrative_count?: number
  }
  coherence: Record<string, number | null>
  purity: Record<string, number | null>
  forecast_evaluation: {
    actual_top_10?: unknown[]
    baseline_hits?: number
    vanguard_hits?: number
    [key: string]: unknown
  }
  correlation: {
    baseline_correlation?: number | null
    vanguard_correlation?: number | null
    baseline_samples?: number
    vanguard_samples?: number
    [key: string]: number | null | undefined
  }
  label_audit:
    | Array<{
        cluster: number
        label: string
        volume: number
        subclusters: string[]
      }>
    | Record<string, unknown>
  pipeline_status: Record<string, unknown>
}

export async function getEvaluationSummary() {
  const { data } = await api.get<ApiEnvelope<EvaluationSummary>>('/evaluation/summary')
  return unwrapData(data)
}
