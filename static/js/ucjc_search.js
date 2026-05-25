// =============================================================
//  ucjc_search.js — Core search library v1
//  Shared by schedule_search.js and user_search.js.
//  Exposes window.UcjcSearch = { normalize, buildIndex, search,
//                                 highlight, escHtml, debounce }
// =============================================================

(function (global) {
  'use strict';

  // ── Text normalization ──────────────────────────────────────────
  // Lowercase + strip diacritics so "Lógica" matches "logica"
  function normalize(str) {
    return String(str || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[̀-ͯ]/g, '');
  }

  // ── HTML escaping ───────────────────────────────────────────────
  function escHtml(s) {
    return String(s || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function escRe(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // ── Build search index ──────────────────────────────────────────
  // items     : Array<Object>
  // searchKeys: String[] — keys to concatenate for searching
  // Returns   : Array<{ item, token }>
  function buildIndex(items, searchKeys) {
    return items.map(function (item) {
      var parts = searchKeys.map(function (key) {
        var v = item[key];
        return Array.isArray(v) ? v.join(' ') : String(v || '');
      });
      return { item: item, token: normalize(parts.join(' ')) };
    });
  }

  // ── Search ──────────────────────────────────────────────────────
  // Returns items whose token matches ALL whitespace-split terms.
  function search(index, query, maxResults) {
    var q = normalize(query.trim());
    if (!q) return [];
    var terms = q.split(/\s+/).filter(Boolean);
    var results = [];
    for (var i = 0; i < index.length; i++) {
      var entry = index[i];
      var ok = true;
      for (var t = 0; t < terms.length; t++) {
        if (entry.token.indexOf(terms[t]) === -1) { ok = false; break; }
      }
      if (ok) {
        results.push(entry.item);
        if (maxResults && results.length >= maxResults) break;
      }
    }
    return results;
  }

  // ── Highlight ────────────────────────────────────────────────────
  // Wraps normalized matches in <mark class="ucjc-hl">
  // Works on the original (non-normalized) text.
  function highlight(text, query) {
    if (!query || !query.trim()) return escHtml(text);
    var out = escHtml(String(text || ''));
    var terms = normalize(query).split(/\s+/).filter(Boolean);
    // We apply on the normalized version to find positions, but since HTML
    // escaping doesn't affect latin chars we can apply regex on escaped text.
    terms.forEach(function (term) {
      out = out.replace(
        new RegExp('(' + escRe(term) + ')', 'gi'),
        '<mark class="ucjc-hl">$1</mark>'
      );
    });
    return out;
  }

  // ── Debounce ─────────────────────────────────────────────────────
  function debounce(fn, ms) {
    var timer;
    return function () {
      var args = arguments, ctx = this;
      clearTimeout(timer);
      timer = setTimeout(function () { fn.apply(ctx, args); }, ms || 300);
    };
  }

  // ── Row filter helper ─────────────────────────────────────────────
  // Hides table rows (tr[data-search]) that don't match query.
  // Returns count of visible rows.
  function filterRows(query, rowSelector) {
    var rows = document.querySelectorAll(rowSelector || 'tr[data-search]');
    var q    = normalize(query.trim());
    var terms = q ? q.split(/\s+/).filter(Boolean) : [];
    var count = 0;

    rows.forEach(function (row) {
      if (!terms.length) {
        row.style.display = '';
        count++;
        return;
      }
      var hay = normalize(row.dataset.search || row.textContent);
      var match = terms.every(function (t) { return hay.indexOf(t) !== -1; });
      row.style.display = match ? '' : 'none';
      if (match) count++;
    });
    return count;
  }

  // ── Export ────────────────────────────────────────────────────────
  global.UcjcSearch = {
    normalize:  normalize,
    escHtml:    escHtml,
    buildIndex: buildIndex,
    search:     search,
    highlight:  highlight,
    debounce:   debounce,
    filterRows: filterRows,
  };

})(window);
