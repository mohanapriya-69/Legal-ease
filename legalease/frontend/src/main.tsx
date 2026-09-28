import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'sonner'

import { TooltipProvider } from './components/ui/Tooltip'
import { ErrorBoundary } from './components/ErrorBoundary'
import { App } from './App'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 10_000,
    },
    mutations: { retry: 0 },
  },
})

const container = document.getElementById('root')
if (!container) throw new Error('Root element #root is missing from index.html')

createRoot(container).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <TooltipProvider delayDuration={200} skipDelayDuration={300}>
          <ErrorBoundary>
            <App />
          </ErrorBoundary>
          <Toaster
            position="bottom-right"
            closeButton
            richColors
            theme="dark"
            toastOptions={{
              classNames: {
                toast:
                  'rounded-xl border border-navy-600 bg-navy-850 text-ivory-100 shadow-lift font-sans',
                description: 'text-ivory-300/70',
                actionButton: 'bg-gold-500 text-navy-950',
              },
            }}
          />
        </TooltipProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
