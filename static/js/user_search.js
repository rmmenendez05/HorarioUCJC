// =============================================================
//  user_search.js — Barra de búsqueda para Gestión de Usuarios
//  Requiere ucjc_search.js (window.UcjcSearch).
//
//  Funcionalidad:
//    · Autocompletado con resultados agrupados por rol (Profesor / Alumno)
//    · Filtrado en tiempo real de las filas de la tabla
//    · Navegación por teclado (↑ ↓ Enter Escape)
//    · Debounce 300 ms, normalización de acentos/mayúsculas
// =============================================================

(function () {
  'use strict';

  var US = window.UcjcSearch;
  if (!US) { console.warn('user_search.js: UcjcSearch no disponible'); return; }

  // ── DOM refs ────────────────────────────────────────────────────
  var searchWrap  = document.getElementById('user-search-wrap');
  var inputEl     = document.getElementById('user-search-input');
  var clearBtn    = document.getElementById('user-search-clear');
  var dropdown    = document.getElementById('user-search-dropdown');
  var countBadge  = document.getElementById('user-search-count');

  if (!inputEl || !dropdown) return;

  // ── Data ────────────────────────────────────────────────────────
  var DATA = window.USER_SEARCH_DATA || [];
  var KEYS = ['name', 'email', 'area', 'asignaturas', 'titulacion', 'nivel', 'id'];
  var IDX  = US.buildIndex(DATA, KEYS);

  // ── State ───────────────────────────────────────────────────────
  var suggestions = [];
  var activeIdx   = -1;

  // ── Role display helpers ────────────────────────────────────────
  var ROL_LABEL = {
    PROFESOR: { text: 'Profesor', cls: 'bg-blue-900/50 border-blue-700/60 text-blue-300' },
    ALUMNO:   { text: 'Alumno',   cls: 'bg-green-900/50 border-green-700/60 text-green-300' },
    DECANO:   { text: 'Decano',   cls: 'bg-red-900/50 border-red-700/60 text-red-300' },
    IT:       { text: 'IT',       cls: 'bg-zinc-800 border-zinc-700 text-zinc-400' },
  };

  // ── Build dropdown HTML ─────────────────────────────────────────
  function renderDropdown(q) {
    var results = US.search(IDX, q, 10);
    suggestions = results;
    activeIdx   = -1;

    if (!results.length) {
      dropdown.innerHTML =
        '<div class="px-4 py-5 text-center text-xs text-zinc-600">Sin resultados para «' +
        US.escHtml(q) + '»</div>';
      openDropdown();
      return;
    }

    // Group by rol
    var groups = {};
    results.forEach(function (item) {
      if (!groups[item.rol]) groups[item.rol] = [];
      groups[item.rol].push(item);
    });

    var html = '';
    var globalIdx = 0;

    Object.keys(groups).forEach(function (rol) {
      var rInfo = ROL_LABEL[rol] || { text: rol, cls: 'bg-zinc-800 text-zinc-400 border-zinc-700' };
      html += '<div class="px-4 pt-3 pb-1 flex items-center gap-2">' +
        '<span class="text-[10px] font-bold uppercase tracking-widest ' +
        (rol === 'PROFESOR' ? 'text-blue-400' : rol === 'ALUMNO' ? 'text-green-400' : 'text-zinc-400') +
        '">' + US.escHtml(rInfo.text) + 's</span>' +
        '<div class="flex-1 h-px bg-zinc-800/80"></div>' +
        '</div>';

      groups[rol].forEach(function (item) {
        var i = globalIdx++;
        var initials = (item.name.trim().split(' ').slice(0, 2).map(function (w) { return w[0] || ''; }).join('') || item.email[0] || '?').toUpperCase();
        var meta = item.area
          ? '<span class="text-[10px] text-zinc-600 truncate">' + US.escHtml(item.area) + '</span>'
          : item.titulacion
          ? '<span class="text-[10px] text-zinc-600 truncate">' + US.escHtml(item.titulacion) + (item.nivel ? ' · ' + US.escHtml(item.nivel) : '') + '</span>'
          : '<span class="text-[10px] text-zinc-600 font-mono">ID ' + US.escHtml(item.id) + '</span>';

        html += '<div class="us-item flex items-center gap-3 px-4 py-2.5 cursor-pointer hover:bg-zinc-800/50 transition-colors" data-i="' + i + '" data-pk="' + item.pk + '">' +
          '<div class="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ' + rInfo.cls + '">' + US.escHtml(initials) + '</div>' +
          '<div class="flex-1 min-w-0">' +
            '<div class="text-sm text-zinc-200 truncate leading-snug">' + US.highlight(item.name || item.email, q) + '</div>' +
            meta +
          '</div>' +
          '<span class="shrink-0 text-[9px] px-1.5 py-0.5 rounded-full border ' + rInfo.cls + '">' + US.escHtml(rInfo.text) + '</span>' +
          '</div>';
      });
    });

    html += '<div class="h-1.5"></div>';
    dropdown.innerHTML = html;

    // Bind events
    dropdown.querySelectorAll('.us-item').forEach(function (el) {
      el.addEventListener('mouseenter', function () { setActive(parseInt(el.dataset.i)); });
      el.addEventListener('mousedown',  function (e) {
        e.preventDefault();
        selectItem(parseInt(el.dataset.i));
      });
    });

    openDropdown();
  }

  // ── Keyboard navigation ─────────────────────────────────────────
  function setActive(i) {
    dropdown.querySelectorAll('.us-item').forEach(function (el) {
      el.classList.remove('bg-zinc-800/70');
    });
    activeIdx = i;
    if (i >= 0) {
      var el = dropdown.querySelector('.us-item[data-i="' + i + '"]');
      if (el) { el.classList.add('bg-zinc-800/70'); el.scrollIntoView({ block: 'nearest' }); }
    }
  }

  function moveActive(dir) {
    var items = dropdown.querySelectorAll('.us-item');
    if (!items.length) return;
    var next = activeIdx + dir;
    if (next < 0) next = items.length - 1;
    if (next >= items.length) next = 0;
    setActive(next);
  }

  // ── Select item from dropdown ───────────────────────────────────
  function selectItem(i) {
    var item = suggestions[i];
    if (!item) return;
    closeDropdown();
    inputEl.value = item.name || item.email;
    applyFilter(inputEl.value);
    // Scroll + flash the matching row
    var row = document.querySelector('tr[data-uid="' + item.pk + '"]');
    if (row) {
      row.scrollIntoView({ behavior: 'smooth', block: 'center' });
      row.classList.add('us-flash');
      setTimeout(function () { row.classList.remove('us-flash'); }, 1800);
    }
    updateClearBtn();
  }

  // ── Table filter ────────────────────────────────────────────────
  function applyFilter(q) {
    var count = US.filterRows(q, 'tr[data-uid]');
    if (countBadge) {
      if (q.trim()) {
        countBadge.textContent = count + ' resultado' + (count !== 1 ? 's' : '');
        countBadge.classList.remove('hidden');
      } else {
        countBadge.classList.add('hidden');
      }
    }
  }

  // ── Dropdown open/close ─────────────────────────────────────────
  function openDropdown()  { dropdown.classList.remove('hidden'); }
  function closeDropdown() { dropdown.classList.add('hidden'); activeIdx = -1; }

  // ── Clear ───────────────────────────────────────────────────────
  function clearSearch() {
    inputEl.value = '';
    closeDropdown();
    applyFilter('');
    updateClearBtn();
    inputEl.focus();
  }

  function updateClearBtn() {
    if (!clearBtn) return;
    clearBtn.style.display = inputEl.value ? 'flex' : 'none';
  }

  // ── Debounced handler ────────────────────────────────────────────
  var _debouncedHandler = US.debounce(function (q) {
    applyFilter(q);
    if (q.trim().length >= 1) renderDropdown(q);
    else closeDropdown();
  }, 300);

  // ── Event listeners ─────────────────────────────────────────────
  inputEl.addEventListener('input', function () {
    updateClearBtn();
    _debouncedHandler(inputEl.value);
  });

  inputEl.addEventListener('keydown', function (e) {
    var isOpen = !dropdown.classList.contains('hidden');
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      isOpen ? moveActive(1) : (inputEl.value.trim() && renderDropdown(inputEl.value));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault(); moveActive(-1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIdx >= 0 && suggestions[activeIdx]) selectItem(activeIdx);
      else { closeDropdown(); applyFilter(inputEl.value); }
    } else if (e.key === 'Escape') {
      closeDropdown(); inputEl.blur();
    }
  });

  inputEl.addEventListener('focus', function () {
    var q = inputEl.value.trim();
    if (q.length >= 1) renderDropdown(q);
  });

  if (clearBtn) clearBtn.addEventListener('click', clearSearch);

  // Click outside → close
  document.addEventListener('click', function (e) {
    if (searchWrap && !searchWrap.contains(e.target)) closeDropdown();
  });

  // ── Flash animation CSS ─────────────────────────────────────────
  (function () {
    var s = document.createElement('style');
    s.textContent = [
      '@keyframes usFlash{0%,100%{background:transparent}25%,75%{background:rgba(220,38,38,.12)}}',
      '.us-flash{animation:usFlash 1.8s ease;}',
      '.ucjc-hl{background:rgba(220,38,38,.25);color:#fca5a5;border-radius:2px;font-style:normal;}',
    ].join('');
    document.head.appendChild(s);
  })();

})();
