import { History, RotateCcw } from 'lucide-react'

import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { SkeletonText } from '../ui/Skeleton'
import type { DocumentVersion } from '../../types/api'
import { formatDateTime, formatRelative } from '../../utils/format'
import { cn } from '../../utils/cn'

export function VersionPanel({
  versions,
  isLoading,
  restoring,
  onRestore,
  onCreateSnapshot,
}: {
  versions: DocumentVersion[]
  isLoading: boolean
  restoring: boolean
  onRestore: (versionNumber: number) => void
  onCreateSnapshot: () => void
}) {
  return (
    <div className="flex flex-col gap-4">
      <Button size="sm" variant="outline" onClick={onCreateSnapshot} className="w-full">
        Save a named version
      </Button>

      {isLoading ? (
        <SkeletonText lines={6} />
      ) : versions.length ? (
        <ol className="flex flex-col gap-2">
          {versions.map((version) => (
            <li
              key={version.id}
              className="rounded-lg border border-navy-700 bg-navy-900/40 p-3 transition-colors hover:border-navy-500"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <Badge variant="neutral" size="sm">
                      v{version.version_number}
                    </Badge>
                    {version.version_number === latestOf(versions) ? (
                      <Badge variant="success" size="sm">
                        Current
                      </Badge>
                    ) : null}
                  </div>
                  <p className="mt-1.5 truncate text-xs text-ivory-200/80">
                    {version.label || 'Saved version'}
                  </p>
                  <p
                    className="mt-0.5 text-[0.625rem] text-ivory-300/40"
                    title={formatDateTime(version.created_at)}
                  >
                    {formatRelative(version.created_at)} &middot;{' '}
                    {version.content.sections.length} sections
                  </p>
                </div>
                <Button
                  size="icon-sm"
                  variant="ghost"
                  disabled={restoring || version.version_number === latestOf(versions)}
                  aria-label={`Restore version ${version.version_number}`}
                  onClick={() => {
                    if (
                      window.confirm(
                        `Restore version ${version.version_number}? The current text will be snapshotted first, so nothing is lost.`,
                      )
                    ) {
                      onRestore(version.version_number)
                    }
                  }}
                >
                  <RotateCcw aria-hidden />
                </Button>
              </div>
            </li>
          ))}
        </ol>
      ) : (
        <p
          className={cn(
            'rounded-lg border border-dashed border-navy-600 p-4 text-center text-xs',
            'leading-relaxed text-ivory-300/50',
          )}
        >
          <History className="mx-auto mb-2 size-4 text-ivory-300/30" aria-hidden />
          No versions yet. A snapshot is taken automatically before every AI rewrite.
        </p>
      )}
    </div>
  )
}

function latestOf(versions: DocumentVersion[]): number {
  return versions.reduce((max, version) => Math.max(max, version.version_number), 0)
}
