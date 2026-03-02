"""
YouTube transcript extraction service.
Detects YouTube URLs and fetches video transcripts.
Falls back to Whisper ASR when transcript API is unavailable.
"""

import re
from typing import Optional, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

from audio_service import download_audio, cleanup_audio
from whisper_service import transcribe_audio
from transcript_cleaner import clean_transcript


# ──────────────────────────────────────────────
# URL Detection
# ──────────────────────────────────────────────

YOUTUBE_PATTERNS = [
    # Standard: https://www.youtube.com/watch?v=VIDEO_ID
    r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
    # Short: https://youtu.be/VIDEO_ID
    r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
    # Embed: https://www.youtube.com/embed/VIDEO_ID
    r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    # Shorts: https://www.youtube.com/shorts/VIDEO_ID
    r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
]


def is_youtube_url(url: str) -> bool:
    """Check if a URL is a YouTube video link."""
    for pattern in YOUTUBE_PATTERNS:
        if re.search(pattern, url):
            return True
    return False


def extract_video_id(url: str) -> Optional[str]:
    """Extract the video ID from a YouTube URL."""
    for pattern in YOUTUBE_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


# ──────────────────────────────────────────────
# Transcript Fetching (API + Whisper Fallback)
# ──────────────────────────────────────────────

def _fetch_via_api(video_id: str) -> Optional[Dict[str, Any]]:
    """
    Try to fetch transcript via YouTube Transcript API.
    Returns None if transcripts are disabled/unavailable (triggers fallback).
    Raises RuntimeError for fatal errors (e.g., video doesn't exist).
    """
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)

        full_text = " ".join(snippet.text for snippet in transcript)
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        if not full_text or len(full_text) < 50:
            return None  # Too short, try Whisper

        return {
            "text": full_text,
            "language": transcript.language,
            "method": "api",
        }

    except (TranscriptsDisabled, NoTranscriptFound):
        # These are expected — fallback to Whisper
        return None
    except VideoUnavailable:
        raise RuntimeError(
            "This video is unavailable, private, or does not exist."
        )
    except Exception:
        # Unknown API error — try Whisper as fallback
        return None


def _fetch_via_whisper(url: str) -> Dict[str, Any]:
    """
    Download audio and transcribe with Whisper.
    Used as fallback when transcript API is unavailable.
    """
    audio_path = None
    try:
        print("📥 No transcript available. Downloading audio for Whisper...")
        audio_path = download_audio(url)

        result = transcribe_audio(audio_path)
        cleaned = clean_transcript(result["text"])

        if not cleaned or len(cleaned) < 20:
            raise RuntimeError(
                "Could not extract meaningful speech from this video. "
                "It may be music-only or have very little spoken content."
            )

        return {
            "text": cleaned,
            "language": result["language"],
            "method": "whisper",
        }
    finally:
        if audio_path:
            cleanup_audio(audio_path)


def fetch_transcript(url: str) -> Dict[str, Any]:
    """
    Fetch the transcript for a YouTube video.
    Strategy: Try API first → fallback to Whisper if unavailable.

    Args:
        url: YouTube video URL.

    Returns:
        dict with keys: video_id, text, domain, language, method

    Raises:
        ValueError: If URL is not a valid YouTube URL.
        RuntimeError: If both API and Whisper fail.
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {url}")

    # Step 1: Try transcript API (fast)
    result = _fetch_via_api(video_id)

    # Step 2: If API fails, fallback to Whisper (slower but universal)
    if result is None:
        result = _fetch_via_whisper(url)

    # Truncate very long transcripts
    MAX_CHARS = 30000
    text = result["text"]
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "... [transcript truncated]"

    return {
        "video_id": video_id,
        "text": text,
        "domain": "youtube.com",
        "language": result["language"],
        "method": result["method"],  # "api" or "whisper"
    }
