<!-- sdlc:auto:start adr -->
# ADR-0004: Use AWS for Cloud

Status: Proposed  
Date: 2026-10-22

## Context and Problem Statement

Which Cloud technology does the project use? Decided in architecture v1.

## Considered Options

- AWS
- GCP
- Azure

## Decision Outcome

Chosen option: AWS, because AWS provides EC2 for hosting the Docker Compose stack and EBS for persistent volumes. A single small instance keeps costs minimal while supporting all workloads: the Python web server, PostgreSQL with pgvector, and MinIO.

## Consequences

A single EC2 instance is a single point of failure. For this lightweight, non-critical application that is an accepted trade-off.
<!-- sdlc:auto:end adr -->