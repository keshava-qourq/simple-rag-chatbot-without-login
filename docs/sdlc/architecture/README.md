# Architecture

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
## Overview

_No entries for this phase yet._
<!-- sdlc:auto:end narrative -->

<!-- sdlc:auto:start building-blocks -->
## Building Block View

| ID | Name | Technology | Responsibility | Depends on |
|---|---|---|---|---|
| fe | Web Frontend | React 19 | Renders the chat interface and file-upload widget, generates and persists a browser UUID in localStorage, stores and restores conversation history in localStorage, and communicates with the backend REST API for document upload and chat queries. | api |
| api | Backend API and RAG Pipeline | FastAPI 0.115 | Exposes REST endpoints for document upload and chat, parses and chunks uploaded documents, generates embeddings and answers via Google Gemini, stores and retrieves files via MinIO, performs pgvector similarity search, and runs a scheduled cleanup task for inactive data. | db, storage, ai |
| db | Database | PostgreSQL 16 | Stores document metadata (filename, file type, browser UUID, status, timestamps) and document chunk embeddings using the pgvector extension for vector similarity search. | — |
| storage | File Storage | MinIO | Persists original uploaded PDF, TXT, and DOCX files in an S3-compatible object store so returning users can chat against previously uploaded documents without re-uploading. | — |
| ai | AI Provider | Google Gemini | Provides gemini-embedding-001 for document chunk and query embeddings, and gemini-2.5-flash for answer generation grounded in retrieved document content. Access is via server-side API key only. | — |

```mermaid
graph TD
  c_fe["Web Frontend"]
  c_api["Backend API and RAG Pipeline"]
  c_db["Database"]
  c_storage["File Storage"]
  c_ai["AI Provider"]
  c_fe --> c_api
  c_api --> c_db
  c_api --> c_storage
  c_api --> c_ai
```
<!-- sdlc:auto:end building-blocks -->

<!-- sdlc:auto:start runtime -->
## Runtime View

### Document Upload and Processing

A user selects a PDF, TXT, or DOCX file in the web interface and submits it. The backend stores the file in MinIO, parses the text, chunks it with overlap, generates embeddings via gemini-embedding-001, persists embeddings in PostgreSQL with pgvector, and returns document metadata to the frontend.

- **Components:** fe, api, storage, ai, db
- **Modules:** routers.documents, services.file_storage, services.document_parser, services.chunker, services.embedding, models.document
- **Key functions:** upload_document(file, browser_uuid), store_file(file, browser_uuid), parse_pdf(path), parse_docx(path), parse_txt(path), chunk_text(text, chunk_size, overlap), generate_embeddings(chunks), save_chunks(document_id, chunks, embeddings)

```mermaid
sequenceDiagram
  participant FE as Web Frontend
  participant API as FastAPI Backend
  participant MINIO as MinIO
  participant GEM as Google Gemini
  participant DB as PostgreSQL
  FE->>API: POST /api/documents/upload (file, browser_uuid)
  API->>API: Validate file type (PDF/TXT/DOCX)
  API->>MINIO: Store original file
  MINIO-->>API: object key
  API->>API: Parse document to extract text
  API->>API: Chunk text with overlap
  API->>GEM: Generate embeddings (gemini-embedding-001)
  GEM-->>API: embedding vectors
  API->>DB: Insert document record and chunk embeddings
  DB-->>API: success
  API-->>FE: 201 Created (document metadata, status=ready)
```

### Chat Query with RAG

A user types a question in the chat interface. The frontend sends the question and browser UUID to the backend. The backend embeds the question, performs pgvector similarity search to retrieve relevant chunks, sends the chunks and question to Gemini 2.5 Flash for answer generation, and returns the answer. The frontend stores the Q&A pair in localStorage.

- **Components:** fe, api, ai, db
- **Modules:** routers.chat, services.embedding, services.retrieval, services.generation, models.document
- **Key functions:** chat(question, browser_uuid), check_documents_exist(browser_uuid), generate_query_embedding(question), similarity_search(query_embedding, browser_uuid, top_k), generate_answer(question, retrieved_chunks)

```mermaid
sequenceDiagram
  participant FE as Web Frontend
  participant API as FastAPI Backend
  participant DB as PostgreSQL
  participant GEM as Google Gemini
  FE->>API: POST /api/chat (question, browser_uuid)
  API->>DB: Check documents exist for browser_uuid
  alt No documents found
    API-->>FE: 200 (message: no documents available)
  else Documents exist
    API->>GEM: Embed question (gemini-embedding-001)
    GEM-->>API: query embedding
    API->>DB: pgvector similarity search (top-k chunks)
    DB-->>API: matched chunks
    alt No chunks above threshold
      API-->>FE: 200 (message: no relevant information found)
    else Chunks found
      API->>GEM: Generate answer (gemini-2.5-flash, question + chunks)
      GEM-->>API: generated answer
      API-->>FE: 200 (answer text)
    end
  end
  FE->>FE: Store Q&A pair in localStorage
```

### Inactive Data Cleanup

A scheduled task runs periodically inside the FastAPI process. It queries the database for browser UUIDs whose last activity is older than approximately 30 days, deletes their document chunk embeddings and document records from PostgreSQL, and removes the corresponding original files from MinIO.

- **Components:** api, db, storage
- **Modules:** services.cleanup, models.document, services.file_storage
- **Key functions:** run_cleanup_task(), find_inactive_uuids(threshold_days=30), delete_documents_by_uuid(browser_uuid), delete_files_from_minio(object_keys)

```mermaid
sequenceDiagram
  participant SCHED as APScheduler
  participant API as FastAPI Backend
  participant DB as PostgreSQL
  participant MINIO as MinIO
  SCHED->>API: Trigger cleanup job
  API->>DB: Find browser_uuids inactive > 30 days
  DB-->>API: list of inactive uuids with object keys
  API->>DB: Delete document_chunks and documents for inactive uuids
  DB-->>API: deleted rows
  API->>MINIO: Delete original files for inactive uuids
  MINIO-->>API: deletion confirmed
```
<!-- sdlc:auto:end runtime -->

<!-- sdlc:auto:start deployment-view -->
## Deployment View

| Name | Service | Runtime | Scaling | Environment |
|---|---|---|---|---|
| User Browser | React 19 SPA served as static files | Browser | N/A (client-side) | prod |
| EC2 Application Host | Docker Compose on AWS EC2 (t3.small) | Docker | Single instance | prod |
| FastAPI Container | FastAPI 0.115 application server | Docker (uvicorn) | Single container | prod |
| PostgreSQL Container | PostgreSQL 16 with pgvector extension | Docker | Single container | prod |
| MinIO Container | MinIO S3-compatible object storage (bitnamilegacy/minio:2024.10.13) | Docker | Single container | prod |
| Google Gemini API | External SaaS AI provider | SaaS | Managed by Google | prod |

| Source | Target | Protocol |
|---|---|---|
| User Browser | FastAPI Container | HTTPS |
| FastAPI Container | PostgreSQL Container | TCP (internal Docker network) |
| FastAPI Container | MinIO Container | HTTP (internal Docker network) |
| FastAPI Container | Google Gemini API | HTTPS |

```mermaid
graph LR
  n_User_Browser["User Browser<br/>React 19 SPA served as static files"]
  n_EC2_Application_Host["EC2 Application Host<br/>Docker Compose on AWS EC2 (t3.small)"]
  n_FastAPI_Container["FastAPI Container<br/>FastAPI 0.115 application server"]
  n_PostgreSQL_Container["PostgreSQL Container<br/>PostgreSQL 16 with pgvector extension"]
  n_MinIO_Container["MinIO Container<br/>MinIO S3-compatible object storage (bitnamilegacy/minio:2024.10.13)"]
  n_Google_Gemini_API["Google Gemini API<br/>External SaaS AI provider"]
  n_User_Browser -->|"HTTPS"| n_FastAPI_Container
  n_FastAPI_Container -->|"TCP (internal Docker network)"| n_PostgreSQL_Container
  n_FastAPI_Container -->|"HTTP (internal Docker network)"| n_MinIO_Container
  n_FastAPI_Container -->|"HTTPS"| n_Google_Gemini_API
```
<!-- sdlc:auto:end deployment-view -->

<!-- sdlc:auto:start decisions -->
## Architecture Decisions

| Layer | Choice | ADR |
|---|---|---|
| Frontend | React 19 | [ADR-0001](adr/frontend.md) |
| Backend | FastAPI 0.115 | [ADR-0002](adr/backend.md) |
| Database | PostgreSQL 16 | [ADR-0003](adr/database.md) |
| Cloud | AWS | [ADR-0004](adr/cloud.md) |
<!-- sdlc:auto:end decisions -->

<!-- sdlc:auto:start links -->
## Related Documents

- [Data Model](data-model.md)
- [API Specification](api/openapi.yaml)
- [Architecture Decision Records](adr/README.md)
<!-- sdlc:auto:end links -->
