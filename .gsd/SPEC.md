# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision
Blog Summarizer is an MVP web application that allows users to paste a blog URL, automatically extracts the article content, summarizes it using the Gemini API, stores the structured summary in SQLite, and displays all summaries on a clean dashboard. Simple, modular, and production-ready.

## Goals
1. Accept a blog URL and extract clean article text via scraping
2. Summarize extracted content using Google Gemini API into structured JSON (title, summary, key points, difficulty, takeaway)
3. Store all summaries persistently in SQLite
4. Serve a frontend with a submission page and a dashboard listing all summaries

## Non-Goals (Out of Scope)
- YouTube or Instagram content support
- User authentication or accounts
- Real-time collaboration
- Content editing or re-summarization
- Deployment to cloud (local MVP only)

## Users
Individual users who want to quickly summarize blog posts for reference or study.

## Constraints
- **Tech stack**: Python/FastAPI backend, vanilla HTML/CSS/JS frontend, SQLite, Gemini API
- **API key**: Must use environment variable `GEMINI_API_KEY`, never hardcoded
- **Scope**: Blogs only (no video, social media)
- **Complexity**: Keep it simple and modular

## Success Criteria
- [ ] User can paste a URL and receive a structured summary
- [ ] Summaries are persisted in SQLite and survive server restarts
- [ ] Dashboard lists all saved summaries with title, domain, difficulty, summary, key points, takeaway, and original URL
- [ ] Proper error handling for invalid URLs, empty articles, API failures, and network timeouts
- [ ] Code is clean, modular, and fully runnable with no placeholders
