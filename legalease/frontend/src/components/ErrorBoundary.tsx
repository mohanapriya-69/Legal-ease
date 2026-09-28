import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  error: Error | null
}

/**
 * Catches render-time crashes so a single bad page never leaves a blank
 * screen. Logs to the console; the UI never shows a stack trace to the user.
 */
export class ErrorBoundary extends Component<Props, State> {
  override state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  override componentDidCatch(error: Error, info: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error('[legalease] render error', error, info.componentStack)
  }

  override render() {
    if (this.state.error) {
      return (
        <div className="flex min-h-dvh items-center justify-center px-6">
          <div className="w-full max-w-md rounded-2xl border border-rose-500/30 bg-navy-850 p-8 text-center">
            <h1 className="font-display text-xl font-semibold text-ivory-50">
              Something broke on this page
            </h1>
            <p className="mt-3 text-sm leading-relaxed text-ivory-300/70">
              The interface hit an unexpected error. Reloading usually clears it. If it keeps
              happening, check the browser console and the backend logs.
            </p>
            <p className="mt-4 rounded-lg border border-navy-600 bg-navy-900/60 px-3 py-2 font-mono text-[0.6875rem] break-all text-rose-300/80">
              {this.state.error.message}
            </p>
            <div className="mt-6 flex justify-center gap-2">
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="rounded-lg bg-gold-500 px-4 py-2 text-sm font-medium text-navy-950 transition-colors hover:bg-gold-400"
              >
                Reload
              </button>
              <button
                type="button"
                onClick={() => this.setState({ error: null })}
                className="rounded-lg border border-navy-600 px-4 py-2 text-sm font-medium text-ivory-200 transition-colors hover:border-navy-500"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
