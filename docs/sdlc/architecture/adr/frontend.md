<!-- sdlc:auto:start adr -->
# ADR-0001: Use React 19 for Frontend

Status: Accepted  
Date: 2026-10-22

## Context and Problem Statement

Which Frontend technology does the project use? Decided in architecture v2.

## Considered Options

- React 19
- Vue 3
- Svelte 5

## Decision Outcome

Chosen option: React 19, because Approved stack. SPA with chat UI, file upload, and localStorage-based conversation history fits a client-rendered React application.

## Consequences

No SSR means initial load requires JS, but the app is a single interactive page so SEO is irrelevant.
<!-- sdlc:auto:end adr -->