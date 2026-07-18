import { Component, type ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'

type Props = { children: ReactNode }
type State = { error: Error | null }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-warn/30 bg-warn/10">
            <AlertTriangle className="h-7 w-7 text-warn" />
          </div>
          <div>
            <p className="text-lg font-semibold text-ink">This page hit a rendering error</p>
            <p className="mx-auto mt-1.5 max-w-md text-sm leading-6 text-ink-muted">
              {this.state.error.message}
            </p>
          </div>
          <Button variant="secondary" onClick={() => this.setState({ error: null })}>
            Try again
          </Button>
        </div>
      )
    }
    return this.props.children
  }
}
