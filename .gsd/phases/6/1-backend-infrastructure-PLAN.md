---
phase: 6
plan: 1
wave: 1
---

# Plan 1: Backend Infrastructure & AI Tagging

Add a new `category` column to the database and update the Gemini service to automatically categorize summaries.

## Tasks
1. **Add `category` column to DB**
   - Update `database.py` to include `category` in the schema.
   - Run a migration script to add the column and set a default.
2. **Update Gemini prompts**
   - Modify `gemini_service.py` to return a `category` tag (AI, Web Dev, ML, Cybersecurity, General).
   - Ensure the JSON parsing handles the new field.

## Verification
- Run `python backend/database.py` to verify schema update.
- Trigger a new summary and check the DB for the `category` value.
