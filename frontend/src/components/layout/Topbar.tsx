import { LogOut, PanelLeftClose, PanelLeftOpen, Search } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

export function Topbar({
  collapsed,
  onToggleSidebar,
}: {
  collapsed: boolean
  onToggleSidebar: () => void
}) {
  const { user, logout } = useAuth()

  return (
    <header className="flex h-16 items-center justify-between gap-4 border-b border-line bg-surface/60 px-5 backdrop-blur">
      <div className="flex min-w-0 flex-1 items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleSidebar}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <PanelLeftOpen className="h-[18px] w-[18px]" />
          ) : (
            <PanelLeftClose className="h-[18px] w-[18px]" />
          )}
        </Button>

        <div className="relative w-full max-w-md">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
          <Input
            placeholder="Search narratives, entities, reports…"
            className="h-10 rounded-lg pl-9"
            aria-label="Search"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Badge tone="ok" className="hidden sm:inline-flex">
          <span className="mr-1.5 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-ok" />
          API live
        </Badge>
        <div className="hidden items-center gap-3 sm:flex">
          <div className="flex h-9 w-9 items-center justify-center rounded-full border border-line bg-surface-3 text-xs font-semibold uppercase text-ink">
            {(user?.username ?? 'A').slice(0, 2)}
          </div>
          <div className="text-right leading-tight">
            <p className="text-sm font-medium text-ink">{user?.username ?? 'Analyst'}</p>
            <p className="text-[11px] text-ink-faint">{user?.email}</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={logout} aria-label="Logout">
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  )
}
