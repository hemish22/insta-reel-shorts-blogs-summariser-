"""
FastAPI application for Blog Summarizer.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from models import SummarizeRequest, SummaryResponse
from database import init_db, save_summary, get_all_summaries, delete_summary
from scraper import scrape_article
from gemini_service import summarize_text, summarize_youtube
from youtube_service import is_youtube_url, fetch_transcript
from instagram_service import is_instagram_url, fetch_instagram_transcript


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    print("✅ Database initialized")
    yield


app = FastAPI(
    title="Blog Summarizer",
    description="Paste a blog, YouTube, or Instagram URL — get a structured AI summary.",
    version="1.2.0",
    lifespan=lifespan,
)

# CORS — allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ──────────────────────────────────────────────
# Pages
# ──────────────────────────────────────────────

@app.get("/")
async def serve_homepage():
    """Serve the homepage."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/dashboard")
async def serve_dashboard():
    """Serve the dashboard page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))


# ──────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────

@app.post("/summarize", response_model=SummaryResponse)
async def summarize_url(request: SummarizeRequest):
    """
    Accept a blog, YouTube, or Instagram URL.
    Extract content → summarize with Gemini → store in DB.
    """
    url = request.url.strip()

    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")

    # ── Route: Instagram ──
    if is_instagram_url(url):
        try:
            transcript_data = fetch_instagram_transcript(url)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process Instagram reel: {str(e)}",
            )

        try:
            summary_data = summarize_youtube(transcript_data["text"])
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Summarization failed: {str(e)}",
            )

        result = {
            "title": summary_data["title"],
            "domain": transcript_data["domain"],
            "difficulty": summary_data["difficulty"],
            "summary": summary_data["summary"],
            "key_points": summary_data["key_points"],
            "takeaway": summary_data["takeaway"],
            "original_url": url,
            "source_type": "instagram",
            "tools_mentioned": summary_data.get("tools_mentioned", []),
        }

    # ── Route: YouTube ──
    elif is_youtube_url(url):
        try:
            transcript_data = fetch_transcript(url)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch transcript: {str(e)}",
            )

        try:
            summary_data = summarize_youtube(transcript_data["text"])
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Summarization failed: {str(e)}",
            )

        result = {
            "title": summary_data["title"],
            "domain": transcript_data["domain"],
            "difficulty": summary_data["difficulty"],
            "summary": summary_data["summary"],
            "key_points": summary_data["key_points"],
            "takeaway": summary_data["takeaway"],
            "original_url": url,
            "source_type": "youtube",
            "tools_mentioned": summary_data.get("tools_mentioned", []),
        }

    # ── Route: Blog ──
    else:
        try:
            article = scrape_article(url)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except TimeoutError as e:
            raise HTTPException(status_code=504, detail=str(e))
        except ConnectionError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to scrape article: {str(e)}",
            )

        try:
            summary_data = summarize_text(article["text"])
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Summarization failed: {str(e)}",
            )

        result = {
            "title": summary_data["title"],
            "domain": article["domain"],
            "difficulty": summary_data["difficulty"],
            "summary": summary_data["summary"],
            "key_points": summary_data["key_points"],
            "takeaway": summary_data["takeaway"],
            "original_url": url,
            "source_type": "blog",
            "tools_mentioned": [],
        }

    # ── Store in DB ──
    try:
        row_id = save_summary(result)
        result["id"] = row_id
    except Exception as e:
        if "UNIQUE" in str(e):
            result["id"] = None
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save summary: {str(e)}",
            )

    return result


@app.get("/summaries")
async def list_summaries():
    """Return all saved summaries."""
    try:
        summaries = get_all_summaries()
        return {"summaries": summaries, "count": len(summaries)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve summaries: {str(e)}",
        )


@app.delete("/summaries/{summary_id}")
async def remove_summary(summary_id: int):
    """Delete a summary by ID."""
    deleted = delete_summary(summary_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Summary not found.")
    return {"message": "Summary deleted.", "id": summary_id}
