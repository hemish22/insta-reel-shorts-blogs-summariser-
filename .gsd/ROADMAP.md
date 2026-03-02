# ROADMAP.md

> **Current Milestone**: v1.1 — Enhanced Dashboard + YouTube ✅
> **Previous Milestone**: v1.0 ✅ Complete

---

## Milestone v1.0 — Blog Summarizer MVP ✅
All 4 phases complete. Core flow working: URL → scrape → summarize → store → display.

---

## Milestone v1.1 — Enhanced Dashboard + YouTube Support

> **Goal**: Polished dashboard with search/filter/delete, plus YouTube video summarization via transcript extraction.

### Must-Haves
- [x] Clean, scannable card layout with date, platform/domain, and original link prominent
- [x] Search/filter bar to find past summaries quickly
- [x] Expand/collapse for summary details (compact list by default)
- [x] Smooth animations and responsive mobile design
- [x] Delete individual summaries
- [x] YouTube video summarization via transcript

### Phases

#### Phase 1: Enhanced Dashboard UI ✅
**Status**: ✅ Complete
**Objective**: Redesign the dashboard with compact card layout, search bar, expand/collapse, and delete

---

#### Phase 2: YouTube Video Summarization ✅
**Status**: ✅ Complete
**Objective**: Allow users to paste a YouTube URL, extract the transcript, and summarize it via Gemini
**Depends on**: Phase 1

**Tasks**:
- [ ] Install `youtube-transcript-api` for transcript extraction
- [ ] Create `youtube_service.py` — detect YouTube URLs, extract transcript
- [ ] Update `main.py` `/summarize` endpoint to handle YouTube URLs alongside blog URLs
- [ ] Create YouTube-specific Gemini prompt (key insights, tools mentioned, summary, optional timestamps)
- [ ] Update frontend to show YouTube summaries with video metadata (channel, duration)
- [ ] Update database schema if needed (source_type field: blog vs youtube)

**Verification**:
- Paste a YouTube tech video URL → get structured summary
- Summary appears on dashboard with YouTube source indicator
- Blog URL flow still works without regression
