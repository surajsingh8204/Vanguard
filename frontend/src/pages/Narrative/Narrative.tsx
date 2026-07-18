import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { GitBranch, Layers, Radar } from 'lucide-react'
import narrativeAnalysis from '@/assets/narrative-analysis.png'
import { getNarrativeClusters, getNarrativeSummary } from '@/api/narrative'
import { PageHeader } from '@/components/shared/PageHeader'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Panel } from '@/components/shared/Panel'
import { StatCard } from '@/components/shared/StatCard'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { cn, formatNumber, truncate } from '@/lib/utils'

export function Narrative() {
  const [query, setQuery] = useState('')
  const [minSize, setMinSize] = useState(0)
  const [selected, setSelected] = useState<string | null>(null)

  const summaryQuery = useQuery({
    queryKey: ['narrative-summary'],
    queryFn: getNarrativeSummary,
  })

  const clusterQuery = useQuery({
    queryKey: ['narrative-clusters', selected],
    queryFn: () =>
      getNarrativeClusters({
        page: 1,
        limit: 1,
        cluster: selected ?? undefined,
      }),
    enabled: Boolean(selected),
  })

  const rows = useMemo(() => {
    const stats = summaryQuery.data?.statistics ?? {}
    const labels = summaryQuery.data?.cluster_labels ?? {}
    return Object.entries(stats)
      .map(([id, item]) => ({
        id,
        label: labels[id] || item.label,
        size: item.size,
      }))
      .filter((row) => row.size >= minSize)
      .filter((row) => {
        if (!query.trim()) return true
        const q = query.toLowerCase()
        return row.id.includes(q) || row.label.toLowerCase().includes(q)
      })
      .sort((a, b) => b.size - a.size)
  }, [summaryQuery.data, query, minSize])

  const maxSize = rows.length ? rows[0].size : 1
  const selectedDocs = clusterQuery.data?.items?.[0]?.items ?? []

  const relatedSubclusters = useMemo(() => {
    if (!selected) return []
    const subclusterLabels = summaryQuery.data?.subcluster_labels ?? {}
    const entry = subclusterLabels[selected]

    // Nested shape from artifacts: { "9": { "0": "label", "1": "label" } }
    if (entry && typeof entry === 'object' && !Array.isArray(entry)) {
      return Object.entries(entry)
        .map(([subId, label]) => ({
          id: `${selected}-${subId}`,
          label: String(label ?? ''),
        }))
        .filter((item) => item.label && item.label !== 'Unknown')
    }

    // Flat fallback: { "9-0": "label" }
    return Object.entries(subclusterLabels)
      .filter(([key]) => key.startsWith(`${selected}-`) || key === selected)
      .map(([key, label]) => ({
        id: key,
        label: typeof label === 'string' ? label : '',
      }))
      .filter((item) => item.label)
  }, [selected, summaryQuery.data])

  if (summaryQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-72" />
        <Skeleton className="h-96" />
      </div>
    )
  }

  if (summaryQuery.isError) {
    return <ErrorState message="Failed to load narrative summary." />
  }

  const meta = summaryQuery.data?.metadata

  return (
    <div className="space-y-7">
      <PageHeader
        title="Narrative Intelligence"
        description="Browse clustered narratives, their volumes, and supporting source documents."
        image={narrativeAnalysis}
      />

      <div className="grid gap-5 sm:grid-cols-3">
        <StatCard
          label="Narrative clusters"
          value={formatNumber(meta?.cluster_count)}
          icon={GitBranch}
          tone="accent"
        />
        <StatCard
          label="Subclusters"
          value={formatNumber(meta?.subcluster_count)}
          icon={Layers}
          tone="blue"
          delay={0.05}
        />
        <StatCard
          label="Signals (warnings / emerging)"
          value={`${formatNumber(meta?.warnings?.length ?? 0)} / ${formatNumber(meta?.top_insights?.length ?? 0)}`}
          icon={Radar}
          tone="warn"
          delay={0.1}
        />
      </div>

      <div className="flex flex-wrap gap-3">
        <Input
          className="h-10 max-w-sm rounded-lg"
          placeholder="Filter by label or cluster id…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Input
          className="h-10 max-w-[150px] rounded-lg"
          type="number"
          min={0}
          placeholder="Min volume"
          value={minSize || ''}
          onChange={(e) => setMinSize(Number(e.target.value) || 0)}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.15fr_1fr]">
        <Panel
          title={`Narratives (${rows.length})`}
          subtitle="Sorted by volume · click to inspect documents"
          bodyClassName="p-0"
        >
          {rows.length ? (
            <div className="max-h-[620px] overflow-auto">
              <table className="w-full text-left text-sm">
                <thead className="sticky top-0 bg-surface-3/95 text-xs uppercase tracking-wider text-ink-faint backdrop-blur">
                  <tr>
                    <th className="px-6 py-3.5 font-medium">ID</th>
                    <th className="px-3 py-3.5 font-medium">Label</th>
                    <th className="px-6 py-3.5 font-medium">Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr
                      key={row.id}
                      className={cn(
                        'cursor-pointer border-t border-line/60 transition-colors hover:bg-surface-3/40',
                        selected === row.id && 'bg-accent/5',
                      )}
                      onClick={() => setSelected(row.id)}
                    >
                      <td className="px-6 py-4 font-mono text-ink-muted">#{row.id}</td>
                      <td className="px-3 py-4 leading-6">{truncate(row.label, 84)}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2.5">
                          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-surface-3">
                            <div
                              className="h-full rounded-full bg-accent-2"
                              style={{ width: `${(row.size / maxSize) * 100}%` }}
                            />
                          </div>
                          <span className="font-mono text-xs">{row.size}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-6">
              <EmptyState title="No narratives match filters" />
            </div>
          )}
        </Panel>

        <Panel
          title="Narrative detail"
          subtitle={selected ? `Cluster #${selected}` : 'Select a narrative on the left'}
          action={
            selected ? (
              <Button variant="secondary" size="sm" onClick={() => setSelected(null)}>
                Clear
              </Button>
            ) : undefined
          }
        >
          {!selected ? (
            <EmptyState
              title="Select a narrative"
              description="Source documents and subclusters will appear here."
            />
          ) : clusterQuery.isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-20" />
              <Skeleton className="h-20" />
              <Skeleton className="h-20" />
            </div>
          ) : clusterQuery.isError ? (
            <ErrorState message="Failed to load cluster documents." />
          ) : (
            <div className="space-y-5">
              {relatedSubclusters.length ? (
                <div>
                  <p className="mb-2 text-xs font-medium uppercase tracking-wider text-ink-faint">
                    Subclusters
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {relatedSubclusters.map((item) => (
                      <Badge key={item.id} tone="info">
                        {truncate(item.label, 44)}
                      </Badge>
                    ))}
                  </div>
                </div>
              ) : null}

              {selectedDocs.length === 0 ? (
                <EmptyState title="No documents returned for this cluster" />
              ) : (
                <div className="max-h-[520px] space-y-3.5 overflow-auto pr-1">
                  {selectedDocs.slice(0, 20).map((doc, index) => {
                    const title = String(doc.title ?? doc.source ?? `Document ${index + 1}`)
                    const text = String(doc.text ?? doc.content ?? '')
                    const source = String(doc.source ?? doc.url ?? '—')
                    const date = String(doc.date ?? doc.published_at ?? '')
                    return (
                      <article
                        key={`${selected}-${index}`}
                        className="rounded-xl border border-line/70 bg-surface/60 px-5 py-4"
                      >
                        <p className="text-sm font-medium leading-6 text-ink">
                          {truncate(title, 100)}
                        </p>
                        <p className="mt-1 text-xs text-ink-faint">
                          {truncate(source, 60)}
                          {date && date !== 'Unknown Date' ? ` · ${date}` : ''}
                        </p>
                        {text ? (
                          <p className="mt-2.5 text-sm leading-7 text-ink-muted">
                            {truncate(text, 300)}
                          </p>
                        ) : null}
                      </article>
                    )
                  })}
                  {selectedDocs.length > 20 ? (
                    <p className="text-xs text-ink-faint">
                      Showing 20 of {selectedDocs.length} documents.
                    </p>
                  ) : null}
                </div>
              )}
            </div>
          )}
        </Panel>
      </div>
    </div>
  )
}
