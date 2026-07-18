import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import axios from 'axios'
import { toast } from 'sonner'
import globeNetwork from '@/assets/globe-network.png'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export function Login() {
  const { user, loading, login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (!loading && user) return <Navigate to="/dashboard" replace />

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    try {
      await login(email, password)
      toast.success('Welcome back')
      navigate('/dashboard')
    } catch (error) {
      let message = 'Login failed. Check your credentials.'
      if (axios.isAxiosError(error)) {
        message = String(error.response?.data?.detail ?? message)
      } else if (error instanceof Error) {
        message = error.message
      }
      toast.error(message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(36,49,73,0.35)_1px,transparent_1px),linear-gradient(90deg,rgba(36,49,73,0.35)_1px,transparent_1px)] bg-[size:48px_48px] [mask-image:radial-gradient(ellipse_at_center,black_30%,transparent_75%)]" />
      <img
        src={globeNetwork}
        alt=""
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-1/2 h-[720px] w-[720px] max-w-none -translate-x-1/2 -translate-y-1/2 opacity-30 [mask-image:radial-gradient(circle_at_center,black_35%,transparent_70%)]"
      />

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="relative w-full max-w-md rounded-xl border border-line bg-surface-2/90 p-8 shadow-2xl backdrop-blur"
      >
        <div className="mb-8">
          <p className="font-mono text-xs tracking-[0.25em] text-accent">VANGUARD</p>
          <h1 className="mt-2 text-2xl font-semibold text-ink">Analyst sign in</h1>
          <p className="mt-1 text-sm text-ink-muted">
            Access narrative intelligence, graphs, and RAG analysis.
          </p>
        </div>

        <form className="space-y-4" onSubmit={onSubmit}>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <Button className="w-full" disabled={submitting}>
            {submitting ? 'Signing in…' : 'Sign in'}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-ink-muted">
          No account?{' '}
          <Link to="/register" className="text-accent hover:underline">
            Register
          </Link>
        </p>
      </motion.div>
    </div>
  )
}
