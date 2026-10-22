<!-- sdlc:auto:start adr -->
# ADR-0002: Use FastAPI 0.115 for Backend

Status: Accepted  
Date: 2026-10-22

## Context and Problem Statement

Which Backend technology does the project use? Decided in architecture v2.

## Considered Options

- FastAPI 0.115
- Flask
- Django

## Decision Outcome

Chosen option: FastAPI 0.115, because Approved stack. Python async support pairs well with Gemini API calls and file processing. Pydantic models validate upload and chat payloads.

## Consequences

Single-process deployment means the cleanup task runs in-process rather than in a separate worker, acceptable for MVP scale.
<!-- sdlc:auto:end adr -->