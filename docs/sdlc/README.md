# Simple RAG chatbot without login — SDLC Documentation

> Maintained by QuorQ AI SDLC. Text between `sdlc:auto` markers is regenerated; anything outside them is yours and is kept.

<!-- sdlc:auto:start overview -->
Build simple RAG chatbot without login but with history use gemini-2.5-flash for answers and gemini-embedding-001 for embeddings

**Documentation version:** v1
<!-- sdlc:auto:end overview -->

## Contents

<!-- sdlc:auto:start contents -->
| Document | State |
|---|---|
| [Requirements](requirements/README.md) | v1 approved |
| [Architecture](architecture/README.md) | 0 entries |
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
| [Changelog](CHANGELOG.md) | 1 version |
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
<!-- sdlc:auto:end open-gaps -->
