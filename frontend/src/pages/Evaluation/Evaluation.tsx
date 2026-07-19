import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import ReactECharts from 'echarts-for-react'
import smartCity from '@/assets/smart-city.png'
import { getEvaluationSummary } from '@/api/evaluation'
import { PageHeader } from '@/components/shared/PageHeader'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Panel } from '@/components/shared/Panel'
import { GaugeChart, DonutChart, CHART_PALETTE } from '@/components/shared/DonutChart'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { formatNumber, formatScore, truncate } from '@/lib/utils'

function mean(values: Array<number | null | undefined>) {
  const nums = values.filter(
    (v): v is number => typeof v === 'number' && Number.isFinite(v),
  )
  if (!nums.length) return null
  return nums.reduce((a, b) => a + b, 0) / nums.length
}

export function Evaluation() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['evaluation'],
    queryFn: getEvaluationSummary,
  })

  const coherenceRows = useMemo(() => {
    return Object.entries(data?.coherence ?? {})
      .map(([id, value]) => ({ id, value: value ?? 0 }))
      .sort((a, b) => b.value - a.value)
  }, [data])

  const coherenceBands = useMemo(() => {
    const values = Object.values(data?.coherence ?? {}).filter(
      (v): v is number => typeof v === 'number',
    )
    const bands = [
      { name: 'Strong (≥ 0.5)', value: values.filter((v) => v >= 0.5).length },
      { name: 'Moderate (0.35–0.5)', value: values.filter((v) => v >= 0.35 && v < 0.5).length },
      { name: 'Weak (< 0.35)', value: values.filter((v) => v < 0.35).length },
    ]
    return bands.filter((b) => b.value > 0)
  }, [data])

  const scatterOption = useMemo(() => {
    const coherence = data?.coherence ?? {}
    const purity = data?.purity ?? {}
    const points = Object.keys(coherence)
      .filter((id) => coherence[id] != null && purity[id] != null)
      .map((id) => ({
        id,
        value: [purity[id], coherence[id]],
      }))

    return {
      backgroundColor: 'transparent',
      grid: { left: 8, right: 24, top: 24, bottom: 8, containLabel: true },
      tooltip: {
        backgroundColor: '#111a2c',
        borderColor: '#243149',
        textStyle: { color: '#e8eef7', fontSize: 12 },
        formatter: (params: { data: { id: string; value: number[] } }) =>
          `Cluster #${params.data.id}<br/>purity: ${params.data.value[0]}<br/>coherence: ${params.data.value[1]}`,
      },
      xAxis: {
        name: 'purity',
        nameTextStyle: { color: '#5a6a84' },
        axisLabel: { color: '#5a6a84', fontSize: 10 },
        splitLine: { lineStyle: { color: '#182338' } },
      },
      yAxis: {
        name: 'coherence',
        nameTextStyle: { color: '#5a6a84' },
        axisLabel: { color: '#5a6a84', fontSize: 10 },
        splitLine: { lineStyle: { color: '#182338' } },
      },
      series: [
        {
          type: 'scatter',
          data: points,
          symbolSize: 14,
          itemStyle: {
            color: '#5b8def',
            opacity: 0.8,
            borderColor: '#0b1220',
            borderWidth: 1,
          },
          emphasis: { itemStyle: { color: '#3ddc97' } },
        },
      ],
    }
  }, [data])

  const coherenceBarOption = useMemo(() => {
    return {
      backgroundColor: 'transparent',
      grid: { left: 8, right: 16, top: 12, bottom: 8, containLabel: true },
      tooltip: {
        backgroundColor: '#111a2c',
        borderColor: '#243149',
        textStyle: { color: '#e8eef7', fontSize: 12 },
      },
      xAxis: {
        type: 'category',
        data: coherenceRows.map((r) => `#${r.id}`),
        axisLabel: { color: '#8b9bb4', fontSize: 10, fontFamily: 'IBM Plex Mono' },
        axisLine: { lineStyle: { color: '#243149' } },
      },
      yAxis: {
        type: 'value',
        max: 1,
        axisLabel: { color: '#5a6a84', fontSize: 10 },
        splitLine: { lineStyle: { color: '#182338' } },
      },
      series: [
        {
          type: 'bar',
          data: coherenceRows.map((r, i) => ({
            value: r.value,
            itemStyle: {
              color: CHART_PALETTE[i % CHART_PALETTE.length],
              borderRadius: [4, 4, 0, 0],
            },
          })),
          barWidth: 12,
        },
      ],
    }
  }, [coherenceRows])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-56" />
        <Skeleton className="h-96" />
      </div>
    )
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load evaluation summary." />
  }

  const avgCoherence = mean(Object.values(data.coherence ?? {}))
  const avgPurity = mean(Object.values(data.purity ?? {}))
  const baseline = data.correlation?.baseline_correlation
  const vanguard = data.correlation?.vanguard_correlation
  const audits = Array.isArray(data.label_audit)
    ? data.label_audit
    : Object.values(data.label_audit ?? {})
  const temporalBuckets = Number(data.metadata?.temporal_buckets ?? 0)
  const narrativeCount = Number(data.metadata?.narrative_count ?? 0)

  return (
    <div className="space-y-7">
      <PageHeader
        title="Evaluation"
        description="Cluster quality, forecast validation, and correlation benchmarks."
        image={smartCity}
        action={<Badge tone="ok">pipeline {data.metadata.status}</Badge>}
      />

      <div className="rounded-xl border border-line/70 bg-surface/50 px-4 py-3 text-sm text-ink-muted">
        Temporal coverage: {formatNumber(narrativeCount)} narratives across{' '}
        {formatNumber(temporalBuckets)} bucket
        {temporalBuckets === 1 ? '' : 's'}. Forecast correlations populate once the
        timeline has at least two comparable buckets.
      </div>
      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <Panel bodyClassName="p-4">
          <GaugeChart value={avgCoherence} title="Avg coherence" color="#3ddc97" />
        </Panel>
        <Panel bodyClassName="p-4">
          <GaugeChart
            value={avgPurity}
            max={400}
            title="Avg purity (words)"
            color="#5b8def"
            formatter={(v) => v.toFixed(0)}
          />
        </Panel>
        <Panel bodyClassName="p-4">
          <GaugeChart
            value={typeof vanguard === 'number' && Number.isFinite(vanguard) ? vanguard : null}
            title="Vanguard correlation"
            color="#9d7bef"
          />
        </Panel>
        <Panel bodyClassName="p-4">
          <GaugeChart
            value={typeof baseline === 'number' && Number.isFinite(baseline) ? baseline : null}
            title="Baseline correlation"
            color="#f0b429"
          />
        </Panel>
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        <Panel title="Coherence quality mix" subtitle="Clusters grouped by coherence band">
          {coherenceBands.length ? (
            <DonutChart
              data={coherenceBands}
              height={260}
              centerValue={String(formatNumber(data.metadata.coherence_count))}
              centerLabel="clusters scored"
            />
          ) : (
            <EmptyState title="No coherence scores" />
          )}
        </Panel>

        <Panel
          title="Coherence vs purity"
          subtitle="Each point is a cluster"
          className="xl:col-span-2"
        >
          <ReactECharts option={scatterOption} style={{ height: 300 }} notMerge />
        </Panel>
      </div>

      <Panel title="Coherence by cluster" subtitle="Semantic tightness of each narrative cluster">
        {coherenceRows.length ? (
          <ReactECharts option={coherenceBarOption} style={{ height: 300 }} notMerge />
        ) : (
          <EmptyState title="No coherence scores" />
        )}
      </Panel>

      <div className="grid gap-5 xl:grid-cols-[1.5fr_1fr]">
        <Panel
          title="Label audit"
          subtitle="Generated labels with volumes and subclusters"
          bodyClassName="p-0"
        >
          {audits.length ? (
            <div className="max-h-[420px] overflow-auto">
              <table className="w-full text-left text-sm">
                <thead className="sticky top-0 bg-surface-3/95 text-xs uppercase tracking-wider text-ink-faint backdrop-blur">
                  <tr>
                    <th className="px-6 py-3 font-medium">Cluster</th>
                    <th className="px-3 py-3 font-medium">Label</th>
                    <th className="px-3 py-3 font-medium">Volume</th>
                    <th className="px-6 py-3 font-medium">Subclusters</th>
                  </tr>
                </thead>
                <tbody>
                  {audits.map((audit) => (
                    <tr key={audit.cluster} className="border-t border-line/60 hover:bg-surface-3/30">
                      <td className="px-6 py-3.5 font-mono text-ink-muted">#{audit.cluster}</td>
                      <td className="px-3 py-3.5 leading-6">{truncate(audit.label, 70)}</td>
                      <td className="px-3 py-3.5 font-mono">{formatNumber(audit.volume)}</td>
                      <td className="px-6 py-3.5 font-mono">{audit.subclusters.length}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-6">
              <EmptyState title="No label audit data" />
            </div>
          )}
        </Panel>

        <Panel title="Forecast validation" subtitle="Hit rates against actual top narratives">
          <dl className="space-y-4 text-sm">
            <div className="flex justify-between gap-3 border-b border-line/60 pb-3">
              <dt className="text-ink-muted">Vanguard hits</dt>
              <dd className="font-mono text-lg text-ink">
                {formatNumber(Number(data.forecast_evaluation?.vanguard_hits ?? 0))}
              </dd>
            </div>
            <div className="flex justify-between gap-3 border-b border-line/60 pb-3">
              <dt className="text-ink-muted">Baseline hits</dt>
              <dd className="font-mono text-lg text-ink">
                {formatNumber(Number(data.forecast_evaluation?.baseline_hits ?? 0))}
              </dd>
            </div>
            <div className="flex justify-between gap-3 border-b border-line/60 pb-3">
              <dt className="text-ink-muted">Correlation samples</dt>
              <dd className="font-mono text-lg text-ink">
                {formatNumber(Number(data.correlation?.vanguard_samples ?? 0))}
              </dd>
            </div>
            <div className="flex justify-between gap-3">
              <dt className="text-ink-muted">Clusters audited</dt>
              <dd className="font-mono text-lg text-ink">
                {formatNumber(data.metadata.label_audit_count)}
              </dd>
            </div>
          </dl>
          <p className="mt-5 rounded-xl border border-line/70 bg-surface/60 px-4 py-3 text-xs leading-6 text-ink-faint">
            {temporalBuckets < 2
              ? 'Only one temporal bucket was available before the latest analytics rebuild. Re-run analytics after the hourly/day auto-resolution fix to populate forecast validation.'
              : 'Forecast validation compares ranked forecast scores against recent growth in the same timeline.'}
          </p>
          <p className="mt-3 font-mono text-xs text-ink-faint">
            avg coherence {formatScore(avgCoherence)} · avg purity {formatScore(avgPurity, 0)}
          </p>
        </Panel>
      </div>
    </div>
  )
}
