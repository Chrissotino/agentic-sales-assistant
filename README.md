# Agentic Sales Assistant (MVP)

A production-style backend MVP that transforms spoken or typed post-meeting sales updates into structured CRM actions for HubSpot.

> **Audience:** portfolio reviewers, hiring managers, architects, and client demo stakeholders.

---

## 1) What this project solves

Sales teams lose momentum after customer meetings because notes are unstructured and CRM updates are delayed.
This project reduces that gap by converting natural language updates into actionable CRM operations:

- Extracts intent + entities from text or voice updates.
- Creates structured meeting notes and follow-up tasks.
- Optionally prepares deal-related actions.
- Persists full processing history locally for traceability.

---

## 2) Product overview

Input example (rep voice/text):

> "Just finished a meeting with Müller AG. They are interested in an implementation for around 25 users. They want an offer by next Friday. Please send product information and create a follow-up task for next week."

System behavior:

1. **Ingest** text or audio.
2. **Transcribe** audio via OpenAI (or deterministic local fallback if not configured).
3. **Extract** structured action plan using a typed Pydantic schema.
4. **Execute** actions through HubSpot client wrapper.
5. **Persist** raw input, transcript, extracted payload, and execution result.

---

## 3) Why Python + FastAPI

- **Fast implementation velocity** with strong maintainability.
- **Type-safe contracts** using Pydantic request/response models.
- **Clean API experience** for internal tools and integration demos.
- **Reliable testability** for service and API layers.

---

## 4) Design decisions

- **Modular architecture**: routes, services, clients, repositories are separated.
- **MVP pragmatism**: simulation-safe mode for secrets-free local runs.
- **Typed extraction output**: no free-form downstream parsing.
- **Persistence-first audit trail**: interaction lifecycle saved in SQLite.
- **CRM abstraction**: HubSpot implemented now, connector pattern ready for expansion.

---

## 5) Architecture overview

```text
┌──────────────────────────┐
│ Sales Rep Update         │
│ - Text                   │
│ - Voice                  │
└─────────────┬────────────┘
              │
              v
┌──────────────────────────┐
│ FastAPI API Layer        │
│ /intake/* /actions/*     │
└─────────────┬────────────┘
              │
              v
┌───────────────────────────────────────────────────┐
│ Service Layer                                      │
│ - IntakeService                                    │
│ - ExtractionService                                │
│ - ActionExecutionService                           │
└───────┬───────────────────────────────┬───────────┘
        │                               │
        v                               v
┌──────────────────────┐      ┌──────────────────────┐
│ OpenAI Client        │      │ HubSpot Client       │
│ - Transcription      │      │ - Contact/Company    │
│ - Structured extract │      │ - Deal/Note/Task     │
└──────────┬───────────┘      └──────────┬───────────┘
           │                              │
           └──────────────┬───────────────┘
                          v
                 ┌──────────────────────┐
                 │ SQLite + SQLAlchemy  │
                 │ interactions table   │
                 └──────────────────────┘
```

---

## 6) Request flow

```text
POST /api/v1/intake/text OR /api/v1/intake/voice
  -> Extraction pipeline (typed schema)
  -> Optional interaction persistence
  -> Returns structured action plan

POST /api/v1/actions/execute
  -> Executes note/task/deal actions via HubSpot wrapper
  -> Persists execution result (if interaction_id provided)
  -> Returns operation summary
```

---

## 7) Repository structure

```text
agentic-sales-assistant/
├── app/
│   ├── api/            # FastAPI routes
│   ├── clients/        # OpenAI + HubSpot wrappers
│   ├── core/           # settings + logging
│   ├── db/             # SQLAlchemy base/session
│   ├── models/         # ORM models
│   ├── prompts/        # extraction prompt templates
│   ├── repositories/   # DB access layer
│   ├── schemas/        # Pydantic contracts
│   ├── services/       # orchestration/business logic
│   └── main.py         # FastAPI app entrypoint
├── alembic/            # DB migrations
├── scripts/            # sample payloads
├── tests/              # pytest suite
├── .env.example
├── requirements.txt
└── README.md
```

---

## 8) API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Service health status |
| POST | `/api/v1/intake/text` | Intake text and extract actions |
| POST | `/api/v1/intake/voice` | Upload audio, transcribe, extract actions |
| POST | `/api/v1/actions/execute` | Execute structured actions in HubSpot |
| GET | `/api/v1/interactions` | List persisted interactions |

---

## 9) Quickstart (developer setup)

### Prerequisites

- Python 3.12+
- pip

### Install

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Run migrations

```bash
alembic upgrade head
```

### Start the API

```bash
uvicorn app.main:app --reload
```

### Run tests

```bash
pytest -q
```

---

## 10) Environment configuration

| Variable | Description | Default |
|---|---|---|
| `APP_NAME` | Service name | `agentic-sales-assistant` |
| `APP_ENV` | Environment label | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `API_V1_PREFIX` | API prefix | `/api/v1` |
| `OPENAI_API_KEY` | OpenAI API key | empty |
| `OPENAI_MODEL` | Extraction model | `gpt-4.1-mini` |
| `HUBSPOT_ACCESS_TOKEN` | HubSpot private app token | empty |
| `HUBSPOT_BASE_URL` | HubSpot API base | `https://api.hubapi.com` |
| `DB_URL` | SQLAlchemy DB URL | `sqlite:///./sales_assistant.db` |
| `ENABLE_CRM_SIMULATION` | Force mock-safe CRM behavior | `true` |

---

## 11) Example API requests and responses

### Intake text

```bash
curl -X POST 'http://localhost:8000/api/v1/intake/text' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Met Müller AG. Interested in implementation for 25 users. Need offer by next Friday and product info.",
    "persist": true
  }'
```

Example response (shape):

```json
{
  "interaction_id": 12,
  "extracted": {
    "account_name": "Müller AG",
    "contact_name": null,
    "meeting_type": null,
    "meeting_summary": "Customer interested in implementation for about 25 users and asked for an offer.",
    "customer_interest": "implementation",
    "products_requested": ["product information"],
    "requested_follow_up_date": null,
    "create_task": true,
    "create_note": true,
    "create_or_update_deal": true,
    "prepare_quote_request": true,
    "prepare_email_draft": false,
    "send_product_information": true,
    "urgency": "high",
    "next_steps": ["Prepare quote", "Create follow-up task"],
    "confidence_score": 0.82
  }
}
```

### Intake voice

```bash
curl -X POST 'http://localhost:8000/api/v1/intake/voice?persist=true' \
  -F 'file=@./sample_note.m4a'
```

### Execute actions

```bash
curl -X POST 'http://localhost:8000/api/v1/actions/execute' \
  -H 'Content-Type: application/json' \
  -d @scripts/demo_payload.json
```

---

## 12) HubSpot integration notes

- The wrapper includes practical methods for:
  - search/create contact
  - search/create company
  - create note
  - create task
  - search/create/update deal
- In local mode (no token or simulation enabled), the same methods return deterministic simulated outputs.
- This keeps development and demos stable without external dependencies.

---

## 13) AI extraction design

The extraction prompt enforces:

- extract only evidence-backed facts
- avoid hallucinated customer details
- return `null` for ambiguity
- keep summaries concise and commercially useful
- infer actions only when strongly justified

Schema contracts live in `app/schemas/extraction.py`.

---

## 14) Security and operational notes

- Store secrets only in `.env` (never commit credentials).
- Add authn/authz and rate-limiting before production exposure.
- Add PII redaction and audit logging hardening for enterprise rollout.

---

## 15) MVP limitations

- Single-user/internal API assumptions.
- Limited HubSpot object associations (can be expanded).
- No async job queue yet for long-running workflows.

---

## 16) Future CRM connectors

Planned connectors behind a common interface:

- Salesforce
- Pipedrive
- Zoho CRM

---

## 17) Roadmap

### Near-term (v1.1)
- Better extraction evaluation set + prompt versioning.
- Deal stage mapping and richer task metadata.
- Improved error semantics and retry handling.

### Mid-term (v1.2)
- CRM association graph (contact ↔ company ↔ deal ↔ engagements).
- Human review queue for high-impact actions.
- Background workers for async execution.

### Long-term (v2)
- Multi-tenant auth model.
- Multi-CRM runtime connector selection.
- Analytics dashboard for sales operations KPIs.

---

## 18) Portfolio/interview demo talking points

- Clean API/service/client separation.
- Typed LLM extraction contracts and confidence scoring.
- Safe fallback patterns for incomplete integration environments.
- Extensible CRM connector strategy without overengineering.
