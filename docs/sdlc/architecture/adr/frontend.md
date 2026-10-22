<!-- sdlc:auto:start adr -->
# ADR-0001: Use React 19 for Frontend

Status: Proposed  
Date: 2026-10-22

## Context and Problem Statement

Which Frontend technology does the project use? Decided in architecture v1.

## Considered Options

- React 19
- Next.js
- Vue 3

## Decision Outcome

Chosen option: React 19, because The frontend is a pure client-side chat interface with file upload and localStorage-based conversation history. No server-side rendering, SEO, or complex routing is needed, so a React SPA is the simplest fit.

## Consequences

No SSR means the initial load requires JavaScript. Conversation history in localStorage is lost when switching browsers or devices, which is accepted per NFR-005.
<!-- sdlc:auto:end adr -->