# Traceability Matrix

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start legend -->
Built from recorded links, not written by a model: requirement key → plan item (`source_stable_key`) → development ticket (`stable_key`) → the ticket's test steps → the last live deployment that started after the work finished.
<!-- sdlc:auto:end legend -->

<!-- sdlc:auto:start matrix -->
| Requirement | Epic | Title | Plan items | Sprint | Design | Code | Commits | Ticket | Tests | Deployed |
|---|---|---|---|---|---|---|---|---|---|---|
| US-001 | EPIC-001 | Generate and persist a browser UUID for anonymous identification | US-001 | 1 | fe | — | — | not started | not run | — |
| US-002 | EPIC-001 | Handle browser identifier scope across devices | US-002 | 1 | fe | — | — | not started | not run | — |
| US-003 | EPIC-002 | Upload supported document formats through the web interface | US-003, US-003-T1, US-003-T2, US-003-T3 | 1 | POST /api/documents, api, doc_proc, documents, fe, object_store | — | — | not started | not run | — |
| US-004 | EPIC-002 | Receive feedback on upload and processing status | US-004 | 2 | GET /api/documents/{document_id}/status, api, documents, fe | — | — | not started | not run | — |
| US-005 | EPIC-003 | Parse uploaded documents to extract text | US-005 | 1 | doc_proc, documents | — | — | not started | not run | — |
| US-006 | EPIC-003 | Chunk document text with overlap strategy | US-006 | 2 | chunks, doc_proc | — | — | not started | not run | — |
| US-007 | EPIC-003 | Generate embeddings using gemini-embedding-001 | US-007 | 2 | chunks, rag | — | — | not started | not run | — |
| US-008 | EPIC-004 | Store embeddings and uploaded files on the server | US-008 | 3 | chunks, db, documents, object_store | — | — | not started | not run | — |
| US-009 | EPIC-004 | Retrieve relevant chunks via vector similarity search | US-009 | 3 | chunks, db, rag | — | — | not started | not run | — |
| US-010 | EPIC-005 | Ask questions and receive grounded answers | US-010, US-010-T1, US-010-T2, US-010-T3 | 4 | POST /api/chat, api, chunks, documents, fe, rag | — | — | not started | not run | — |
| US-011 | EPIC-005 | Handle questions when no documents or no relevant content exists | US-011 | 4 | POST /api/chat, api, chunks, documents | — | — | not started | not run | — |
| US-012 | EPIC-006 | Store conversation history in browser localStorage | US-012 | 4 | fe | — | — | not started | not run | — |
| US-013 | EPIC-006 | Restore conversation history on return visits | US-013 | 4 | fe | — | — | not started | not run | — |
| US-014 | EPIC-007 | Persist documents and embeddings across visits tied to browser UUID | US-014 | 3 | GET /api/documents, api, db, documents | — | — | not started | not run | — |
| US-015 | EPIC-007 | Remove documents inactive for approximately 30 days | US-015 | 5 | chunks, cleanup, db, documents, object_store, user_activity | — | — | not started | not run | — |
| US-016 | EPIC-008 | Document upload API endpoint | US-016 | 2 | POST /api/documents, api, documents | — | — | not started | not run | — |
| US-017 | EPIC-008 | Chat query API endpoint | US-017 | 5 | POST /api/chat, api, documents | — | — | not started | not run | — |
| US-018 | EPIC-009 | Provide basic application setup and usage documentation | US-018 | 5 | — | — | — | not started | not run | — |
<!-- sdlc:auto:end matrix -->
