import { motion } from 'framer-motion'
import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

export function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  tone = 'default',
  delay = 0,
}: {
  label: string
  value: string
  hint?: string
  icon?: LucideIcon
  tone?: 'default' | 'accent' | 'blue' | 'warn'
  delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay }}
      className="relative overflow-hidden rounded-2xl border border-line/80 bg-gradient-to-br from-surface-2/90 to-surface-2/40 px-6 py-5"
    >
      <div
        className={cn(
          'pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full blur-2xl',
          tone === 'accent' && 'bg-accent/10',
          tone === 'blue' && 'bg-accent-2/10',
          tone === 'warn' && 'bg-warn/10',
          tone === 'default' && 'bg-line/20',
        )}
      />
      <div className="flex items-start justify-between gap-3">
        <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-ink-faint">
          {label}
        </p>
        {Icon ? (
          <span
            className={cn(
              'flex h-8 w-8 items-center justify-center rounded-lg border',
              tone === 'accent' && 'border-accent/25 bg-accent/10 text-accent',
              tone === 'blue' && 'border-accent-2/25 bg-accent-2/10 text-accent-2',
              tone === 'warn' && 'border-warn/25 bg-warn/10 text-warn',
              tone === 'default' && 'border-line bg-surface-3/60 text-ink-muted',
            )}
          >
            <Icon className="h-4 w-4" />
          </span>
        ) : null}
      </div>
      <p className="mt-3 font-mono text-3xl font-semibold tracking-tight text-ink">{value}</p>
      {hint ? <p className="mt-1.5 text-xs text-ink-muted">{hint}</p> : null}
    </motion.div>
  )
}
