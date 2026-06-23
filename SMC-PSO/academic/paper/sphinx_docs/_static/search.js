/*
============================================================================
LUNR.JS SEARCH UI - MODERN SEARCH INTERFACE FOR SPHINX DOCUMENTATION
============================================================================
Purpose: Client-side full-text search with modal overlay and keyboard shortcuts
Features: Ctrl+K to open, fuzzy matching, instant results, keyboard navigation
Performance: <200ms search latency for 821 documents
============================================================================
*/

(function() {
  'use strict';

  // -------------------------------------------------------------------------
  // STATE MANAGEMENT
  // -------------------------------------------------------------------------

  let searchIndex = null;          // Lunr.js index object
  let searchDocs = null;            // Document metadata
  let searchModal = null;           // Modal overlay DOM element
  let searchInput = null;           // Input field DOM element
  let searchResults = null;         // Results container DOM element
  let isIndexLoaded = false;        // Prevent double-loading
  let selectedResultIndex = -1;    // For keyboard navigation

  // -------------------------------------------------------------------------
  // INITIALIZATION (runs on page load)
  // -------------------------------------------------------------------------

  function init() {
    // Create modal HTML structure
    createSearchModal();

    // Bind keyboard shortcuts
    document.addEventListener('keydown', handleGlobalKeydown);

    // Click outside modal to close
    searchModal.addEventListener('click', function(e) {
      if (e.target === searchModal) {
        closeSearchModal();
      }
    });

    // Load search index asynchronously
    loadSearchIndex();
  }

  // -------------------------------------------------------------------------
  // KEYBOARD SHORTCUTS
  // -------------------------------------------------------------------------

  function handleGlobalKeydown(e) {
    // Ctrl+K or Cmd+K to open search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      openSearchModal();
      return;
    }

    // ESC to close (if modal is open)
    if (e.key === 'Escape' && searchModal.classList.contains('active')) {
      e.preventDefault();
      closeSearchModal();
      return;
    }

    // Arrow keys for result navigation (if modal is open and has results)
    if (searchModal.classList.contains('active') && searchResults.children.length > 1) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        navigateResults(1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        navigateResults(-1);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        activateSelectedResult();
      }
    }
  }

  // -------------------------------------------------------------------------
  // SEARCH INDEX LOADING
  // -------------------------------------------------------------------------

  function loadSearchIndex() {
    if (isIndexLoaded) return;

    console.log('[SEARCH] Loading search index...');

    // Try to load from _static/searchindex.json
    fetch(DOCUMENTATION_OPTIONS.URL_ROOT + '_static/searchindex.json')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        // Store documents for later retrieval
        searchDocs = {};
        data.docs.forEach(doc => {
          searchDocs[doc.id] = doc;
        });

        // Build Lunr.js index
        searchIndex = lunr(function() {
          this.ref('id');
          this.field('title', { boost: 10 });
          this.field('headings', { boost: 5 });
          this.field('body');

          // Add documents to index
          data.docs.forEach(doc => {
            this.add(doc);
          });
        });

        isIndexLoaded = true;
        console.log(`[SEARCH] Index loaded: ${Object.keys(searchDocs).length} documents`);
      })
      .catch(error => {
        console.error('[SEARCH] Failed to load search index:', error);
        showError('Search index unavailable. Please try refreshing the page.');
      });
  }

  // -------------------------------------------------------------------------
  // MODAL UI CREATION
  // -------------------------------------------------------------------------

  function createSearchModal() {
    const modalHTML = `
      <div id="search-modal" class="search-modal" role="dialog" aria-modal="true" aria-labelledby="search-title">
        <div class="search-modal-content">
          <div class="search-header">
            <label for="search-input" id="search-title" class="sr-only">Search documentation</label>
            <input
              type="text"
              id="search-input"
              class="search-input"
              placeholder="Search 821 documentation files... (Ctrl+K)"
              autocomplete="off"
              aria-label="Search documentation"
            />
            <button class="search-close" aria-label="Close search">[X]</button>
          </div>

          <div id="search-results" class="search-results" role="listbox" aria-label="Search results">
            <div class="search-hint">
              Type to search across all documentation
            </div>
          </div>

          <div class="search-footer">
            <div class="search-shortcuts">
              <kbd>ESC</kbd> to close
              <kbd>↑</kbd><kbd>↓</kbd> to navigate
              <kbd>Enter</kbd> to select
            </div>
            <span class="search-stats" id="search-stats"></span>
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Cache DOM references
    searchModal = document.getElementById('search-modal');
    searchInput = document.getElementById('search-input');
    searchResults = document.getElementById('search-results');

    // Bind search input event
    searchInput.addEventListener('input', debounce(handleSearch, 200));

    // Bind close button
    document.querySelector('.search-close').addEventListener('click', closeSearchModal);
  }

  // -------------------------------------------------------------------------
  // SEARCH EXECUTION
  // -------------------------------------------------------------------------

  function handleSearch(e) {
    const query = e.target.value.trim();

    // Clear results if query is empty
    if (query.length === 0) {
      searchResults.innerHTML = '<div class="search-hint">Type to search...</div>';
      selectedResultIndex = -1;
      updateStats('');
      return;
    }

    // Require at least 2 characters
    if (query.length < 2) {
      searchResults.innerHTML = '<div class="search-hint">Type at least 2 characters...</div>';
      updateStats('');
      return;
    }

    // Check if index is loaded
    if (!isIndexLoaded) {
      searchResults.innerHTML = '<div class="search-loading">Loading search index...</div>';
      return;
    }

    // Execute search
    const startTime = performance.now();

    try {
      // Build Lunr query with wildcards and fuzzy matching
      const results = searchIndex.search(query + '* ' + query + '~1');

      const endTime = performance.now();
      const searchTime = (endTime - startTime).toFixed(0);

      // Display results
      displayResults(results, query, searchTime);

    } catch (error) {
      console.error('[SEARCH] Query error:', error);
      searchResults.innerHTML = '<div class="search-error">Invalid search query. Try different keywords.</div>';
    }
  }

  // -------------------------------------------------------------------------
  // RESULTS DISPLAY
  // -------------------------------------------------------------------------

  function displayResults(results, query, searchTime) {
    selectedResultIndex = -1;

    // Update stats
    updateStats(`${results.length} results in ${searchTime}ms`);

    // No results
    if (results.length === 0) {
      searchResults.innerHTML = `
        <div class="search-no-results">
          <p>No results found for "${escapeHTML(query)}"</p>
          <p class="search-hint">Try different keywords or check spelling</p>
        </div>
      `;
      return;
    }

    // Limit to top 50 results
    const topResults = results.slice(0, 50);

    // Render results
    const resultsHTML = topResults.map((result, index) => {
      const doc = searchDocs[result.ref];
      if (!doc) return '';

      return `
        <a href="${escapeHTML(doc.url)}" class="search-result-item" role="option" data-index="${index}">
          <div class="search-result-title">
            ${highlightMatch(doc.title, query) || 'Untitled'}
          </div>
          <div class="search-result-snippet">
            ${highlightMatch(doc.body.substring(0, 200), query)}...
          </div>
          <div class="search-result-meta">
            ${escapeHTML(doc.url)}
          </div>
        </a>
      `;
    }).join('');

    searchResults.innerHTML = resultsHTML;
  }

  // -------------------------------------------------------------------------
  // KEYBOARD NAVIGATION
  // -------------------------------------------------------------------------

  function navigateResults(direction) {
    const resultItems = searchResults.querySelectorAll('.search-result-item');
    if (resultItems.length === 0) return;

    // Remove previous selection
    if (selectedResultIndex >= 0 && selectedResultIndex < resultItems.length) {
      resultItems[selectedResultIndex].classList.remove('selected');
    }

    // Calculate new index
    selectedResultIndex += direction;

    // Wrap around
    if (selectedResultIndex < 0) {
      selectedResultIndex = resultItems.length - 1;
    } else if (selectedResultIndex >= resultItems.length) {
      selectedResultIndex = 0;
    }

    // Add new selection
    const selectedItem = resultItems[selectedResultIndex];
    selectedItem.classList.add('selected');

    // Scroll into view
    selectedItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }

  function activateSelectedResult() {
    const resultItems = searchResults.querySelectorAll('.search-result-item');
    if (selectedResultIndex >= 0 && selectedResultIndex < resultItems.length) {
      resultItems[selectedResultIndex].click();
    }
  }

  // -------------------------------------------------------------------------
  // MODAL CONTROLS
  // -------------------------------------------------------------------------

  function openSearchModal() {
    searchModal.classList.add('active');
    searchInput.focus();
    document.body.style.overflow = 'hidden';  // Prevent background scrolling
  }

  function closeSearchModal() {
    searchModal.classList.remove('active');
    searchInput.value = '';
    searchResults.innerHTML = '<div class="search-hint">Type to search...</div>';
    selectedResultIndex = -1;
    updateStats('');
    document.body.style.overflow = '';  // Restore scrolling
  }

  // -------------------------------------------------------------------------
  // UTILITY FUNCTIONS
  // -------------------------------------------------------------------------

  function updateStats(text) {
    const statsEl = document.getElementById('search-stats');
    if (statsEl) {
      statsEl.textContent = text;
    }
  }

  function escapeHTML(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function highlightMatch(text, query) {
    if (!text) return '';

    // Escape HTML first
    text = escapeHTML(text);

    // Highlight query terms
    const queryTerms = query.split(/\s+/).filter(t => t.length > 0);
    queryTerms.forEach(term => {
      const regex = new RegExp(`(${escapeRegex(term)})`, 'gi');
      text = text.replace(regex, '<mark>$1</mark>');
    });

    return text;
  }

  function escapeRegex(text) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function debounce(func, wait) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }

  function showError(message) {
    searchResults.innerHTML = `<div class="search-error">${escapeHTML(message)}</div>`;
  }

  // -------------------------------------------------------------------------
  // AUTO-INITIALIZE
  // -------------------------------------------------------------------------

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
