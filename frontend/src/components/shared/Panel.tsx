import { cn } from '@/lib/utils'

export function Panel({
  title,
  subtitle,
  action,
  className,
  bodyClassName,
  children,
}: {
  title?: string
  subtitle?: string
  action?: React.ReactNode
  className?: string
  bodyClassName?: string
  children: React.ReactNode
}) {
  return (
    <section
      className={cn(
        'rounded-2xl border border-line/80 bg-gradient-to-b from-surface-2/80 to-surface-2/40 shadow-[0_1px_0_rgba(255,255,255,0.03)_inset]',
        className,
      )}
    >
      {title ? (
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line/60 px-6 py-4">
          <div>
            <h2 className="text-sm font-semibold tracking-wide text-ink">{title}</h2>
            {subtitle ? <p className="mt-0.5 text-xs text-ink-faint">{subtitle}</p> : null}
          </div>
          {action}
        </header>
      ) : null}
      <div className={cn('p-6', bodyClassName)}>{children}</div>
    </section>
  )
}
