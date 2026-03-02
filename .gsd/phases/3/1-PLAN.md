---
phase: 3
plan: 1
wave: 1
---

# Phase 3: Whisper ASR Fallback + Instagram Reels

## Goal
When a video has no transcript (YouTube with disabled captions, Instagram Reels), download the audio via `yt-dlp`, transcribe with Whisper (local, base model), clean the text, and summarize via Gemini.

## Tasks

### Task 1: Install dependencies
- `openai-whisper` (local ASR, base model ~150MB)
- `yt-dlp` (video/audio downloader — YouTube + Instagram)
- `ffmpeg` must be available (Whisper dependency)
- Update `requirements.txt`

### Task 2: Create `audio_service.py`
- Download audio from YouTube/Instagram via yt-dlp
- Extract to temporary .wav file
- Cleanup temp files after use

### Task 3: Create `whisper_service.py`
- Load Whisper base model (lazy, cached)
- Transcribe audio file → text
- Return transcript with language info

### Task 4: Create `transcript_cleaner.py`
- Remove filler words (um, uh, ah, like)
- Remove repeated words/phrases
- Normalize whitespace

### Task 5: Create `instagram_service.py`
- Detect Instagram Reel/post URLs
- Download audio via yt-dlp
- Return transcript via Whisper pipeline

### Task 6: Update `youtube_service.py` — add Whisper fallback
- Try transcript API first
- If TranscriptsDisabled/NoTranscriptFound → download audio → Whisper

### Task 7: Update `main.py` — unified routing
- Blog → scraper
- YouTube → transcript API → fallback Whisper
- Instagram → Whisper pipeline

### Task 8: Update frontend
- Instagram source indicator (📸)
- Status messages for audio processing

### Task 9: Update database
- Support `source_type: "instagram"`

## Verify
- YouTube with transcript → fast API path
- YouTube without transcript → Whisper fallback
- Instagram Reel → download + Whisper
- Dashboard shows all source types correctly
