import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileJson, X } from 'lucide-react'
import socialMesh from '@/assets/social-mesh.png'
import { getLatestReports, getReportContent, getReportHistory } from '@/api/reports'
import { PageHeader } from '@/components/shared/PageHeader'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Panel } from '@/components/shared/Panel'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { cn, formatDate } from '@/lib/utils'

export function Reports() {
  const [reportType, setReportType] = useState('')
  const [page, setPage] = useState(1)
  const [showHistory, setShowHistory] = useState(false)
  const [openFile, setOpenFile] = useState<string | null>(null)

  const query = useQuery({
    queryKey: ['reports', showHistory ? 'history' : 'latest', page, reportType],
    queryFn: () =>
      showHistory
        ? getReportHistory({
            page,
            limit: 50,
            report_type: reportType.trim() || undefined,
          })
        : getLatestReports({
            page,
            limit: 25,
            report_type: reportType.trim() || undefined,
          }),
  })

  const contentQuery = useQuery({
    queryKey: ['report-content', openFile],
    queryFn: () => getReportContent(openFile!),
    enabled: openFile != null,
  })

  const types = useMemo(() => {
    const items = query.data?.items ?? []
    return Array.from(new Set(items.map((item) => item.report_type))).sort()
  }, [query.data])

  if (query.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-96" />
      </div>
    )
  }

  if (query.isError) {
    return <ErrorState message="Failed to load reports." />
  }

  const data = query.data!

  return (
    <div className="space-y-7">
      <PageHeader
        title="Reports"
        description="Generated evaluation and intelligence reports. Click a report to read its contents."
        image={socialMesh}
        action={
          <div className="flex gap-2">
            <Button
              size="sm"
              variant={showHistory ? 'secondary' : 'default'}
              onClick={() => {
                setShowHistory(false)
                setPage(1)
              }}
            >
              Latest
            </Button>
            <Button
              size="sm"
              variant={showHistory ? 'default' : 'secondary'}
              onClick={() => {
                setShowHistory(true)
                setPage(1)
              }}
            >
              History
            </Button>
          </div>
        }
      />

      <div className="flex flex-wrap items-center gap-3">
        <Input
          className="h-9 max-w-xs rounded-lg"
          placeholder="Filter report type…"
          value={reportType}
          onChange={(e) => {
            setReportType(e.target.value)
            setPage(1)
          }}
        />
        <Badge>{data.total} reports</Badge>
        {types.slice(0, 6).map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => {
              setReportType(reportType === type ? '' : type)
              setPage(1)
            }}
            className={cn(
              'rounded-lg border px-2.5 py-1.5 text-xs transition-colors',
              reportType === type
                ? 'border-accent/40 bg-accent/10 text-accent'
                : 'border-line text-ink-muted hover:text-ink',
            )}
          >
            {type}
          </button>
        ))}
      </div>

      <div className={cn('grid gap-5', openFile ? 'xl:grid-cols-[1fr_1.2fr]' : '')}>
        <Panel bodyClassName="p-0">
          {data.items.length ? (
            <div className="max-h-[620px] overflow-auto">
              <table className="w-full text-left text-sm">
                <thead className="sticky top-0 bg-surface-3/95 text-xs uppercase tracking-wider text-ink-faint backdrop-blur">
                  <tr>
                    <th className="px-6 py-3.5 font-medium">Type</th>
                    <th className="px-3 py-3.5 font-medium">Created</th>
                    <th className="px-6 py-3.5 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((item) => (
                    <tr
                      key={item.filename}
                      className={cn(
                        'cursor-pointer border-t border-line/60 transition-colors hover:bg-surface-3/40',
                        openFile === item.filename && 'bg-accent/5',
                      )}
                      onClick={() => setOpenFile(item.filename)}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2.5">
                          <FileJson className="h-4 w-4 shrink-0 text-accent-2" />
                          <div>
                            <p className="font-medium text-ink">{item.report_type}</p>
                            <p className="mt-0.5 font-mono text-[11px] text-ink-faint">
                              {item.filename}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-3 py-4 text-xs text-ink-muted">
                        {formatDate(item.created_at)}
                      </td>
                      <td className="px-6 py-4">
                        <Badge tone={item.status === 'available' ? 'ok' : 'warn'}>
                          {item.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-6">
              <EmptyState title="No reports found" />
            </div>
          )}
        </Panel>

        {openFile ? (
          <Panel
            title={contentQuery.data?.report_type ?? 'Report'}
            subtitle={openFile}
            action={
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setOpenFile(null)}
                aria-label="Close report"
              >
                <X className="h-4 w-4" />
              </Button>
            }
            bodyClassName="p-0"
          >
            {contentQuery.isLoading ? (
              <div className="space-y-3 p-6">
                <Skeleton className="h-6 w-1/2" />
                <Skeleton className="h-40" />
              </div>
            ) : contentQuery.isError ? (
              <div className="p-6">
                <ErrorState message="Failed to load report content." />
              </div>
            ) : (
              <pre className="max-h-[560px] overflow-auto whitespace-pre-wrap p-6 font-mono text-xs leading-6 text-ink-muted">
                {JSON.stringify(contentQuery.data?.content, null, 2)}
              </pre>
            )}
          </Panel>
        ) : null}
      </div>

      <div className="flex items-center justify-between">
        <p className="text-xs text-ink-faint">
          Page {data.page} of {Math.max(data.pages, 1)}
        </p>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="secondary"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            Previous
          </Button>
          <Button
            size="sm"
            variant="secondary"
            disabled={page >= data.pages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
