import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import ReactECharts from 'echarts-for-react'
import {
  AlertTriangle,
  ArrowRight,
  Database,
  GitBranch,
  Radar as RadarIcon,
} from 'lucide-react'
import globeNetwork from '@/assets/globe-network.png'
import narrativeAnalysis from '@/assets/narrative-analysis.png'
import clusterGraph from '@/assets/cluster-graph.png'
import { getDashboardSummary } from '@/api/dashboard'
import { getNarrativeSummary } from '@/api/narrative'
import { PageHeader } from '@/components/shared/PageHeader'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Panel } from '@/components/shared/Panel'
import { StatCard } from '@/components/shared/StatCard'
import { DonutChart, CHART_PALETTE } from '@/components/shared/DonutChart'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { formatDate, formatNumber, formatScore, truncate } from '@/lib/utils'

export function Dashboard() {
  const dashboardQuery = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardSummary,
  })
  const narrativeQuery = useQuery({
    queryKey: ['narrative-summary'],
    queryFn: getNarrativeSummary,
  })

  const data = dashboardQuery.data
  const narrative = narrativeQuery.data

  const donutData = useMemo(() => {
    const stats = data?.cluster_statistics ?? narrative?.statistics ?? {}
    const entries = Object.entries(stats)
      .map(([id, item]) => ({ id, label: item.label, size: item.size }))
      .sort((a, b) => b.size - a.size)
    const top = entries.slice(0, 8).map((item) => ({
      name: `#${item.id} ${truncate(item.label, 26)}`,
      value: item.size,
    }))
    const rest = entries.slice(8).reduce((sum, item) => sum + item.size, 0)
    if (rest > 0) top.push({ name: 'Other narratives', value: rest })
    return top
  }, [data, narrative])

  const influenceBarOption = useMemo(() => {
    const rows = (data?.top_narratives ?? [])
      .map(([id, item]) => ({
        id,
        label: truncate(item.label, 34),
        score: item.score,
      }))
      .reverse()
    return {
      backgroundColor: 'transparent',
      grid: { left: 8, right: 40, top: 8, bottom: 8, containLabel: true },
      xAxis: {
        type: 'value',
        max: 1,
        axisLabel: { color: '#5a6a84', fontSize: 10 },
        splitLine: { lineStyle: { color: '#182338' } },
      },
      yAxis: {
        type: 'category',
        data: rows.map((r) => `#${r.id}`),
        axisLabel: { color: '#8b9bb4', fontSize: 11, fontFamily: 'IBM Plex Mono' },
        axisLine: { show: false },
        axisTick: { show: false },
      },
      tooltip: {
        backgroundColor: '#111a2c',
        borderColor: '#243149',
        textStyle: { color: '#e8eef7', fontSize: 12 },
        formatter: (params: { dataIndex: number }) => {
          const row = rows[params.dataIndex]
          return `${row.label}<br/>influence: ${row.score.toFixed(3)}`
        },
      },
      series: [
        {
          type: 'bar',
          data: rows.map((r, i) => ({
            value: r.score,
            itemStyle: {
              color: CHART_PALETTE[i % CHART_PALETTE.length],
              borderRadius: [0, 6, 6, 0],
            },
          })),
          barWidth: 14,
          label: {
            show: true,
            position: 'right',
            color: '#8b9bb4',
            fontSize: 10,
            fontFamily: 'IBM Plex Mono',
            formatter: (p: { value: number }) => p.value.toFixed(2),
          },
        },
      ],
    }
  }, [data])

  if (dashboardQuery.isLoading || narrativeQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-5 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
        <Skeleton className="h-96" />
      </div>
    )
  }

  if (dashboardQuery.isError) {
    return <ErrorState message="Failed to load dashboard data from /dashboard/" />
  }

  const status = data?.pipeline_status ?? {}
  const brief = data?.executive_brief
  const stats = data?.system_statistics
  const impactReports = data?.impact_reports ?? []
  const observations = brief?.strategic_observations ?? []
  // Risks can be plain strings or { narrative, warning_score } objects.
  const risks = (brief?.emerging_risks ?? []).map((item) =>
    typeof item === 'string'
      ? { narrative: item, score: null as number | null }
      : {
          narrative: String(item?.narrative ?? ''),
          score:
            typeof item?.warning_score === 'number' ? item.warning_score : null,
        },
  )
  const priorities = brief?.priority_narratives ?? []
  const totalVolume = donutData.reduce((sum, item) => sum + item.value, 0)

  return (
    <div className="space-y-7">
      <PageHeader
        title="Intelligence Command"
        description="Live view of pipeline status, narrative pressure, and strategic context."
        image={globeNetwork}
        action={
          <Badge tone={status.status === 'completed' ? 'ok' : 'warn'}>
            pipeline {status.status ?? 'unknown'}
          </Badge>
        }
      />

      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Documents processed"
          value={formatNumber(status.documents_processed)}
          hint={`Vector index · ${formatNumber(status.vector_index_size)} embeddings`}
          icon={Database}
          tone="accent"
        />
        <StatCard
          label="Active narratives"
          value={formatNumber(status.cluster_count)}
          hint={`${formatNumber(status.subcluster_count)} subclusters tracked`}
          icon={GitBranch}
          tone="blue"
          delay={0.05}
        />
        <StatCard
          label="Influence signals"
          value={formatNumber(stats?.influence_count)}
          hint={`${formatNumber(stats?.narrative_count)} high-priority narratives`}
          icon={RadarIcon}
          tone="accent"
          delay={0.1}
        />
        <StatCard
          label="Risk warnings"
          value={formatNumber(stats?.warning_count)}
          hint={`${formatNumber(stats?.forecast_count)} active forecasts`}
          icon={AlertTriangle}
          tone="warn"
          delay={0.15}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        <Panel
          title="Narrative share"
          subtitle="Corpus distribution across discovered clusters"
        >
          {donutData.length ? (
            <>
              <DonutChart
                data={donutData}
                height={280}
                centerValue={formatNumber(totalVolume)}
                centerLabel="chunks"
                backdrop={clusterGraph}
              />
              <ul className="mt-4 max-h-40 space-y-1.5 overflow-auto pr-1 text-xs">
                {donutData.map((item, i) => (
                  <li key={item.name} className="flex items-center gap-2 text-ink-muted">
                    <span
                      className="h-2.5 w-2.5 shrink-0 rounded-full"
                      style={{ background: CHART_PALETTE[i % CHART_PALETTE.length] }}
                    />
                    <span className="min-w-0 flex-1 truncate">{item.name}</span>
                    <span className="font-mono text-ink">{item.value}</span>
                  </li>
                ))}
              </ul>
              <div className="relative mt-5 overflow-hidden rounded-xl border border-line/70">
                <img
                  src={narrativeAnalysis}
                  alt="Narrative monitoring illustration"
                  className="h-28 w-full object-cover object-center"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-surface via-surface/45 to-transparent" />
                <p className="absolute bottom-2.5 left-4 text-xs font-medium text-ink">
                  Continuous media monitoring across {donutData.length} narrative groups
                </p>
              </div>
            </>
          ) : (
            <EmptyState title="No cluster statistics available" />
          )}
        </Panel>

        <Panel
          title="Influence pressure"
          subtitle="Composite influence score per narrative"
          className="xl:col-span-2"
        >
          {(data?.top_narratives?.length ?? 0) > 0 ? (
            <ReactECharts option={influenceBarOption} style={{ height: 420 }} notMerge />
          ) : (
            <EmptyState title="No influence scores loaded" />
          )}
        </Panel>
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        <Panel
          title="AI executive brief"
          subtitle="Strategic observations generated by the pipeline"
          className="xl:col-span-2"
        >
          {brief?.summary ? (
            <p className="mb-5 text-sm leading-7 text-ink-muted">{brief.summary}</p>
          ) : null}

          {priorities.length ? (
            <div className="mb-5">
              <p className="mb-2 text-xs font-medium uppercase tracking-wider text-ink-faint">
                Priority narratives
              </p>
              <ul className="space-y-2">
                {priorities.map((item) => (
                  <li
                    key={item}
                    className="rounded-xl border border-accent-2/20 bg-accent-2/5 px-4 py-3 text-sm leading-6 text-ink"
                  >
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {risks.length ? (
            <div className="mb-5">
              <p className="mb-2 text-xs font-medium uppercase tracking-wider text-ink-faint">
                Emerging risks
              </p>
              <ul className="space-y-2">
                {risks.map((item, index) => (
                  <li
                    key={`${item.narrative}-${index}`}
                    className="flex items-start justify-between gap-3 rounded-xl border border-warn/25 bg-warn/5 px-4 py-3 text-sm leading-6 text-ink"
                  >
                    <span className="min-w-0 flex-1">{truncate(item.narrative, 120)}</span>
                    {item.score != null ? (
                      <span className="shrink-0 rounded-lg bg-warn/15 px-2 py-0.5 font-mono text-xs font-semibold text-warn">
                        {item.score.toFixed(2)}
                      </span>
                    ) : null}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {observations.length ? (
            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wider text-ink-faint">
                Strategic observations
              </p>
              <ul className="space-y-2.5">
                {observations.map((item) => (
                  <li
                    key={item}
                    className="flex items-start gap-3 rounded-xl border border-line/70 bg-surface/60 px-4 py-3.5 text-sm leading-6 text-ink-muted"
                  >
                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ) : !priorities.length && !risks.length && !brief?.summary ? (
            <EmptyState title="No executive brief generated yet" />
          ) : null}
        </Panel>

        <div className="space-y-5">
          <Panel title="System status" subtitle="Pipeline metadata">
            <dl className="space-y-4 text-sm">
              <div className="flex justify-between gap-3">
                <dt className="text-ink-muted">Last update</dt>
                <dd className="text-right font-mono text-xs text-ink">
                  {formatDate(status.timestamp)}
                </dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-ink-muted">Embedding model</dt>
                <dd className="text-right text-xs text-ink">{status.embedding_model ?? '—'}</dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-ink-muted">Pipeline version</dt>
                <dd className="text-right font-mono text-ink">
                  v{status.pipeline_version ?? '—'}
                </dd>
              </div>
              <div className="flex justify-between gap-3">
                <dt className="text-ink-muted">Timeline points</dt>
                <dd className="text-right font-mono text-ink">
                  {formatNumber(stats?.timeline_points)}
                </dd>
              </div>
            </dl>
          </Panel>

          <Panel title="Impact chains" subtitle="Cross-narrative influence">
            {impactReports.length ? (
              <ul className="max-h-[340px] space-y-3 overflow-auto pr-1">
                {impactReports.slice(0, 6).map((report) => (
                  <li
                    key={report.source}
                    className="rounded-xl border border-line/70 bg-surface/60 px-4 py-3"
                  >
                    <p className="text-sm font-medium leading-6 text-ink">
                      {truncate(report.source, 64)}
                    </p>
                    <div className="mt-2 flex items-center gap-2 text-xs text-ink-faint">
                      <ArrowRight className="h-3.5 w-3.5 shrink-0" />
                      impacts {report.impacts.length} narrative
                      {report.impacts.length === 1 ? '' : 's'}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState title="No impact chains computed" />
            )}
          </Panel>
        </div>
      </div>

      <Panel
        title="Top narratives"
        subtitle="Ranked by composite influence (volume, PageRank, betweenness)"
        bodyClassName="p-0"
      >
        {(data?.top_narratives?.length ?? 0) > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead className="text-xs uppercase tracking-wider text-ink-faint">
                <tr className="border-b border-line">
                  <th className="px-6 py-3.5 font-medium">ID</th>
                  <th className="px-4 py-3.5 font-medium">Narrative</th>
                  <th className="px-4 py-3.5 font-medium">Influence</th>
                  <th className="px-4 py-3.5 font-medium">Volume</th>
                  <th className="px-6 py-3.5 font-medium">PageRank</th>
                </tr>
              </thead>
              <tbody>
                {data?.top_narratives.map(([id, item]) => (
                  <tr key={id} className="border-b border-line/60 last:border-0 hover:bg-surface-3/30">
                    <td className="px-6 py-4 font-mono text-ink-muted">#{id}</td>
                    <td className="px-4 py-4 leading-6 text-ink">{truncate(item.label, 88)}</td>
                    <td className="px-4 py-4">
                      <div className="flex items-center gap-2.5">
                        <div className="h-1.5 w-20 overflow-hidden rounded-full bg-surface-3">
                          <div
                            className="h-full rounded-full bg-accent"
                            style={{ width: `${Math.min(item.score * 100, 100)}%` }}
                          />
                        </div>
                        <span className="font-mono text-xs text-accent">
                          {formatScore(item.score, 2)}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-4 font-mono">{formatNumber(item.volume)}</td>
                    <td className="px-6 py-4 font-mono">{formatScore(item.pagerank_score, 2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-6">
            <EmptyState title="No top narratives in dashboard response" />
          </div>
        )}
      </Panel>
    </div>
  )
}
