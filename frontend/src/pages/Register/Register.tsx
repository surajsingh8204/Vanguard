import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { toast } from 'sonner'
import axios from 'axios'
import aiGlobe from '@/assets/ai-globe.png'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export function Register() {
  const { user, loading, register } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (!loading && user) return <Navigate to="/dashboard" replace />

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    try {
      await register({ username, email, password })
      toast.success('Account created')
      navigate('/dashboard')
    } catch (error) {
      let message = 'Registration failed'
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
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(61,220,151,0.08),transparent_40%),radial-gradient(circle_at_80%_10%,rgba(91,141,239,0.1),transparent_35%)]" />
      <img
        src={aiGlobe}
        alt=""
        aria-hidden
        className="pointer-events-none absolute inset-0 h-full w-full object-cover opacity-20 [mask-image:radial-gradient(ellipse_at_center,black_20%,transparent_75%)]"
      />

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative w-full max-w-md rounded-xl border border-line bg-surface-2/90 p-8 backdrop-blur"
      >
        <div className="mb-8">
          <p className="font-mono text-xs tracking-[0.25em] text-accent">VANGUARD</p>
          <h1 className="mt-2 text-2xl font-semibold text-ink">Create analyst account</h1>
          <p className="mt-1 text-sm text-ink-muted">
            Username 3–50 chars. Password at least 8 characters.
          </p>
        </div>

        <form className="space-y-4" onSubmit={onSubmit}>
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              required
              minLength={3}
              maxLength={50}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
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
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <Button className="w-full" disabled={submitting}>
            {submitting ? 'Creating…' : 'Create account'}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-ink-muted">
          Already registered?{' '}
          <Link to="/login" className="text-accent hover:underline">
            Sign in
          </Link>
        </p>
      </motion.div>
    </div>
  )
}
