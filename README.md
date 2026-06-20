# DocQuery AI

> AI-powered document search and analysis system supporting legal, medical, financial and educational documents with source citations, confidence scoring and real-time processing.

---

## Live Demo
- **GitHub**: [github.com/mizan192/docquery-ai](https://github.com/mizan192/docquery-ai)
---

## What It Does

Users can upload PDF or TXT documents and ask natural language questions. The system finds the most relevant sections using vector similarity search and generates AI-powered answers with source citations showing exactly which part of the document was used.

**Example:**
- Upload a legal contract → Ask "What are the termination conditions?" → Get answer with exact clause reference
- Upload a medical report → Ask "What does my blood test show?" → Get simplified explanation with normal ranges
- Upload a financial report → Ask "What was the revenue in 2025?" → Get answer with specific figures

---

## Key Features

- **RAG Pipeline** — Retrieval Augmented Generation for accurate document-based answers
- **Smart Document Categories** — Legal, Medical, Financial, Educational with domain-specific AI prompts
- **Source Citation** — Every answer shows which document and chunk was used
- **Confidence Score** — Shows how confident the AI is in each answer
- **Background Processing** — Document chunking and embedding runs in background via Celery
- **Real-time Progress** — Track document processing progress (0% to 100%)
- **JWT Authentication** — Secure user registration and login
- **Chat History** — All conversations saved and searchable
- **Table Extraction** — pdfplumber extracts both text and table data from PDFs
- **Multi-user Support** — Each user only sees their own documents

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI (Python) |
| **Database** | PostgreSQL |
| **Vector Search** | pgvector (cosine similarity) |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **LLM** | Google flan-t5-base (local, free) |
| **Background Tasks** | Celery + Redis |
| **PDF Extraction** | pdfplumber |
| **Authentication** | JWT (python-jose + passlib) |
| **ORM** | SQLAlchemy (async) |
| **Migrations** | Alembic |
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
     |                                          |
     |                                    Text chunking (500 chars)
     |                                          |
     |                                    sentence-transformers embedding
     |                                          |
     |                                    pgvector storage
     |
     |--- Ask Question ---> Generate question embedding
                                  |
                            pgvector cosine similarity search
                                  |
                            Top K relevant chunks retrieved
                                  |
                            flan-t5 LLM generates answer
                                  |
                            Source citation + confidence score
                                  |
                            Response with answer + sources
```

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
| POST | `/api/v1/chat` | Ask question and save to chat history |
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

### 3. Ask Question
```bash
curl -X POST http://localhost:8010/api/v1/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the termination conditions?", "top_k": 3}'
```

### 4. Example Response
```json
{
  "id": 1,
  "question": "What are the termination conditions?",
  "answer": "The contract can be terminated with 30 days written notice by either party.",
  "overall_accuracy": 87,
  "sources": [
    {
      "document_filename": "contract.pdf",
      "chunk_index": 12,
      "chunk_text": "Either party may terminate this agreement...",
      "confidence_score": 0.87,
      "confidence_percent": 87
    }
  ],
  "created_at": "2026-06-15T00:00:00Z"
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
source venv/bin/activate  # Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# install pgvector
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
CREATE USER raguser WITH PASSWORD 'yourpass';
CREATE DATABASE ragdb OWNER user;
GRANT ALL PRIVILEGES ON DATABASE yourdb TO user;
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

```bash
# build and start all services
docker-compose up --build -d

# run migrations
docker-compose run migrate

# check status
docker-compose ps
```

Services started:
- **FastAPI** → http://localhost:8010
- **PostgreSQL** → localhost:5433
- **Redis** → localhost:6380

---

## Known Limitations

- Scanned PDFs (image-based) are not supported — requires OCR (planned enhancement)
- Local LLM (flan-t5-base) gives basic answers — can be upgraded to OpenAI/Anthropic for better quality
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
│   │   ├── embedding.py       # Vector embedding generation
│   │   ├── extraction.py      # PDF/TXT text extraction
│   │   ├── llm.py             # LLM answer generation
│   │   ├── prompts.py         # Category-specific prompt templates
│   │   └── rag.py             # Shared RAG pipeline
│   └── worker/
│       └── tasks.py           # Celery background tasks
├── alembic/                   # Database migrations
├── docker/                    # Docker configuration
├── docker-compose.yml
├── requirements.txt
└── run.py
```

---

## What I Learned Building This

- Designing and implementing a production-ready RAG pipeline from scratch
- Vector similarity search using pgvector and cosine distance
- Background task processing with Celery and Redis for scalable document processing
- Domain-specific prompt engineering for different document categories
- JWT authentication and multi-user data isolation
- Database migration management with Alembic
- Docker containerization of multi-service applications

---

## Author

**Mijanur Rahman**
- Python Backend Developer | AI Integration | Odoo Developer
- [LinkedIn](https://linkedin.com/in/your-profile)
- [GitHub](https://github.com/mizan192)
- Email: miz1998an@gmail.com
