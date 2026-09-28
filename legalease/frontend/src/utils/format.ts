/** Display helpers shared across the UI. */

const RELATIVE = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })

export function formatDate(value?: string | null): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date)
}

export function formatDateTime(value?: string | null): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

/** Compact numeric form for tight layouts: 4 Mar 2026. */
export function formatShortDate(value?: string | null): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return new Intl.DateTimeFormat('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(date)
}

export function formatRelative(value?: string | null): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'

  const seconds = (date.getTime() - Date.now()) / 1000
  const units: Array<[Intl.RelativeTimeFormatUnit, number]> = [
    ['year', 60 * 60 * 24 * 365],
    ['month', 60 * 60 * 24 * 30],
    ['week', 60 * 60 * 24 * 7],
    ['day', 60 * 60 * 24],
    ['hour', 60 * 60],
    ['minute', 60],
  ]

  for (const [unit, size] of units) {
    if (Math.abs(seconds) >= size || unit === 'minute') {
      return RELATIVE.format(Math.round(seconds / size), unit)
    }
  }
  return 'just now'
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value)
}

export function pluralize(count: number, singular: string, plural?: string): string {
  return `${formatNumber(count)} ${count === 1 ? singular : (plural ?? `${singular}s`)}`
}

export function titleCase(value: string): string {
  return value
    .split(/[\s_-]+/)
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

export function truncate(value: string, max: number): string {
  if (value.length <= max) return value
  return `${value.slice(0, Math.max(0, max - 1)).trimEnd()}…`
}

/** Split a heading such as "3.2 Payment" into its number and label. */
export function splitHeading(heading: string): { number: string; label: string } {
  const match = heading.match(/^\s*(\d+(?:\.\d+)*)[.)]?\s+(.*)$/)
  if (!match) return { number: '', label: heading.trim() }
  return { number: match[1], label: match[2].trim() }
}

export function wordCount(text: string): number {
  return text.trim() ? text.trim().split(/\s+/).length : 0
}
