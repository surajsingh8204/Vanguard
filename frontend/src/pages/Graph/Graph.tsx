import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import CytoscapeComponent from 'react-cytoscapejs'
import ReactECharts from 'echarts-for-react'
import { ArrowRight } from 'lucide-react'
import aiGlobe from '@/assets/ai-globe.png'
import particleNetwork from '@/assets/particle-network.png'
import { getGraphNetwork, getGraphSummary } from '@/api/graph'
import { PageHeader } from '@/components/shared/PageHeader'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Panel } from '@/components/shared/Panel'
import { StatCard } from '@/components/shared/StatCard'
import { DonutChart, CHART_PALETTE } from '@/components/shared/DonutChart'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Circle, Share2, Users, Waypoints } from 'lucide-react'
import { formatNumber, formatScore, truncate } from '@/lib/utils'

export function Graph() {
  const [search, setSearch] = useState('')
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [hoverId, setHoverId] = useState<number | null>(null)

  const summaryQuery = useQuery({
    queryKey: ['graph-summary'],
    queryFn: getGraphSummary,
  })

  const networkQuery = useQuery({
    queryKey: ['graph-network'],
    queryFn: () => getGraphNetwork({ page: 1, limit: 500 }),
  })

  const communityByNode = useMemo(() => {
    const map = new Map<number, string>()
    Object.entries(summaryQuery.data?.communities ?? {}).forEach(([community, nodes]) => {
      nodes.forEach((node) => map.set(node, community))
    })
    return map
  }, [summaryQuery.data])

  const influencerById = useMemo(() => {
    const map = new Map<number, { score: number; volume: number }>()
    for (const item of summaryQuery.data?.influencers ?? []) {
      map.set(Number(item.id), { score: item.score, volume: item.volume })
    }
    return map
  }, [summaryQuery.data])

  const elements = useMemo(() => {
    const nodes = networkQuery.data?.nodes.items ?? []
    const edges = networkQuery.data?.edges.items ?? []
    const q = search.trim().toLowerCase()

    const filteredNodes = q
      ? nodes.filter(
          (n) => String(n.id).includes(q) || n.label.toLowerCase().includes(q),
        )
      : nodes
    const nodeIds = new Set(filteredNodes.map((n) => n.id))

    const communityKeys = Object.keys(summaryQuery.data?.communities ?? {})
    const maxVolume = Math.max(
      1,
      ...filteredNodes.map((n) => influencerById.get(n.id)?.volume ?? 0),
    )

    return [
      ...filteredNodes.map((node) => {
        const community = communityByNode.get(node.id)
        const colorIndex = community ? communityKeys.indexOf(community) : -1
        const volume = influencerById.get(node.id)?.volume ?? 0
        // Scale node size 30–72px by narrative volume.
        const size = 30 + Math.sqrt(volume / maxVolume) * 42
        return {
          data: {
            id: String(node.id),
            label: truncate(node.label, 42),
            fullLabel: node.label,
            size,
            color:
              colorIndex >= 0
                ? CHART_PALETTE[colorIndex % CHART_PALETTE.length]
                : '#5b8def',
          },
        }
      }),
      ...edges
        .filter((e) => nodeIds.has(e.source) && nodeIds.has(e.target))
        .map((edge, index) => ({
          data: {
            id: `e-${edge.source}-${edge.target}-${index}`,
            source: String(edge.source),
            target: String(edge.target),
            weight: edge.weight,
          },
        })),
    ]
  }, [networkQuery.data, search, communityByNode, summaryQuery.data, influencerById])

  const communityDonut = useMemo(() => {
    return Object.entries(summaryQuery.data?.communities ?? {})
      .map(([community, nodes]) => ({
        name: `Community ${community}`,
        value: nodes.length,
      }))
      .sort((a, b) => b.value - a.value)
  }, [summaryQuery.data])

  const centralityOption = useMemo(() => {
    const pagerank = summaryQuery.data?.centrality?.pagerank ?? {}
    const betweenness = summaryQuery.data?.centrality?.betweenness ?? {}
    const rows = Object.entries(pagerank)
      .map(([id, value]) => ({
        id,
        pagerank: value,
        betweenness: betweenness[id] ?? 0,
      }))
      .sort((a, b) => b.pagerank - a.pagerank)
      .slice(0, 12)

    return {
      backgroundColor: 'transparent',
      grid: { left: 8, right: 16, top: 36, bottom: 8, containLabel: true },
      legend: {
        top: 0,
        textStyle: { color: '#8b9bb4', fontSize: 11 },
        itemWidth: 12,
        itemHeight: 8,
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#111a2c',
        borderColor: '#243149',
        textStyle: { color: '#e8eef7', fontSize: 12 },
      },
      xAxis: {
        type: 'category',
        data: rows.map((r) => `#${r.id}`),
        axisLabel: { color: '#8b9bb4', fontSize: 10, fontFamily: 'IBM Plex Mono' },
        axisLine: { lineStyle: { color: '#243149' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#5a6a84', fontSize: 10 },
        splitLine: { lineStyle: { color: '#182338' } },
      },
      series: [
        {
          name: 'PageRank',
          type: 'bar',
          data: rows.map((r) => r.pagerank),
          itemStyle: { color: '#5b8def', borderRadius: [4, 4, 0, 0] },
          barWidth: 10,
        },
        {
          name: 'Betweenness',
          type: 'bar',
          data: rows.map((r) => r.betweenness),
          itemStyle: { color: '#3ddc97', borderRadius: [4, 4, 0, 0] },
          barWidth: 10,
        },
      ],
    }
  }, [summaryQuery.data])

  const selectedNode = useMemo(() => {
    if (selectedId == null) return null
    return networkQuery.data?.nodes.items.find((n) => n.id === selectedId) ?? null
  }, [selectedId, networkQuery.data])

  const selectedEdges = useMemo(() => {
    if (selectedId == null) return []
    return (networkQuery.data?.edges.items ?? []).filter(
      (e) => e.source === selectedId || e.target === selectedId,
    )
  }, [selectedId, networkQuery.data])

  const hoverNode = useMemo(() => {
    if (hoverId == null) return null
    return networkQuery.data?.nodes.items.find((n) => n.id === hoverId) ?? null
  }, [hoverId, networkQuery.data])

  const hoverEdgeCount = useMemo(() => {
    if (hoverId == null) return 0
    return (networkQuery.data?.edges.items ?? []).filter(
      (e) => e.source === hoverId || e.target === hoverId,
    ).length
  }, [hoverId, networkQuery.data])

  const communityLegend = useMemo(() => {
    const communityKeys = Object.keys(summaryQuery.data?.communities ?? {})
    return Object.entries(summaryQuery.data?.communities ?? {})
      .map(([community, nodes]) => ({
        community,
        count: nodes.length,
        color: CHART_PALETTE[communityKeys.indexOf(community) % CHART_PALETTE.length],
      }))
      .sort((a, b) => b.count - a.count)
  }, [summaryQuery.data])

  if (summaryQuery.isLoading || networkQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-[520px]" />
      </div>
    )
  }

  if (summaryQuery.isError || networkQuery.isError) {
    return <ErrorState message="Failed to load graph data." />
  }

  const meta = summaryQuery.data?.metadata
  const influencers = summaryQuery.data?.influencers ?? []
  const mappings = summaryQuery.data?.influence_mappings ?? []
  const nodeLabels = new Map(
    (networkQuery.data?.nodes.items ?? []).map((n) => [n.id, n.label]),
  )

  return (
    <div className="space-y-7">
      <PageHeader
        title="Knowledge Graph"
        description="Narrative relationships, communities, and influence structure."
        image={aiGlobe}
      />

      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Nodes" value={formatNumber(meta?.node_count)} icon={Circle} tone="blue" />
        <StatCard
          label="Edges"
          value={formatNumber(meta?.edge_count)}
          icon={Share2}
          tone="accent"
          delay={0.05}
        />
        <StatCard
          label="Communities"
          value={formatNumber(meta?.community_count)}
          icon={Users}
          tone="blue"
          delay={0.1}
        />
        <StatCard
          label="Influencers"
          value={formatNumber(influencers.length)}
          icon={Waypoints}
          tone="accent"
          delay={0.15}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.6fr_1fr]">
        <Panel
          title="Network view"
          subtitle="Color = community · size = narrative volume · edge label = similarity weight"
          action={
            <Input
              className="h-9 w-56 rounded-lg"
              placeholder="Filter by id or label"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          }
          bodyClassName="p-0"
        >
          {elements.length ? (
            <div className="relative overflow-hidden">
              <img
                src={particleNetwork}
                alt=""
                aria-hidden
                className="pointer-events-none absolute inset-0 h-full w-full object-cover opacity-30 [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_85%)]"
              />
              <CytoscapeComponent
                elements={elements}
                style={{ width: '100%', height: 600, position: 'relative', zIndex: 1 }}
                layout={{
                  name: 'cose',
                  animate: false,
                  nodeRepulsion: 400000,
                  idealEdgeLength: 140,
                  padding: 60,
                }}
                stylesheet={[
                  {
                    selector: 'node',
                    style: {
                      label: 'data(label)',
                      color: '#c6d2e4',
                      'background-color': 'data(color)',
                      'border-color': '#0b1220',
                      'border-width': 2,
                      'font-size': '9px',
                      'font-family': 'IBM Plex Sans, sans-serif',
                      'text-valign': 'bottom',
                      'text-halign': 'center',
                      'text-margin-y': 6,
                      'text-wrap': 'wrap',
                      'text-max-width': '110px',
                      'text-background-color': '#0b1220',
                      'text-background-opacity': 0.75,
                      'text-background-padding': '2px',
                      'text-background-shape': 'roundrectangle',
                      width: 'data(size)',
                      height: 'data(size)',
                    },
                  },
                  {
                    selector: 'edge',
                    style: {
                      width: 'mapData(weight, 0.3, 0.7, 1.5, 5)',
                      'line-color': '#3b4d70',
                      'curve-style': 'bezier',
                      opacity: 0.75,
                      label: 'data(weight)',
                      'font-size': '8px',
                      color: '#5a6a84',
                      'text-background-color': '#0b1220',
                      'text-background-opacity': 0.8,
                      'text-background-padding': '1px',
                    },
                  },
                  {
                    selector: 'node:selected',
                    style: {
                      'border-color': '#3ddc97',
                      'border-width': 4,
                    },
                  },
                ] as never}
                cy={(cy) => {
                  cy.on('tap', 'node', (event) => {
                    setSelectedId(Number(event.target.id()))
                  })
                  cy.on('mouseover', 'node', (event) => {
                    setHoverId(Number(event.target.id()))
                  })
                  cy.on('mouseout', 'node', () => setHoverId(null))
                }}
              />

              {hoverNode ? (
                <div className="pointer-events-none absolute left-4 top-4 z-10 w-80 rounded-xl border border-line bg-surface/95 px-4 py-3.5 shadow-xl backdrop-blur">
                  <div className="flex items-center gap-2">
                    <Badge tone="info">#{hoverNode.id}</Badge>
                    <Badge>community {communityByNode.get(hoverNode.id) ?? '—'}</Badge>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-ink">
                    {truncate(hoverNode.label, 140)}
                  </p>
                  <p className="mt-1.5 font-mono text-xs text-ink-faint">
                    influence {formatScore(influencerById.get(hoverNode.id)?.score ?? null, 2)} ·
                    volume {formatNumber(influencerById.get(hoverNode.id)?.volume ?? null)} ·
                    {' '}{hoverEdgeCount} connection{hoverEdgeCount === 1 ? '' : 's'}
                  </p>
                </div>
              ) : (
                <div className="pointer-events-none absolute left-4 top-4 z-10 rounded-lg border border-line/70 bg-surface/80 px-3 py-2 text-xs text-ink-faint backdrop-blur">
                  Hover a node for details · click to pin · scroll to zoom · drag to pan
                </div>
              )}

              <div className="absolute bottom-4 left-4 z-10 flex max-w-[85%] flex-wrap gap-x-4 gap-y-1.5 rounded-lg border border-line/70 bg-surface/85 px-3.5 py-2.5 backdrop-blur">
                {communityLegend.map((item) => (
                  <span key={item.community} className="flex items-center gap-1.5 text-[11px] text-ink-muted">
                    <span
                      className="h-2.5 w-2.5 rounded-full"
                      style={{ background: item.color }}
                    />
                    community {item.community} ({item.count})
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-6">
              <EmptyState title="No graph nodes available" />
            </div>
          )}
        </Panel>

        <div className="space-y-5">
          <Panel title="Communities" subtitle="Cluster groups by shared structure">
            {communityDonut.length ? (
              <DonutChart
                data={communityDonut}
                height={240}
                centerValue={String(meta?.community_count ?? 0)}
                centerLabel="communities"
              />
            ) : (
              <EmptyState title="No communities detected" />
            )}
          </Panel>

          <Panel title="Selected node" subtitle="Click a node in the network">
            {!selectedNode ? (
              <p className="py-6 text-center text-sm text-ink-faint">Nothing selected</p>
            ) : (
              <div className="space-y-4 text-sm">
                <div className="flex items-center gap-2">
                  <Badge tone="info">#{selectedNode.id}</Badge>
                  <Badge>community {communityByNode.get(selectedNode.id) ?? '—'}</Badge>
                </div>
                <p className="leading-6 text-ink">{selectedNode.label}</p>
                <div>
                  <p className="mb-2 text-xs uppercase tracking-wider text-ink-faint">
                    Connections ({selectedEdges.length})
                  </p>
                  <div className="max-h-48 space-y-2 overflow-auto pr-1">
                    {selectedEdges.map((edge) => {
                      const other = edge.source === selectedNode.id ? edge.target : edge.source
                      return (
                        <div
                          key={`${edge.source}-${edge.target}`}
                          className="rounded-lg border border-line/70 bg-surface/60 px-3 py-2.5 text-xs leading-5"
                        >
                          <span className="font-mono text-accent-2">#{other}</span>{' '}
                          <span className="text-ink-muted">
                            {truncate(nodeLabels.get(other) ?? '', 56)}
                          </span>
                          <span className="ml-1 font-mono text-ink-faint">
                            w={formatScore(edge.weight, 2)}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            )}
          </Panel>
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <Panel title="Centrality" subtitle="PageRank vs betweenness for the most central narratives">
          <ReactECharts option={centralityOption} style={{ height: 320 }} notMerge />
        </Panel>

        <Panel title="Influence rankings" subtitle="Composite influence per narrative" bodyClassName="p-0">
          <div className="max-h-[360px] overflow-auto">
            <table className="w-full text-left text-sm">
              <thead className="sticky top-0 bg-surface-3/95 text-xs uppercase tracking-wider text-ink-faint backdrop-blur">
                <tr>
                  <th className="px-6 py-3 font-medium">ID</th>
                  <th className="px-3 py-3 font-medium">Narrative</th>
                  <th className="px-3 py-3 font-medium">Score</th>
                  <th className="px-6 py-3 font-medium">Volume</th>
                </tr>
              </thead>
              <tbody>
                {influencers.map((item) => (
                  <tr key={item.id} className="border-t border-line/60 hover:bg-surface-3/30">
                    <td className="px-6 py-3 font-mono text-ink-muted">#{item.id}</td>
                    <td className="px-3 py-3 leading-6">{truncate(item.label, 56)}</td>
                    <td className="px-3 py-3">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-16 overflow-hidden rounded-full bg-surface-3">
                          <div
                            className="h-full rounded-full bg-accent-2"
                            style={{ width: `${Math.min(item.score * 100, 100)}%` }}
                          />
                        </div>
                        <span className="font-mono text-xs">{formatScore(item.score, 2)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-3 font-mono">{formatNumber(item.volume)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>

      <Panel title="Influence chains" subtitle="Which narratives drive which others">
        {mappings.length ? (
          <div className="grid gap-4 lg:grid-cols-2">
            {mappings.slice(0, 8).map((mapping) => (
              <div
                key={mapping.source}
                className="rounded-xl border border-line/70 bg-surface/60 px-5 py-4"
              >
                <p className="text-sm font-medium leading-6 text-ink">
                  {truncate(mapping.source, 80)}
                </p>
                <ul className="mt-3 space-y-2">
                  {mapping.targets.map((target) => (
                    <li key={target.id} className="flex items-start gap-2.5 text-xs leading-5">
                      <ArrowRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-accent" />
                      <span className="min-w-0 flex-1 text-ink-muted">
                        <span className="font-mono text-accent-2">#{target.id}</span>{' '}
                        {truncate(target.label, 70)}
                      </span>
                      <span className="shrink-0 font-mono text-ink-faint">
                        {formatScore(target.weight, 2)}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState title="No influence mappings available" />
        )}
      </Panel>
    </div>
  )
}
