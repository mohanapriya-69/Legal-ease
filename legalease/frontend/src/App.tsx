import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'

import { AppLayout } from './components/layout/AppLayout'
import { RootLayout } from './components/layout/RootLayout'
import { Landing } from './pages/Landing'
import { NotFound } from './pages/NotFound'
import { PageFallback } from './components/PageFallback'

// The wizard and editor pull in Framer Motion, Radix and the whole document
// surface, so they load on demand rather than blocking the landing page.
const Dashboard = lazy(() =>
  import('./pages/Dashboard').then((m) => ({ default: m.Dashboard })),
)
const Templates = lazy(() =>
  import('./pages/Templates').then((m) => ({ default: m.Templates })),
)
const CreateWizard = lazy(() =>
  import('./pages/CreateWizard').then((m) => ({ default: m.CreateWizard })),
)
const DocumentEditor = lazy(() =>
  import('./pages/DocumentEditor').then((m) => ({ default: m.DocumentEditor })),
)

export function App() {
  return (
    <Routes>
      {/* Marketing site: nav + footer */}
      <Route element={<RootLayout />}>
        <Route index element={<Landing />} />
        <Route element={<AppLayout />}>
          <Route
            path="create"
            element={
              <Suspense fallback={<PageFallback label="Loading the intake wizard" />}>
                <CreateWizard />
              </Suspense>
            }
          />
        </Route>
      </Route>

      {/* App: nav only, no marketing footer */}
      <Route element={<AppLayout />}>
        <Route
          path="dashboard"
          element={
            <Suspense fallback={<PageFallback label="Loading your documents" />}>
              <Dashboard />
            </Suspense>
          }
        />
        <Route
          path="templates"
          element={
            <Suspense fallback={<PageFallback label="Loading templates" />}>
              <Templates />
            </Suspense>
          }
        />
        <Route
          path="document/:id"
          element={
            <Suspense fallback={<PageFallback label="Opening the editor" />}>
              <DocumentEditor />
            </Suspense>
          }
        />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}
