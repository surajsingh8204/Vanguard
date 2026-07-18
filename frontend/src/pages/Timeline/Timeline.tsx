import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
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
  const parts = cleaned.split('-')
  if (parts.length >= 2) {
    const [year, month] = parts
    const date = new Date(Number(year), Number(month) - 1)
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

  const totalEvents = useMemo(
    () => evolutionEntries.reduce((sum, item) => sum + item.events.length, 0),
    [evolutionEntries],
  )

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
      />

      <div className="grid gap-5 sm:grid-cols-3">
        <StatCard
          label="Narratives tracked"
          value={formatNumber(evolutionEntries.length)}
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
        title="Narrative evolution"
        subtitle="Monthly snapshots of how each narrative developed"
        action={
          <Input
            className="h-9 w-64 rounded-lg"
            placeholder="Filter narratives…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        }
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
                              {event.summary}…
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
            description="Populated from narrative/evolution.json after a pipeline run."
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
                      {item.warning_score.toFixed(2)}
                    </span>
                  </div>
                  <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                    {item.reasons?.map((reason) => (
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
                      {item.score.toFixed(2)}
                    </span>
                  </div>
                  <div className="mt-2.5 grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-xs text-ink-faint sm:grid-cols-4">
                    <span>slope {item.slope.toFixed(1)}</span>
                    <span>mom {item.momentum.toFixed(2)}x</span>
                    <span>infl {item.influence.toFixed(2)}</span>
                    <span>vol {formatNumber(item.current_volume)}</span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState
              title="No forecasts"
              description="Forecasts require populated daily timelines from the pipeline."
            />
          )}
        </Panel>
      </div>
    </div>
  )
}
