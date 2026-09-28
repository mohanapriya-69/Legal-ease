import { useMemo } from 'react'

import { assetUrl } from '../../services'
import type { DocumentContent, SignatureBlock } from '../../types/api'
import { splitHeading } from '../../utils/format'
import { cn } from '../../utils/cn'

/**
 * A4 preview that mirrors the exporter geometry: 210x297mm, 25mm margins,
 * 11pt serif, 1.5 line spacing. It is a faithful preview, not a generic
 * "document-looking" box, so what you see matches what you download.
 */
export function A4Preview({
  content,
  organization,
  logoPath,
  footerText,
  page,
  highlightIndex,
  onSelectSection,
  className,
}: {
  content: DocumentContent
  organization?: string | null
  logoPath?: string | null
  footerText?: string | null
  page: number
  highlightIndex?: number | null
  onSelectSection?: (index: number) => void
  className?: string
}) {
  const logo = logoPath ? assetUrl(`/api/branding/logo/${logoPath}`) : null

  const blocks = useMemo(() => {
    const list: Array<{ kind: 'heading' | 'intro' | 'section' | 'signatures'; index?: number }> = []
    if (content.intro) list.push({ kind: 'intro' })
    content.sections.forEach((_, index) => list.push({ kind: 'section', index }))
    if (content.signature_blocks.length) list.push({ kind: 'signatures' })
    return list
  }, [content])

  const PAGE_BLOCKS = 3
  const start = (page - 1) * PAGE_BLOCKS
  const visible = blocks.slice(start, start + PAGE_BLOCKS)
  const totalPages = Math.max(1, Math.ceil(blocks.length / PAGE_BLOCKS))

  return (
    <div className={cn('flex flex-col items-center gap-4', className)}>
      <article className="preview-page">
        {/* Letterhead */}
        <header className="preview-header">
          {logo ? (
            <img src={logo} alt="" className="preview-logo" />
          ) : organization ? (
            <p className="preview-organization">{organization}</p>
          ) : null}
        </header>

        <div className="preview-body">
          <h1 className="preview-title">{content.title}</h1>
          {content.subtitle ? <p className="preview-subtitle">{content.subtitle}</p> : null}

          {visible.length === 0 ? (
            <p className="preview-paragraph text-ink-600/60">This page is blank.</p>
          ) : null}

          {visible.map((block) => {
            if (block.kind === 'intro') {
              return (
                <p key="intro" className="preview-paragraph">
                  {content.intro}
                </p>
              )
            }

            if (block.kind === 'signatures') {
              return (
                <SignatureGrid key="signatures" blocks={content.signature_blocks} />
              )
            }

            const section = content.sections[block.index ?? 0]
            const { number, label } = splitHeading(section.heading)
            const active = highlightIndex === block.index

            return (
              <section
                key={section.id}
                className={cn(
                  'preview-section',
                  active && 'preview-section-active',
                  onSelectSection && 'preview-section-clickable',
                )}
                onClick={() => onSelectSection?.(block.index ?? 0)}
              >
                <h2 className="preview-heading">
                  {number ? <span className="preview-heading-number">{number}.</span> : null}
                  {label}
                </h2>
                {section.content ? (
                  <p className="preview-paragraph">{section.content}</p>
                ) : null}
                {section.bullets.length ? (
                  <ul className="preview-bullets">
                    {section.bullets.map((bullet, i) => (
                      <li key={i}>{bullet}</li>
                    ))}
                  </ul>
                ) : null}
                {section.table ? (
                  <table className="preview-table">
                    {section.table.caption ? (
                      <caption className="preview-table-caption">{section.table.caption}</caption>
                    ) : null}
                    {section.table.headers.length ? (
                      <thead>
                        <tr>
                          {section.table.headers.map((cell, i) => (
                            <th key={i}>{cell}</th>
                          ))}
                        </tr>
                      </thead>
                    ) : null}
                    <tbody>
                      {section.table.rows.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {row.map((cell, cellIndex) => (
                            <td key={cellIndex}>{cell}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : null}
              </section>
            )
          })}
        </div>

        <footer className="preview-footer">
          <span className="preview-footer-left">
            {footerText || organization || content.title}
          </span>
          <span className="preview-footer-right">
            Page {page} of {totalPages}
          </span>
        </footer>
      </article>

      {content.disclaimer ? (
        <p className="max-w-[21cm] px-1 text-center text-[0.6875rem] leading-relaxed text-ivory-300/40">
          {content.disclaimer}
        </p>
      ) : null}
    </div>
  )
}

function SignatureGrid({ blocks }: { blocks: SignatureBlock[] }) {
  return (
    <div className="mt-8 grid gap-8 sm:grid-cols-2">
      {blocks.map((block, index) => (
        <div key={`${block.party_label}-${index}`}>
          <p className="preview-paragraph font-medium">
            {block.party_label}
            {block.role ? `, ${block.role}` : ''}
          </p>
          <div className="mt-5 flex flex-col gap-5">
            {block.fields.map((field) => (
              <div key={field}>
                <div className="signature-line" />
                <p className="mt-1 text-[0.625rem] tracking-wide text-ink-600/60 uppercase">
                  {field}
                </p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
