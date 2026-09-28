import { Copy, FileText, MoreHorizontal, Pencil, Trash2 } from 'lucide-react'
import { createElement } from 'react'
import { Link } from 'react-router-dom'

import { StatusBadge } from '../ui/Badge'
import { Card } from '../ui/Card'
import { ExportMenu } from './ExportMenu'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/DropdownMenu'
import { templateIcon } from '../icons'
import { formatRelative, formatShortDate, truncate } from '../../utils/format'
import type { DocumentSummary, TemplateItem } from '../../types/api'

export function DocumentCard({
  document,
  template,
  onDelete,
  onDuplicate,
  onOpen,
}: {
  document: DocumentSummary
  template?: TemplateItem
  onDelete?: () => void
  onDuplicate?: () => void
  onOpen?: () => void
}) {
  const Icon = template ? templateIcon(template.icon) : FileText

  return (
    <Card className="group relative flex h-full flex-col p-5 transition-colors hover:border-gold-500/35">
      <div className="flex items-start gap-3.5">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl border border-navy-600 bg-navy-800/70 text-gold-400">
          {createElement(Icon, { className: 'size-[1.15rem]', 'aria-hidden': true })}
        </span>

        <div className="min-w-0 flex-1">
          <Link
            to={`/document/${document.id}`}
            className="rounded-sm font-display text-[0.9375rem] leading-snug font-semibold text-ivory-50 transition-colors hover:text-gold-300 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold-400"
            onClick={onOpen}
          >
            {truncate(document.title, 70)}
          </Link>
          <p className="mt-1 text-xs text-ivory-300/50">
            {template?.title ?? document.document_type} &middot; {document.section_count} sections
            &middot; {document.word_count.toLocaleString()} words
          </p>
        </div>

        <div className="flex shrink-0 items-center gap-1">
          <ExportMenu documentId={document.id} title={document.title} />
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                type="button"
                className="rounded-md p-1.5 text-ivory-300/55 transition-colors hover:bg-navy-700/70 hover:text-ivory-50"
                aria-label={`Actions for ${document.title}`}
              >
                <MoreHorizontal className="size-4" aria-hidden />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-52">
              <DropdownMenuItem asChild>
                <Link to={`/document/${document.id}`}>
                  <Pencil aria-hidden />
                  Open in editor
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem
                disabled={!onDuplicate}
                onSelect={() => onDuplicate?.()}
              >
                <Copy aria-hidden />
                Duplicate
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem destructive disabled={!onDelete} onSelect={() => onDelete?.()}>
                <Trash2 aria-hidden />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <p className="mt-4 line-clamp-2 flex-1 text-sm leading-relaxed text-ivory-300/60">
        {jurisdictionLine(document)}
      </p>

      <div className="mt-5 flex items-center justify-between border-t border-navy-700/60 pt-3.5">
        <StatusBadge status={document.status} />
        <span
          className="text-[0.6875rem] text-ivory-300/40"
          title={formatShortDate(document.updated_at)}
        >
          Updated {formatRelative(document.updated_at)}
        </span>
      </div>
    </Card>
  )
}

function jurisdictionLine(document: DocumentSummary): string {
  const bits: string[] = []
  if (document.jurisdiction) bits.push(document.jurisdiction)
  if (document.effective_date) bits.push(`Effective ${formatShortDate(document.effective_date)}`)
  if (document.generation_source === 'demo') bits.push('Drafted in demo mode')
  return bits.length
    ? bits.join('  ·  ')
    : 'No jurisdiction or effective date set yet.'
}
