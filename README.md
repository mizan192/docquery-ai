# DocQuery AI

> AI-powered document search and analysis system supporting legal, medical, financial and educational documents with source citations, confidence scoring, conversational memory and real-time processing.

---

## Live Demo

- **GitHub**: [github.com/mizan192/docquery-ai](https://github.com/mizan192/docquery-ai)
- **Docker Hub**: [hub.docker.com/r/mizan19/docquery-ai](https://hub.docker.com/repository/docker/mizan19/docquery-ai/general)

---

## What It Does

Users can upload PDF or TXT documents and ask natural language questions. The system finds the most relevant sections using vector similarity search and generates AI-powered answers with source citations showing exactly which part of the document was used. Follow-up questions are supported via LangChain conversational memory.

**Example:**
- Upload a legal contract → Ask "What are the termination conditions?" → Get answer with exact clause reference
- Upload a medical report → Ask "What does my blood test show?" → Get simplified explanation with normal ranges
- Upload a financial report → Ask "What was the revenue in 2025?" → Get answer with specific figures
- Ask follow-up → "Can you explain that in more detail?" → System remembers previous context!

---

## Key Features

- **RAG Pipeline** — Retrieval Augmented Generation built from scratch without LangChain abstraction
- **LangChain Conversational Memory** — Follow-up questions work using DB-backed memory (persists across restarts)
- **Smart Document Categories** — Legal, Medical, Financial, Educational with domain-specific AI prompts
- **Source Citation** — Every answer shows which document and chunk was used
- **Confidence Score** — Shows how confident the AI is in each answer
- **Background Processing** — Document chunking and embedding runs in background via Celery
- **Real-time Progress** — Track document processing progress (0% to 100%)
- **JWT Authentication** — Secure user registration and login
- **Chat History** — All conversations saved and searchable
- **Table Extraction** — pdfplumber extracts both text and table data from PDFs
- **Multi-user Support** — Each user only sees their own documents
- **Unit Tested** — 36 unit tests covering chunking, extraction and API endpoints
- **Dockerized** — Full Docker setup with docker-compose for one-command deployment

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI (Python) |
| **Database** | PostgreSQL |
| **Vector Search** | pgvector (cosine similarity) |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **LLM** | Google flan-t5-base (local, free, no API key needed) |
| **Conversational Memory** | LangChain (ConversationBufferWindowMemory) |
| **Background Tasks** | Celery + Redis |
| **PDF Extraction** | pdfplumber (text + tables) |
| **Authentication** | JWT (python-jose + passlib) |
| **ORM** | SQLAlchemy (async) |
| **Migrations** | Alembic |
| **Testing** | pytest (36 tests) |
| **Containerization** | Docker + Docker Compose |

---

## System Architecture

```
User Request
     |
FastAPI (Port 8010)
     |
JWT Auth Check
     |
     |--- Upload PDF ---> Save to DB ---> Celery Task Queue (Redis)
     |                                          |
     |                                    Background Worker
     |                                          |
     |                                    pdfplumber extraction
     |                                    (text + tables)
     |                                          |
     |                                    Text chunking (500 chars)
     |                                          |
     |                                    sentence-transformers embedding
     |                                          |
     |                                    pgvector storage
     |
     |--- Ask Question ---> LangChain Memory (last 3 Q&A from DB)
                                  |
                            Generate question embedding
                                  |
                            pgvector cosine similarity search
                                  |
                            Top K relevant chunks retrieved
                                  |
                            flan-t5 LLM generates answer
                            (with conversation context)
                                  |
                            Source citation + confidence score
                                  |
                            Save to ChatHistory (becomes memory!)
                                  |
                            Response with answer + sources + used_memory
```

---

## LangChain Conversational Memory

The system uses a DB-backed conversation memory approach — production-ready and works across server restarts and multiple workers.

```
Q1: "what is the refund policy?"
-> DB empty, used_memory = false
-> answer saved to ChatHistory

Q2: "what if I paid by card?"
-> fetches Q1 from ChatHistory DB
-> feeds into LangChain ConversationBufferWindowMemory
-> formats as "Human: ... AI: ..."
-> adds to LLM prompt as context
-> used_memory = true
-> LLM gives connected answer!

Q3: "what about digital products?"
-> fetches Q1, Q2 from DB (k=3 window)
-> LLM sees full conversation context
-> used_memory = true
```

Why DB-backed instead of in-memory:
- Persists after server restart
- Works with multiple Celery workers
- Reuses existing ChatHistory table (no extra storage)

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get JWT token |

### Documents
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/documents/upload` | Upload PDF or TXT document |
| GET | `/api/v1/documents/{id}/status` | Check processing progress |

### Search & Chat
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/search` | Search documents without saving history |
| POST | `/api/v1/chat` | Ask question with conversational memory |
| GET | `/api/v1/chat/history` | Get all chat history |
| GET | `/api/v1/chat/history/{document_id}` | Get chat history for specific document |

### Health
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Check server and database status |

---

## Example API Usage

### 1. Register and Login
```bash
# register
curl -X POST http://localhost:8010/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "user", "password": "password123"}'

# login
curl -X POST http://localhost:8010/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 2. Upload Document
```bash
curl -X POST http://localhost:8010/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@contract.pdf" \
  -F "category=legal"
```

### 3. Ask Question with Memory
```bash
# first question
curl -X POST http://localhost:8010/api/v1/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the termination conditions?", "document_id": 1, "top_k": 3}'

# follow-up question (memory active!)
curl -X POST http://localhost:8010/api/v1/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the notice period?", "document_id": 1, "top_k": 3}'
```

### 4. Example Response
```json
{
  "id": 2,
  "question": "What is the notice period?",
  "answer": "Based on the termination conditions mentioned earlier, the notice period is 30 days written notice.",
  "overall_accuracy": 87,
  "used_memory": true,
  "sources": [
    {
      "document_filename": "contract.pdf",
      "chunk_index": 12,
      "chunk_text": "Either party may terminate this agreement with 30 days written notice...",
      "confidence_score": 0.87,
      "confidence_percent": 87
    }
  ],
  "created_at": "2026-07-29T00:00:00Z"
}
```

---

## Document Categories

| Category | Best For | Special Behavior |
|---|---|---|
| `general` | Any document | Simple clear answers |
| `legal` | Contracts, agreements | References clauses and sections |
| `medical` | Health reports, prescriptions | Explains terms simply, adds doctor disclaimer |
| `financial` | Annual reports, statements | Highlights figures and financial context |
| `educational` | Textbooks, course material | Step by step explanations with examples |

---

## Unit Tests

The project includes 36 unit tests covering core services and API endpoints.

```bash
# run all tests
pytest -v

# run specific test file
pytest tests/test_chunking.py -v
pytest tests/test_extraction.py -v
pytest tests/test_api.py -v
```

Test coverage:
```
tests/test_chunking.py    7 tests  -> chunk size, overlap, empty text, edge cases
tests/test_extraction.py  21 tests -> txt extraction, table conversion, file types
tests/test_api.py         8 tests  -> auth endpoints, protected routes
```

---

## Local Development Setup

### Requirements
- Python 3.10+
- PostgreSQL 14+ with pgvector extension
- Redis

### Installation

```bash
# clone repository
git clone https://github.com/mizan192/docquery-ai.git
cd docquery-ai

# create virtual environment
python -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# install pgvector system package
sudo apt install postgresql-14-pgvector
```

### Environment Setup

```bash
# create .env file
cp .env.example .env

# update .env with your values
DATABASE_URL=postgresql+asyncpg://raguser:ragpass@localhost:5432/ragdb
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

### Database Setup

```bash
# create database and user in PostgreSQL
sudo -u postgres psql
CREATE USER raguser WITH PASSWORD 'ragpass';
CREATE DATABASE ragdb OWNER raguser;
GRANT ALL PRIVILEGES ON DATABASE ragdb TO raguser;
\q

# run migrations
alembic upgrade head
```

### Run

```bash
# terminal 1 - start celery worker
celery -A app.worker.tasks.celery_app worker --loglevel=info

# terminal 2 - start FastAPI
python run.py
```

Open: http://localhost:8010/docs

---

## Docker Setup

### Option 1 — Pull from Docker Hub (Fastest)

```bash
# pull image directly
docker pull mizan19/docquery-ai:latest
```

Docker Hub: [hub.docker.com/r/mizan19/docquery-ai](https://hub.docker.com/repository/docker/mizan19/docquery-ai/general)

### Option 2 — Build Locally

```bash
# build and start all services
docker-compose up --build -d

# run migrations (first time only)
docker-compose run migrate

# check all containers running
docker-compose ps
```

### Docker Services

| Service | Port | Description |
|---|---|---|
| FastAPI | 8010 | Main API server |
| PostgreSQL | 5433 | Database |
| Redis | 6380 | Message broker for Celery |
| Celery | - | Background task worker |

### Useful Docker Commands

```bash
# view logs
docker-compose logs fastapi
docker-compose logs celery

# stop all services
docker-compose down

# fresh start (removes all data)
docker-compose down -v
docker-compose up --build -d
```

---

## Known Limitations

- Scanned PDFs (image-based) not supported — requires OCR (planned enhancement)
- Local LLM (flan-t5-base) gives basic answers — can be upgraded to OpenAI/Anthropic
- Conversation memory limited to last 3 Q&A pairs to fit flan-t5 token limit
- Multi-language support planned for future release

---

## Project Structure

```
docquery-ai/
├── app/
│   ├── core/
│   │   ├── celery_app.py      # Celery configuration
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── logging.py         # Structured logging
│   │   └── security.py        # JWT authentication
│   ├── models/                # SQLAlchemy DB models
│   ├── routers/               # FastAPI route handlers
│   ├── schemas/               # Pydantic request/response schemas
│   ├── services/
│   │   ├── chunking.py        # Text chunking logic
│   │   ├── conversation.py    # LangChain DB-backed memory
│   │   ├── embedding.py       # Vector embedding generation
│   │   ├── extraction.py      # PDF/TXT text + table extraction
│   │   ├── llm.py             # LLM answer generation
│   │   ├── prompts.py         # Category-specific prompt templates
│   │   └── rag.py             # Shared RAG pipeline
│   └── worker/
│       └── tasks.py           # Celery background tasks
├── tests/
│   ├── test_api.py            # API endpoint tests
│   ├── test_chunking.py       # Chunking service tests
│   └── test_extraction.py     # Extraction service tests
├── alembic/                   # Database migrations
├── docker/
│   ├── Dockerfile             # FastAPI container
│   └── Dockerfile.celery      # Celery container
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── run.py
```

---

## What I Learned Building This

- Designing and implementing a production-ready RAG pipeline from scratch without frameworks
- Vector similarity search using pgvector and cosine distance scoring
- Background task processing with Celery and Redis for scalable document embedding
- DB-backed conversational memory with LangChain for production-grade follow-up questions
- Domain-specific prompt engineering for legal, medical and financial documents
- PDF table extraction with pdfplumber for structured data in financial reports
- JWT authentication and multi-user data isolation
- Database migration management with Alembic
- Docker containerization of multi-service AI applications
- Unit testing with pytest for core business logic

---

## Author

**Mijanur Rahman**
- Python Backend Developer | AI Integration | Odoo Developer
- [LinkedIn](https://linkedin.com/in/your-profile)
- [GitHub](https://github.com/mizan192)
- [Docker Hub](https://hub.docker.com/r/mizan19)
- Email: miz1998an@gmail.com
