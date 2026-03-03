"""
Gemini API integration for blog summarization.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY environment variable is not set. "
        "Create a .env file in the backend/ directory with:\n"
        "GEMINI_API_KEY=your_api_key_here"
    )

genai.configure(api_key=API_KEY)

# Use Gemini 2.5 Flash for speed and quality
MODEL_NAME = "gemini-2.5-flash"

SUMMARIZATION_PROMPT = """You are an expert blog summarizer. Analyze the following blog article and return a structured JSON summary.

IMPORTANT: Return ONLY valid JSON, no markdown, no code fences, no extra text.

The JSON must have exactly these fields:
{{
    "title": "A clear, concise title for the article",
    "summary": "A comprehensive 2-3 sentence summary of the article's main message",
    "key_points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
    "difficulty": "Beginner OR Intermediate OR Advanced",
    "category": "AI OR Web Dev OR ML OR Cybersecurity OR General",
    "takeaway": "The single most important actionable takeaway from this article"
}}

Rules:
- "title": If the article has a clear title, use it. Otherwise, create a descriptive one.
- "summary": Capture the core message in 2-3 clear sentences.
- "key_points": Extract exactly 5 key points. Each should be a concise, standalone insight.
- "difficulty": Rate based on the technical depth and assumed reader knowledge.
- "category": Choose the most relevant tag. Use "General" if none of the others fit strictly.
- "takeaway": One actionable sentence the reader should remember.

ARTICLE TEXT:
{article_text}
"""

YOUTUBE_SUMMARIZATION_PROMPT = """You are an expert video content summarizer. Analyze the following YouTube video transcript and return a structured JSON summary.

IMPORTANT: Return ONLY valid JSON, no markdown, no code fences, no extra text.

The JSON must have exactly these fields:
{{
    "title": "A clear, concise title for the video",
    "summary": "A comprehensive 2-3 sentence summary of the video's main message",
    "key_points": ["Insight 1", "Insight 2", "Insight 3", "Insight 4", "Insight 5"],
    "difficulty": "Beginner OR Intermediate OR Advanced",
    "takeaway": "The single most important actionable takeaway from this video",
    "tools_mentioned": ["Tool or resource 1", "Tool or resource 2"],
    "category": "AI OR Web Dev OR ML OR Cybersecurity OR General"
}}

Rules:
- "title": Create a clear, descriptive title for the video content.
- "summary": Capture the core message in 2-3 clear sentences.
- "key_points": Extract exactly 5 key insights. Each should be a concise, standalone point.
- "difficulty": Rate based on the technical depth and assumed viewer knowledge.
- "takeaway": One actionable sentence the viewer should remember.
- "tools_mentioned": List any tools, libraries, frameworks, services, or resources mentioned. Use an empty list [] if none.
- "category": Choose the most relevant tag. Use "General" if none of the others fit strictly.

VIDEO TRANSCRIPT:
{transcript_text}
"""


import re as _re


def _parse_json_robust(text: str) -> dict:
    """
    Attempt to parse JSON with multiple recovery strategies:
    1. Direct parse
    2. Auto-close truncated brackets/braces
    3. Regex field extraction as last resort
    """
    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Auto-close truncated JSON
    # Count open vs close brackets and braces
    repaired = text.rstrip().rstrip(",")
    open_braces = repaired.count("{") - repaired.count("}")
    open_brackets = repaired.count("[") - repaired.count("]")

    # Check if we're in the middle of a string value (unclosed quote)
    quote_count = repaired.count('"')
    if quote_count % 2 != 0:
        repaired += '"'

    repaired += "]" * max(0, open_brackets)
    repaired += "}" * max(0, open_braces)

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Regex extraction of known fields
    def _extract(field_name: str, fallback=""):
        pattern = rf'"{field_name}"\s*:\s*"((?:[^"\\]|\\.)*)?"'
        m = _re.search(pattern, text, _re.DOTALL)
        return m.group(1).replace('\\"', '"') if m else fallback

    def _extract_list(field_name: str):
        pattern = rf'"{field_name}"\s*:\s*\[(.*?)\]'
        m = _re.search(pattern, text, _re.DOTALL)
        if m:
            items = _re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
            return items
        return []

    result = {
        "title": _extract("title", "Untitled"),
        "summary": _extract("summary", text[:300]),
        "key_points": _extract_list("key_points") or ["See summary above"],
        "difficulty": _extract("difficulty", "Intermediate"),
        "category": _extract("category", "General"),
        "takeaway": _extract("takeaway", "See summary for details."),
        "tools_mentioned": _extract_list("tools_mentioned"),
    }

    # Validate we got at least a title or summary
    if result["title"] == "Untitled" and result["summary"] == text[:300]:
        raise RuntimeError(
            f"Gemini returned unparseable response:\n{text[:500]}"
        )

    return result


def _call_gemini(prompt: str) -> dict:
    """
    Send a prompt to Gemini and parse the JSON response.
    Shared by both blog and YouTube summarization.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1024,
            ),
        )

        # Extract text from response
        response_text = response.text.strip()

        # Clean potential markdown code fences
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            response_text = "\n".join(lines).strip()

        # Parse JSON — with robust recovery for truncated responses
        result = _parse_json_robust(response_text)
        return result

    except genai.types.BlockedPromptException:
        raise RuntimeError(
            "The content was blocked by Gemini's safety filters."
        )
    except Exception as e:
        if "API key" in str(e).lower():
            raise RuntimeError(
                "Invalid Gemini API key. Please check your GEMINI_API_KEY."
            )
        if isinstance(e, RuntimeError):
            raise
        raise RuntimeError(f"Gemini API error: {str(e)}")


def summarize_text(text: str) -> dict:
    """
    Send article text to Gemini API and get a structured summary.

    Returns:
        dict with keys: title, summary, key_points, difficulty, takeaway
    """
    prompt = SUMMARIZATION_PROMPT.format(article_text=text)
    result = _call_gemini(prompt)

    # Validate required fields
    required_fields = ["title", "summary", "key_points", "difficulty", "category", "takeaway"]
    for field in required_fields:
        if field not in result:
            raise RuntimeError(f"Gemini response missing required field: {field}")

    # Ensure key_points is a list
    if not isinstance(result["key_points"], list):
        result["key_points"] = [result["key_points"]]

    # Validate difficulty and category
    valid_difficulties = ["Beginner", "Intermediate", "Advanced"]
    if result["difficulty"] not in valid_difficulties:
        result["difficulty"] = "Intermediate"
    
    valid_categories = ["AI", "Web Dev", "ML", "Cybersecurity", "General"]
    if result["category"] not in valid_categories:
        result["category"] = "General"

    return result


def summarize_youtube(transcript_text: str) -> dict:
    """
    Send YouTube transcript to Gemini API and get a structured summary.

    Returns:
        dict with keys: title, summary, key_points, difficulty, takeaway, tools_mentioned
    """
    prompt = YOUTUBE_SUMMARIZATION_PROMPT.format(transcript_text=transcript_text)
    result = _call_gemini(prompt)

    # Validate required fields
    required_fields = ["title", "summary", "key_points", "difficulty", "category", "takeaway"]
    for field in required_fields:
        if field not in result:
            raise RuntimeError(f"Gemini response missing required field: {field}")

    # Ensure key_points is a list
    if not isinstance(result["key_points"], list):
        result["key_points"] = [result["key_points"]]

    # Ensure tools_mentioned is a list (optional field)
    if "tools_mentioned" not in result:
        result["tools_mentioned"] = []
    if not isinstance(result["tools_mentioned"], list):
        result["tools_mentioned"] = [result["tools_mentioned"]]

    # Validate difficulty and category
    valid_difficulties = ["Beginner", "Intermediate", "Advanced"]
    if result["difficulty"] not in valid_difficulties:
        result["difficulty"] = "Intermediate"

    valid_categories = ["AI", "Web Dev", "ML", "Cybersecurity", "General"]
    if result["category"] not in valid_categories:
        result["category"] = "General"

    return result

