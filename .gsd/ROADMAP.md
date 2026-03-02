# ROADMAP.md

> **Current Phase**: Not started
> **Milestone**: v1.0 — Blog Summarizer MVP

## Must-Haves (from SPEC)
- [ ] URL input → article extraction → Gemini summarization → SQLite storage → dashboard display
- [ ] Structured summary: title, domain, difficulty, summary, key points, takeaway, original URL
- [ ] Error handling for invalid URL, empty article, API failure, network timeout

## Phases

### Phase 1: Backend Foundation
**Status**: ⬜ Not Started
**Objective**: Set up FastAPI app, SQLite database, models, and scraper
**Deliverables**: `main.py`, `database.py`, `models.py`, `scraper.py`, `requirements.txt`

### Phase 2: Gemini Integration & API Endpoint
**Status**: ⬜ Not Started
**Objective**: Implement Gemini API service and the `/summarize` POST endpoint
**Deliverables**: `gemini_service.py`, complete `/summarize` endpoint in `main.py`

### Phase 3: Frontend
**Status**: ⬜ Not Started
**Objective**: Build homepage (URL input) and dashboard (summary list) with clean UI
**Deliverables**: `index.html`, `dashboard.html`, `styles.css`, `script.js`

### Phase 4: Polish & Documentation
**Status**: ⬜ Not Started
**Objective**: Error handling, README, final testing
**Deliverables**: `README.md`, verified end-to-end flow
