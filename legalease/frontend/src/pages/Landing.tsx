import { motion } from 'framer-motion'
import { ArrowRight, Check, Clock, Download, PenLine, Sparkles, Wand2 } from 'lucide-react'
import { Link } from 'react-router-dom'

import { templateIcon } from '../components/icons'
import { GoldRule, Logo } from '../components/layout/Logo'
import { LegalDisclaimer } from '../components/layout/Disclaimer'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { useTemplates } from '../hooks/useTemplates'
import { ERROR_MESSAGES } from '../services'

const STEPS = [
  {
    icon: LayoutGridIcon,
    title: 'Pick a template',
    body: 'Start from one of 18 agreement types, each with the clauses that usually matter.',
  },
  {
    icon: PenLine,
    title: 'Answer guided questions',
    body: 'Parties, terms, dates and jurisdiction. No legal jargon required.',
  },
  {
    icon: Sparkles,
    title: 'Generate a structured draft',
    body: 'You get numbered sections, bullets and signature blocks, ready to edit.',
  },
  {
    icon: Download,
    title: 'Review, revise and export',
    body: 'Autosaved editing, AI section rewrites, version history, PDF/DOCX/TXT.',
  },
]

// Kept local so the feature list does not depend on lucide's icon registry size.
function LayoutGridIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" className={className} aria-hidden>
      <rect x="3" y="3" width="7.5" height="7.5" rx="1.6" />
      <rect x="13.5" y="3" width="7.5" height="7.5" rx="1.6" />
      <rect x="3" y="13.5" width="7.5" height="7.5" rx="1.6" />
      <rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.6" />
    </svg>
  )
}

const CAPABILITIES = [
  {
    icon: Wand2,
    title: 'Section-level AI rewrites',
    body: 'Simplify dense language, make it more formal, expand a thin clause, or add protective language without regenerating the whole document.',
  },
  {
    icon: Clock,
    title: 'Autosave and version history',
    body: 'Every edit is persisted locally. Restore any earlier version, with a snapshot taken automatically before each AI rewrite.',
  },
  {
    icon: Download,
    title: 'Three export formats',
    body: 'A4 PDF with page numbers and letterhead, an editable Word file, and clean plain text.',
  },
]

export function Landing() {
  const { templates, isLoading, isError, total } = useTemplates({})
  const featured = templates.filter((t) => t.popular).slice(0, 6)
  const showcase = (featured.length ? featured : templates).slice(0, 6)

  return (
    <>
      {/* ------------------------------------------------------------ Hero */}
      <section className="relative overflow-hidden">
        <div className="mx-auto max-w-7xl px-4 pt-16 pb-20 sm:px-6 lg:px-8 lg:pt-24 lg:pb-28">
          <div className="grid items-center gap-14 lg:grid-cols-[1.05fr_0.95fr]">
            <div>
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              >
                <Badge variant="gold" size="sm">
                  <Sparkles className="size-3" aria-hidden />
                  AI-assisted legal drafting
                </Badge>

                <h1 className="mt-6 font-display text-[2.5rem] leading-[1.08] font-semibold tracking-tight text-ivory-50 sm:text-5xl lg:text-[3.75rem]">
                  Professional legal
                  <br />
                  documents,{' '}
                  <span className="relative inline-block">
                    <span className="relative z-10 bg-gradient-to-r from-gold-200 via-gold-400 to-gold-200 bg-clip-text text-transparent">
                      drafted in minutes
                    </span>
                    <span
                      className="absolute inset-x-0 bottom-1.5 -z-0 h-3 bg-gold-500/12 blur-[6px]"
                      aria-hidden
                    />
                  </span>
                </h1>

                <GoldRule className="mt-7" />

                <p className="mt-6 max-w-xl text-base leading-relaxed text-ivory-300/75">
                  LegalEase walks you through a structured intake, has the AI draft a
                  properly structured agreement, and hands you an editable document you can
                  revise section by section, version, and export as PDF, Word or plain text.
                </p>

                <div className="mt-9 flex flex-col gap-3 sm:flex-row">
                  <Button asChild size="lg">
                    <Link to="/create">
                      Draft a document
                      <ArrowRight aria-hidden />
                    </Link>
                  </Button>
                  <Button asChild size="lg" variant="outline">
                    <Link to="/templates">
                      Browse {isLoading ? 'templates' : `${total || 18} templates`}
                    </Link>
                  </Button>
                </div>

                <dl className="mt-12 grid max-w-lg grid-cols-3 gap-6 border-t border-navy-700/60 pt-8">
                  {[
                    { value: '18', label: 'Document types' },
                    { value: '6', label: 'Intake steps' },
                    { value: '3', label: 'Export formats' },
                  ].map((stat) => (
                    <div key={stat.label}>
                      <dt className="sr-only">{stat.label}</dt>
                      <dd>
                        <span className="block font-display text-2xl font-semibold text-gold-300">
                          {stat.value}
                        </span>
                        <span className="mt-1 block text-xs tracking-wide text-ivory-300/55">
                          {stat.label}
                        </span>
                      </dd>
                    </div>
                  ))}
                </dl>
              </motion.div>
            </div>

            <HeroPreview />
          </div>
        </div>
      </section>

      {/* --------------------------------------------------------- How it works */}
      <section className="border-y border-navy-700/50 bg-navy-950/40 py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <SectionHeading
            eyebrow="How it works"
            title="Four steps from blank page to signed-ready draft"
            body="Every step is guided, so you never have to know what a governing-law clause is before you start."
          />

          <ol className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {STEPS.map((step, index) => (
              <motion.li
                key={step.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ duration: 0.45, delay: index * 0.07, ease: [0.22, 1, 0.36, 1] }}
              >
                <Card className="group h-full p-6 hover:border-gold-500/35">
                  <div className="flex items-center gap-3">
                    <span className="flex size-10 items-center justify-center rounded-xl border border-gold-500/25 bg-navy-800 text-gold-400 transition-colors group-hover:border-gold-500/50">
                      <step.icon className="size-5" aria-hidden />
                    </span>
                    <span className="font-mono text-xs text-ivory-300/35">
                      0{index + 1}
                    </span>
                  </div>
                  <h3 className="mt-5 font-display text-base font-semibold text-ivory-50">
                    {step.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-ivory-300/65">{step.body}</p>
                </Card>
              </motion.li>
            ))}
          </ol>
        </div>
      </section>

      {/* ------------------------------------------------------ Template showcase */}
      <section className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-end justify-between gap-6">
            <SectionHeading
              eyebrow="Template library"
              title="Start from the agreement you actually need"
              body="Each template arrives with suggested sections and clauses pre-selected, so the draft starts close to final."
            />
            <Button asChild variant="ghost" size="sm">
              <Link to="/templates">
                See all
                <ArrowRight aria-hidden />
              </Link>
            </Button>
          </div>

          {isError ? (
            <Card className="mt-10 border-rose-500/30 p-6">
              <p className="text-sm text-rose-200">
                {ERROR_MESSAGES.NETWORK_ERROR} The template library needs the backend running.
              </p>
            </Card>
          ) : (
            <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {showcase.map((template, index) => {
                const Icon = templateIcon(template.icon)
                return (
                  <motion.div
                    key={template.id}
                    initial={{ opacity: 0, y: 14 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: '-40px' }}
                    transition={{
                      duration: 0.4,
                      delay: Math.min(index, 5) * 0.05,
                      ease: [0.22, 1, 0.36, 1],
                    }}
                  >
                    <Link
                      to={`/create?template=${template.id}`}
                      className="group block h-full rounded-card focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold-400"
                    >
                      <Card className="flex h-full flex-col p-6 group-hover:border-gold-500/40 group-hover:bg-navy-850">
                        <div className="flex items-start justify-between gap-4">
                          <span className="flex size-11 items-center justify-center rounded-xl border border-navy-600 bg-navy-800/70 text-gold-400 transition-colors group-hover:border-gold-500/30">
                            <Icon className="size-5" aria-hidden />
                          </span>
                          {template.popular ? (
                            <Badge variant="gold" size="sm">
                              Popular
                            </Badge>
                          ) : null}
                        </div>
                        <h3 className="mt-5 font-display text-base font-semibold text-ivory-50">
                          {template.title}
                        </h3>
                        <p className="mt-2 flex-1 text-sm leading-relaxed text-ivory-300/60">
                          {template.description}
                        </p>
                        <div className="mt-5 flex items-center gap-3 text-[0.6875rem] text-ivory-300/45">
                          <span className="rounded-full border border-navy-600 px-2 py-0.5">
                            {template.category}
                          </span>
                          <span className="inline-flex items-center gap-1">
                            <Clock className="size-3" aria-hidden />~{template.estimated_minutes} min
                          </span>
                        </div>
                      </Card>
                    </Link>
                  </motion.div>
                )
              })}
            </div>
          )}
        </div>
      </section>

      {/* -------------------------------------------------------- Capabilities */}
      <section className="border-y border-navy-700/50 bg-navy-950/40 py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <SectionHeading
            eyebrow="Built for real work"
            title="Not a chatbot with a legal skin"
            body="The drafting output is a structured document contract, so every part of the pipeline - preview, database, and all three exporters - agrees on the same content."
          />
          <div className="mt-14 grid gap-6 lg:grid-cols-3">
            {CAPABILITIES.map((item) => (
              <Card key={item.title} className="p-7">
                <span className="flex size-10 items-center justify-center rounded-xl border border-navy-600 bg-navy-800/70 text-gold-400">
                  <item.icon className="size-5" aria-hidden />
                </span>
                <h3 className="mt-5 font-display text-base font-semibold text-ivory-50">
                  {item.title}
                </h3>
                <p className="mt-2.5 text-sm leading-relaxed text-ivory-300/65">{item.body}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------- Disclaimer */}
      <section className="py-20">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <LegalDisclaimer className="border-amber-500/30" />
          <div className="mt-6 rounded-2xl border border-navy-700/60 bg-navy-900/40 p-6">
            <h2 className="font-display text-lg font-semibold text-ivory-50">
              Why the disclaimer is impossible to miss
            </h2>
            <ul className="mt-4 flex flex-col gap-2.5 text-sm leading-relaxed text-ivory-300/65">
              {[
                'The full disclaimer is shown before you can generate anything.',
                'It appears at the top of every document and in the editor chrome.',
                'A short form is printed on every exported PDF page.',
                'A tick box is required before generation, so it cannot be skipped by accident.',
              ].map((item) => (
                <li key={item} className="flex items-start gap-2.5">
                  <Check className="mt-0.5 size-4 shrink-0 text-gold-400" aria-hidden />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* --------------------------------------------------------------- CTA */}
      <section className="pb-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-3xl border border-gold-500/25 bg-gradient-to-br from-navy-800 via-navy-850 to-navy-900 px-8 py-14 text-center">
            <div
              className="pointer-events-none absolute -top-24 left-1/2 size-72 -translate-x-1/2 rounded-full bg-gold-500/12 blur-3xl"
              aria-hidden
            />
            <div className="relative">
              <Logo className="justify-center" linkTo={null} />
              <h2 className="mt-6 font-display text-2xl font-semibold tracking-tight text-ivory-50 sm:text-3xl">
                Ready to draft something properly?
              </h2>
              <p className="mx-auto mt-3 max-w-lg text-sm leading-relaxed text-ivory-300/70">
                Six short steps. A structured first draft you can actually edit.
              </p>
              <Button asChild size="lg" className="mt-8">
                <Link to="/create">
                  Start drafting
                  <ArrowRight aria-hidden />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}

/* ------------------------------------------------------------------ Parts */

function SectionHeading({
  eyebrow,
  title,
  body,
}: {
  eyebrow: string
  title: string
  body: string
}) {
  return (
    <div className="max-w-2xl">
      <p className="text-[0.6875rem] font-medium tracking-[0.18em] text-gold-400/85 uppercase">
        {eyebrow}
      </p>
      <h2 className="mt-3 font-display text-2xl font-semibold tracking-tight text-ivory-50 sm:text-3xl">
        {title}
      </h2>
      <p className="mt-3 text-sm leading-relaxed text-ivory-300/65 sm:text-base">{body}</p>
    </div>
  )
}

/** Static preview of the editor, so the hero shows the real product surface. */
function HeroPreview() {
  const sections = [
    { n: '01', heading: 'Definitions', width: 'w-full' },
    { n: '02', heading: 'Scope of Services', width: 'w-11/12' },
    { n: '03', heading: 'Fees and Payment', width: 'w-full' },
    { n: '04', heading: 'Term and Termination', width: 'w-4/5' },
    { n: '05', heading: 'Confidentiality', width: 'w-10/12' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 24, rotateX: 6 }}
      animate={{ opacity: 1, y: 0, rotateX: 0 }}
      transition={{ duration: 0.7, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
      className="relative [perspective:1400px]"
    >
      <div
        className="pointer-events-none absolute -inset-6 rounded-3xl bg-gold-500/8 blur-3xl"
        aria-hidden
      />
      <div className="relative rounded-2xl border border-navy-600/80 bg-navy-850/90 p-1.5 shadow-lift backdrop-blur">
        {/* toolbar */}
        <div className="flex items-center gap-2 rounded-t-xl border-b border-navy-700/80 px-3.5 py-2.5">
          <div className="flex gap-1.5" aria-hidden>
            <span className="size-2.5 rounded-full bg-navy-600" />
            <span className="size-2.5 rounded-full bg-navy-600" />
            <span className="size-2.5 rounded-full bg-navy-600" />
          </div>
          <div className="ml-2 h-4 w-40 rounded bg-navy-700/70" />
          <div className="ml-auto flex items-center gap-1.5">
            <span className="rounded-full border border-gold-500/30 bg-gold-500/10 px-2 py-0.5 text-[0.5625rem] font-medium text-gold-300">
              Live AI
            </span>
            <span className="rounded border border-navy-600 px-2 py-0.5 text-[0.5625rem] text-ivory-300/60">
              PDF
            </span>
          </div>
        </div>

        <div className="grid grid-cols-[5.5rem_1fr] gap-2 p-2">
          {/* sidebar */}
          <div className="flex flex-col gap-1.5 rounded-lg border border-navy-700/70 p-2">
            {['Outline', 'Versions', 'Brand'].map((item, i) => (
              <div
                key={item}
                className={`rounded px-2 py-1.5 text-[0.5625rem] ${
                  i === 0 ? 'bg-navy-700/80 text-gold-300' : 'text-ivory-300/45'
                }`}
              >
                {item}
              </div>
            ))}
            <div className="mt-auto space-y-1.5 pt-3">
              {Array.from({ length: 4 }, (_, i) => (
                <div key={i} className="h-1.5 rounded bg-navy-700/60" style={{ width: `${70 - i * 8}%` }} />
              ))}
            </div>
          </div>

          {/* A4 page */}
          <div className="rounded-lg bg-ivory-100 p-4 shadow-inner">
            <div className="text-center">
              <div className="mx-auto h-1.5 w-28 rounded bg-ink-900/70" />
              <div className="mx-auto mt-1.5 h-1 w-40 rounded bg-ink-900/25" />
            </div>
            <div className="mt-4 space-y-2.5">
              {sections.map((section) => (
                <div key={section.n}>
                  <div className="flex items-baseline gap-1.5">
                    <span className="font-mono text-[0.5rem] text-ink-600/60">{section.n}</span>
                    <span className="h-1.5 w-28 rounded bg-ink-900/55" />
                  </div>
                  <div className="mt-1 space-y-1">
                    <div className={`h-1 rounded bg-ink-900/18 ${section.width}`} />
                    <div className="h-1 w-10/12 rounded bg-ink-900/18" />
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 flex items-end justify-between border-t border-ink-900/12 pt-2">
              <div className="h-1 w-16 rounded bg-ink-900/25" />
              <span className="font-mono text-[0.5rem] text-ink-600/50">Page 1 of 4</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
