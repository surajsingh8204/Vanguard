import { api, unwrapData, type ApiEnvelope } from './client'

export type EvolutionEntry = { date: string; summary: string }

export type Forecast = {
  narrative: string
  score: number
  slope: number
  momentum: number
  influence: number
  emergence: number
  current_volume: number
}

export type EarlyWarning = {
  narrative: string
  warning_score: number
  reasons: string[]
  volume: number
}

export type Spike = {
  narrative: string
  day: string
  count: number
  volume: number
  momentum: number
  z_score: number
}

export type TimelineData = {
  timeline: Record<string, Record<string, number>>
  forecasts: Forecast[]
  early_warnings: EarlyWarning[]
  strategic_context: unknown
  influence_scores: unknown
  evolution?: Record<string, EvolutionEntry[]>
  spikes?: Spike[]
  emerging?: unknown[]
}

export async function getTimeline() {
  const { data } = await api.get<ApiEnvelope<TimelineData>>('/temporal/timeline')
  return unwrapData(data)
}
