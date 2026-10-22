<!-- sdlc:auto:start adr -->
# ADR-0003: Use PostgreSQL 16 with pgvector for Database

Status: Accepted  
Date: 2026-10-22

## Context and Problem Statement

Which Database technology does the project use? Decided in architecture v2.

## Considered Options

- PostgreSQL 16 with pgvector
- pgvector on PostgreSQL 15
- Qdrant

## Decision Outcome

Chosen option: PostgreSQL 16 with pgvector, because Approved stack. pgvector provides 768-dimensional vector similarity search inside the relational database, avoiding a separate vector service.

## Consequences

pgvector's HNSW or IVFFLAT indexes are less performant than a dedicated vector DB at very large scale, but sufficient for MVP document volumes.
<!-- sdlc:auto:end adr -->