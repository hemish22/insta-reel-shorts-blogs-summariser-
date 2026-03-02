# DECISIONS.md — Architecture Decision Records

## ADR-001: Use SQLite for MVP storage
**Date**: 2026-03-02
**Decision**: SQLite via `sqlite3` stdlib — no ORM
**Rationale**: Simplest persistence for MVP, zero setup, file-based

## ADR-002: Vanilla frontend
**Date**: 2026-03-02
**Decision**: Plain HTML/CSS/JS, no frameworks
**Rationale**: Keeps frontend simple, no build step, easy to serve from FastAPI
