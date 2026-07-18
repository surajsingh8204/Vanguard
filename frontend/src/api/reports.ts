import { api, unwrapData, type ApiEnvelope } from './client'

export type ReportItem = {
  report_type: string
  created_at: string
  latest_run: string
  filename: string
  status: string
}

export type ReportPage = {
  items: ReportItem[]
  page: number
  limit: number
  total: number
  pages: number
}

export async function getLatestReports(params?: {
  page?: number
  limit?: number
  report_type?: string
}) {
  const { data } = await api.get<ApiEnvelope<ReportPage>>('/reports/latest', {
    params,
  })
  return unwrapData(data)
}

export async function getReportHistory(params?: {
  page?: number
  limit?: number
  report_type?: string
}) {
  const { data } = await api.get<ApiEnvelope<ReportPage>>('/reports/history', {
    params,
  })
  return unwrapData(data)
}

export type ReportContent = ReportItem & { content: unknown }

export async function getReportContent(filename: string) {
  const { data } = await api.get<ApiEnvelope<ReportContent>>('/reports/content', {
    params: { filename },
  })
  return unwrapData(data)
}
