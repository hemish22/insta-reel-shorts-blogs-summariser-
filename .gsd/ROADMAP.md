# ROADMAP.md

> **Current Milestone**: v1.2 — Whisper ASR + Instagram Reels
> **Previous Milestone**: v1.1 ✅ Complete

---

## Milestone v1.0 — Blog Summarizer MVP ✅
All 4 phases complete. Core flow working: URL → scrape → summarize → store → display.

---

## Milestone v1.1 — Enhanced Dashboard + YouTube ✅
Phase 1: Enhanced Dashboard ✅ | Phase 2: YouTube Transcript Summarization ✅

---

## Milestone v1.2 — Whisper ASR + Instagram Reels

> **Goal**: Unified text extraction layer — when transcripts are unavailable, download video, extract audio, run Whisper ASR to generate transcript, then summarize via Gemini. Support YouTube (no transcript), Instagram Reels, and any video with speech.

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

**Verification**:
- YouTube video WITH transcript → uses API (fast, existing flow)
- YouTube video WITHOUT transcript → downloads, Whisper transcribes, summary generated
- Instagram Reel → downloads, Whisper transcribes, summary generated
- All entries appear on dashboard with correct source indicators
- Blog flow still works without regression
