# 🧠 AI Knowledge Base — Insta Reel & Blog Summarizer

Transform any content—Instagram Reels, YouTube Videos, or Blog Articles—into structured, actionable knowledge using Gemini 1.5 Pro.

![Dashboard Preview](blog_summarizer/frontend/dashboard.png) *(Note: Add actual screenshot after push)*

## ✨ Key Features

- **🚀 Universal Summarization**: Supports Instagram Reels, YouTube (Videos/Shorts), and any Blog Article/Webpage.
- **⏱️ Real-time Progress**: Live stepper showing scraping, transcription, and AI processing steps.
- **🗂️ Smart Knowledge Base**: 
    - AI-powered categorization (Web Dev, AI, ML, etc.).
    - Automated difficulty scoring (Beginner to Advanced).
    - Intelligent search across titles, summaries, and tools mentioned.
- **⭐ Personalization**:
    - Favorite/Bookmark your most important insights.
    - Manual Refinement: Edit AI summaries to add your own context.
- **📤 Export & Portability**:
    - One-click copy to clipboard.
    - Download as formatted Markdown for Notion/Obsidian.
- **🎨 Premium UI**: Dark mode, glassmorphism, smooth animations, and interactive stats.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python), SQLite, BeautifulSoup4, yt-dlp, Google Gemini API.
- **Frontend**: Vanilla JS (ES6+), CSS3 (Modern Design System), Lucide Icons.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- [Google Gemini API Key](https://aistudio.google.com/apikey)

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/hemish22/insta-reel-shorts-blogs-summariser-.git
cd insta-reel-shorts-blogs-summariser-

# Install dependencies
cd blog_summarizer/backend
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in `blog_summarizer/backend/`:
```bash
GEMINI_API_KEY=your_google_gemini_api_key
```

### 4. Run the App
```bash
# From blog_summarizer/backend
uvicorn main:app --reload
```
Visit **[http://localhost:8000](http://localhost:8000)** to start summarizing.

---

## 📁 Project Structure

```text
.
├── blog_summarizer/        # Main Application
│   ├── backend/            # FastAPI, Scrapers, YouTube/Insta logic
│   ├── frontend/           # HTML, CSS, JS (Dashboard & Home)
│   └── database.py         # SQLite schema & migrations
├── docs/                   # Project documentation
└── scripts/                # Utility scripts
```

## 📝 License
MIT License. Free for personal and commercial use.

---
*Built with ❤️ by [hemish22](https://github.com/hemish22)*
