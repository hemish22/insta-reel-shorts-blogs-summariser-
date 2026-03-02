/**
 * Blog Summarizer — Frontend Logic
 */

const API_BASE = '';

// ──────────────────────────────────────────────
// Homepage: Submit URL
// ──────────────────────────────────────────────

async function submitUrl() {
    const input = document.getElementById('url-input');
    const btn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const spinner = document.getElementById('btn-spinner');
    const status = document.getElementById('status');
    const resultSection = document.getElementById('result-section');

    const url = input.value.trim();

    if (!url) {
        showStatus(status, 'Please enter a blog URL.', 'error');
        input.focus();
        return;
    }

    // Basic URL validation
    if (!url.match(/^https?:\/\/.+\..+/) && !url.match(/^.+\..+/)) {
        showStatus(status, 'Please enter a valid URL (e.g., https://example.com/article)', 'error');
        return;
    }

    // Set loading state
    btn.disabled = true;
    btnText.textContent = 'Summarizing...';
    spinner.classList.add('spinner--active');
    showStatus(status, '⏳ Scraping article and generating summary... This may take a few seconds.', 'loading');
    resultSection.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/summarize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Something went wrong.');
        }

        // Show success
        showStatus(status, '✅ Summary generated successfully!', 'success');
        renderSummaryCard(resultSection, data);
        resultSection.style.display = 'block';

    } catch (err) {
        showStatus(status, `❌ ${err.message}`, 'error');
    } finally {
        btn.disabled = false;
        btnText.textContent = 'Summarize';
        spinner.classList.remove('spinner--active');
    }
}

// ──────────────────────────────────────────────
// Dashboard: Load All Summaries
// ──────────────────────────────────────────────

async function loadSummaries() {
    const section = document.getElementById('summaries-section');
    const totalEl = document.getElementById('total-count');
    const domainsEl = document.getElementById('domains-count');
    const latestEl = document.getElementById('latest-date');

    if (!section) return;

    try {
        const response = await fetch(`${API_BASE}/summaries`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to load summaries.');
        }

        const summaries = data.summaries || [];

        // Update stats
        if (totalEl) totalEl.textContent = summaries.length;
        if (domainsEl) {
            const uniqueDomains = new Set(summaries.map(s => s.domain));
            domainsEl.textContent = uniqueDomains.size;
        }
        if (latestEl && summaries.length > 0) {
            const date = new Date(summaries[0].created_at);
            latestEl.textContent = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }

        // Render summaries or empty state
        if (summaries.length === 0) {
            section.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state__icon">📭</div>
                    <div class="empty-state__text">No summaries yet</div>
                    <div class="empty-state__hint">Go to the homepage and paste a blog URL to get started.</div>
                </div>
            `;
        } else {
            section.innerHTML = '';
            summaries.forEach(summary => renderSummaryCard(section, summary));
        }

    } catch (err) {
        section.innerHTML = `
            <div class="status status--visible status--error">
                ❌ ${err.message}
            </div>
        `;
    }
}

// ──────────────────────────────────────────────
// Render a Summary Card
// ──────────────────────────────────────────────

function renderSummaryCard(container, data) {
    const difficultyClass = `badge--${(data.difficulty || 'intermediate').toLowerCase()}`;

    const keyPointsHtml = (data.key_points || [])
        .map(point => `<li>${escapeHtml(point)}</li>`)
        .join('');

    const dateHtml = data.created_at
        ? `<div class="summary-card__date">📅 ${new Date(data.created_at).toLocaleString()}</div>`
        : '';

    const card = document.createElement('div');
    card.className = 'summary-card';
    card.innerHTML = `
        <div class="summary-card__header">
            <h2 class="summary-card__title">${escapeHtml(data.title)}</h2>
            <div class="summary-card__meta">
                <span class="badge badge--domain">${escapeHtml(data.domain)}</span>
                <span class="badge ${difficultyClass}">${escapeHtml(data.difficulty)}</span>
            </div>
        </div>

        <div class="summary-card__section">
            <div class="summary-card__label">Summary</div>
            <p class="summary-card__text">${escapeHtml(data.summary)}</p>
        </div>

        <div class="summary-card__section">
            <div class="summary-card__label">Key Points</div>
            <ul class="key-points">${keyPointsHtml}</ul>
        </div>

        <div class="summary-card__section">
            <div class="summary-card__label">Takeaway</div>
            <div class="takeaway-box">${escapeHtml(data.takeaway)}</div>
        </div>

        <a href="${escapeHtml(data.original_url)}" target="_blank" rel="noopener noreferrer" class="original-link">
            🔗 Read original article →
        </a>
        ${dateHtml}
    `;

    container.appendChild(card);
}

// ──────────────────────────────────────────────
// Utilities
// ──────────────────────────────────────────────

function showStatus(el, message, type) {
    if (!el) return;
    el.textContent = message;
    el.className = `status status--visible status--${type}`;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Allow Enter key to submit
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('url-input');
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') submitUrl();
        });
    }
});
