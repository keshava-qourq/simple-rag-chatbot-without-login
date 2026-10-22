# Data Model

<!-- sdlc:auto:start entities -->
### documents

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | UUID | True | — | False |
| browser_uuid | UUID | False | — | False |
| filename | VARCHAR(255) | False | — | False |
| file_type | VARCHAR(10) | False | — | False |
| minio_object_key | VARCHAR(512) | False | — | False |
| status | VARCHAR(20) | False | — | False |
| created_at | TIMESTAMPTZ | False | — | False |
| last_active_at | TIMESTAMPTZ | False | — | False |

### document_chunks

| Field | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | UUID | True | — | False |
| document_id | UUID | False | documents.id | False |
| chunk_index | INTEGER | False | — | False |
| content | TEXT | False | — | False |
| embedding | VECTOR(768) | False | — | False |
| created_at | TIMESTAMPTZ | False | — | False |
<!-- sdlc:auto:end entities -->

<!-- sdlc:auto:start relationships -->
| Source | Target | Type |
|---|---|---|
| documents | document_chunks | one-to-many |
<!-- sdlc:auto:end relationships -->

<!-- sdlc:auto:start er-diagram -->
```mermaid
erDiagram
  documents {
    UUID id PK
    UUID browser_uuid
    VARCHAR_255_ filename
    VARCHAR_10_ file_type
    VARCHAR_512_ minio_object_key
    VARCHAR_20_ status
    TIMESTAMPTZ created_at
    TIMESTAMPTZ last_active_at
  }
  document_chunks {
    UUID id PK
    UUID document_id FK
    INTEGER chunk_index
    TEXT content
    VECTOR_768_ embedding
    TIMESTAMPTZ created_at
  }
  documents ||--o{ document_chunks : "one-to-many"
```
<!-- sdlc:auto:end er-diagram -->
