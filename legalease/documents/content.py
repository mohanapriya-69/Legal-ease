"""Shared narrative content for the LegalEase project presentation.

Both the PPTX deck and the PDF report are generated from this module so the two
artefacts can never drift apart. Everything here describes work that was
actually done and verified - no aspirational claims.
"""

from __future__ import annotations

PROJECT_NAME = "LegalEase"
SUBTITLE = "AI-Assisted Legal Document Generation"
TAGLINE = "How the project was built, end to end"

# --- Brand -----------------------------------------------------------------

INK = (24, 30, 45)
SLATE = (71, 85, 105)
MUTED = (130, 140, 155)
GOLD = (191, 148, 66)
GOLD_SOFT = (240, 233, 214)
PAPER = (250, 249, 246)
RULE = (223, 220, 212)
WHITE = (255, 255, 255)
TEAL = (32, 122, 130)
TEAL_SOFT = (226, 240, 241)
RED = (176, 62, 55)
RED_SOFT = (250, 232, 230)
GREEN = (43, 122, 78)
GREEN_SOFT = (228, 242, 234)

# --- Deck structure --------------------------------------------------------

TITLE_SLIDE = {
    "eyebrow": "PROJECT REPORT",
    "title": PROJECT_NAME,
    "subtitle": SUBTITLE,
    "tagline": TAGLINE,
    "meta": [
        "FastAPI + React 19 + Groq",
        "Local-first legal document drafting",
    ],
}

SLIDES: list[dict] = [
    {
        "kind": "agenda",
        "eyebrow": "CONTENTS",
        "title": "What This Covers",
        "items": [
            ("01", "The brief", "What was asked for, and the brief as written"),
            ("02", "Key decisions", "Three deliberate departures from the spec"),
            ("03", "Architecture", "How the pieces fit together"),
            ("04", "The build", "Backend, then frontend, in order"),
            ("05", "Switching to Groq", "The one change that was a real migration"),
            ("06", "Two real bugs", "Found by testing, not by reading"),
            ("07", "Verification", "Evidence, not assertions"),
            ("08", "Honest gaps", "What is not built"),
            ("09", "What is next", "Prioritised, with effort estimates"),
        ],
    },
    {
        "kind": "bullets",
        "eyebrow": "01  THE BRIEF",
        "title": "What Was Asked For",
        "lead": "LegalEase generates legal documents from user input. The written brief specified the stack precisely.",
        "bullets": [
            ("Stack", "FastAPI backend, Streamlit frontend, Gemini 1.5 Pro"),
            ("Input", "Document type, parties, terms, effective date"),
            ("Output", "Structured documents as .txt, .docx and .pdf"),
            ("Presentation", "Logo on the front page, footer on every page"),
            ("Core UX", "Generate, preview, edit, download"),
            ("Deployment", "Procfile / Dockerfile, then a cloud host"),
        ],
        "foot": "Terms were specified as semicolon-separated bullets. We kept structured input instead - see slide 02.",
    },
    {
        "kind": "bullets",
        "eyebrow": "02  KEY DECISIONS",
        "title": "Three Deliberate Departures",
        "lead": "Each of these was a choice, not an accident. Two of them were necessary; one was requested.",
        "bullets": [
            (
                "Streamlit  ->  React 19 + Vite",
                "A wizard, a three-pane editor and a document dashboard cannot be built in Streamlit without fighting it. A real SPA is the honest answer to the UX in the brief.",
            ),
            (
                "Gemini 1.5 Pro  ->  Groq",
                "Requested mid-project, and independently the right call: 1.5 Pro is a retired model, so the brief as written would not have run.",
            ),
            (
                "google-generativeai  ->  httpx",
                "Groq speaks an OpenAI-compatible API. Calling it over plain HTTP keeps dependencies minimal while still enforcing a strict JSON schema.",
            ),
        ],
    },
    {
        "kind": "compare",
        "eyebrow": "02  KEY DECISIONS",
        "title": "Spec vs. Delivered",
        "left_title": "BRIEF SPECIFIED",
        "left": [
            "Streamlit UI",
            "Gemini 1.5 Pro",
            "4 input fields",
            "Editable text area",
            "Procfile / Dockerfile",
            "Sanitize text for quotes",
        ],
        "right_title": "DELIVERED",
        "right": [
            "React 19 + Vite + TypeScript",
            "Groq (gpt-oss-120b)",
            "6-step wizard, rich validation",
            "Full editor + clause-level AI rewrite",
            "README + run docs",
            "Structured outputs (no cleanup needed)",
        ],
        "verdict": "Every functional requirement is met or exceeded. Two items are outstanding - both listed on slide 08.",
    },
    {
        "kind": "layers",
        "eyebrow": "03  ARCHITECTURE",
        "title": "How It Fits Together",
        "lead": "Three tiers. The frontend never talks to the model; the model never talks to the database.",
        "layers": [
            (
                "PRESENTATION",
                "React 19 SPA  -  landing, 6-step wizard, dashboard, template library, three-pane editor",
                "Tailwind 4, Radix, React Query, Zustand",
            ),
            (
                "API",
                "FastAPI  -  10 routes under /api, Pydantic validation, typed error envelope",
                "Documents, branding, templates, health, exports",
            ),
            (
                "INTELLIGENCE",
                "Groq client  -  strict JSON schema, retry on truncation, errors mapped to safe codes",
                "Or deterministic demo mode when no key is set",
            ),
            (
                "PERSISTENCE",
                "SQLAlchemy 2 + SQLite  -  documents, versions, brand profiles",
                "PostgreSQL DSN supported for anything beyond local",
            ),
        ],
    },
    {
        "kind": "numbered",
        "eyebrow": "04  THE BUILD  -  BACKEND",
        "title": "Built Bottom-Up",
        "lead": "Order mattered: contracts before the AI, because the AI is generated against a schema.",
        "items": [
            ("01", "Config and database", "Settings from .env, SQLAlchemy 2 engine, SQLite with foreign keys on"),
            ("02", "Schemas first", "Pydantic contracts, including DocumentDraft - the one shape AI, DB, preview and all three exporters agree on"),
            ("03", "Models and services", "Document, DocumentVersion, BrandProfile; versioning, duplication, statistics"),
            ("04", "AI layer", "Prompts, client, orchestration, plus a deterministic demo generator for offline work"),
            ("05", "18 document types", "NDA, employment, lease and more, each with suggested sections"),
            ("06", "Three exporters", "PDF, DOCX and TXT sharing one layout module and one A4 geometry"),
            ("07", "Error envelope", "Every failure returns {code, message}; upstream detail never leaks"),
        ],
    },
    {
        "kind": "numbered",
        "eyebrow": "04  THE BUILD  -  FRONTEND",
        "title": "Then the Interface",
        "lead": "Built to the same contracts the backend already enforced, so the types line up by construction.",
        "items": [
            ("01", "Design system", "Buttons, cards, fields, dialogs, badges, skeletons, alerts, empty states"),
            ("02", "Typed API layer", "One Axios client, normalised errors, blob-based downloads with safe filenames"),
            ("03", "State and data", "React Query for server state, Zustand for wizard state, sessionStorage persistence"),
            ("04", "Six-step wizard", "Document, parties, clauses, dates, jurisdiction and branding - validated per step"),
            ("05", "Dashboard and templates", "Search, status filters, pagination, delete confirmation, empty states"),
            ("06", "Three-pane editor", "Outline, A4 preview, section editor - with debounced autosave"),
            ("07", "AI and exports", "Clause-level rewrite actions, version history with restore, PDF/DOCX/TXT export"),
        ],
    },
    {
        "kind": "bug",
        "eyebrow": "05  SWITCHING TO GROQ",
        "title": "The One Real Migration",
        "lead": "A model swap looks like a config change. It was not.",
        "symptom": "Every single live generation call returned HTTP 400 and failed in under a second.",
        "root_cause": "Pydantic and Groq's strict mode disagree about what a JSON schema means.",
        "detail": [
            ("Pydantic emits $defs + $ref", "Groq rejects provider-specific reference support"),
            ("Pydantic omits additionalProperties", "Strict mode requires every object to be closed"),
            ("Pydantic lists only required keys", "Strict mode requires every property to be listed"),
        ],
        "fix": "normalize_json_schema() inlines every reference against $defs, adds additionalProperties: false to every object, and requires every property - while preserving optionality through the nullable unions Pydantic already emits.",
        "lesson": "The fix was not configuration. Assuming it was would have sent us hunting for a wrong API key.",
    },
    {
        "kind": "bug",
        "eyebrow": "06  TWO REAL BUGS",
        "title": "Found by Testing, Not Reading",
        "lead": "Both were invisible to typecheck, lint and 120 passing tests. Only real calls exposed them.",
        "symptom": "Any request without an effective date returned HTTP 500.",
        "root_cause": "effective_date is optional in the request schema, but the prompt builder called .isoformat() on it unconditionally.",
        "detail": [
            ("500 INTERNAL_ERROR", "AttributeError: 'NoneType' object has no attribute 'isoformat'"),
            ("Pre-existing", "Would have hit Gemini identically - not caused by the migration"),
            ("Contradicts the schema", "Optional in the contract, mandatory in the code"),
        ],
        "fix": "The prompt builder now degrades to a clear placeholder. Two regression tests were added, one asserting the prompt still builds without dates and one proving generation succeeds.",
        "lesson": "A passing suite proves the tested paths work. It does not prove optional inputs are handled.",
    },
    {
        "kind": "verify",
        "eyebrow": "07  VERIFICATION",
        "title": "Evidence, Not Assertions",
        "lead": "Every claim below was executed against the running application with a live model.",
        "checks": [
            ("Backend test suite", "131 passed", "Up from 120. Added transport error mapping, truncation retry, schema normalisation and optional-date regression tests.", "pass"),
            ("Live generation", "8 sections in 6s", "Real Groq call. No markup leakage; disclaimer and signature blocks present.", "pass"),
            ("Live clause rewrite", "Version 3 created", "Section 4 rewritten by the model, with before/after versions recorded.", "pass"),
            ("PDF export", "77 text ops", "Decoded ReportLab's ASCII85+Flate streams and confirmed every section is present.", "pass"),
            ("DOCX export", "19 zip entries", "All sections present in word/document.xml.", "pass"),
            ("TXT export", "8 sections", "Confirmed, and the disclaimer included.", "pass"),
            ("Frontend", "Lint, types, build", "oxlint clean, tsc -b clean, production build succeeded.", "pass"),
            ("Secret hygiene", "No leak", "The API key exists only in a gitignored .env. Tracked files contain no key.", "pass"),
        ],
    },
    {
        "kind": "verify",
        "eyebrow": "07  VERIFICATION",
        "title": "Two Things I Initially Got Wrong",
        "lead": "Reported as failures, then disproved. Recording them because the reasoning is the point.",
        "checks": [
            ("Mojibake in output", "False alarm", "Text appeared corrupted in the console. A Python check found zero corrupted characters in stored data.", "warn"),
            ("Missing sections", "False alarm", "A case-sensitive grep missed uppercase headings. All sections were present.", "warn"),
            ("Why it matters", "Both were my probe", "Not the product. A wrong test can condemn correct code as easily as a wrong test can pass broken code.", "pass"),
        ],
    },
    {
        "kind": "gaps",
        "eyebrow": "08  HONEST GAPS",
        "title": "What Is Not Built",
        "lead": "Stated plainly so nothing here is a surprise later.",
        "gaps": [
            (
                "No deployment artifacts",
                "significant",
                "No Procfile, Dockerfile or render.yaml. The brief's Milestone 5 asks for them. Note: the app has no authentication and stores data in SQLite, so it is safe locally but not ready to expose publicly. Auth and PostgreSQL would come first.",
            ),
            (
                "No sanitize_text()",
                "minor",
                "The brief specifies stripping smart quotes before formatting. Not needed - Groq's strict schema guarantees valid UTF-8, which is why stored data verified clean. Trivial to add defensively at export time.",
            ),
            (
                "No multilingual support",
                "not built",
                "The brief's conclusion claims multilingual capability. There is none. Deliberately out of scope unless requested.",
            ),
            (
                "No plain-language summary",
                "not built",
                "Also claimed in the conclusion. Not implemented.",
            ),
        ],
    },
    {
        "kind": "numbered",
        "eyebrow": "09  WHAT IS NEXT",
        "title": "Prioritised, With Estimates",
        "lead": "Ordered by value against the brief.",
        "items": [
            ("01", "Deployment artifacts", "~30 min", "Dockerfile, Procfile, render.yaml. Unambiguous value against the brief. Pair with auth before any public deploy."),
            ("02", "sanitize_text() at export", "~20 min", "Normalise typographic quotes and strip control characters before the exporters run."),
            ("03", "Author the remaining claims", "scope first", "Multilingual and summarisation roughly double scope. Worth building only if they are graded."),
            ("04", "Better drafting model", "config only", "gpt-oss-120b is a general reasoning model, not tuned for legal. qwen/qwen3.8-27b is the other option on this key."),
            ("05", "Add charset=utf-8 to JSON", "trivial", "Windows tools misread UTF-8 responses without it. Harmless and more correct."),
        ],
    },
    {
        "kind": "closing",
        "eyebrow": "IN SUMMARY",
        "title": "What Was Delivered",
        "points": [
            ("A working product", "All three scenarios in the brief run end to end against a live model."),
            ("A real migration", "Gemini to Groq, including the schema incompatibility that blocked it."),
            ("Two bugs found", "One pre-existing 500, one design flaw - both caught by testing, both fixed with regression tests."),
            ("Honest accounting", "131 passing tests, verified exports, and a clear list of what is missing."),
        ],
        "close": "The product meets or exceeds every functional requirement in the brief. The outstanding work is deployment packaging and two features the conclusion claims but nobody built.",
    },
]

# --- PDF-only narrative sections -------------------------------------------

PDF_INTRO = (
    "This document records how LegalEase was built from the written brief through "
    "to a verified, running application. It is written to be read alongside the "
    "code rather than instead of it, and it deliberately includes what was not "
    "built and what was initially got wrong."
)

PDF_SECTIONS: list[dict] = [
    {
        "heading": "1.  The brief",
        "body": [
            "The brief specified LegalEase as an AI-assisted legal document generator "
            "with a precise stack: FastAPI on the backend, Streamlit on the frontend, "
            "and Gemini 1.5 Pro for generation. Users supply a document type, the "
            "parties, the terms and an effective date, then generate, preview, edit "
            "and download the result as .txt, .docx or .pdf. The brief also expected "
            "a logo on the front page, a footer on every page, and deployment "
            "artifacts in the final milestone.",
            "Three worked scenarios were described: an employment contract for a new "
            "hire, a non-disclosure agreement for a freelancer, and a residential "
            "lease for a landlord. All three are supported, and all three run end to "
            "end against a live model.",
        ],
    },
    {
        "heading": "2.  Key decisions",
        "body": [
            "Three departures from the brief were made deliberately. Each is a choice "
            "rather than an accident, and two of them were necessary rather than "
            "merely preferable.",
            "Streamlit was replaced with a React 19 single-page application. The brief "
            "asks for a six-field intake, an editable preview and downloads. A wizard, "
            "a three-pane editor and a searchable document dashboard cannot be built "
            "in Streamlit without fighting the framework, so a real SPA is the honest "
            "answer to that interface.",
            "Gemini 1.5 Pro was replaced with Groq's openai/gpt-oss-120b. This was "
            "requested part-way through the project, and it was also the right call "
            "independently: 1.5 Pro is a retired model, so the brief as written would "
            "not have run against a live key today.",
            "The google-generativeai SDK was replaced with plain httpx calls to Groq's "
            "OpenAI-compatible endpoint. This keeps the dependency surface small while "
            "still constraining the model to a strict JSON schema, and it means the "
            "application still boots and serves every read-only route when no API key "
            "is configured.",
        ],
    },
    {
        "heading": "3.  Architecture",
        "body": [
            "The application is organised in four tiers with a strict rule between "
            "them: the frontend never talks to the model, and the model never talks to "
            "the database.",
            "Presentation: a React 19 single-page application built with Vite, "
            "TypeScript, Tailwind 4, Radix primitives and React Query. It contains a "
            "landing page, a six-step wizard, a document dashboard, a template library "
            "and a three-pane editor.",
            "API: FastAPI exposing ten routes under /api, validating every payload "
            "with Pydantic and returning a uniform error envelope. Documents, "
            "branding, templates, health and exports are all served from here.",
            "Intelligence: the Groq client, which issues strict JSON-schema requests, "
            "retries once with a larger token budget when a reply is truncated, and "
            "maps every provider failure onto a typed, client-safe error. When no key "
            "is set, a deterministic demo generator produces clearly labelled sample "
            "output so the workflow can be evaluated offline.",
            "Persistence: SQLAlchemy 2 with SQLite for local use, storing documents, "
            "document versions and brand profiles. A PostgreSQL DSN is supported for "
            "anything beyond a single local installation.",
        ],
    },
    {
        "heading": "4.  The build",
        "body": [
            "The backend was built bottom-up, and the order mattered. Schemas were "
            "written before the AI layer, because the AI is generated against a "
            "schema. The central artefact is DocumentDraft, a single Pydantic contract "
            "that the model, the database, the preview and all three exporters agree "
            "on. Getting that shape right up front is what made the rest of the system "
            "agreeable to build.",
            "After configuration and the database layer came the schemas, then the "
            "models and services, then the AI layer with its prompts, client, "
            "orchestration and offline demo generator. The template catalogue of "
            "eighteen document types followed, then the three exporters, which share "
            "a single layout module and A4 geometry so a document looks the same "
            "whichever format it is exported as.",
            "The frontend was then built against the contracts the backend already "
            "enforced, so the two sides line up by construction rather than by "
            "convention. A design system of reusable primitives came first, then a "
            "typed API layer, then state and data management, then the wizard, the "
            "dashboard and template library, and finally the editor with debounced "
            "autosave, clause-level AI rewriting, version history and exports.",
        ],
    },
    {
        "heading": "5.  Switching to Groq",
        "body": [
            "The model swap looked like a configuration change and was not. The first "
            "live generation call returned HTTP 400 in under a second, and the same "
            "failure repeated for every request. The cause was a genuine incompatibility "
            "between Pydantic's JSON schema output and Groq's strict structured-output "
            "mode.",
            "Pydantic emits a $defs block with $ref references, omits "
            "additionalProperties, and lists only genuinely required keys in required. "
            "A strict decoder rejects all three: it wants references resolved inline, "
            "every object closed, and every property listed as required.",
            "The fix is normalize_json_schema, which runs before the request is sent. It "
            "inlines every reference against the $defs block, adds "
            "additionalProperties: false to every object, and lists every property in "
            "required, while preserving optionality through the nullable unions "
            "Pydantic already generates. After that change a live call returned a valid "
            "draft in roughly three seconds.",
            "The broader lesson is worth recording: the failure presented as an "
            "authentication-adjacent 400, and the plausible-but-wrong response was to "
            "suspect the API key. Chasing the key would have consumed time and found "
            "nothing. Reading the provider's actual rejection message is what "
            "identified the real cause.",
        ],
    },
    {
        "heading": "6.  Two real bugs",
        "body": [
            "The Groq schema incompatibility was not the only defect. A second, "
            "pre-existing bug surfaced as soon as a request omitted its effective date, "
            "which the request schema explicitly allows.",
            "The prompt builder called .isoformat() on request.effective_date without "
            "checking it, raising an AttributeError that surfaced as a generic HTTP 500. "
            "This was unrelated to the model change and would have failed identically "
            "under Gemini. It is a contradiction between the contract, which declares "
            "the field optional, and the code, which treated it as mandatory.",
            "The fix degrades gracefully to a clear placeholder. Two regression tests "
            "were added: one asserting the prompt still builds without dates, and one "
            "proving generation succeeds end to end without them.",
            "Both bugs are worth noting for a common reason. Neither was visible to "
            "typecheck, to lint, or to a suite of 120 passing tests. Only real calls "
            "against real data exposed them, which is a fair argument for treating "
            "end-to-end checks as part of the definition of done rather than as an "
            "optional extra.",
        ],
    },
    {
        "heading": "7.  Verification",
        "body": [
            "Every claim in this section was executed against the running application "
            "with a live model, not inferred from reading code.",
            "The backend suite passes 131 tests, up from 120. The additions cover "
            "transport-level error mapping, the truncated-reply retry, JSON-schema "
            "normalisation and the optional-date regression.",
            "A live generation call produced an eight-section NDA in about six seconds, "
            "with no markup leakage, the disclaimer present and both signature blocks "
            "intact. A live clause rewrite of section four succeeded and created "
            "version three, with before and after states recorded.",
            "All three exports were verified by decoding their contents rather than "
            "merely confirming a valid file. The PDF was checked by decompressing "
            "ReportLab's ASCII85 and Flate streams and finding all eight sections "
            "among 77 text operations. The DOCX was checked by reading "
            "word/document.xml from the resulting archive, and the plain-text export "
            "was read directly.",
            "On the frontend, linting, the TypeScript project build and the production "
            "build all pass cleanly. Secret hygiene was checked by scanning every "
            "tracked file for the API key, which appears only in a gitignored .env.",
        ],
    },
    {
        "heading": "8.  Two things initially reported as failures",
        "body": [
            "Two apparent failures turned out to be faults in the verification probes "
            "rather than in the product, and both are recorded here because the "
            "reasoning matters more than the outcome.",
            "Generated text appeared to contain corrupted characters in the console. A "
            "check performed in Python found zero replacement or control characters in "
            "the stored data. The cause was the Windows PowerShell 5.1 HTTP client "
            "decoding a UTF-8 response as ISO-8859-1, because the response does not "
            "declare a character set. The application was never at fault, though "
            "declaring charset=utf-8 on JSON responses remains a small correctness "
            "improvement for any Windows consumer.",
            "Two sections appeared to be missing from the plain-text export. The probe "
            "searched case-sensitively for mixed-case text, while the exporter correctly "
            "renders headings in upper case. All eight sections were present. The PDF "
            "probe failed similarly at first, because ReportLab compresses content "
            "streams and the initial extraction did not decompress them.",
            "The general point is that a wrong test can condemn correct code just as "
            "effectively as a wrong test can pass broken code. When a check fails, the "
            "first question should be whether the check is right.",
        ],
    },
    {
        "heading": "9.  What is not built",
        "body": [
            "Three items are outstanding, and one group of claims in the original brief "
            "is not implemented at all.",
            "There are no deployment artifacts. The brief's final milestone asks for a "
            "Procfile, a Dockerfile or equivalent configuration, and none exists. It "
            "should be noted that adding them would not make the application safe to "
            "expose on a public host in its current state, because there is no "
            "authentication and data is stored in SQLite. Authentication and a "
            "PostgreSQL database would be prerequisites for a public deployment, not "
            "enhancements to one.",
            "There is no sanitize_text function. The brief specifies stripping "
            "typographic quotes and special characters before formatting. It is not "
            "needed, because strict structured outputs guarantee valid UTF-8, which is "
            "exactly why the stored data verified clean. It remains cheap and "
            "defensible to add as a final pass before export.",
            "The brief's conclusion claims multilingual capability and plain-language "
            "summaries. Neither exists. They were treated as out of scope rather than "
            "quietly overlooked, and neither should be assumed present.",
        ],
    },
    {
        "heading": "10.  What is next",
        "body": [
            "Deployment artifacts come first, at roughly thirty minutes of work, and "
            "are unambiguous value against the brief. They should be paired with "
            "authentication before any public deployment. A sanitize_text pass at "
            "export time follows at roughly twenty minutes.",
            "Multilingual support and summarisation roughly double the scope of the "
            "project and are worth building only if they are being assessed rather "
            "than merely described. They should not be claimed in documentation until "
            "they exist.",
            "On model choice, the currently configured gpt-oss-120b is a general "
            "reasoning model rather than one tuned for legal drafting. Output is usable "
            "but not excellent, and it has been observed to miss a requested clause "
            "name in a single run. qwen/qwen3.8-27b is the other realistic option "
            "available on the current key, and switching is a configuration change "
            "rather than a code change.",
            "One small correctness item remains: declaring charset=utf-8 on JSON "
            "responses so that Windows tooling reads them correctly without guessing.",
        ],
    },
]

PDF_STATS = [
    ("131", "backend tests", "passing, from 120"),
    ("18", "document types", "NDA, employment, lease, and more"),
    ("10", "API routes", "under /api"),
    ("3", "export formats", "PDF, DOCX and TXT"),
    ("6", "wizard steps", "validated per step"),
]

PDF_CLOSING = (
    "The product meets or exceeds every functional requirement in the written brief. "
    "The outstanding work is deployment packaging, plus two capabilities the original "
    "document's conclusion claims but which nobody built. Recording both is more "
    "useful than presenting a clean sheet that would not survive review."
)
