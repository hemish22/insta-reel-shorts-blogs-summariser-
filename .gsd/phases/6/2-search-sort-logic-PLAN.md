---
phase: 6
plan: 2
wave: 2
---

# Plan 2: Advanced Search & Sorting UI

Implement the core search/sort logic and add the necessary UI components to the dashboard.

## Tasks
1. **Add Sort Dropdown & Filter UI**
   - Modify `dashboard.html` to add the sort menu and domain filter chips container.
2. **Implement Smart Search**
   - Update `script.js` to search through summary, key points, and tools.
3. **Implement Sorting Logic**
   - Add `sortSummaries` function to `script.js` for Date, Title, Difficulty, and Category.
4. **Interactive Stats**
   - Bind click events to stats cards to filter the list (e.g., clicking "YouTube" filter for YouTube sources).

## Verification
- Open dashboard, verify Sort dropdown is functional.
- Perform a search for a tool name (e.g., 'Python') and ensure it finds relevant items.
