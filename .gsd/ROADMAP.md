# ROADMAP.md

> **Current Milestone**: v2.0 — Knowledge Base & Refinement
> **Previous Milestone**: v1.3 ✅ Complete

---

## Milestone v1.0 — Blog Summarizer MVP ✅
All 4 phases complete. Core flow working: URL → scrape → summarize → store → display.

---

## Milestone v1.1 — Enhanced Dashboard + YouTube ✅
Phase 1: Enhanced Dashboard ✅ | Phase 2: YouTube Transcript Summarization ✅

---

## Milestone v1.2 — Whisper ASR + Instagram Reels ✅
All tasks complete. Transcripts fallback, local Whisper, and Instagram support verified.

---

## Milestone v1.3 — Real-time Progress & UI Overhaul ✅
Phase 4: SSE Progress Stepper ✅ | Phase 5: UI Overhaul (Slate theme) ✅

---

## Milestone v2.0 — Knowledge Base & Refinement
> **Goal**: Transform the app from a simple summarizer into a powerful personal knowledge base. Add smart organization, manual refinement, and export capabilities.

### Must-Haves
- [ ] Download video audio via `yt-dlp` (YouTube + Instagram)
- [ ] Local Whisper ASR (whisper-base model for MVP)
- [ ] Fallback pipeline: try transcript API → if fails → Whisper
- [ ] Instagram Reel URL detection + summarization
- [ ] Transcript cleaning (filler words, repeated phrases)
- [ ] Frontend: Instagram/Reel source indicator

### Phases

#### Phase 3: Whisper ASR Fallback + Instagram Reels
**Status**: ⬜ Not Started
**Objective**: When a video has no transcript, download audio via yt-dlp, transcribe with Whisper, clean the text, and summarize. Support Instagram Reels as a new source.
**Depends on**: Phase 2

**Tasks**:
- [ ] Install `openai-whisper`, `yt-dlp`, `ffmpeg` dependencies
- [ ] Create `audio_service.py` — download video audio via yt-dlp, extract to wav/mp3
- [ ] Create `whisper_service.py` — transcribe audio using Whisper base model
- [ ] Create `transcript_cleaner.py` — remove filler words (um, uh), repeated phrases
- [ ] Create `instagram_service.py` — detect Instagram Reel URLs, download via yt-dlp
- [ ] Update `youtube_service.py` — fallback: transcript API → if fails → Whisper pipeline
- [ ] Update `main.py` — unified routing: blog / YouTube / Instagram
- [ ] Update frontend — Instagram source indicator (📸), Reel metadata
- [ ] Update database — `source_type: "instagram"` support

#### Phase 6: Knowledge Base Organization
**Status**: ✅ Complete
- Advanced Sorting (Date, Difficulty, Domain)
- Smart Search Logic
- Interactive Stats & Filter Chips
- AI categorization tags
**Depends on**: Phase 5

**Tasks**:
- [ ] Implement Sort Dropdown (Date, Difficulty, Domain, Title)
- [ ] Add Domain Tagging (AI, Web, ML, etc.) & chips
- [ ] Implement Smart Search (Summary, Key Points, Tools)
- [ ] Make Stats Cards interactive (Filtering on click)

#### Phase 7: Personalization & Export
**Status**: ✅ Complete
- Favorites / Bookmarking system
- Manual Summary Editing (refinement)
- Export to Markdown & Copy to Clipboard
- Premium Hover Animations (Glow & Elevation)

**Tasks**:
- [ ] **Favorites**: Add bookmark/star functionality
- [ ] **Manual Refinement**: Add "Edit Summary" button + backend update
- [ ] **Export System**: Markdown, PDF, Copy to Clipboard
- [ ] **Visual Hierarchy**: Color-coded borders based on categories

**Verification**:
- YouTube video WITH transcript → uses API (fast, existing flow)
- YouTube video WITHOUT transcript → downloads, Whisper transcribes, summary generated
- Instagram Reel → downloads, Whisper transcribes, summary generated
- All entries appear on dashboard with correct source indicators
- Blog flow still works without regression
