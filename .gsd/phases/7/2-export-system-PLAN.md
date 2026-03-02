---
phase: 7
plan: 2
wave: 2
---

# Plan 2: Export System

Provide options to export summaries as Markdown or copy content to the clipboard.

## Tasks
1. **Frontend Export Logic**
   - Implement `exportAsMarkdown(id)`: Generate a formatted MD string (Title, Summary, Points, Takeaway).
   - Implement `copyToClipboard(id)`: Copy the summary content using the Clipboard API.
2. **Export UI**
   - Add an "Export" dropdown menu to `history-card` with "Copy to Clipboard" and "Download .md" options.
   - Use Lucide icons (copy, download).

## Verification
- Click "Download .md" and verify a `.md` file with correct content is downloaded.
- Click "Copy" and verify the terminal/editor can paste the summary.
