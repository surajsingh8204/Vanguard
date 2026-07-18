import { useCallback, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'

export function MainLayout() {
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(
    () => localStorage.getItem('vanguard_sidebar') === 'collapsed',
  )

  const toggleSidebar = useCallback(() => {
    setCollapsed((prev) => {
      const next = !prev
      localStorage.setItem('vanguard_sidebar', next ? 'collapsed' : 'open')
      return next
    })
  }, [])

  return (
    <div className="flex h-full min-h-screen">
      <Sidebar collapsed={collapsed} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar collapsed={collapsed} onToggleSidebar={toggleSidebar} />
        <main className="flex-1 overflow-auto px-6 py-7 md:px-8">
          <div className="mx-auto w-full max-w-[1500px]">
            {/* key resets the boundary when navigating between pages */}
            <ErrorBoundary key={location.pathname}>
              <Outlet />
            </ErrorBoundary>
          </div>
        </main>
      </div>
    </div>
  )
}
