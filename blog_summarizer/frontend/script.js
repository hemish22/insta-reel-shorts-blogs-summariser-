/**
 * Blog Summarizer — Frontend Logic
 */

const API_BASE = '';

// In-memory state for dashboard
let allSummaries = [];
let filteredSummaries = [];
let activeFilter = null;
let allExpanded = false;

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

    if (!url.match(/^https?:\/\/.+\..+/) && !url.match(/^.+\..+/)) {
        showStatus(status, 'Please enter a valid URL (e.g., https://example.com/article)', 'error');
        return;
    }

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
    if (!section) return;

    try {
        const response = await fetch(`${API_BASE}/summaries`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to load summaries.');
        }

        allSummaries = data.summaries || [];
        filteredSummaries = [...allSummaries];

        updateStats(allSummaries);
        buildFilterChips(allSummaries);
        renderDashboardList(filteredSummaries);

        // Show search bar if there are summaries
        const searchBar = document.getElementById('search-bar');
        if (searchBar) searchBar.style.display = allSummaries.length > 0 ? 'block' : 'none';

        // Setup search input
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(handleSearch, 200));
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
// Stats
// ──────────────────────────────────────────────

function updateStats(summaries) {
    const totalEl = document.getElementById('total-count');
    const domainsEl = document.getElementById('domains-count');
    const latestEl = document.getElementById('latest-date');

    if (totalEl) totalEl.textContent = summaries.length;
    if (domainsEl) {
        const uniqueDomains = new Set(summaries.map(s => s.domain));
        domainsEl.textContent = uniqueDomains.size;
    }
    if (latestEl && summaries.length > 0) {
        const date = new Date(summaries[0].created_at);
        latestEl.textContent = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } else if (latestEl) {
        latestEl.textContent = '—';
    }
}

// ──────────────────────────────────────────────
// Filter Chips (by domain)
// ──────────────────────────────────────────────

function buildFilterChips(summaries) {
    const container = document.getElementById('filter-chips');
    if (!container) return;

    const domains = [...new Set(summaries.map(s => s.domain))].sort();
    if (domains.length <= 1) {
        container.innerHTML = '';
        return;
    }

    container.innerHTML = domains.map(domain => `
        <button class="filter-chip" data-domain="${escapeHtml(domain)}" onclick="toggleFilter('${escapeHtml(domain)}')">
            🌐 ${escapeHtml(domain)}
        </button>
    `).join('');
}

function toggleFilter(domain) {
    if (activeFilter === domain) {
        activeFilter = null;
    } else {
        activeFilter = domain;
    }

    // Update chip styles
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.classList.toggle('filter-chip--active', chip.dataset.domain === activeFilter);
    });

    applyFilters();
}

// ──────────────────────────────────────────────
// Search
// ──────────────────────────────────────────────

function handleSearch() {
    applyFilters();
    const clearBtn = document.getElementById('clear-search');
    const input = document.getElementById('search-input');
    if (clearBtn) clearBtn.style.display = input.value.trim() ? 'block' : 'none';
}

function clearSearch() {
    const input = document.getElementById('search-input');
    if (input) input.value = '';
    document.getElementById('clear-search').style.display = 'none';
    applyFilters();
}

function applyFilters() {
    const searchInput = document.getElementById('search-input');
    const query = searchInput ? searchInput.value.trim().toLowerCase() : '';

    filteredSummaries = allSummaries.filter(s => {
        // Domain filter
        if (activeFilter && s.domain !== activeFilter) return false;

        // Search filter
        if (query) {
            const searchableText = [
                s.title, s.domain, s.summary, s.takeaway, s.difficulty,
                ...(s.key_points || [])
            ].join(' ').toLowerCase();
            return searchableText.includes(query);
        }

        return true;
    });

    renderDashboardList(filteredSummaries);
}

// ──────────────────────────────────────────────
// Render Dashboard List (Compact Cards)
// ──────────────────────────────────────────────

function renderDashboardList(summaries) {
    const section = document.getElementById('summaries-section');
    const resultsInfo = document.getElementById('results-info');
    const resultsCount = document.getElementById('results-count');

    if (!section) return;

    if (allSummaries.length === 0) {
        section.innerHTML = `
            <div class="empty-state">
                <div class="empty-state__icon">📭</div>
                <div class="empty-state__text">No summaries yet</div>
                <div class="empty-state__hint">Go to the homepage and paste a blog URL to get started.</div>
            </div>
        `;
        if (resultsInfo) resultsInfo.style.display = 'none';
        return;
    }

    if (summaries.length === 0) {
        section.innerHTML = `<div class="no-results">No summaries match your search.</div>`;
        if (resultsInfo) resultsInfo.style.display = 'none';
        return;
    }

    if (resultsInfo) {
        resultsInfo.style.display = 'flex';
        if (resultsCount) {
            resultsCount.textContent = `${summaries.length} ${summaries.length === 1 ? 'summary' : 'summaries'}`;
        }
    }

    section.innerHTML = '';
    summaries.forEach((summary, index) => {
        section.appendChild(createHistoryCard(summary, index));
    });
}

// ──────────────────────────────────────────────
// History Card (Compact with Expand)
// ──────────────────────────────────────────────

function createHistoryCard(data, index) {
    const card = document.createElement('div');
    card.className = 'history-card';
    card.id = `card-${data.id}`;
    card.style.animationDelay = `${index * 0.05}s`;

    const difficultyClass = `badge--${(data.difficulty || 'intermediate').toLowerCase()}`;

    const date = data.created_at
        ? new Date(data.created_at).toLocaleDateString('en-US', {
            year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        })
        : '';

    const keyPointsHtml = (data.key_points || [])
        .map(point => `<li>${escapeHtml(point)}</li>`)
        .join('');

    card.innerHTML = `
        <div class="history-card__preview" onclick="toggleCard(${data.id})">
            <div class="history-card__info">
                <div class="history-card__title">${escapeHtml(data.title)}</div>
                <div class="history-card__meta-row">
                    <span class="history-card__meta-item"><span>🌐</span> ${escapeHtml(data.domain)}</span>
                    <span class="history-card__meta-item"><span>📅</span> ${date}</span>
                    <span class="badge ${difficultyClass}" style="font-size: 0.7rem; padding: 2px 8px;">${escapeHtml(data.difficulty)}</span>
                </div>
            </div>
            <div class="history-card__actions">
                <button class="btn-icon" onclick="event.stopPropagation(); deleteSummary(${data.id})" title="Delete">🗑️</button>
                <button class="history-card__expand" id="expand-btn-${data.id}">▼</button>
            </div>
        </div>
        <div class="history-card__detail" id="detail-${data.id}">
            <div class="history-card__detail-inner">
                <div class="detail-grid">
                    <div class="detail-section detail-section--full">
                        <div class="detail-label">Summary</div>
                        <p class="detail-text">${escapeHtml(data.summary)}</p>
                    </div>
                    <div class="detail-section detail-section--full">
                        <div class="detail-label">Key Points</div>
                        <ul class="key-points">${keyPointsHtml}</ul>
                    </div>
                    <div class="detail-section detail-section--full">
                        <div class="detail-label">Takeaway</div>
                        <div class="takeaway-box">${escapeHtml(data.takeaway)}</div>
                    </div>
                </div>
                <div class="detail-footer">
                    <a href="${escapeHtml(data.original_url)}" target="_blank" rel="noopener noreferrer" class="original-link">
                        🔗 Read original article →
                    </a>
                    <span class="history-card__meta-item" style="font-size: 0.75rem;"><span>📅</span> ${date}</span>
                </div>
            </div>
        </div>
    `;

    return card;
}

// ──────────────────────────────────────────────
// Expand / Collapse
// ──────────────────────────────────────────────

function toggleCard(id) {
    const detail = document.getElementById(`detail-${id}`);
    const expandBtn = document.getElementById(`expand-btn-${id}`);

    if (!detail) return;

    const isOpen = detail.classList.contains('history-card__detail--open');
    detail.classList.toggle('history-card__detail--open', !isOpen);
    if (expandBtn) expandBtn.classList.toggle('history-card__expand--open', !isOpen);
}

function toggleExpandAll() {
    allExpanded = !allExpanded;
    const btn = document.getElementById('expand-all-btn');
    if (btn) btn.textContent = allExpanded ? 'Collapse All' : 'Expand All';

    document.querySelectorAll('.history-card__detail').forEach(detail => {
        detail.classList.toggle('history-card__detail--open', allExpanded);
    });
    document.querySelectorAll('.history-card__expand').forEach(btn => {
        btn.classList.toggle('history-card__expand--open', allExpanded);
    });
}

// ──────────────────────────────────────────────
// Delete
// ──────────────────────────────────────────────

async function deleteSummary(id) {
    if (!confirm('Delete this summary?')) return;

    try {
        const response = await fetch(`${API_BASE}/summaries/${id}`, { method: 'DELETE' });
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Failed to delete.');
        }

        // Remove from local state
        allSummaries = allSummaries.filter(s => s.id !== id);
        filteredSummaries = filteredSummaries.filter(s => s.id !== id);

        // Animate out
        const card = document.getElementById(`card-${id}`);
        if (card) {
            card.style.opacity = '0';
            card.style.transform = 'translateX(-20px)';
            card.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                card.remove();
                updateStats(allSummaries);
                buildFilterChips(allSummaries);

                if (allSummaries.length === 0) {
                    renderDashboardList([]);
                    document.getElementById('search-bar').style.display = 'none';
                }

                const resultsCount = document.getElementById('results-count');
                if (resultsCount) {
                    resultsCount.textContent = `${filteredSummaries.length} ${filteredSummaries.length === 1 ? 'summary' : 'summaries'}`;
                }
            }, 300);
        }

        showToast('Summary deleted');

    } catch (err) {
        showToast(`Error: ${err.message}`);
    }
}

// ──────────────────────────────────────────────
// Homepage: Render Summary Card (unchanged)
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

function debounce(fn, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

function showToast(message) {
    let toast = document.querySelector('.toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('toast--visible');
    setTimeout(() => toast.classList.remove('toast--visible'), 2500);
}

// Allow Enter key to submit on homepage
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('url-input');
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') submitUrl();
        });
    }
});
