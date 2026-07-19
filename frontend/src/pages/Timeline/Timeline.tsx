import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ReactECharts from 'echarts-for-react'
import { CalendarClock, Flame, TrendingUp } from 'lucide-react'
import mediaStream from '@/assets/media-stream.png'
import { getTimeline } from '@/api/timeline'
import { getNarrativeSummary } from '@/api/narrative'
import { PageHeader } from '@/components/shared/PageHeader'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Panel } from '@/components/shared/Panel'
import { StatCard } from '@/components/shared/StatCard'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { cn, formatNumber, truncate } from '@/lib/utils'

function prettyDate(raw: string) {
  const cleaned = raw.replace(/-+$/, '').trim()
  if (!cleaned || cleaned.toLowerCase().startsWith('unknown')) return 'Undated'

  if (cleaned.includes('T')) {
    const date = new Date(cleaned)
    if (!Number.isNaN(date.getTime())) {
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    }
  }

  const parts = cleaned.split('-')
  if (parts.length >= 3) {
    const date = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]))
    if (!Number.isNaN(date.getTime())) {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    }
  }

  if (parts.length >= 2) {
    const date = new Date(Number(parts[0]), Number(parts[1]) - 1)
    if (!Number.isNaN(date.getTime())) {
      return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    }
  }

  return cleaned
}

export function Timeline() {
  const [filter, setFilter] = useState('')
  const [expanded, setExpanded] = useState<string | null>(null)

  const timelineQuery = useQuery({
    queryKey: ['timeline'],
    queryFn: getTimeline,
  })
  const narrativeQuery = useQuery({
    queryKey: ['narrative-summary'],
    queryFn: getNarrativeSummary,
  })

  const volumeEntries = useMemo(() => {
    const timeline = timelineQuery.data?.timeline ?? {}
    const q = filter.trim().toLowerCase()
    return Object.entries(timeline)
      .filter(([label]) => !q || label.toLowerCase().includes(q))
      .map(([label, days]) => {
        const points = Object.entries(days)
          .map(([date, count]) => ({ date, count: Number(count) || 0 }))
          .sort((a, b) => a.date.localeCompare(b.date))
        const total = points.reduce((sum, item) => sum + item.count, 0)
        return { label, points, total }
      })
      .filter((item) => item.points.length > 0)
      .sort((a, b) => b.total - a.total)
  }, [timelineQuery.data, filter])

  const evolutionEntries = useMemo(() => {
    const evolution = timelineQuery.data?.evolution ?? {}
    const q = filter.trim().toLowerCase()
    return Object.entries(evolution)
      .filter(([label]) => !q || label.toLowerCase().includes(q))
      .map(([label, events]) => ({
        label,
        events: [...events].sort((a, b) => a.date.localeCompare(b.date)),
      }))
      .sort((a, b) => b.events.length - a.events.length)
  }, [timelineQuery.data, filter])

  const chartOption = useMemo(() => {
    const top = volumeEntries.slice(0, 8)
    const allBuckets = Array.from(
      new Set(top.flatMap((item) => item.points.map((point) => point.date))),
    ).sort()

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#111a2c',
        borderColor: '#243149',
        textStyle: { color: '#e8eef7', fontSize: 12 },
      },
      legend: {
        type: 'scroll',
        top: 0,
        textStyle: { color: '#8b9bb4', fontSize: 11 },
      },
      grid: { left: 8, right: 16, top: 40, bottom: 8, containLabel: true },
      xAxis: {
        type: 'category',
        data: allBuckets.map(prettyDate),
        axisLabel: { color: '#5a6a84', fontSize: 10 },
        axisLine: { lineStyle: { color: '#243149' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#5a6a84', fontSize: 10 },
        splitLine: { lineStyle: { color: '#182338' } },
      },
      series: top.map((item) => {
        const lookup = Object.fromEntries(item.points.map((point) => [point.date, point.count]))
        return {
          name: truncate(item.label, 28),
          type: 'line',
          smooth: true,
          showSymbol: allBuckets.length <= 12,
          data: allBuckets.map((bucket) => lookup[bucket] ?? 0),
        }
      }),
    }
  }, [volumeEntries])

  const totalEvents = useMemo(
    () => evolutionEntries.reduce((sum, item) => sum + item.events.length, 0),
    [evolutionEntries],
  )
  const bucketCount = volumeEntries[0]?.points.length ?? 0

  if (timelineQuery.isLoading || narrativeQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-56" />
        <Skeleton className="h-96" />
      </div>
    )
  }

  if (timelineQuery.isError) {
    return <ErrorState message="Failed to load temporal timeline." />
  }

  const data = timelineQuery.data!
  const forecasts = Array.isArray(data.forecasts) ? data.forecasts : []
  const warnings = Array.isArray(data.early_warnings) ? data.early_warnings : []
  const spikes = Array.isArray(data.spikes) ? data.spikes : []

  return (
    <div className="space-y-7">
      <PageHeader
        title="Timeline"
        description="How narratives evolved over time, with spikes, forecasts, and early warnings."
        image={mediaStream}
        action={
          <Badge tone="info">
            {bucketCount} temporal {bucketCount === 1 ? 'bucket' : 'buckets'}
          </Badge>
        }
      />

      <div className="grid gap-5 sm:grid-cols-3">
        <StatCard
          label="Narratives tracked"
          value={formatNumber(volumeEntries.length || evolutionEntries.length)}
          hint={`${formatNumber(totalEvents)} evolution snapshots`}
          icon={CalendarClock}
          tone="blue"
        />
        <StatCard
          label="Volume spikes"
          value={formatNumber(spikes.length)}
          hint="Sudden activity bursts"
          icon={Flame}
          tone="warn"
          delay={0.05}
        />
        <StatCard
          label="Forecasts & warnings"
          value={`${formatNumber(forecasts.length)} / ${formatNumber(warnings.length)}`}
          hint="Active forecasts / early warnings"
          icon={TrendingUp}
          tone="accent"
          delay={0.1}
        />
      </div>

      <Panel
        title="Narrative activity"
        subtitle="Volume over time for the largest narratives"
        action={
          <Input
            className="h-9 w-64 rounded-lg"
            placeholder="Filter narratives…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        }
      >
        {volumeEntries.length ? (
          <ReactECharts option={chartOption} style={{ height: 360 }} notMerge />
        ) : (
          <EmptyState
            title="No timeline volume data"
            description="Populated from analytics/timeline.json after a pipeline run."
          />
        )}
      </Panel>

      <Panel
        title="Narrative evolution"
        subtitle="Snapshots of how each narrative developed across temporal buckets"
      >
        {evolutionEntries.length ? (
          <div className="space-y-4">
            {evolutionEntries.map(({ label, events }) => {
              const isOpen = expanded === label
              return (
                <div
                  key={label}
                  className="overflow-hidden rounded-xl border border-line/70 bg-surface/50"
                >
                  <button
                    type="button"
                    className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition-colors hover:bg-surface-3/30"
                    onClick={() => setExpanded(isOpen ? null : label)}
                  >
                    <p className="min-w-0 flex-1 text-sm font-medium leading-6 text-ink">
                      {truncate(label, 110)}
                    </p>
                    <div className="flex shrink-0 items-center gap-2">
                      <Badge tone="info">{events.length} snapshots</Badge>
                      <span
                        className={cn(
                          'text-ink-faint transition-transform',
                          isOpen && 'rotate-180',
                        )}
                      >
                        ▾
                      </span>
                    </div>
                  </button>

                  {isOpen ? (
                    <div className="border-t border-line/60 px-5 py-5">
                      <ol className="relative space-y-6 border-l border-line/70 pl-6">
                        {events.map((event, index) => (
                          <li key={`${event.date}-${index}`} className="relative">
                            <span className="absolute -left-[30px] top-1 h-3 w-3 rounded-full border-2 border-surface bg-accent" />
                            <p className="font-mono text-xs text-accent">
                              {prettyDate(event.date)}
                            </p>
                            <p className="mt-1.5 text-sm leading-7 text-ink-muted">
                              {event.summary}
                            </p>
                          </li>
                        ))}
                      </ol>
                    </div>
                  ) : null}
                </div>
              )
            })}
          </div>
        ) : (
          <EmptyState
            title="No evolution data"
            description="Evolution appears after analytics rebuild. Single-day corpora now use hourly buckets automatically."
          />
        )}
      </Panel>

      <div className="grid gap-5 xl:grid-cols-2">
        <Panel
          title="Early warnings"
          subtitle="Signals crossing alert thresholds, ranked by warning score"
        >
          {warnings.length ? (
            <ul className="space-y-2.5">
              {warnings.slice(0, 12).map((item, index) => (
                <li
                  key={index}
                  className="rounded-xl border border-warn/25 bg-warn/5 px-4 py-3.5"
                >
                  <div className="flex items-start justify-between gap-3">
                    <p className="min-w-0 flex-1 text-sm font-medium leading-6 text-ink">
                      {truncate(item.narrative, 90)}
                    </p>
                    <span className="shrink-0 rounded-lg bg-warn/15 px-2.5 py-1 font-mono text-xs font-semibold text-warn">
                      {Number(item.warning_score ?? 0).toFixed(2)}
                    </span>
                  </div>
                  <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                    {(item.reasons ?? []).map((reason) => (
                      <Badge key={reason} tone="warn">
                        {reason}
                      </Badge>
                    ))}
                    <span className="ml-auto font-mono text-xs text-ink-faint">
                      vol {formatNumber(item.volume)}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              title="No early warnings"
              description="Warnings appear when forecast momentum crosses thresholds."
            />
          )}
        </Panel>

        <Panel
          title="Forecasts"
          subtitle="Projected trajectories — slope, momentum, influence, emergence"
        >
          {forecasts.length ? (
            <ul className="space-y-2.5">
              {forecasts.slice(0, 12).map((item, index) => (
                <li
                  key={index}
                  className="rounded-xl border border-line bg-surface/60 px-4 py-3.5"
                >
                  <div className="flex items-start justify-between gap-3">
                    <p className="min-w-0 flex-1 text-sm font-medium leading-6 text-ink">
                      {truncate(item.narrative, 90)}
                    </p>
                    <span
                      className={cn(
                        'shrink-0 rounded-lg px-2.5 py-1 font-mono text-xs font-semibold',
                        item.score >= 1
                          ? 'bg-accent/15 text-accent'
                          : 'bg-surface-3/60 text-ink-muted',
                      )}
                    >
                      {Number(item.score ?? 0).toFixed(2)}
                    </span>
                  </div>
                  <div className="mt-2.5 grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-xs text-ink-faint sm:grid-cols-4">
                    <span>slope {Number(item.slope ?? 0).toFixed(1)}</span>
                    <span>mom {Number(item.momentum ?? 0).toFixed(2)}x</span>
                    <span>infl {Number(item.influence ?? 0).toFixed(2)}</span>
                    <span>vol {formatNumber(item.current_volume)}</span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              title="No forecasts"
              description="Forecasts require populated timelines from the pipeline."
            />
          )}
        </Panel>
      </div>

      <Panel title="Detected spikes" subtitle="Narratives with sudden volume or momentum shifts">
        {spikes.length ? (
          <ul className="grid gap-2.5 md:grid-cols-2">
            {spikes.slice(0, 12).map((item, index) => (
              <li
                key={`${item.narrative}-${index}`}
                className="rounded-xl border border-line bg-surface/60 px-4 py-3.5"
              >
                <p className="text-sm font-medium leading-6 text-ink">
                  {truncate(item.narrative, 80)}
                </p>
                <div className="mt-2 flex flex-wrap gap-3 font-mono text-xs text-ink-faint">
                  <span>{prettyDate(item.day)}</span>
                  <span>count {formatNumber(item.count)}</span>
                  <span>mom {Number(item.momentum ?? 0).toFixed(2)}x</span>
                  <span>z {Number(item.z_score ?? 0).toFixed(2)}</span>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState title="No spikes detected for this corpus window" />
        )}
      </Panel>
    </div>
  )
}
