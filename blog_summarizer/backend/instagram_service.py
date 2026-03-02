"""
Instagram Reel/Post service.
Detects Instagram URLs and extracts content via audio download + Whisper.
"""

import re
from typing import Optional, Dict, Any

from audio_service import download_audio, cleanup_audio
from whisper_service import transcribe_audio
from transcript_cleaner import clean_transcript


# ──────────────────────────────────────────────
# URL Detection
# ──────────────────────────────────────────────

INSTAGRAM_PATTERNS = [
    # Reels: https://www.instagram.com/reel/CODE/
    r'(?:https?://)?(?:www\.)?instagram\.com/reel/([A-Za-z0-9_-]+)',
    # Reels alt: https://www.instagram.com/reels/CODE/
    r'(?:https?://)?(?:www\.)?instagram\.com/reels/([A-Za-z0-9_-]+)',
    # Posts with video: https://www.instagram.com/p/CODE/
    r'(?:https?://)?(?:www\.)?instagram\.com/p/([A-Za-z0-9_-]+)',
]


def is_instagram_url(url: str) -> bool:
    """Check if a URL is an Instagram Reel or post."""
    for pattern in INSTAGRAM_PATTERNS:
        if re.search(pattern, url):
            return True
    return False


def extract_post_id(url: str) -> Optional[str]:
    """Extract the post/reel shortcode from an Instagram URL."""
    for pattern in INSTAGRAM_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


# ──────────────────────────────────────────────
# Content Extraction
# ──────────────────────────────────────────────

def fetch_instagram_transcript(url: str) -> Dict[str, Any]:
    """
    Download an Instagram Reel/post, extract audio, and transcribe.

    Args:
        url: Instagram Reel/post URL.

    Returns:
        dict with keys: post_id, text, domain, language

    Raises:
        ValueError: If URL is invalid.
        RuntimeError: If download or transcription fails.
    """
    post_id = extract_post_id(url)
    if not post_id:
        raise ValueError(f"Could not extract post ID from URL: {url}")

    audio_path = None
    try:
        # Step 1: Download audio
        audio_path = download_audio(url)

        # Step 2: Transcribe with Whisper
        result = transcribe_audio(audio_path)

        # Step 3: Clean transcript
        cleaned_text = clean_transcript(result["text"])

        if not cleaned_text or len(cleaned_text) < 20:
            raise RuntimeError(
                "Could not extract meaningful spoken content from this reel. "
                "It may be music-only or have very little speech."
            )

        # Truncate very long transcripts
        MAX_CHARS = 30000
        if len(cleaned_text) > MAX_CHARS:
            cleaned_text = cleaned_text[:MAX_CHARS] + "... [transcript truncated]"

        return {
            "post_id": post_id,
            "text": cleaned_text,
            "domain": "instagram.com",
            "language": result["language"],
        }

    finally:
        # Always clean up temp audio
        if audio_path:
            cleanup_audio(audio_path)
