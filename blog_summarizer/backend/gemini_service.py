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
    "takeaway": "The single most important actionable takeaway from this article"
}}

Rules:
- "title": If the article has a clear title, use it. Otherwise, create a descriptive one.
- "summary": Capture the core message in 2-3 clear sentences.
- "key_points": Extract exactly 5 key points. Each should be a concise, standalone insight.
- "difficulty": Rate based on the technical depth and assumed reader knowledge.
- "takeaway": One actionable sentence the reader should remember.

ARTICLE TEXT:
{article_text}
"""


def summarize_text(text: str) -> dict:
    """
    Send article text to Gemini API and get a structured summary.

    Args:
        text: The cleaned article text.

    Returns:
        dict with keys: title, summary, key_points, difficulty, takeaway

    Raises:
        RuntimeError: If Gemini API call fails or returns invalid JSON.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = SUMMARIZATION_PROMPT.format(article_text=text)

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
            # Remove first and last lines (code fences)
            lines = [l for l in lines if not l.strip().startswith("```")]
            response_text = "\n".join(lines).strip()

        # Parse JSON
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            raise RuntimeError(
                f"Gemini returned invalid JSON. Raw response:\n{response_text[:500]}"
            )

        # Validate required fields
        required_fields = ["title", "summary", "key_points", "difficulty", "takeaway"]
        for field in required_fields:
            if field not in result:
                raise RuntimeError(f"Gemini response missing required field: {field}")

        # Ensure key_points is a list
        if not isinstance(result["key_points"], list):
            result["key_points"] = [result["key_points"]]

        # Validate difficulty
        valid_difficulties = ["Beginner", "Intermediate", "Advanced"]
        if result["difficulty"] not in valid_difficulties:
            result["difficulty"] = "Intermediate"  # Default fallback

        return result

    except genai.types.BlockedPromptException:
        raise RuntimeError(
            "The article content was blocked by Gemini's safety filters."
        )
    except Exception as e:
        if "API key" in str(e).lower():
            raise RuntimeError(
                "Invalid Gemini API key. Please check your GEMINI_API_KEY."
            )
        if isinstance(e, RuntimeError):
            raise
        raise RuntimeError(f"Gemini API error: {str(e)}")
