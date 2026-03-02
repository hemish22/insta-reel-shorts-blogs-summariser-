---
phase: 7
plan: 1
wave: 1
---

# Plan 1: Personalization (Favorites & Manual Edits)

Enable users to bookmark summaries and manually edit the AI-generated content.

## Tasks
1. **Database Schema Update**
   - Update `database.py`: Add `is_favorite` (INTEGER DEFAULT 0) and `summary_edited` (TEXT) columns.
   - Run migration in `init_db`.
2. **Backend API Endpoints**
   - Update `main.py`: 
     - `POST /summaries/{id}/favorite`: Toggle favorite status.
     - `PUT /summaries/{id}/edit`: Update the summary text.
3. **Frontend UI - Star & Edit**
   - Update `script.js` & `dashboard.html`:
     - Add star icon and "Edit" button to history cards.
     - Implement `toggleFavorite(id)` and `editSummary(id)` functions.
     - Create a simple inline edit mode or modal for editing.

## Verification
- Star a summary, refresh, and ensure it stays starred.
- Edit a summary, save, and ensure the updated text persists in the DB.
