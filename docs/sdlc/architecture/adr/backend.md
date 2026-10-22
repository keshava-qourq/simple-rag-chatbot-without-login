<!-- sdlc:auto:start adr -->
# ADR-0002: Use FastAPI 0.115 for Backend

Status: Proposed  
Date: 2026-10-22

## Context and Problem Statement

Which Backend technology does the project use? Decided in architecture v1.

## Considered Options

- FastAPI 0.115
- Flask
- Django

## Decision Outcome

Chosen option: FastAPI 0.115, because The RAG pipeline is I/O-heavy (Gemini API calls, file parsing, database queries). FastAPI's async support and Python-native document processing libraries (pypdf, python-docx) make it the natural choice. The approved version 0.115 is what the repository is scaffolded against.

## Consequences

FastAPI does not include built-in task scheduling, so APScheduler is added for the cleanup job. No background queue is used since Redis was explicitly removed from the stack.
<!-- sdlc:auto:end adr -->