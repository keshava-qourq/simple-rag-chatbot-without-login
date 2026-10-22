<!-- sdlc:auto:start adr -->
# ADR-0003: Use PostgreSQL 16 for Database

Status: Proposed  
Date: 2026-10-22

## Context and Problem Statement

Which Database technology does the project use? Decided in architecture v1.

## Considered Options

- PostgreSQL 16
- SQLite
- MySQL

## Decision Outcome

Chosen option: PostgreSQL 16, because PostgreSQL with the pgvector extension stores document metadata and vector embeddings in a single database, avoiding a separate vector service. At this scale, pgvector similarity search is fast enough for a handful of users and small documents.

## Consequences

Running PostgreSQL as a container on EC2 means the operator is responsible for backups and updates. For this lightweight scope that is acceptable.
<!-- sdlc:auto:end adr -->