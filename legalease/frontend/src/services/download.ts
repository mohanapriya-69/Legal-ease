/**
 * Download helpers.
 *
 * Exports are fetched as blobs so a failed request surfaces as a toast rather
 * than navigating the browser to an error page.
 */

import { API_BASE_URL, ApiError } from './client'

export type ExportFormat = 'pdf' | 'docx' | 'txt'

const EXTENSION: Record<ExportFormat, string> = {
  pdf: 'pdf',
  docx: 'docx',
  txt: 'txt',
}

const MIME: Record<ExportFormat, string> = {
  pdf: 'application/pdf',
  docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  txt: 'text/plain',
}

/** Turn a title into a safe, readable filename. Mirrors the backend rule. */
export function exportFilename(title: string, format: ExportFormat): string {
  const base = (title || 'document')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^A-Za-z0-9 _-]+/g, ' ')
    .replace(/[-_ ]{2,}/g, ' ')
    .trim()
    .replace(/^[ ._-]+|[ ._-]+$/g, '')
    .slice(0, 80)
    .replace(/[ ._-]+$/, '')

  return `${base || 'document'}.${EXTENSION[format]}`
}

function readDispositionFilename(header?: string | null): string | null {
  if (!header) return null
  const star = /filename\*\s*=\s*UTF-8''([^;]+)/i.exec(header)
  if (star?.[1]) {
    try {
      return decodeURIComponent(star[1])
    } catch {
      /* fall through */
    }
  }
  const plain = /filename="([^"]+)"/i.exec(header)
  return plain?.[1] ?? null
}

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.rel = 'noopener'
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  // Give the browser a moment to start the download before revoking.
  setTimeout(() => URL.revokeObjectURL(url), 2000)
}

/**
 * Download an export, showing a progress callback.
 * Throws `ApiError` with a user-safe message on failure.
 */
export async function downloadExport(
  url: string,
  title: string,
  format: ExportFormat,
  onProgress?: (percent: number | null) => void,
): Promise<string> {
  onProgress?.(0)

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${url}`, {
      method: 'GET',
      headers: { Accept: MIME[format] },
    })
  } catch {
    throw new ApiError(
      'NETWORK_ERROR',
      'Cannot reach the LegalEase API. Is the backend running on port 8000?',
      0,
    )
  }

  if (!response.ok) {
    let message = 'The document could not be exported. Please try again.'
    let code = 'EXPORT_FAILED'
    try {
      const payload = (await response.json()) as {
        error?: { code?: string; message?: string }
      }
      if (payload?.error?.message) message = payload.error.message
      if (payload?.error?.code) code = payload.error.code
    } catch {
      /* non-JSON error body; keep the default message */
    }
    onProgress?.(null)
    throw new ApiError(code, message, response.status)
  }

  const total = Number(response.headers.get('content-length') ?? '0')
  const blob =
    total > 0
      ? await readWithProgress(response, total, MIME[format], onProgress)
      : await response.blob()

  const filename =
    readDispositionFilename(response.headers.get('content-disposition')) ??
    exportFilename(title, format)

  triggerDownload(blob, filename)
  onProgress?.(100)
  return filename
}

async function readWithProgress(
  response: Response,
  total: number,
  mime: string,
  onProgress?: (percent: number | null) => void,
): Promise<Blob> {
  const reader = response.body?.getReader()
  if (!reader) return response.blob()

  const chunks: Uint8Array[] = []
  let received = 0

  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    if (value) {
      chunks.push(value)
      received += value.length
      onProgress?.(Math.min(99, Math.round((received / total) * 100)))
    }
  }

  return new Blob(chunks as BlobPart[], { type: mime })
}
