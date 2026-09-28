import { ChevronDown, GripVertical, List, Loader2, Plus, Trash2, Wand2, X } from 'lucide-react'
import { useState } from 'react'

import { Button } from '../ui/Button'
import { Textarea } from '../ui/Input'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/DropdownMenu'
import type { DocumentSection, RewriteAction } from '../../types/api'
import { cn } from '../../utils/cn'
import { wordCount } from '../../utils/format'

const REWRITE_ACTIONS: Array<{ action: RewriteAction; label: string }> = [
  { action: 'rewrite_professional', label: 'Rewrite professionally' },
  { action: 'simplify', label: 'Simplify language' },
  { action: 'more_formal', label: 'Make more formal' },
  { action: 'expand', label: 'Expand section' },
  { action: 'shorten', label: 'Shorten section' },
  { action: 'fix_grammar', label: 'Fix grammar' },
  { action: 'add_protection', label: 'Add protection clause' },
]

interface Props {
  section: DocumentSection
  index: number
  total: number
  active: boolean
  readOnly: boolean
  rewriting: boolean
  onFocus: () => void
  onChange: (patch: Partial<DocumentSection>) => void
  onMove: (direction: -1 | 1) => void
  onRemove: () => void
  onRewrite: (action: RewriteAction, instruction?: string) => void
  onDrop: (targetIndex: number) => void
  onDragStart: (index: number) => void
}

export function SectionEditor({
  section,
  index,
  total,
  active,
  readOnly,
  rewriting,
  onFocus,
  onChange,
  onMove,
  onRemove,
  onRewrite,
  onDrop,
  onDragStart,
}: Props) {
  const [expanded, setExpanded] = useState(active)
  const [customOpen, setCustomOpen] = useState(false)
  const [instruction, setInstruction] = useState('')
  const [newBullet, setNewBullet] = useState('')

  const words = wordCount(section.content)

  return (
    <section
      id={`section-${index}`}
      draggable={!readOnly}
      onDragStart={() => onDragStart(index)}
      onDragOver={(event) => event.preventDefault()}
      onDrop={() => onDrop(index)}
      onClick={onFocus}
      className={cn(
        'group relative rounded-card border bg-navy-900/35 transition-colors',
        active
          ? 'border-gold-500/45 shadow-[0_0_0_1px_rgba(201,162,39,0.12)]'
          : 'border-navy-700 hover:border-navy-500',
        readOnly && 'cursor-default',
      )}
    >
      <header className="flex items-center gap-2 px-3 py-2.5">
        {!readOnly ? (
          <GripVertical
            className="size-4 shrink-0 cursor-grab text-ivory-300/25 active:cursor-grabbing"
            aria-hidden
          />
        ) : null}

        <button
          type="button"
          onClick={() => {
            setExpanded((v) => !v)
            onFocus()
          }}
          aria-expanded={expanded}
          className="flex min-w-0 flex-1 items-center gap-2 text-left"
        >
          <span className="shrink-0 font-mono text-[0.6875rem] text-gold-400/70">
            {String(index + 1).padStart(2, '0')}
          </span>
          <span className="truncate text-sm font-medium text-ivory-50">
            {section.heading || 'Untitled section'}
          </span>
          <ChevronDown
            className={cn(
              'ml-auto size-4 shrink-0 text-ivory-300/40 transition-transform',
              expanded && 'rotate-180',
            )}
            aria-hidden
          />
        </button>

        <span className="shrink-0 text-[0.625rem] text-ivory-300/35">{words}w</span>

        {!readOnly ? (
          <RewriteMenu
            disabled={rewriting}
            onRewrite={(action, text) => onRewrite(action, text)}
            customOpen={customOpen}
            setCustomOpen={setCustomOpen}
            instruction={instruction}
            setInstruction={setInstruction}
          />
        ) : null}
      </header>

      {expanded ? (
        <div className="border-t border-navy-700/60 px-3 py-4">
          <label className="sr-only" htmlFor={`heading-${index}`}>
            Section heading
          </label>
          <input
            id={`heading-${index}`}
            value={section.heading}
            maxLength={300}
            readOnly={readOnly}
            placeholder="Section heading"
            onChange={(event) => onChange({ heading: event.target.value })}
            className="mb-3 w-full rounded-lg border border-navy-600 bg-navy-950/50 px-3 py-2 text-sm font-medium text-ivory-50 outline-none transition-colors placeholder:text-ivory-300/30 focus:border-gold-500/60 read-only:opacity-70"
          />

          <label className="sr-only" htmlFor={`content-${index}`}>
            Section content
          </label>
          <Textarea
            id={`content-${index}`}
            value={section.content}
            readOnly={readOnly}
            rows={Math.min(18, Math.max(4, Math.ceil(words / 22)))}
            placeholder="Section text…"
            onChange={(event) => onChange({ content: event.target.value })}
            className="min-h-24 font-serif text-[0.8125rem] leading-relaxed"
          />

          {/* Bullets */}
          {section.bullets.length ? (
            <ul className="mt-3 flex flex-col gap-1.5">
              {section.bullets.map((bullet, bulletIndex) => (
                <li key={bulletIndex} className="flex items-start gap-2">
                  <List className="mt-2 size-3.5 shrink-0 text-ivory-300/40" aria-hidden />
                  <input
                    value={bullet}
                    readOnly={readOnly}
                    aria-label={`Bullet ${bulletIndex + 1}`}
                    onChange={(event) => {
                      const next = [...section.bullets]
                      next[bulletIndex] = event.target.value
                      onChange({ bullets: next })
                    }}
                    className="min-w-0 flex-1 rounded border border-transparent bg-transparent px-1.5 py-1 text-[0.8125rem] text-ivory-200 outline-none transition-colors hover:border-navy-600 focus:border-gold-500/50 read-only:opacity-70"
                  />
                  {!readOnly ? (
                    <button
                      type="button"
                      aria-label={`Remove bullet ${bulletIndex + 1}`}
                      className="mt-1 rounded p-1 text-ivory-300/40 transition-colors hover:text-rose-300"
                      onClick={() =>
                        onChange({
                          bullets: section.bullets.filter((_, i) => i !== bulletIndex),
                        })
                      }
                    >
                      <X className="size-3.5" aria-hidden />
                    </button>
                  ) : null}
                </li>
              ))}
            </ul>
          ) : null}

          {!readOnly ? (
            <div className="mt-3">
              {newBullet ? (
                <div className="flex gap-2">
                  <input
                    autoFocus
                    value={newBullet}
                    onChange={(event) => setNewBullet(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter') {
                        event.preventDefault()
                        onChange({ bullets: [...section.bullets, newBullet.trim()] })
                        setNewBullet('')
                      } else if (event.key === 'Escape') {
                        setNewBullet('')
                      }
                    }}
                    placeholder="Bullet text, then press Enter"
                    className="min-w-0 flex-1 rounded-lg border border-navy-600 bg-navy-950/50 px-3 py-1.5 text-[0.8125rem] text-ivory-50 outline-none focus:border-gold-500/60"
                  />
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => {
                      onChange({ bullets: [...section.bullets, newBullet.trim()] })
                      setNewBullet('')
                    }}
                  >
                    Add
                  </Button>
                </div>
              ) : (
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-ivory-300/60"
                  onClick={() => setNewBullet(' ')}
                >
                  <Plus aria-hidden />
                  Add bullet
                </Button>
              )}
            </div>
          ) : null}

          {!readOnly ? (
            <footer className="mt-4 flex items-center gap-1 border-t border-navy-700/50 pt-3">
              <Button
                size="sm"
                variant="ghost"
                disabled={index === 0}
                onClick={() => onMove(-1)}
              >
                Move up
              </Button>
              <Button
                size="sm"
                variant="ghost"
                disabled={index === total - 1}
                onClick={() => onMove(1)}
              >
                Move down
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="ml-auto text-ivory-300/50 hover:text-rose-300"
                onClick={onRemove}
              >
                <Trash2 aria-hidden />
                Delete section
              </Button>
            </footer>
          ) : null}

          {rewriting ? (
            <p className="mt-3 flex items-center gap-2 text-xs text-gold-300">
              <Loader2 className="size-3.5 animate-spin" aria-hidden />
              Revising this section…
            </p>
          ) : null}
        </div>
      ) : null}
    </section>
  )
}

function RewriteMenu({
  disabled,
  onRewrite,
  customOpen,
  setCustomOpen,
  instruction,
  setInstruction,
}: {
  disabled: boolean
  onRewrite: (action: RewriteAction, instruction?: string) => void
  customOpen: boolean
  setCustomOpen: (open: boolean) => void
  instruction: string
  setInstruction: (value: string) => void
}) {
  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            size="icon-sm"
            variant="ghost"
            disabled={disabled}
            aria-label="Rewrite this section with AI"
            className="shrink-0 opacity-0 transition-opacity group-hover:opacity-100 focus-visible:opacity-100"
          >
            {disabled ? <Loader2 className="animate-spin" aria-hidden /> : <Wand2 aria-hidden />}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56">
          <DropdownMenuLabel>Revise with AI</DropdownMenuLabel>
          {REWRITE_ACTIONS.map((item) => (
            <DropdownMenuItem
              key={item.action}
              disabled={disabled}
              onSelect={() => onRewrite(item.action)}
            >
              {item.label}
            </DropdownMenuItem>
          ))}
          <DropdownMenuSeparator />
          <DropdownMenuItem
            disabled={disabled}
            onSelect={(event) => {
              event.preventDefault()
              setCustomOpen(true)
            }}
          >
            <Wand2 aria-hidden />
            Custom instruction…
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {customOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy-950/75 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl border border-navy-600 bg-navy-850 p-6 shadow-lift">
            <h3 className="font-display text-lg font-semibold text-ivory-50">
              Custom rewrite instruction
            </h3>
            <p className="mt-1.5 text-sm text-ivory-300/65">
              Tell the AI what to change. The rest of the document is left untouched.
            </p>
            <Textarea
              autoFocus
              rows={4}
              value={instruction}
              maxLength={2000}
              placeholder="e.g. Make this mutual and add a 30-day notice period."
              className="mt-4"
              onChange={(event) => setInstruction(event.target.value)}
            />
            <div className="mt-5 flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setCustomOpen(false)}>
                Cancel
              </Button>
              <Button
                disabled={!instruction.trim() || disabled}
                onClick={() => {
                  onRewrite('rewrite_professional', instruction.trim())
                  setInstruction('')
                  setCustomOpen(false)
                }}
              >
                <Wand2 aria-hidden />
                Rewrite section
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  )
}
