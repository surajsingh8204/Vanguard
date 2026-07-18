import { cn } from '@/lib/utils'

export function Badge({
  className,
  tone = 'default',
  ...props
}: React.ComponentProps<'span'> & {
  tone?: 'default' | 'ok' | 'warn' | 'danger' | 'info'
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded px-2 py-0.5 text-xs font-medium tracking-wide',
        tone === 'default' && 'bg-surface-3 text-ink-muted border border-line',
        tone === 'ok' && 'bg-ok/15 text-ok border border-ok/30',
        tone === 'warn' && 'bg-warn/15 text-warn border border-warn/30',
        tone === 'danger' && 'bg-danger/15 text-danger border border-danger/30',
        tone === 'info' && 'bg-accent-2/15 text-accent-2 border border-accent-2/30',
        className,
      )}
      {...props}
    />
  )
}
