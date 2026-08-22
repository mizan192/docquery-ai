---
name: docquery-ai
description: DocSense AI project — FastAPI + pgvector RAG document search. Use when answering questions about the codebase.
---

# DocSense AI (docquery-ai)

## Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (async) |
| ORM | SQLAlchemy (async) |
| DB | PostgreSQL + pgvector |
| Embeddings | sentence-transformers (local, no external API) |
| Task queue | Celery + Redis |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Migrations | Alembic |

## Project structure

```
docquery-ai/
├── app/
│   ├── main.py            # FastAPI entry, lifespan, router registration
│   ├── config.py          # Pydantic Settings (env vars)
│   ├── database.py        # AsyncSession, engine, init_db
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic request/response schemas
│   ├── routers/           # FastAPI route handlers
│   │   ├── auth.py        # Login, register
│   │   ├── documents.py   # CRUD documents
│   │   ├── search.py      # Vector search
│   │   ├── chat.py        # Conversational Q&A
│   │   └── health.py      # /health
│   ├── services/          # Business logic
│   │   ├── embedding.py   # Vector embeddings via sentence-transformers
│   │   ├── chunking.py    # Document chunking
│   │   ├── rag.py         # Retrieval-Augmented Generation pipeline
│   │   ├── llm.py         # LLM interface (local / external fallback)
│   │   ├── extraction.py  # PDF text extraction
│   │   └── prompts.py     # Prompt templates
│   ├── core/
│   │   ├── security.py    # JWT encode/decode, password hashing
│   │   ├── exceptions.py  # Custom HTTP exceptions
│   │   ├── logging.py     # Logger setup
│   │   └── celery_app.py  # Celery app config
│   └── worker/
│       └── tasks.py       # Async background tasks (Celery)
├── alembic/               # DB migrations
├── docker/                # Docker configs
├── docker-compose.yml
├── requirements.txt
└── run.py
```

## Key conventions

- **Async everything** — DB sessions use `AsyncSession`, routes are `async def`.
- **pgvector** — embeddings stored in vector columns, queried via cosine distance.
- **Local-first AI** — sentence-transformers for embeddings (no OpenAI key needed by default). LLM can be swapped later.
- **Celery** — long-running jobs (embedding large docs) delegated to worker.
- **Auth** — JWT bearer token on all endpoints except `/auth/login` and `/auth/register`.

## Running locally

```bash
uvicorn app.main:app --reload
# worker:
celery -A app.worker.tasks worker --loglevel=info
```

## API docs

Swagger UI: `/docs` (with bearer token support)
