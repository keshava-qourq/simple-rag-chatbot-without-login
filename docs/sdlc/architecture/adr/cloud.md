<!-- sdlc:auto:start adr -->
# ADR-0004: Use AWS for Cloud

Status: Accepted  
Date: 2026-10-22

## Context and Problem Statement

Which Cloud technology does the project use? Decided in architecture v2.

## Considered Options

- AWS
- GCP
- Azure

## Decision Outcome

Chosen option: AWS, because Approved deployment target. Single EC2 instance running Docker Compose keeps infrastructure simple and cost-effective for MVP.

## Consequences

Single instance is a single point of failure with no auto-scaling, acceptable for development and low-traffic MVP.
<!-- sdlc:auto:end adr -->