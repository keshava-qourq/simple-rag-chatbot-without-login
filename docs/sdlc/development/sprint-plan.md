# Sprint Plan

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start sprints -->
## Sprint 1: Sprint 1

Establish anonymous identity and the document upload foundation (browser UUID, upload UI/endpoint, initial file storage).

Capacity: 20 points · Committed: 16

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-001 | Story | Generate and persist a browser UUID for anonymous identification | 2 | frontend-agent | — |
| US-002 | Story | Handle browser identifier scope across devices | 1 | qa-agent | US-001 |
| US-003 | Story | Upload supported document formats through the web interface | 8 | backend-agent | — |
| ↳ US-003-T1 | Task | Build file upload widget with client-side format validation | — | frontend-agent | — |
| ↳ US-003-T2 | Task | Implement POST /api/documents endpoint with format validation | — | backend-agent | — |
| ↳ US-003-T3 | Task | Store uploaded file in MinIO associated with browser UUID | — | backend-agent | — |
| US-005 | Story | Parse uploaded documents to extract text | 5 | backend-agent | US-003 |

## Sprint 2: Sprint 2

Complete upload status feedback, text chunking, and Gemini embedding generation.

Capacity: 20 points · Committed: 16

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-004 | Story | Receive feedback on upload and processing status | 5 | frontend-agent | US-003 |
| US-006 | Story | Chunk document text with overlap strategy | 3 | backend-agent | US-005 |
| US-007 | Story | Generate embeddings using gemini-embedding-001 | 5 | integration-agent | US-006 |
| US-016 | Story | Document upload API endpoint | 3 | backend-agent | US-003, US-005 |

## Sprint 3: Sprint 3

Persist embeddings and files, enable vector similarity retrieval, and expose document persistence across visits.

Capacity: 20 points · Committed: 15

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-008 | Story | Store embeddings and uploaded files on the server | 5 | backend-agent | US-007, US-003 |
| US-009 | Story | Retrieve relevant chunks via vector similarity search | 5 | backend-agent | US-008 |
| US-014 | Story | Persist documents and embeddings across visits tied to browser UUID | 5 | backend-agent | US-008 |

## Sprint 4: Sprint 4

Deliver the core chat experience with grounded Gemini 2.5 Flash answers, no-match handling, and browser conversation history.

Capacity: 20 points · Committed: 16

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-010 | Story | Ask questions and receive grounded answers | 8 | integration-agent | US-009 |
| ↳ US-010-T1 | Task | Build chat interface for submitting questions and displaying answers | — | frontend-agent | — |
| ↳ US-010-T2 | Task | Implement POST /api/chat endpoint orchestrating retrieval and generation | — | backend-agent | — |
| ↳ US-010-T3 | Task | Ensure generated answers exclude citations and source references | — | integration-agent | — |
| US-011 | Story | Handle questions when no documents or no relevant content exists | 3 | backend-agent | US-010, US-009 |
| US-012 | Story | Store conversation history in browser localStorage | 3 | frontend-agent | US-010 |
| US-013 | Story | Restore conversation history on return visits | 2 | frontend-agent | US-012 |

## Sprint 5: Sprint 5

Add automatic inactive-data cleanup, finalize REST API contracts, and ship setup documentation.

Capacity: 20 points · Committed: 11

| Key | Type | Title | Points | Role | Depends on |
|---|---|---|---|---|---|
| US-015 | Story | Remove documents inactive for approximately 30 days | 5 | devops-agent | US-008, US-014 |
| US-017 | Story | Chat query API endpoint | 3 | backend-agent | US-010, US-011 |
| US-018 | Story | Provide basic application setup and usage documentation | 3 | devops-agent | US-010, US-015, US-016, US-017 |

## Unscheduled

_Nothing unscheduled._
<!-- sdlc:auto:end sprints -->
