import { Download, FileText, Loader2, Sheet, Type } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { Button } from '../ui/Button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/DropdownMenu'
import { ApiError, documentsApi } from '../../services'
import { downloadExport, type ExportFormat } from '../../services/download'

const FORMATS: Array<{
  format: ExportFormat
  label: string
  hint: string
  icon: typeof FileText
}> = [
  { format: 'pdf', label: 'PDF', hint: 'A4, paginated, letterhead', icon: FileText },
  { format: 'docx', label: 'Word', hint: 'Editable .docx', icon: Sheet },
  { format: 'txt', label: 'Plain text', hint: 'Markdown-free, clean', icon: Type },
]

export function ExportMenu({
  documentId,
  title,
  disabled,
  className,
}: {
  documentId: string
  title: string
  disabled?: boolean
  className?: string
}) {
  const [busy, setBusy] = useState<ExportFormat | null>(null)

  async function run(format: ExportFormat, label: string) {
    setBusy(format)
    try {
      const filename = await downloadExport(
        documentsApi.exportUrl(documentId, format),
        title,
        format,
      )
      toast.success(`Downloaded ${filename}`)
    } catch (error) {
      toast.error(
        error instanceof ApiError
          ? error.userMessage
          : `Could not export the ${label} file.`,
      )
    } finally {
      setBusy(null)
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          className={className}
          disabled={disabled}
          size="sm"
          variant="secondary"
          aria-label="Export document"
        >
          {busy ? <Loader2 className="animate-spin" aria-hidden /> : <Download aria-hidden />}
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-60">
        <DropdownMenuLabel>Download as</DropdownMenuLabel>
        {FORMATS.map((item) => (
          <DropdownMenuItem
            key={item.format}
            disabled={busy !== null}
            onSelect={() => void run(item.format, item.label)}
          >
            {busy === item.format ? (
              <Loader2 className="animate-spin" aria-hidden />
            ) : (
              <item.icon aria-hidden />
            )}
            <span className="flex-1">{item.label}</span>
            <span className="text-[0.6875rem] text-ivory-300/45">{item.hint}</span>
          </DropdownMenuItem>
        ))}
        <DropdownMenuSeparator />
        <p className="px-2.5 py-1.5 text-[0.6875rem] leading-relaxed text-ivory-300/45">
          Exported files include the legal disclaimer.
        </p>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
