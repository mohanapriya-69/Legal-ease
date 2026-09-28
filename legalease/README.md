# LegalEase

AI-assisted legal document drafting. Answer a few questions, generate a
structured agreement, then refine it clause by clause with AI rewrites,
version history, branding and PDF/DOCX/TXT export.

> **Not legal advice.** Generated documents are a starting point for review, not
> a substitute for advice from a qualified lawyer. Laws vary by jurisdiction, and
> no output here is guaranteed to be valid or enforceable. Review important
> agreements before signing.

## Stack

| Layer | Technology |
| --- | --- |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2, SQLite |
| AI | Groq chat completions with structured outputs |
| Frontend | React 19, TypeScript, Vite, Tailwind 4, React Query |

## Requirements

- Python 3.11+
- Node.js 20+

## Setup

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and add your key:

```ini
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-120b
DEMO_MODE=false
```

Create a key at <https://console.groq.com/keys> and see which models it can
reach at `https://api.groq.com/openai/v1/models`.

Then start the API:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive docs are at <http://127.0.0.1:8000/docs>.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The app is at <http://localhost:5173>. The frontend calls the API directly on
`127.0.0.1:8000` (configured via `VITE_API_URL` in `frontend/.env`); there is no
dev proxy, so CORS is genuinely exercised during development.

## Commands

### Backend

| Command | Purpose |
| --- | --- |
| `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` | Run the API |
| `python -m pytest -q` | Run the test suite (131 tests) |
| `python -m pytest -q tests/test_ai.py` | AI generation, rewrite, and schema tests |

### Frontend

| Command | Purpose |
| --- | --- |
| `npm run dev` | Dev server |
| `npm run build` | Typecheck and production build |
| `npm run lint` | Lint with oxlint |
| `npm run preview` | Serve the production build |

## AI modes

`GET /api/ai/status` reports the active mode; the UI surfaces the same state in
its status pill.

| Mode | When | Behaviour |
| --- | --- | --- |
| `groq` | `GROQ_API_KEY` is set | Live drafting via the configured model |
| `demo` | No key, `DEMO_MODE=true` | Deterministic sample output, labelled "Demo AI Response" |
| `unconfigured` | Neither | Generation returns `503 AI_NOT_CONFIGURED`; all read-only routes still work |

Demo mode exists so the whole workflow can be evaluated offline. It never calls a
model and never pretends to.

## Configuration

### Backend (`backend/.env`)

| Variable | Default | Notes |
| --- | --- | --- |
| `GROQ_API_KEY` | _(unset)_ | Never commit this |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | No model name is hardcoded in source |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | Change for a proxy or regional endpoint |
| `GROQ_TEMPERATURE` | `0.3` | |
| `GROQ_MAX_TOKENS` | `8192` | Doubled once on a truncated reply |
| `GROQ_TIMEOUT_SECONDS` | `120` | |
| `GROQ_MAX_RETRIES` | `2` | |
| `DEMO_MODE` | `false` | |
| `DATABASE_URL` | `sqlite:///./legalease.db` | PostgreSQL DSN works too |
| `FRONTEND_URL` | `http://localhost:5173` | Must be an explicit origin, never `*` |

### Frontend (`frontend/.env`)

| Variable | Default |
| --- | --- |
| `VITE_API_URL` | `http://127.0.0.1:8000` |
| `VITE_DEBUG_API` | `false` |

## API

Base path `/api`. Errors always return `{"error": {"code", "message"}}`; codes
are stable strings, and provider failures are translated so no upstream detail
ever reaches the client.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health and AI status |
| `GET` | `/api/ai/status` | AI readiness only |
| `GET` | `/api/templates` | Document template catalog |
| `POST` | `/api/documents/generate` | Generate a draft |
| `GET` | `/api/documents` | List, filter, paginate |
| `GET` | `/api/documents/{id}` | Fetch one |
| `PATCH` | `/api/documents/{id}` | Update / autosave |
| `DELETE` | `/api/documents/{id}` | Delete |
| `POST` | `/api/documents/{id}/duplicate` | Duplicate |
| `POST` | `/api/documents/{id}/rewrite-section` | AI section rewrite |
| `GET` | `/api/documents/{id}/versions` | Version history |
| `POST` | `/api/documents/{id}/versions/{n}/restore` | Restore a version |
| `GET` | `/api/documents/{id}/export/{pdf\|docx\|txt}` | Export |
| `GET`/`POST` | `/api/brand-profiles` | Manage branding |
| `POST` | `/api/brand-profiles/{id}/logo` | Upload a logo (PNG/JPEG, 2 MB) |

## How generation works

`backend/app/ai/client.py` calls Groq's OpenAI-compatible endpoint with
`response_format: json_schema` and `strict: true`, so replies are constrained to
the Pydantic contract rather than merely hoped to be well formed.

Groq's strict mode is stricter than Pydantic's output. `normalize_json_schema()`
bridges the gap before the request is sent: it inlines every `$ref` against
`$defs`, adds `additionalProperties: false` to every object, and lists every
property in `required` while preserving optionality through the nullable unions
Pydantic already generates. Without that step the API rejects the request
outright.

A reply cut short by the token budget is retried once at double the budget.
Everything else — auth, quota, timeout, malformed output — is mapped to a typed
error and a client-safe message.

## Project layout

```
legalease/
├── backend/
│   ├── app/
│   │   ├── ai/          # client, prompts, generator, demo mode
│   │   ├── routes/      # documents, branding, health, templates
│   │   ├── schemas/     # request/response contracts
│   │   ├── services/    # persistence, versioning, exports
│   │   ├── templates/   # 18 document types, disclaimer
│   │   └── utils/       # typed errors, security helpers
│   ├── tests/           # 131 tests
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/  # ui, layout, wizard, editor, documents
    │   ├── hooks/       # React Query, autosave, debounce
    │   ├── pages/       # landing, dashboard, templates, wizard, editor
    │   ├── services/    # typed API client
    │   ├── store/       # wizard state
    │   └── types/       # API contracts mirroring the backend
    └── package.json
```

## Notes

- **No authentication.** This is a local, single-user application. Adding auth
  before exposing it on a network is a prerequisite, not an enhancement.
- **The API key lives in `backend/.env`,** which `.gitignore` excludes. Only
  `.env.example` is tracked, and it contains no secret.
- **SQLite is a development default.** Point `DATABASE_URL` at PostgreSQL for
  anything beyond a single local install.
