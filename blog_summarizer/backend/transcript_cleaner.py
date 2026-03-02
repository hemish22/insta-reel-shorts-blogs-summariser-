"""
Transcript cleaning service.
Removes filler words, repeated phrases, and normalizes whitespace.
"""

import re


# Common filler words/sounds to remove
FILLER_WORDS = [
    r'\bum+\b', r'\buh+\b', r'\bah+\b', r'\beh+\b', r'\bmm+\b',
    r'\bhmm+\b', r'\bhm+\b', r'\bohh?\b', r'\byeah\b',
    r'\byou know\b', r'\blike\b(?=\s+(um|uh|ah|so|you know))',
    r'\bI mean\b', r'\bbasically\b', r'\bactually\b',
    r'\bkind of\b', r'\bsort of\b',
    r'\bright\??\s*right',  # "right right"
]


def clean_transcript(text: str) -> str:
    """
    Clean a raw transcript by removing filler words and normalizing.

    Args:
        text: Raw transcript text.

    Returns:
        Cleaned transcript text.
    """
    if not text:
        return text

    cleaned = text

    # Remove common filler words
    for pattern in FILLER_WORDS:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Remove consecutive duplicate words (e.g., "the the", "and and")
    cleaned = re.sub(r'\b(\w+)\s+\1\b', r'\1', cleaned, flags=re.IGNORECASE)

    # Remove consecutive duplicate short phrases (2-3 words repeated)
    cleaned = re.sub(
        r'\b((?:\w+\s+){1,2}\w+)\s+\1\b',
        r'\1',
        cleaned,
        flags=re.IGNORECASE,
    )

    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Remove orphaned punctuation from removals
    cleaned = re.sub(r'\s+([,.])', r'\1', cleaned)
    cleaned = re.sub(r'([,.])\s*([,.])', r'\1', cleaned)

    # Capitalize first letter
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned
