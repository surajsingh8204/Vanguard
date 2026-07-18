export function EmptyState({
  title,
  description,
}: {
  title: string
  description?: string
}) {
  return (
    <div className="flex min-h-[180px] flex-col items-center justify-center rounded-lg border border-dashed border-line bg-surface-2/50 px-6 py-10 text-center">
      <p className="text-sm font-medium text-ink">{title}</p>
      {description ? (
        <p className="mt-1 max-w-md text-sm text-ink-muted">{description}</p>
      ) : null}
    </div>
  )
}
