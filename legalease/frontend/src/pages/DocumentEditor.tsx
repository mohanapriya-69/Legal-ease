import {
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  Cloud,
  CloudOff,
  Eye,
  FileText,
  History,
  Loader2,
  Lock,
  Plus,
  Save,
  Settings2,
} from 'lucide-react'
import { useCallback, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'

import { ExportMenu } from '../components/documents/ExportMenu'
import { A4Preview } from '../components/editor/A4Preview'
import { SectionEditor } from '../components/editor/SectionEditor'
import { VersionPanel } from '../components/editor/VersionPanel'
import { LegalDisclaimerInline } from '../components/layout/Disclaimer'
import { AiModePill } from '../components/layout/AiStatusBanner'
import { Alert } from '../components/ui/Alert'
import { Badge, StatusBadge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Input, Textarea } from '../components/ui/Input'
import { Skeleton } from '../components/ui/Skeleton'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/DropdownMenu'
import { useAutosave, type AutosavePayload } from '../hooks/useAutosave'
import {
  useDocument,
  useDocumentVersions,
  useRestoreVersion,
  useRewriteSection,
} from '../hooks/useDocuments'
import { useBranding } from '../hooks/useBranding'
import { ApiError, documentsApi } from '../services'
import type {
  DocumentContent,
  DocumentRecord,
  DocumentSection,
  DocumentStatus,
  RewriteAction,
} from '../types/api'
import { cn } from '../utils/cn'
import { formatRelative, wordCount } from '../utils/format'

type Panel = 'outline' | 'versions' | 'brand'
type Pane = 'edit' | 'preview'

export function DocumentEditor() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [panel, setPanel] = useState<Panel>('outline')
  const [pane, setPane] = useState<Pane>('preview')
  const [activeIndex, setActiveIndex] = useState<number | null>(null)
  const [page, setPage] = useState(1)
  const [readOnly, setReadOnly] = useState(false)
  const dragSource = useRef<number | null>(null)

  const { data: document, isLoading, isError, error } = useDocument(id)
  const { data: versions, isLoading: versionsLoading } = useDocumentVersions(id)
  const rewrite = useRewriteSection(id)
  const restore = useRestoreVersion(id)
  const { active: brand } = useBranding()

  /** The editable copy. The server copy is authoritative after each save. */
  const [draft, setDraft] = useState<DocumentContent | null>(null)
  const [draftId, setDraftId] = useState<string | null>(null)

  // Reset the editable copy when a different document is opened. Adjusting state
  // during render avoids an extra render pass, and keying on `id` (rather than
  // `updated_at`) stops a save response from clobbering newer keystrokes.
  if (document && document.id !== draftId) {
    setDraftId(document.id)
    setDraft(document.content)
  }

  const save = useCallback(
    async ({ value, createVersion, versionLabel }: AutosavePayload<DocumentContent>) => {
      await documentsApi.update(id as string, {
        content: value,
        title: value.title,
        create_version: createVersion,
        version_label: versionLabel,
      })
    },
    [id],
  )

  const autosave = useAutosave<DocumentContent | null>({
    value: draft,
    save: ({ value, createVersion, versionLabel }) => {
      if (!value) return Promise.resolve()
      return save({ value, createVersion, versionLabel })
    },
    enabled: Boolean(id) && draft !== null && !readOnly,
    delay: 1200,
    onError: (caught) => {
      toast.error(
        caught instanceof ApiError
          ? `Autosave failed: ${caught.userMessage}`
          : 'Autosave failed. Your edits are still on screen — save manually to retry.',
      )
    },
  })

  /* ------------------------------------------------------------- editing */
  function patchSection(index: number, patch: Partial<DocumentSection>) {
    setDraft((current) => {
      if (!current) return current
      const sections = current.sections.map((section, i) =>
        i === index ? { ...section, ...patch } : section,
      )
      return { ...current, sections }
    })
  }

  function moveSection(index: number, direction: -1 | 1) {
    setDraft((current) => {
      if (!current) return current
      const target = index + direction
      if (target < 0 || target >= current.sections.length) return current
      const sections = [...current.sections]
      const [moved] = sections.splice(index, 1)
      sections.splice(target, 0, moved)
      return { ...current, sections: renumber(sections) }
    })
  }

  function removeSection(index: number) {
    setDraft((current) => {
      if (!current) return current
      if (current.sections.length <= 1) {
        toast.error('A document needs at least one section.')
        return current
      }
      return {
        ...current,
        sections: renumber(current.sections.filter((_, i) => i !== index)),
      }
    })
    if (activeIndex === index) setActiveIndex(null)
  }

  function addSection() {
    setDraft((current) => {
      if (!current) return current
      const next = current.sections.length + 1
      const section: DocumentSection = {
        id: `section-${Date.now()}`,
        heading: `${next}. New section`,
        content: '',
        bullets: [],
        table: null,
      }
      return { ...current, sections: [...current.sections, section] }
    })
  }

  function dropSection(target: number) {
    const source = dragSource.current
    dragSource.current = null
    if (source === null || source === target) return
    setDraft((current) => {
      if (!current) return current
      const sections = [...current.sections]
      const [moved] = sections.splice(source, 1)
      sections.splice(target, 0, moved)
      return { ...current, sections: renumber(sections) }
    })
    setActiveIndex(target)
  }

  function patchTitle(title: string) {
    setDraft((current) => (current ? { ...current, title } : current))
  }

  function patchIntro(intro: string) {
    setDraft((current) => (current ? { ...current, intro } : current))
  }

  async function onRewrite(index: number, action: RewriteAction, instruction?: string) {
    if (!id || !draft) return
    // Persist the current text first so the AI rewrites what is on screen.
    await autosave.saveNow()
    rewrite.mutate(
      {
        section_index: index,
        action,
        ...(instruction ? { custom_instruction: instruction } : {}),
      },
      {
        onSuccess: (result) => {
          setDraft(result.document.content)
          setActiveIndex(index)
          toast.success(`Section ${index + 1} revised`)
        },
      },
    )
  }

  async function saveVersion(label: string) {
    if (!id || !draft) return
    try {
      await documentsApi.update(id, {
        content: draft,
        title: draft.title,
        create_version: true,
        version_label: label,
      })
      toast.success(`Saved "${label}"`)
    } catch (caught) {
      toast.error(caught instanceof ApiError ? caught.userMessage : 'Could not save a version.')
    }
  }

  async function setStatus(status: DocumentStatus) {
    if (!id) return
    try {
      await documentsApi.setStatus(id, status)
      toast.success(`Marked as ${status}`)
    } catch (caught) {
      toast.error(caught instanceof ApiError ? caught.userMessage : 'Could not change the status.')
    }
  }

  async function handleManualSave() {
    if (!draft) return
    await autosave.saveNow()
  }

  async function handleRestore(versionNumber: number) {
    try {
      const restored = await restore.mutateAsync(versionNumber)
      setDraft(restored.content)
    } catch {
      // `useRestoreVersion` already surfaced the failure.
    }
  }

  /* --------------------------------------------------------------- guards */
  if (isLoading) return <EditorSkeleton />
  if (isError || !id) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-20">
        <Alert variant="danger" title="Could not open this document">
          {error instanceof ApiError ? error.userMessage : 'The document could not be loaded.'}
        </Alert>
        <Button className="mt-6" variant="outline" onClick={() => navigate('/dashboard')}>
          <ChevronLeft aria-hidden />
          Back to documents
        </Button>
      </div>
    )
  }
  if (!draft || !document) return <EditorSkeleton />

  const totalWords = wordCount(
    [draft.intro, ...draft.sections.map((s) => `${s.heading} ${s.content} ${s.bullets.join(' ')}`)].join(' '),
  )

  return (
    <div className="flex h-dvh flex-col overflow-hidden">
      {/* ------------------------------------------------------------ toolbar */}
      <header className="flex flex-col gap-3 border-b border-navy-700/70 bg-navy-950/90 px-4 py-3 backdrop-blur-xl">
        <div className="flex flex-wrap items-center gap-2.5">
          <Button asChild size="icon-sm" variant="ghost" aria-label="Back to documents">
            <Link to="/dashboard">
              <ChevronLeft aria-hidden />
            </Link>
          </Button>

          <Input
            value={draft.title}
            maxLength={300}
            readOnly={readOnly}
            aria-label="Document title"
            onChange={(event) => patchTitle(event.target.value)}
            className="h-9 min-w-0 max-w-md flex-1 border-transparent bg-transparent font-display font-semibold hover:border-navy-600 focus:bg-navy-900"
          />

          <StatusBadge status={document.status} />
          <AiModePill />

          <div className="ml-auto flex flex-wrap items-center gap-2">
            <SaveIndicator
              state={autosave.state}
              onSave={() => void handleManualSave()}
            />

            <div className="flex rounded-lg border border-navy-600 p-0.5">
              {(['edit', 'preview'] as Pane[]).map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setPane(option)}
                  aria-pressed={pane === option}
                  className={cn(
                    'rounded-md px-3 py-1.5 text-xs font-medium capitalize transition-colors',
                    pane === option
                      ? 'bg-navy-700 text-ivory-50'
                      : 'text-ivory-300/60 hover:text-ivory-50',
                  )}
                >
                  {option}
                </button>
              ))}
            </div>

            <Button
              size="sm"
              variant="outline"
              onClick={() => setReadOnly((v) => !v)}
              aria-pressed={readOnly}
            >
              {readOnly ? <FileText aria-hidden /> : <Lock aria-hidden />}
              {readOnly ? 'Read only' : 'Editing'}
            </Button>

            <ExportMenu documentId={document.id} title={draft.title} disabled={autosave.isDirty} />

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button size="icon-sm" variant="ghost" aria-label="Document options">
                  <Settings2 aria-hidden />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-60">
                <DropdownMenuLabel>Status</DropdownMenuLabel>
                {(['draft', 'generated', 'completed'] as DocumentStatus[]).map((option) => (
                  <DropdownMenuItem
                    key={option}
                    onSelect={() => void setStatus(option)}
                    disabled={option === document.status}
                  >
                    {option === document.status ? <CheckCircle2 aria-hidden /> : <FileText aria-hidden />}
                    <span className="capitalize">{option}</span>
                  </DropdownMenuItem>
                ))}
                <DropdownMenuSeparator />
                <DropdownMenuItem onSelect={() => void saveVersion('Manual snapshot')}>
                  <Save aria-hidden />
                  Save a named version
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => navigate('/create')}>
                  <Plus aria-hidden />
                  Draft another document
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        <LegalDisclaimerInline />
      </header>

      {/* -------------------------------------------------------------- body */}
      <div className="grid min-h-0 flex-1 lg:grid-cols-[16rem_minmax(0,1fr)] xl:grid-cols-[16rem_minmax(0,1fr)_minmax(0,26rem)]">
        {/* Sidebar */}
        <aside className="hidden min-h-0 flex-col border-r border-navy-700/60 bg-navy-950/50 lg:flex">
          <nav className="flex border-b border-navy-700/60 p-2" aria-label="Editor panels">
            {([
              { id: 'outline', label: 'Outline', icon: FileText },
              { id: 'versions', label: 'Versions', icon: History },
              { id: 'brand', label: 'Brand', icon: Cloud },
            ] as const).map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setPanel(item.id)}
                aria-pressed={panel === item.id}
                className={cn(
                  'flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium transition-colors',
                  panel === item.id
                    ? 'bg-navy-700 text-ivory-50'
                    : 'text-ivory-300/55 hover:text-ivory-50',
                )}
              >
                <item.icon className="size-3.5" aria-hidden />
                {item.label}
              </button>
            ))}
          </nav>

          <div className="min-h-0 flex-1 overflow-y-auto p-3">
            {panel === 'outline' ? (
              <OutlineList
                document={document}
                activeIndex={activeIndex}
                onSelect={(index) => {
                  setActiveIndex(index)
                  setPane('edit')
                  window.document
                    .getElementById(`section-${index}`)
                    ?.scrollIntoView({ behavior: 'smooth', block: 'center' })
                }}
              />
            ) : null}

            {panel === 'versions' ? (
              <VersionPanel
                versions={versions ?? []}
                isLoading={versionsLoading}
                restoring={restore.isPending}
                onRestore={(versionNumber: number) => void handleRestore(versionNumber)}
                onCreateSnapshot={() => {
                  const label = window.prompt('Version label', 'Manual snapshot')
                  if (label?.trim()) void saveVersion(label.trim())
                }}
              />
            ) : null}

            {panel === 'brand' ? <BrandPanel document={document} /> : null}
          </div>

          <footer className="border-t border-navy-700/60 p-3 text-[0.625rem] leading-relaxed text-ivory-300/40">
            <p>
              {draft.sections.length} sections &middot; {totalWords.toLocaleString()} words
            </p>
            <p className="mt-0.5">
              Created {formatRelative(document.created_at)} &middot; autosaved locally
            </p>
          </footer>
        </aside>

        {/* Editor / preview */}
        <main
          className={cn(
            'min-h-0 overflow-y-auto',
            pane === 'edit' ? 'block' : 'hidden lg:block',
            readOnly ? 'bg-navy-900/20' : '',
          )}
        >
          {pane === 'edit' || pane === 'preview' ? (
            <div className="mx-auto flex max-w-3xl flex-col gap-4 p-4 sm:p-6">
              {readOnly ? (
                <Alert variant="info" title="Read-only mode">
                  Editing is disabled, so autosave is paused.
                </Alert>
              ) : null}

              <section className="rounded-card border border-navy-700 bg-navy-900/35 p-4">
                <label className="text-xs font-medium tracking-[0.09em] text-ivory-300/80 uppercase">
                  Introduction
                </label>
                <Textarea
                  value={draft.intro}
                  readOnly={readOnly}
                  rows={4}
                  maxLength={4000}
                  aria-label="Document introduction"
                  placeholder="Opening paragraph naming the parties and the date…"
                  className="mt-3 min-h-24 font-serif"
                  onChange={(event) => patchIntro(event.target.value)}
                />
              </section>

              {draft.sections.map((section, index) => (
                <SectionEditor
                  key={section.id || index}
                  section={section}
                  index={index}
                  total={draft.sections.length}
                  active={activeIndex === index}
                  readOnly={readOnly}
                  rewriting={rewrite.isPending && rewrite.variables?.section_index === index}
                  onFocus={() => setActiveIndex(index)}
                  onChange={(patch) => patchSection(index, patch)}
                  onMove={(direction) => moveSection(index, direction)}
                  onRemove={() => removeSection(index)}
                  onRewrite={(action, instruction) =>
                    void onRewrite(index, action, instruction)
                  }
                  onDrop={dropSection}
                  onDragStart={(from) => {
                    dragSource.current = from
                  }}
                />
              ))}

              {!readOnly ? (
                <Button variant="outline" onClick={addSection} className="self-start">
                  <Plus aria-hidden />
                  Add a section
                </Button>
              ) : null}

              {draft.disclaimer ? (
                <div className="mt-2 rounded-xl border border-amber-500/25 bg-amber-500/6 p-4">
                  <p className="flex items-center gap-1.5 text-xs font-medium text-amber-200">
                    <AlertTriangle className="size-3.5" aria-hidden />
                    Disclaimer on this document
                  </p>
                  <p className="mt-1.5 text-xs leading-relaxed text-amber-50/70">
                    {draft.disclaimer}
                  </p>
                </div>
              ) : null}
            </div>
          ) : null}
        </main>

        {/* Preview */}
        <aside
          className={cn(
            'min-h-0 overflow-y-auto border-l border-navy-700/60 bg-navy-950/60 p-5',
            pane === 'preview' ? 'block' : 'hidden xl:block',
          )}
        >
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="text-xs font-medium tracking-[0.09em] text-ivory-300/80 uppercase">
              A4 preview
            </h2>
            <div className="flex items-center gap-1">
              <Button
                size="icon-sm"
                variant="ghost"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                aria-label="Previous preview page"
              >
                <ChevronLeft aria-hidden />
              </Button>
              <span className="px-1 text-xs text-ivory-300/50">{page}</span>
              <Button
                size="icon-sm"
                variant="ghost"
                onClick={() => setPage((p) => p + 1)}
                aria-label="Next preview page"
              >
                <ChevronLeft className="rotate-180" aria-hidden />
              </Button>
            </div>
          </div>

          <A4Preview
            content={draft}
            organization={brand?.organization_name ?? null}
            logoPath={brand?.logo_path ?? null}
            footerText={brand?.footer_text ?? null}
            page={page}
            highlightIndex={activeIndex}
            onSelectSection={setActiveIndex}
          />
        </aside>
      </div>

      {/* Mobile panel switcher */}
      <nav
        className="flex shrink-0 border-t border-navy-700/60 bg-navy-950/95 p-1.5 lg:hidden"
        aria-label="Editor panels"
      >
        {(['edit', 'preview'] as Pane[]).map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => setPane(option)}
            aria-pressed={pane === option}
            className={cn(
              'flex flex-1 items-center justify-center gap-1.5 rounded-md px-3 py-2 text-xs font-medium transition-colors',
              pane === option ? 'bg-navy-700 text-ivory-50' : 'text-ivory-300/60',
            )}
          >
            {option === 'edit' ? <FileText className="size-3.5" aria-hidden /> : <Eye className="size-3.5" aria-hidden />}
            {option === 'edit' ? 'Edit' : 'A4 preview'}
          </button>
        ))}
      </nav>
    </div>
  )
}

/* ------------------------------------------------------------------ Parts */

function renumber(sections: DocumentSection[]): DocumentSection[] {
  return sections.map((section, index) => ({
    ...section,
    heading: section.heading.replace(/^\s*\d+(\.\d+)*[.)]?\s+/, `${index + 1}. `),
  }))
}

function SaveIndicator({
  state,
  onSave,
}: {
  state: 'idle' | 'dirty' | 'saving' | 'saved' | 'error'
  onSave: () => void
}) {
  const map = {
    idle: { icon: Cloud, text: 'All changes saved', tone: 'text-ivory-300/40' },
    dirty: { icon: Cloud, text: 'Unsaved changes', tone: 'text-amber-300' },
    saving: { icon: Loader2, text: 'Saving…', tone: 'text-ivory-300/60' },
    saved: { icon: CheckCircle2, text: 'Saved', tone: 'text-emerald-300' },
    error: { icon: CloudOff, text: 'Save failed', tone: 'text-rose-300' },
  }[state]

  const Icon = map.icon

  return (
    <button
      type="button"
      onClick={onSave}
      title={state === 'error' ? 'Retry save' : 'Save now'}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs transition-colors hover:bg-navy-800',
        map.tone,
      )}
    >
      <Icon className={cn('size-3.5', state === 'saving' && 'animate-spin')} aria-hidden />
      <span className="hidden sm:inline">{map.text}</span>
    </button>
  )
}

function OutlineList({
  document,
  activeIndex,
  onSelect,
}: {
  document: DocumentRecord
  activeIndex: number | null
  onSelect: (index: number) => void
}) {
  if (!document.content.sections.length) {
    return (
      <p className="rounded-lg border border-dashed border-navy-600 p-4 text-center text-xs text-ivory-300/50">
        This document has no sections.
      </p>
    )
  }

  return (
    <ol className="flex flex-col gap-1">
      {document.content.sections.map((section, index) => (
        <li key={section.id || index}>
          <button
            type="button"
            onClick={() => onSelect(index)}
            className={cn(
              'flex w-full items-start gap-2 rounded-lg px-2.5 py-2 text-left text-xs transition-colors',
              activeIndex === index
                ? 'bg-gold-500/12 text-gold-200'
                : 'text-ivory-200/70 hover:bg-navy-800/70',
            )}
          >
            <span className="mt-px shrink-0 font-mono text-[0.625rem] text-ivory-300/40">
              {String(index + 1).padStart(2, '0')}
            </span>
            <span className="line-clamp-2 min-w-0 flex-1">{section.heading}</span>
          </button>
        </li>
      ))}
    </ol>
  )
}

function BrandPanel({ document }: { document: DocumentRecord }) {
  const { profiles, isLoading } = useBranding()
  const logo = document.content.generation

  if (isLoading) return <Skeleton className="h-24" />

  if (!profiles.length) {
    return (
      <p className="rounded-lg border border-dashed border-navy-600 p-4 text-center text-xs leading-relaxed text-ivory-300/50">
        No brand profile saved. Add letterhead in the wizard and it will be applied to every
        export of this document.
      </p>
    )
  }

  return (
    <ul className="flex flex-col gap-2">
      {profiles.map((profile) => (
        <li key={profile.id} className="rounded-lg border border-navy-700 bg-navy-900/40 p-3">
          <p className="text-sm text-ivory-100">{profile.organization_name ?? 'Unnamed'}</p>
          <p className="mt-0.5 text-[0.625rem] text-ivory-300/45">
            {profile.email || 'No email'} &middot; {profile.website || 'No website'}
          </p>
        </li>
      ))}
      <li className="mt-2">
        <Button asChild size="sm" variant="ghost" className="w-full">
          <Link to="/create">Edit in the wizard</Link>
        </Button>
      </li>
      {logo?.source ? (
        <li>
          <Badge variant="neutral" size="sm" className="w-full justify-center">
            Drafted by {logo.source}
          </Badge>
        </li>
      ) : null}
    </ul>
  )
}

function EditorSkeleton() {
  return (
    <div className="flex h-dvh flex-col">
      <div className="border-b border-navy-700/70 p-4">
        <Skeleton className="h-9 w-72" />
      </div>
      <div className="grid flex-1 lg:grid-cols-[16rem_minmax(0,1fr)]">
        <div className="hidden border-r border-navy-700/60 p-3 lg:block">
          {Array.from({ length: 7 }, (_, i) => (
            <Skeleton key={i} className="mb-2 h-8" />
          ))}
        </div>
        <div className="mx-auto flex max-w-3xl flex-col gap-4 p-6">
          <Skeleton className="h-32 w-full rounded-card" />
          {Array.from({ length: 5 }, (_, i) => (
            <Skeleton key={i} className="h-24 w-full rounded-card" />
          ))}
        </div>
      </div>
    </div>
  )
}
