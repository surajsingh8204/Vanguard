import { NavLink } from 'react-router-dom'
import {
  Activity,
  BarChart3,
  FileText,
  GitBranch,
  LayoutDashboard,
  MessageSquare,
  Network,
  Settings,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/chat', label: 'AI Chat', icon: MessageSquare },
  { to: '/narratives', label: 'Narratives', icon: GitBranch },
  { to: '/graph', label: 'Knowledge Graph', icon: Network },
  { to: '/timeline', label: 'Timeline', icon: Activity },
  { to: '/evaluation', label: 'Evaluation', icon: BarChart3 },
  { to: '/reports', label: 'Reports', icon: FileText },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export function Sidebar({ collapsed }: { collapsed: boolean }) {
  return (
    <aside
      className={cn(
        'flex shrink-0 flex-col border-r border-line bg-surface/85 backdrop-blur transition-[width] duration-300 ease-in-out',
        collapsed ? 'w-[72px]' : 'w-64',
      )}
    >
      <div
        className={cn(
          'flex items-center gap-3 border-b border-line py-5',
          collapsed ? 'justify-center px-0' : 'px-5',
        )}
      >
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-accent/30 bg-accent/10 font-mono text-sm font-semibold text-accent">
          V
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold tracking-[0.18em] text-ink">VANGUARD</p>
            <p className="truncate text-[11px] text-ink-faint">Intelligence Platform</p>
          </div>
        )}
      </div>

      <nav className={cn('flex-1 space-y-1 py-4', collapsed ? 'px-3' : 'px-3')}>
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            title={collapsed ? label : undefined}
            className={({ isActive }) =>
              cn(
                'group relative flex items-center gap-3 rounded-lg py-2.5 text-sm transition-colors',
                collapsed ? 'justify-center px-0' : 'px-3',
                isActive
                  ? 'bg-surface-3 text-ink'
                  : 'text-ink-muted hover:bg-surface-2 hover:text-ink',
              )
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-accent" />
                )}
                <Icon className="h-[18px] w-[18px] shrink-0 opacity-85" />
                {!collapsed && <span className="truncate">{label}</span>}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {!collapsed && (
        <div className="border-t border-line px-5 py-4 text-[11px] text-ink-faint">
          Secure analyst workspace
        </div>
      )}
    </aside>
  )
}
