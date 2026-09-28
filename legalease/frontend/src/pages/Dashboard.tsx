import { motion } from 'framer-motion'
import {
  BadgeCheck,
  FileEdit,
  FileText,
  Filter,
  LayoutTemplate,
  Plus,
  Search,
  Sparkles,
  Trash2,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { DocumentCard } from '../components/documents/DocumentCard'
import { Alert, EmptyState } from '../components/ui/Alert'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Field, Input, NativeSelect } from '../components/ui/Input'
import { SkeletonCard } from '../components/ui/Skeleton'
import { useDashboardStats, useDocuments } from '../hooks/useDocuments'
import { useTemplates } from '../hooks/useTemplates'
import { ApiError } from '../services'
import { documentsApi } from '../services'
import type { DocumentStatus, DocumentSummary } from '../types/api'
import { formatNumber, pluralize } from '../utils/format'
import { useDebouncedValue } from '../hooks/useDebounce'

const STATUS_FILTERS: Array<{ value: '' | DocumentStatus; label: string }> = [
  { value: '', label: 'All statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'generated', label: 'Generated' },
  { value: 'completed', label: 'Completed' },
]

const PAGE_SIZE = 12

export function Dashboard() {
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<'' | DocumentStatus>('')
  const [documentType, setDocumentType] = useState('')
  const [offset, setOffset] = useState(0)
  const [pendingDelete, setPendingDelete] = useState<DocumentSummary | null>(null)
  const [acting, setActing] = useState<string | null>(null)

  const debouncedSearch = useDebouncedValue(search, 300)
  const filters = useMemo(
    () => ({ search: debouncedSearch || undefined, status: status || undefined, document_type: documentType || undefined, limit: PAGE_SIZE, offset }),
    [debouncedSearch, status, documentType, offset],
  )

  const { documents, meta, isLoading, isError, error, refetch } = useDocuments(filters)
  const { data: stats } = useDashboardStats()
  const { templates } = useTemplates({})

  const templateByType = useMemo(
    () => new Map(templates.map((template) => [template.id, template])),
    [templates],
  )

  const total = meta?.total ?? 0
  const canPrevious = offset > 0
  const canNext = offset + PAGE_SIZE < total

  function resetToFirstPage() {
    setOffset(0)
  }

  async function runAction(id: string, action: 'delete' | 'duplicate') {
    setActing(id)
    try {
      if (action === 'delete') {
        await documentsApi.remove(id)
        setPendingDelete(null)
      } else {
        await documentsApi.duplicate(id)
      }
      await refetch()
    } catch (caught) {
      window.alert(
        caught instanceof ApiError ? caught.userMessage : 'That action could not be completed.',
      )
    } finally {
      setActing(null)
    }
  }

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-[0.6875rem] font-medium tracking-[0.18em] text-gold-400/85 uppercase">
            Workspace
          </p>
          <h1 className="mt-2 font-display text-2xl font-semibold tracking-tight text-ivory-50 sm:text-3xl">
            Your documents
          </h1>
          <p className="mt-2 text-sm text-ivory-300/60">
            {stats
              ? `${pluralize(stats.total_documents, 'document')} on this machine, autosaved as you edit.`
              : 'Everything you generate is stored locally in SQLite.'}
          </p>
        </div>
        <div className="flex gap-2">
          <Button asChild variant="outline" size="md">
            <Link to="/templates">
              <LayoutTemplate aria-hidden />
              Templates
            </Link>
          </Button>
          <Button asChild size="md">
            <Link to="/create">
              <Plus aria-hidden />
              New document
            </Link>
          </Button>
        </div>
      </header>

      {stats ? <StatsRow stats={stats} /> : null}

      {/* Filters */}
      <Card className="p-4">
        <div className="grid gap-3 sm:grid-cols-[1fr_auto_auto]">
          <Field label="Search" className="sm:max-w-sm">
            {(id) => (
              <div className="relative">
                <Search
                  className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-ivory-300/40"
                  aria-hidden
                />
                <Input
                  id={id}
                  type="search"
                  value={search}
                  placeholder="Search titles…"
                  className="pl-9"
                  onChange={(event) => {
                    setSearch(event.target.value)
                    resetToFirstPage()
                  }}
                />
              </div>
            )}
          </Field>

          <Field label="Status">
            {(id) => (
              <NativeSelect
                id={id}
                value={status}
                className="min-w-40"
                onChange={(event) => {
                  setStatus(event.target.value as '' | DocumentStatus)
                  resetToFirstPage()
                }}
              >
                {STATUS_FILTERS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </NativeSelect>
            )}
          </Field>

          <Field label="Type">
            {(id) => (
              <NativeSelect
                id={id}
                value={documentType}
                className="min-w-52"
                onChange={(event) => {
                  setDocumentType(event.target.value)
                  resetToFirstPage()
                }}
              >
                <option value="">All document types</option>
                {templates.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.title}
                  </option>
                ))}
              </NativeSelect>
            )}
          </Field>
        </div>

        {(search || status || documentType) && (
          <div className="mt-4 flex items-center gap-3 border-t border-navy-700/60 pt-3.5">
            <Filter className="size-3.5 text-ivory-300/45" aria-hidden />
            <p className="text-xs text-ivory-300/55">
              {isLoading ? 'Filtering…' : `${formatNumber(total)} matching ${total === 1 ? 'document' : 'documents'}`}
            </p>
            <Button
              className="ml-auto"
              size="sm"
              variant="ghost"
              onClick={() => {
                setSearch('')
                setStatus('')
                setDocumentType('')
                resetToFirstPage()
              }}
            >
              Clear filters
            </Button>
          </div>
        )}
      </Card>

      {/* Content */}
      {isError ? (
        <Alert variant="danger" title="Could not load your documents">
          {error instanceof ApiError
            ? error.userMessage
            : 'The API did not respond. Start the backend with uvicorn app.main:app --reload.'}
        </Alert>
      ) : isLoading && !documents.length ? (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }, (_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : documents.length ? (
        <>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {documents.map((document, index) => (
              <motion.div
                key={document.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: Math.min(index, 8) * 0.03 }}
              >
                <DocumentCard
                  document={document}
                  template={templateByType.get(document.document_type)}
                  onDelete={() => setPendingDelete(document)}
                  onDuplicate={() => void runAction(document.id, 'duplicate')}
                />
              </motion.div>
            ))}
          </div>

          {total > PAGE_SIZE ? (
            <div className="flex items-center justify-between gap-4 border-t border-navy-700/60 pt-5">
              <p className="text-xs text-ivory-300/50">
                Showing {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {formatNumber(total)}
              </p>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  disabled={!canPrevious || acting !== null}
                  onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                >
                  Previous
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={!canNext || acting !== null}
                  onClick={() => setOffset(offset + PAGE_SIZE)}
                >
                  Next
                </Button>
              </div>
            </div>
          ) : null}
        </>
      ) : (
        <EmptyState
          icon={search || status || documentType ? Search : Sparkles}
          title={search || status || documentType ? 'No documents match those filters' : 'No documents yet'}
          description={
            search || status || documentType
              ? 'Try a different search term or clear the filters to see everything.'
              : 'Pick a template, answer a few guided questions, and LegalEase will draft a structured first version for you to edit and export.'
          }
          action={
            search || status || documentType ? (
              <Button
                variant="outline"
                onClick={() => {
                  setSearch('')
                  setStatus('')
                  setDocumentType('')
                }}
              >
                Clear filters
              </Button>
            ) : (
              <Button asChild>
                <Link to="/create">
                  <Sparkles aria-hidden />
                  Draft your first document
                </Link>
              </Button>
            )
          }
        />
      )}

      {pendingDelete ? (
        <DeleteDialog
          document={pendingDelete}
          busy={acting === pendingDelete.id}
          onCancel={() => setPendingDelete(null)}
          onConfirm={() => void runAction(pendingDelete.id, 'delete')}
        />
      ) : null}
    </div>
  )
}

/* ------------------------------------------------------------------ Parts */

function StatsRow({ stats }: { stats: import('../types/api').DashboardStats }) {
  const cards = [
    { label: 'Total', value: stats.total_documents, icon: FileText, tone: 'text-ivory-50' },
    { label: 'Drafts', value: stats.drafts, icon: FileEdit, tone: 'text-ivory-200' },
    { label: 'Generated', value: stats.generated, icon: Sparkles, tone: 'text-sky-300' },
    { label: 'Completed', value: stats.completed, icon: BadgeCheck, tone: 'text-emerald-300' },
    { label: 'This month', value: stats.documents_this_month, icon: BadgeCheck, tone: 'text-gold-300' },
  ]

  return (
    <div className="grid gap-4 grid-cols-2 lg:grid-cols-5">
      {cards.map((card) => (
        <Card key={card.label} className="flex items-center gap-3 p-4">
          <span className="flex size-9 items-center justify-center rounded-lg border border-navy-600 bg-navy-800/70">
            <card.icon className={`size-4 ${card.tone}`} aria-hidden />
          </span>
          <div className="min-w-0">
            <p className="font-display text-xl leading-none font-semibold text-ivory-50">
              {formatNumber(card.value)}
            </p>
            <p className="mt-1 truncate text-[0.6875rem] tracking-wide text-ivory-300/50">
              {card.label}
            </p>
          </div>
        </Card>
      ))}
    </div>
  )
}

function DeleteDialog({
  document,
  busy,
  onCancel,
  onConfirm,
}: {
  document: DocumentSummary
  busy: boolean
  onCancel: () => void
  onConfirm: () => void
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-navy-950/75 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-document-title"
      onKeyDown={(event) => {
        if (event.key === 'Escape') onCancel()
      }}
    >
      <div className="w-full max-w-md rounded-2xl border border-navy-600 bg-navy-850 p-6 shadow-lift">
        <span className="flex size-11 items-center justify-center rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300">
          <Trash2 className="size-5" aria-hidden />
        </span>
        <h2
          id="delete-document-title"
          className="mt-4 font-display text-lg font-semibold text-ivory-50"
        >
          Delete this document?
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-ivory-300/70">
          &ldquo;{document.title}&rdquo; and its {pluralize(document.section_count, 'section')} will be
          removed from the database. This cannot be undone.
        </p>
        <div className="mt-6 flex justify-end gap-2">
          <Button variant="ghost" onClick={onCancel} disabled={busy}>
            Cancel
          </Button>
          <Button variant="danger" onClick={onConfirm} loading={busy}>
            <Trash2 aria-hidden />
            Delete document
          </Button>
        </div>
      </div>
    </div>
  )
}
