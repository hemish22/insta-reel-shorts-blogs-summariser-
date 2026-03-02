"""
YouTube transcript extraction service.
Detects YouTube URLs and fetches video transcripts.
"""

import re
from typing import Optional, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)


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
# Transcript Fetching
# ──────────────────────────────────────────────

def fetch_transcript(url: str) -> Dict[str, Any]:
    """
    Fetch the transcript for a YouTube video.

    Args:
        url: YouTube video URL.

    Returns:
        dict with keys: video_id, text, domain, language

    Raises:
        ValueError: If URL is not a valid YouTube URL.
        RuntimeError: If transcript cannot be fetched.
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {url}")

    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)

        # Combine all transcript segments into full text
        full_text = " ".join(
            snippet.text for snippet in transcript
        )

        # Clean up the text
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        if not full_text or len(full_text) < 50:
            raise RuntimeError(
                "Transcript is too short or empty. "
                "The video may not have meaningful spoken content."
            )

        # Truncate very long transcripts (Gemini handles ~30k tokens well)
        MAX_CHARS = 30000
        if len(full_text) > MAX_CHARS:
            full_text = full_text[:MAX_CHARS] + "... [transcript truncated]"

        return {
            "video_id": video_id,
            "text": full_text,
            "domain": "youtube.com",
            "language": transcript.language,
        }

    except TranscriptsDisabled:
        raise RuntimeError(
            "Transcripts are disabled for this video. "
            "The uploader has turned off captions."
        )
    except NoTranscriptFound:
        raise RuntimeError(
            "No transcript found for this video. "
            "Try a video with auto-generated or manual captions."
        )
    except VideoUnavailable:
        raise RuntimeError(
            "This video is unavailable, private, or does not exist."
        )
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to fetch YouTube transcript: {str(e)}")
