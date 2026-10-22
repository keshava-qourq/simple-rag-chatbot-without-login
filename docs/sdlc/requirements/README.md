# Product Requirements

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start narrative -->
## Summary

### REQ-TECH-STACK · approved · source: requirements:technology_stack

Product owner approved the exact technology stack: FastAPI 0.115 (backend), PostgreSQL 16 with pgvector (database), React 19 (frontend), AWS (cloud), Google Gemini (AI provider), MinIO (file storage). No substitutions allowed.

Backend: FastAPI 0.115 — chosen because the RAG pipeline is Python-native (PDF/DOCX parsing, embedding API calls, pgvector queries). FastAPI's async nature suits I/O-heavy Gemini API calls while serving chat. Cloud: AWS — hosts web app, PostgreSQL, and containers (MinIO, Redis removed). A single small EC2 or ECS container can run everything. Database: PostgreSQL 16 with pgvector — stores document metadata and vector embeddings in one database; pgvector similarity search sufficient at small scale. Frontend: React 19 — chat interface with file upload and localStorage history; no SSR or routing complexity needed. Next.js was considered but rejected due to unnecessary SSR overhead. API keys required: GEMINI_API_KEY (server-side env var). Out of scope: native mobile app, voice input, image/video generation, model training, queue/Redis (removed from stack).

**Related:** EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005, EPIC-008

### REQ-SERVICES · approved · source: requirements:services

Product owner approved three runtime services: pgvector in PostgreSQL for vector storage, Google Gemini SaaS for embeddings and answer generation, and MinIO (S3-compatible) for file storage.

Vector store: pgvector (in PostgreSQL) — stores document chunk embeddings alongside document metadata; no separate vector database needed. AI provider: Google Gemini (SaaS, env GEMINI_API_KEY) — uses Gemini 2.5 Flash for answer generation and gemini-embedding-001 for embeddings; one API key covers both. File storage: MinIO (S3-compatible, container bitnamilegacy/minio:2024.10.13) — persists uploaded PDFs, TXTs, DOCX files so returning users can chat against previously uploaded documents; runs as a container alongside the app at no external cost.

**Related:** EPIC-003, EPIC-004, EPIC-007

### REQ-SCOPE · approved · source: requirements:delivery_scope

Delivery scope is lightweight. Capabilities in scope and explicitly out-of-scope items are defined.

In scope: Document upload (PDF, TXT, DOCX) via web interface; server-side parsing, chunking, embedding; embedding storage and similarity search; uploaded file storage; anonymous user ID via browser UUID; document and embedding persistence across visits; chat interface for questions; answer generation grounded in uploaded documents; conversation history in browser localStorage; REST API endpoints for upload and chat; basic app documentation; gemini-embedding-001 for embeddings; Gemini 2.5 Flash for answers; PDF/TXT/DOCX as only supported formats; standard text chunking with overlap; conversation history in localStorage only (no server-side backup); no citations/sources in answers; no file size or upload count limits (reasonable defaults); no rate limiting on Gemini calls; no admin panel or document management dashboard. Out of scope: native mobile app, voice input, image/video generation, model training, queue/Redis (removed).

**Related:** EPIC-001, EPIC-002, EPIC-003, EPIC-004, EPIC-005, EPIC-006, EPIC-007, EPIC-008, EPIC-009

- ⚠ Chunk size and overlap values are implementation details not yet specified
- ⚠ File size and upload count limits are not specified — 'reasonable defaults assumed' but not defined
- ⚠ Similarity threshold for retrieval is not specified
- ⚠ Exact TTL for cleanup is an assumption (~30 days) not finalized

### EPIC-001 · approved · source: requirements:EPIC-001

Anonymous users are identified via a client-side UUID stored in localStorage. No authentication, accounts, or login required. The UUID associates uploaded documents and embeddings with a user across visits on the same browser.

US-001 [critical]: Generate and persist a browser UUID for anonymous identification. AC-001: First-time visitor with no UUID in localStorage gets a UUID generated and stored. AC-002: Returning visitor on same browser gets existing UUID retrieved and used to associate previously uploaded documents. AC-003: Any visitor can upload documents and ask questions without login, account creation, or access restriction. US-002 [low]: Handle browser identifier scope across devices. AC-004: Switching to a different browser or device generates a new UUID; previous documents are not associated with the new session.

**Related:** US-001, US-002, NFR-002, NFR-006

### EPIC-002 · approved · source: requirements:EPIC-002

Users upload PDF, TXT, or DOCX files through the web interface. Other formats are rejected. No file size or upload count limits specified. No admin panel; users cannot delete their own documents through the UI.

US-003 [critical]: Upload supported document formats through the web interface. AC-005: User selects a PDF/TXT/DOCX file and submits; file is uploaded and associated with browser UUID. AC-006: Unsupported file format is rejected with an error message indicating only PDF, TXT, and DOCX are supported. US-004 [medium]: Receive feedback on upload and processing status. AC-007: Processing status indicator displayed while server processes the document. AC-008: Success confirmation displayed when processing and embedding complete. AC-009: Error message displayed if upload or processing fails.

**Related:** US-003, US-004

- ⚠ No file size limits defined — 'reasonable defaults assumed'
- ⚠ No upload count limits defined — 'reasonable defaults assumed'

### EPIC-003 · approved · source: requirements:EPIC-003

Uploaded documents are parsed, chunked, and embedded server-side. Text is extracted from PDF/TXT/DOCX, split into overlapping chunks, and embedded using gemini-embedding-001 via the Google AI API. GEMINI_API_KEY is server-side only.

US-005 [critical]: Parse uploaded documents to extract text. AC-010: PDF text extracted. AC-011: TXT text read from file. AC-012: DOCX text extracted. US-006 [high]: Chunk document text with overlap strategy. AC-013: Extracted text split into chunks with overlap between adjacent chunks (chunk size and overlap are implementation details). US-007 [critical]: Generate embeddings using gemini-embedding-001. AC-014: Embedding vector generated for each chunk using gemini-embedding-001 via Google AI API. AC-015: API key read from server-side env var, never included in client-facing responses.

**Related:** US-005, US-006, US-007, NFR-001

- ⚠ Chunk size and overlap values not specified (implementation details)

### EPIC-004 · approved · source: requirements:EPIC-004

Embeddings are stored in PostgreSQL with pgvector. Original files are stored on the server. Similarity search retrieves the most relevant chunks for a given question. If no chunks match above a threshold, the system indicates no relevant information was found.

US-008 [critical]: Store embeddings and uploaded files on the server. AC-016: Embeddings persisted in PostgreSQL with pgvector, associated with browser UUID and source document. AC-017: Original file stored on server and associated with browser UUID. US-009 [critical]: Retrieve relevant chunks via vector similarity search. AC-018: Question is embedded and compared against stored embeddings using vector similarity search; top matching chunks returned. AC-019: If no relevant chunks found above a similarity threshold, system returns indication that no relevant information was found.

**Related:** US-008, US-009, NFR-002

- ⚠ Similarity threshold value not specified
- ⚠ Number of top chunks to retrieve not specified

### EPIC-005 · approved · source: requirements:EPIC-005

Users interact with a chat interface to ask questions and receive answers from Gemini 2.5 Flash grounded in retrieved document chunks. Answers include no citations or source references. No rate limiting on Gemini API calls.

US-010 [critical]: Ask questions and receive grounded answers. AC-020: User types a question and submits; question sent to server, relevant chunks retrieved, answer generated using Gemini 2.5 Flash grounded in retrieved content. AC-021: Answer displayed in chat interface. AC-022: Answer does not include citations, source references, or indicators of which document chunks were used. US-011 [medium]: Handle questions when no documents or no relevant content exists. AC-023: User with no uploaded documents asks a question; system informs them no documents are available and prompts to upload. AC-024: User with uploaded documents whose question does not match any content; system returns response indicating no relevant information found.

**Related:** US-010, US-011, NFR-004

### EPIC-006 · approved · source: requirements:EPIC-006

Conversation history (questions and answers) is stored in browser localStorage only. No server-side backup. Returning on the same browser restores past conversations. Switching devices or browsers loses history.

US-012 [high]: Store conversation history in browser localStorage. AC-025: After each Q&A exchange, both question and answer stored in localStorage. AC-026: All messages persisted in chronological order. US-013 [high]: Restore conversation history on return visits. AC-027: Returning on same browser loads past conversations from localStorage and displays them. AC-028: Different browser or device shows no previous conversation history.

**Related:** US-012, US-013, NFR-005

### EPIC-007 · approved · source: requirements:EPIC-007

Uploaded documents and embeddings persist on the server tied to the browser UUID. Returning users can chat against previously uploaded documents without re-uploading. A cleanup mechanism removes data for UUIDs inactive for approximately 30 days. No admin panel; users cannot delete their own documents.

US-014 [high]: Persist documents and embeddings across visits tied to browser UUID. AC-029: Returning user on same browser finds previously uploaded documents and embeddings available; can chat without re-uploading. AC-030: Documents and embeddings associated with browser UUID remain accessible across sessions. US-015 [low]: Remove documents inactive for approximately 30 days. AC-031: When a browser UUID has been inactive for approximately 30 days and cleanup runs, documents, embeddings, and stored files are removed from server.

**Related:** US-014, US-015, NFR-002, NFR-003

- ⚠ Exact TTL is an assumption (~30 days), not finalized
- ⚠ Cleanup mechanism type (TTL vs scheduled task) not specified
- ⚠ Cleanup frequency/schedule not specified

### EPIC-008 · approved · source: requirements:EPIC-008

The application exposes REST API endpoints for document upload and chat. Requests include the browser UUID to associate documents and queries with the anonymous user. These endpoints serve the web frontend and could serve other clients.

US-016 [high]: Document upload API endpoint. AC-032: POST to upload endpoint with supported file and browser UUID; server accepts, processes, returns success with document metadata. AC-033: POST with unsupported format returns error indicating format not supported. AC-034: POST without browser UUID returns error indicating UUID is required. US-017 [high]: Chat query API endpoint. AC-035: POST to chat endpoint with question and browser UUID; server retrieves relevant chunks, generates answer using Gemini 2.5 Flash, returns answer. AC-036: POST without browser UUID returns error indicating UUID is required. AC-037: POST with UUID that has no uploaded documents returns response indicating no documents are available.

**Related:** US-016, US-017

- ⚠ API endpoint paths/URLs not specified
- ⚠ Request/response payload schemas not specified
- ⚠ HTTP status codes for error responses not specified

### EPIC-009 · approved · source: requirements:EPIC-009

The application includes basic documentation covering setup, required environment variables (GEMINI_API_KEY), database configuration (PostgreSQL with pgvector), and how to run the application.

US-018 [medium]: Provide basic application setup and usage documentation. AC-038: Step-by-step instructions for setting up and running the application locally. AC-039: List of required environment variables including GEMINI_API_KEY and instructions for configuring PostgreSQL with pgvector. AC-040: Description of supported upload formats (PDF, TXT, DOCX) and the core chatbot workflow.

**Related:** US-018

### NFR-001 · approved · source: requirements:NFR-001

Security: Gemini API key must never be exposed to the client. Stored as a server-side environment variable and never included in any client-facing response or payload.

Applies to: US-007. The GEMINI_API_KEY is stored as a server-side environment variable and is never included in any client-facing response or payload.

**Related:** US-007

### NFR-002 · approved · source: requirements:NFR-002

Privacy: Data isolation by browser UUID. A user's uploaded documents, embeddings, and conversation history are associated only with their browser UUID and are not accessible to or shared with other users.

Applies to: US-001, US-002, US-008, US-014. Data isolation is enforced by associating all documents, embeddings, and history with the browser UUID only.

**Related:** US-001, US-002, US-008, US-014

### NFR-003 · approved · source: requirements:NFR-003

Privacy: Automatic cleanup of inactive data. Documents, embeddings, and stored files for browser UUIDs inactive for approximately 30 days are automatically removed.

Applies to: US-015. Target: approximately 30 days of inactivity before cleanup.

**Related:** US-015

- ⚠ Exact TTL is approximate (~30 days), not finalized

### NFR-004 · approved · source: requirements:NFR-004

Scalability (accepted risk): No rate limiting on Gemini API calls. Assumed not needed at small scale but could be important for cost control with public access.

Applies to: US-010. Accepted risk — no rate limiting is applied to Gemini API calls.

**Related:** US-010

- ⚠ Accepted risk: no rate limiting could lead to cost issues if the app becomes publicly accessible

### NFR-005 · approved · source: requirements:NFR-005

Availability (accepted risk): No server-side conversation history backup. History is stored only in browser localStorage. Switching devices or browsers loses all conversation history.

Applies to: US-012, US-013. Accepted risk — conversation history has no server-side backup.

**Related:** US-012, US-013

### NFR-006 · approved · source: requirements:NFR-006

Security (accepted risk): No authentication or access control. Anyone with the URL can access all features including document upload and chat.

Applies to: US-001. Accepted risk — no authentication, accounts, or login required.

**Related:** US-001

- ⚠ Accepted risk: anyone with the URL can access all features; data isolation relies solely on browser UUID which is not a security boundary
<!-- sdlc:auto:end narrative -->

<!-- sdlc:auto:start summary -->
**Requirements version:** v1  
**Delivery scope:** lightweight  
**Approved:** 2026-10-22

**Capabilities in scope:** Document upload (PDF, TXT, DOCX) through web interface, Server-side document parsing, chunking, and embedding, Embedding storage and similarity search, Uploaded document file storage, Anonymous user identification via browser UUID, Document and embedding persistence across visits, Chat interface for asking questions, Answer generation grounded in uploaded documents, Conversation history stored in browser, REST API endpoints for document upload and chat, Basic application documentation, Google Gemini gemini-embedding-001 for document embeddings, Google Gemini 2.5 Flash for answer generation, PDF, TXT, and DOCX as the only supported upload formats, Standard text chunking with overlap strategy, Conversation history in browser localStorage only (no server-side backup), No citations or sources shown in chat answers, No file size or upload count limits (reasonable defaults assumed), No rate limiting on Gemini API calls, No admin panel or document management dashboard

**Approved technology stack:**

| Layer | Choice | Rationale |
|---|---|---|
| backend | FastAPI | FastAPI is the only backend option on the list, and it's the right fit: the RAG pipeline is Python-native (PDF/DOCX parsing libraries, embedding API calls, pgvector queries all have first-class Python support). FastAPI's async nature suits the I/O-heavy pattern of calling Gemini's API while serving chat requests. The server-side document processing assumption — parsing, chunking, embedding — maps directly to Python libraries like PyPDF2, python-docx, and the Gemini SDK. |
| cloud | AWS | AWS is the only cloud option listed and is a solid default for hosting the web app, PostgreSQL instance, and containerized services (MinIO, Redis) together. At your scale, a single small EC2 instance or ECS container running everything would keep costs minimal. The product's needs — a Python web server, Postgres with pgvector, file storage, and a cleanup task — are all standard AWS workloads. |
| database | PostgreSQL | PostgreSQL with the pgvector extension is explicitly assumed for this project and is the right call. It stores both the document metadata (filename, upload timestamp, browser UUID) and the vector embeddings in one database, so retrieval queries join document info with embeddings without a second service. At your scale — handful of users, small documents — pgvector's similarity search is more than fast enough and you avoid running a separate vector database. |
| frontend | React | The frontend is a chat interface with a file-upload widget and localStorage-based conversation history — no server-side rendering, no SEO needs, no complex routing. React handles this cleanly and is the platform default. The conversation history requirement (localStorage restore on return) is pure client-side state, which is React's home turf. Next.js was considered but its SSR and routing complexity would add overhead the product never uses. |
<!-- sdlc:auto:end summary -->

<!-- sdlc:auto:start epics -->
## EPIC-001: Anonymous User Identification

The system identifies anonymous users via a UUID generated client-side and stored in localStorage. No authentication, accounts, or login are required. Anyone with the URL can use the chatbot. The browser UUID associates uploaded documents and embeddings with a user across visits on the same device/browser.

### US-001: Generate and persist a browser UUID for anonymous identification

**Priority:** critical

> As a visitor to the chatbot, I want to use the chatbot without creating an account or logging in, so that I can immediately upload documents and start chatting with no friction.

| ID | Given | When | Then |
|---|---|---|---|
| AC-001 | A first-time visitor opens the web application | the page loads and no existing UUID is found in localStorage | a UUID is generated client-side and stored in the browser's localStorage |
| AC-002 | A returning visitor opens the web application on the same browser | the page loads | the existing UUID is retrieved from localStorage and used to associate the user with their previously uploaded documents |
| AC-003 | Any visitor to the web application | they interact with the chatbot | they can upload documents and ask questions without any login, account creation, or access restriction |

### US-002: Handle browser identifier scope across devices

**Priority:** low

> As a user of the chatbot, I want my browser UUID to be scoped to my current browser, so that my documents are associated only with the browser I used to upload them.

| ID | Given | When | Then |
|---|---|---|---|
| AC-004 | A user switches to a different browser or device | they visit the site | a new UUID is generated for that browser and previous documents are not associated with the new session |

## EPIC-002: Document Upload

Users upload PDF, TXT, or DOCX files through the web interface. Supported upload formats are limited to PDF, TXT, and DOCX; other formats are rejected. No file size or upload count limits are specified — reasonable defaults are assumed. No admin panel or document management dashboard exists, and users cannot delete their own documents through the UI.

### US-003: Upload supported document formats through the web interface

**Priority:** critical

> As a user of the chatbot, I want to upload PDF, TXT, or DOCX documents through the web interface, so that the chatbot can learn from my documents and answer questions about them.

| ID | Given | When | Then |
|---|---|---|---|
| AC-005 | A user on the web interface with a PDF, TXT, or DOCX file | they select the file and submit the upload | the file is uploaded to the server and associated with the user's browser UUID |
| AC-006 | A user on the web interface with a file that is not PDF, TXT, or DOCX | they attempt to upload the file | the upload is rejected and an error message is displayed indicating only PDF, TXT, and DOCX files are supported |

### US-004: Receive feedback on upload and processing status

**Priority:** medium

> As a user of the chatbot, I want to see upload and processing status while my document is being parsed and embedded, so that I know when my document is ready to chat against.

| ID | Given | When | Then |
|---|---|---|---|
| AC-007 | A user uploads a document | the upload is being processed by the server | a processing status indicator is displayed |
| AC-008 | A document has finished processing and embedding | the processing completes | a success confirmation is displayed |
| AC-009 | An error occurs during upload or processing | the processing fails | an error message is displayed to the user |

## EPIC-003: Server-Side Document Processing

Uploaded documents are parsed, chunked, and embedded server-side. The app extracts text from PDF, TXT, and DOCX files, splits text into chunks using a standard chunking strategy with overlap (chunk size and overlap are implementation details), and generates embeddings using Google's gemini-embedding-001 model via the Google AI API. The GEMINI_API_KEY is stored as a server-side environment variable and never exposed to the client.

### US-005: Parse uploaded documents to extract text

**Priority:** critical

> As a user of the chatbot, I want the system to extract text from my uploaded documents, so that the content can be chunked and embedded for retrieval.

| ID | Given | When | Then |
|---|---|---|---|
| AC-010 | A PDF file is uploaded | the server processes the file | text is extracted from the PDF document |
| AC-011 | A TXT file is uploaded | the server processes the file | the text content is read from the file |
| AC-012 | A DOCX file is uploaded | the server processes the file | text is extracted from the DOCX document |

### US-006: Chunk document text with overlap strategy

**Priority:** high

> As a system operator, I want extracted text to be split into overlapping chunks, so that retrieval can match relevant passages without losing context at chunk boundaries.

| ID | Given | When | Then |
|---|---|---|---|
| AC-013 | Text has been extracted from an uploaded document | the server processes the extracted text | the text is split into chunks using a standard chunking strategy with overlap between adjacent chunks |

### US-007: Generate embeddings using gemini-embedding-001

**Priority:** critical

> As a user of the chatbot, I want my document chunks to be embedded using Google's gemini-embedding-001 model, so that the system can perform semantic similarity search to find relevant content for my questions.

| ID | Given | When | Then |
|---|---|---|---|
| AC-014 | Document chunks are ready for embedding | the server processes the chunks | an embedding vector is generated for each chunk using the gemini-embedding-001 model via the Google AI API |
| AC-015 | The server needs to call the Google AI API | the API call is made | the key is read from a server-side environment variable and is never included in any client-facing response or payload |

## EPIC-004: Embedding Storage and Similarity Search

Generated embeddings are stored in a PostgreSQL database using the pgvector extension. Original uploaded document files are also stored on the server. Similarity search retrieves the most relevant chunks for a given question. Assumption: pgvector (PostgreSQL extension) is used for vector storage — could alternatively use a dedicated vector database like ChromaDB or Pinecone.

### US-008: Store embeddings and uploaded files on the server

**Priority:** critical

> As a system operator, I want embeddings and original files to be persisted in a server-side data store, so that they remain available for retrieval across user visits without re-processing.

| ID | Given | When | Then |
|---|---|---|---|
| AC-016 | Embeddings have been generated for document chunks | the server stores the embeddings | the embeddings are persisted in a PostgreSQL database with the pgvector extension, associated with the browser UUID and source document |
| AC-017 | An original uploaded document file | the upload is accepted | the file is stored on the server and associated with the user's browser UUID |

### US-009: Retrieve relevant chunks via vector similarity search

**Priority:** critical

> As a user of the chatbot, I want the system to find the most relevant document chunks for my question, so that the generated answer is grounded in my uploaded content.

| ID | Given | When | Then |
|---|---|---|---|
| AC-018 | A user submits a question | the system searches for relevant content | the question is embedded and compared against stored embeddings using vector similarity search, and the top matching chunks are returned |
| AC-019 | A user submits a question and no relevant chunks are found above a similarity threshold | the similarity search is performed | the system returns an indication that no relevant information was found in the uploaded documents |

## EPIC-005: Chat Interface and Answer Generation

Users interact with a chat interface to ask questions and receive answers generated by Google Gemini 2.5 Flash, grounded in retrieved document chunks. Answers do not include citations or source references. No rate limiting is applied to Gemini API calls — assumed not needed at small scale but could be important for cost control with public access.

### US-010: Ask questions and receive grounded answers

**Priority:** critical

> As a user of the chatbot, I want to type a question in the chat interface and receive an answer grounded in my uploaded documents, so that I can get information from my documents without reading them manually.

| ID | Given | When | Then |
|---|---|---|---|
| AC-020 | A user on the chat interface with uploaded documents | they type a question and submit it | the question is sent to the server, relevant chunks are retrieved, and an answer is generated using Gemini 2.5 Flash grounded in the retrieved content |
| AC-021 | An answer has been generated by the server | the response is returned to the client | the answer is displayed in the chat interface |
| AC-022 | An answer is generated from retrieved document chunks | the answer is displayed | the answer does not include citations, source references, or indicators of which document chunks were used |

### US-011: Handle questions when no documents or no relevant content exists

**Priority:** medium

> As a user of the chatbot, I want to receive a clear message when the system cannot answer my question, so that I understand whether I need to upload more documents or rephrase my question.

| ID | Given | When | Then |
|---|---|---|---|
| AC-023 | A user with no uploaded documents | they ask a question | the system informs them that no documents are available and prompts them to upload documents first |
| AC-024 | A user with uploaded documents whose question does not match any content | the system performs retrieval and finds no matching chunks | the system returns a response indicating no relevant information was found in the uploaded documents |

## EPIC-006: Conversation History

Conversation history (questions and answers) is stored in the browser's localStorage only. There is no server-side backup of chat history. Returning to the site on the same browser restores past conversations. Switching devices or browsers loses conversation history.

### US-012: Store conversation history in browser localStorage

**Priority:** high

> As a user of the chatbot, I want my conversation history to be saved in my browser, so that I can refer back to previous questions and answers.

| ID | Given | When | Then |
|---|---|---|---|
| AC-025 | A user asks a question and receives an answer | the exchange is completed | both the question and answer are stored in the browser's localStorage |
| AC-026 | Multiple conversations occur | the user continues chatting | all messages are persisted in localStorage in chronological order |

### US-013: Restore conversation history on return visits

**Priority:** high

> As a user of the chatbot, I want my past conversations to be restored when I return to the site on the same browser, so that I can continue where I left off without losing context.

| ID | Given | When | Then |
|---|---|---|---|
| AC-027 | A user returns to the site on the same browser where they previously chatted | the page loads | past conversations are loaded from localStorage and displayed in the chat interface |
| AC-028 | A user visits the site on a different browser or device | the page loads | no previous conversation history is displayed because it is not available in that browser's localStorage |

## EPIC-007: Document and Embedding Persistence

Uploaded documents and their embeddings persist on the server, tied to the user's browser UUID. Returning users can chat against previously uploaded documents without re-uploading. No admin panel or document management dashboard is provided; users cannot delete their own documents through the UI. A cleanup mechanism (TTL or scheduled task) removes documents and embeddings associated with browser IDs inactive for approximately 30 days — the exact TTL is an assumption.

### US-014: Persist documents and embeddings across visits tied to browser UUID

**Priority:** high

> As a user of the chatbot, I want my uploaded documents and their embeddings to persist on the server across visits, so that I can return and immediately chat against my previously uploaded documents without re-uploading.

| ID | Given | When | Then |
|---|---|---|---|
| AC-029 | A user has previously uploaded documents | they return to the site on the same browser | the previously uploaded documents and their embeddings are available on the server and the user can chat against them without re-uploading |
| AC-030 | Documents and embeddings are stored on the server | the server receives a request from that UUID | they are associated with the user's browser UUID and remain accessible across sessions |

### US-015: Remove documents inactive for approximately 30 days

**Priority:** low

> As a system operator, I want documents and embeddings for inactive users to be automatically cleaned up, so that storage does not grow indefinitely with abandoned anonymous sessions.

| ID | Given | When | Then |
|---|---|---|---|
| AC-031 | Documents and embeddings associated with a browser UUID | the browser UUID has been inactive for approximately 30 days and the cleanup mechanism runs | the documents, their embeddings, and stored files are removed from the server |

## EPIC-008: REST API Endpoints

The application exposes REST API endpoints for document upload and chat. These endpoints are used by the web frontend and could be used by other clients. Requests include the browser UUID to associate documents and queries with the anonymous user.

### US-016: Document upload API endpoint

**Priority:** high

> As a client application, I want a REST API endpoint to upload documents programmatically, so that the web frontend (and potentially other clients) can submit documents for processing.

| ID | Given | When | Then |
|---|---|---|---|
| AC-032 | A client sends a POST request to the upload endpoint with a supported file (PDF, TXT, or DOCX) and a browser UUID | the request is received | the server accepts the file, processes it, and returns a success response with document metadata |
| AC-033 | A client sends a POST request to the upload endpoint with an unsupported file format | the request is received | the server returns an error response indicating the format is not supported |
| AC-034 | A client sends a POST request to the upload endpoint without a browser UUID | the request is received | the server returns an error response indicating the UUID is required |

### US-017: Chat query API endpoint

**Priority:** high

> As a client application, I want a REST API endpoint to submit questions and receive answers, so that the web frontend (and potentially other clients) can interact with the RAG chatbot.

| ID | Given | When | Then |
|---|---|---|---|
| AC-035 | A client sends a POST request to the chat endpoint with a question and a browser UUID | the request is received | the server retrieves relevant chunks, generates an answer using Gemini 2.5 Flash, and returns the answer in the response |
| AC-036 | A client sends a POST request to the chat endpoint without a browser UUID | the request is received | the server returns an error response indicating the UUID is required |
| AC-037 | A client sends a POST request to the chat endpoint with a UUID that has no uploaded documents | the request is received | the server returns a response indicating no documents are available |

## EPIC-009: Application Documentation

The application includes basic documentation covering setup, required environment variables (e.g., GEMINI_API_KEY), database configuration (PostgreSQL with pgvector), and how to run the application.

### US-018: Provide basic application setup and usage documentation

**Priority:** medium

> As a developer or user, I want basic documentation explaining how to set up, configure, and run the application, so that I can deploy and use the chatbot without extensive trial and error.

| ID | Given | When | Then |
|---|---|---|---|
| AC-038 | A developer or user consulting the documentation | they read the documentation | they find step-by-step instructions for setting up and running the application locally |
| AC-039 | A developer consulting the documentation | they read the documentation | they find a list of required environment variables including GEMINI_API_KEY and instructions for configuring a PostgreSQL database with the pgvector extension |
| AC-040 | A user or developer consulting the documentation | they read the documentation | they find a description of the supported upload formats (PDF, TXT, DOCX) and the core chatbot workflow |
<!-- sdlc:auto:end epics -->
