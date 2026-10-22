# Simple RAG chatbot without login — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build simple RAG chatbot without login but with history use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings

**Documentation version:** v2
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v1 approved |
| [Architecture](architecture/README.md) | 16 entries |
| [Development](development/README.md) | 0 entries |
| [Testing](testing/README.md) | 0 entries |
| [Deployment](deployment/README.md) | 0 entries |
| [Maintenance](maintenance/README.md) | 0 entries |
| [Data model](architecture/data-model.md) | generated |
| [API (OpenAPI)](architecture/api/openapi.yaml) | generated |
| [Decisions (ADRs)](architecture/adr/README.md) | 4 decisions |
| [Sprint plan](development/sprint-plan.md) | not generated yet |
| [Developer guide](development/developer-guide.md) | generated |
| [API reference](development/api-reference.md) | 1 route |
| [Test report](testing/test-report.md) | not run yet |
| [Deployment guide](deployment/deployment-guide.md) | not deployed yet |
| [Runbook](deployment/runbook.md) | not deployed yet |
| [Release notes](deployment/release-notes.md) | 0 releases |
| [Traceability matrix](traceability-matrix.md) | 18 requirements |
| [Changelog](CHANGELOG.md) | 2 versions |
<!-- sdlc:auto:end contents -->

## Open gaps

<!-- sdlc:auto:start open-gaps -->
### Requirements

- Chunk size and overlap values are implementation details not yet specified
- File size and upload count limits are not specified — 'reasonable defaults assumed' but not defined
- Similarity threshold for retrieval is not specified
- Exact TTL for cleanup is an assumption (~30 days) not finalized
- No file size limits defined — 'reasonable defaults assumed'
- No upload count limits defined — 'reasonable defaults assumed'
- Chunk size and overlap values not specified (implementation details)
- Similarity threshold value not specified
- Number of top chunks to retrieve not specified
- Exact TTL is an assumption (~30 days), not finalized
- Cleanup mechanism type (TTL vs scheduled task) not specified
- Cleanup frequency/schedule not specified
- API endpoint paths/URLs not specified
- Request/response payload schemas not specified
- HTTP status codes for error responses not specified
- Exact TTL is approximate (~30 days), not finalized
- Accepted risk: no rate limiting could lead to cost issues if the app becomes publicly accessible
- Accepted risk: anyone with the URL can access all features; data isolation relies solely on browser UUID which is not a security boundary

### Architecture

- No explicit mapping provided between architecture elements and the 18 known requirement keys (US-001..US-018); traceability_matrix cannot be populated from this input alone.
- No industry/compliance domain was named for this project, so no regulatory trace was performed.
- No detail on UI states (loading/error) or accessibility considerations provided.
- No rate limiting or abuse-prevention strategy described, which is notable given there is no authentication layer.
- No stated upload file-size limit or max concurrent processing jobs.
- Chunk size is approximate (~1000 characters) with no stated overlap strategy or chunking algorithm detail.
- No stated error-handling/retry behavior if text extraction or embedding calls fail mid-document.
- No stated top-k value for retrieved context passages, nor prompt-template details for grounding.
- No fallback behavior described if the Gemini API is unavailable or rate-limited.
- No backup/retention policy or index configuration (e.g., ivfflat/hnsw) specified for pgvector.
- No stated database migration/versioning approach.
- No stated bucket access-policy or encryption-at-rest configuration.
- The 30-day inactivity threshold is stated as approximate; exact schedule/frequency of the cleanup job and precise threshold are not specified.
- No confirmation of whether cleanup is irreversible/permanent deletion vs. soft delete.
- No mention of TLS/HTTPS termination or certificate management for the single EC2 instance.
- Exact value of 'top-k' retrieved chunks is not specified in the input.
- Schedule/frequency of the periodic run is not specified (e.g., hourly, daily).
- No explicit foreign-key/index strategy or embedding dimensionality constraint enforcement described beyond '768-dimensional'.
- No request/response schema details (field names, status codes) given beyond endpoint purpose.
- No explicit authentication/authorization check described for scoping endpoints to the requesting browser UUID (e.g., how server verifies UUID ownership).
- No stated orchestration tool (e.g., Docker Compose file) confirmed explicitly, though described as 'Docker containers'.
- No high-availability, scaling, or backup/disaster-recovery plan for the single-instance deployment.
- No TLS/certificate or domain configuration mentioned for the EC2 host.
- No cost estimate or EC2 instance sizing specified for the MVP deployment.
<!-- sdlc:auto:end open-gaps -->
