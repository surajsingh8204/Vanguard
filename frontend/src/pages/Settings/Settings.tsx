import globeHand from '@/assets/globe-hand.png'
import { useAuth } from '@/contexts/AuthContext'
import { PageHeader } from '@/components/shared/PageHeader'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatDate } from '@/lib/utils'

export function Settings() {
  const { user, logout } = useAuth()
  const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings"
        description="Account profile and client preferences. Model configuration is managed by the backend pipeline."
        image={globeHand}
      />

      <section className="max-w-2xl rounded-lg border border-line bg-surface-2/60 p-5">
        <h2 className="text-sm font-semibold">Profile</h2>
        <dl className="mt-4 space-y-3 text-sm">
          <div className="flex justify-between gap-4 border-b border-line pb-2">
            <dt className="text-ink-muted">Username</dt>
            <dd>{user?.username}</dd>
          </div>
          <div className="flex justify-between gap-4 border-b border-line pb-2">
            <dt className="text-ink-muted">Email</dt>
            <dd>{user?.email}</dd>
          </div>
          <div className="flex justify-between gap-4 border-b border-line pb-2">
            <dt className="text-ink-muted">Role</dt>
            <dd>
              <Badge tone="info">{user?.role ?? 'user'}</Badge>
            </dd>
          </div>
          <div className="flex justify-between gap-4 border-b border-line pb-2">
            <dt className="text-ink-muted">Active</dt>
            <dd>
              <Badge tone={user?.is_active ? 'ok' : 'danger'}>
                {user?.is_active ? 'yes' : 'no'}
              </Badge>
            </dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-ink-muted">Created</dt>
            <dd className="font-mono text-xs">{formatDate(user?.created_at)}</dd>
          </div>
        </dl>
      </section>

      <section className="max-w-2xl rounded-lg border border-line bg-surface-2/60 p-5">
        <h2 className="text-sm font-semibold">Client</h2>
        <dl className="mt-4 space-y-3 text-sm">
          <div className="flex justify-between gap-4 border-b border-line pb-2">
            <dt className="text-ink-muted">API base URL</dt>
            <dd className="font-mono text-xs">{apiUrl}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-ink-muted">Theme</dt>
            <dd>Dark intelligence UI</dd>
          </div>
        </dl>
        <div className="mt-5">
          <Button variant="danger" onClick={logout}>
            Sign out
          </Button>
        </div>
      </section>
    </div>
  )
}
