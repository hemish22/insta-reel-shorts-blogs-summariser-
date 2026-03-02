"""
Whisper speech-to-text service.
Transcribes audio files using OpenAI's Whisper model (local).
"""

import whisper

# ──────────────────────────────────────────────
# Model Loading (lazy, cached)
# ──────────────────────────────────────────────

_model = None
MODEL_NAME = "base"  # ~150MB, runs on CPU. Options: tiny, base, small, medium, large


def _get_model():
    """Load the Whisper model lazily (only on first use)."""
    global _model
    if _model is None:
        print(f"🎙️ Loading Whisper '{MODEL_NAME}' model (first-time download ~150MB)...")
        _model = whisper.load_model(MODEL_NAME)
        print("✅ Whisper model loaded")
    return _model


# ──────────────────────────────────────────────
# Transcription
# ──────────────────────────────────────────────

def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe an audio file using Whisper.

    Args:
        audio_path: Path to audio file (.wav, .mp3, .m4a, etc.)

    Returns:
        dict with keys: text, language

    Raises:
        RuntimeError: If transcription fails.
    """
    try:
        model = _get_model()

        print(f"🎙️ Transcribing audio... (this may take a moment)")
        result = model.transcribe(
            audio_path,
            fp16=False,  # CPU mode
            language=None,  # Auto-detect language
        )

        text = result.get("text", "").strip()
        language = result.get("language", "unknown")

        if not text or len(text) < 20:
            raise RuntimeError(
                "Transcription produced too little text. "
                "The audio may be music-only, silent, or in an unsupported language."
            )

        print(f"✅ Transcribed {len(text)} chars, language: {language}")

        return {
            "text": text,
            "language": language,
        }

    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Whisper transcription failed: {str(e)}")
