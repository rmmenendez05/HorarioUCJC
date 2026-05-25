// =============================================================
//  schedule_search.js — Barra de búsqueda y filtros v2
//  Índice client-side desde window.SCHEDULE_DATA.
//  Requiere ucjc_search.js (window.UcjcSearch).
//  Expone window.reapplySearch para el hook de _reloadGrid.
// =============================================================

(function () {
  'use strict';

  var US = window.UcjcSearch;  // core library

  // ── Refs DOM ──────────────────────────────────────────────────
  var inputBox  = document.getElementById('search-input-box');
  var input     = document.getElementById('search-input');
  var dropdown  = document.getElementById('search-dropdown');

  if (!input || !dropdown) return;

  // ── Data island ───────────────────────────────────────────────
  var DATA = (window.SCHEDULE_DATA || { sesiones: [] }).sesiones;

  // ── Construir índice ──────────────────────────────────────────
  // Entidades únicas: { id, type, label, meta, pks[] }
  var _mapA = {}, _mapP = {}, _mapU = {};

  DATA.forEach(function (s) {
    // Asignatura
    var ka = 'a:' + s.pk_asig;
    if (!_mapA[ka]) _mapA[ka] = { id: ka, type: 'asignatura', label: s.asig, codigo: s.cod, semestre: s.sem, tipo_grupo: s.tg, pks: [] };
    _mapA[ka].pks.push(s.pk);

    // Profesor
    if (s.pr) {
      var kp = 'p:' + s.pr;
      if (!_mapP[kp]) _mapP[kp] = { id: kp, type: 'profesor', label: s.pr, pks: [] };
      _mapP[kp].pks.push(s.pk);
    }

    // Aula
    var ku = 'u:' + s.au;
    if (!_mapU[ku]) _mapU[ku] = { id: ku, type: 'aula', label: s.au, aula_tipo: s.at, pks: [] };
    _mapU[ku].pks.push(s.pk);
  });

  var IDX = {
    asignatura: Object.values(_mapA),
    profesor:   Object.values(_mapP),
    aula:       Object.values(_mapU),
  };

  // ── Estado ───────────────────────────────────────────────────
  var activeFilters  = [];   // [{ id, type, label, pks }]
  var suggestions    = [];   // lista plana de items en el dropdown
  var activeIdx      = -1;

  // ── Utilidades ────────────────────────────────────────────────
  var esc       = US.escHtml.bind(US);
  var normQuery = US.normalize.bind(US);

  function highlight(text, q) {
    if (!q) return esc(text);
    return esc(text).replace(
      new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'),
      '<span class="text-white font-semibold">$1</span>'
    );
  }

  // ── Búsqueda (accent-insensitive) ─────────────────────────────
  function doSearch(q) {
    q = q.trim();
    if (!q) return null;
    var nq = normQuery(q);
    function matchNorm(str) { return normQuery(str).indexOf(nq) !== -1; }
    return {
      asignatura: IDX.asignatura.filter(function (x) { return matchNorm(x.label) || matchNorm(x.codigo); }).slice(0, 5),
      profesor:   IDX.profesor.filter(function (x)   { return matchNorm(x.label); }).slice(0, 4),
      aula:       IDX.aula.filter(function (x)        { return matchNorm(x.label); }).slice(0, 3),
    };
  }

  // ── Dropdown ──────────────────────────────────────────────────
  var CAT_LABELS  = { asignatura: 'Asignaturas', profesor: 'Profesores', aula: 'Aulas' };
  var CAT_CLASSES = { asignatura: 'text-blue-400', profesor: 'text-violet-400', aula: 'text-amber-400' };

  function tipoIcon(tg) {
    if (tg === 'LABORATORIO') return '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/></svg>';
    if (tg === 'PRACTICAS')   return '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>';
    return '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>';
  }
  function profIcon() {
    return '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>';
  }
  function aulaIcon() {
    return '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>';
  }

  function renderDropdown(results, q) {
    suggestions = [];
    var cats = ['asignatura', 'profesor', 'aula'];
    var hasAny = cats.some(function (c) { return results[c].length > 0; });
    var html = '';

    if (!hasAny) {
      html = '<div class="px-4 py-6 text-center text-xs text-zinc-600">Sin resultados para «' + esc(q) + '»</div>';
    } else {
      cats.forEach(function (cat) {
        if (!results[cat].length) return;
        html += '<div class="px-4 pt-3 pb-1 flex items-center gap-2">' +
          '<span class="text-[10px] font-bold uppercase tracking-widest ' + CAT_CLASSES[cat] + '">' + CAT_LABELS[cat] + '</span>' +
          '<div class="flex-1 h-px bg-zinc-800"></div>' +
        '</div>';
        results[cat].forEach(function (item) {
          var i = suggestions.length;
          suggestions.push(item);
          var icon = cat === 'profesor' ? profIcon() : cat === 'aula' ? aulaIcon() : tipoIcon(item.tipo_grupo);
          var meta = '';
          if (cat === 'asignatura') meta = '<span class="shrink-0 text-[10px] px-1.5 py-0.5 rounded ' + (item.semestre === 1 ? 'bg-blue-900/50 text-blue-400' : 'bg-violet-900/50 text-violet-400') + '">S' + item.semestre + '</span>';
          if (cat === 'aula')       meta = '<span class="shrink-0 text-[10px] text-zinc-600">' + esc(item.aula_tipo) + '</span>';
          html += '<div class="suggestion px-4 py-2.5 flex items-center gap-3 cursor-pointer hover:bg-zinc-800/50 transition-colors" data-i="' + i + '">' +
            '<span class="text-zinc-600 shrink-0">' + icon + '</span>' +
            '<span class="flex-1 text-sm text-zinc-300 leading-snug truncate">' + highlight(item.label, q) + '</span>' +
            meta +
          '</div>';
        });
      });
      html += '<div class="h-2"></div>';
    }

    dropdown.innerHTML = html;
    dropdown.querySelectorAll('.suggestion').forEach(function (el) {
      el.addEventListener('mousedown', function (e) {
        e.preventDefault();
        addFilter(suggestions[parseInt(el.dataset.i)]);
      });
      el.addEventListener('mouseenter', function () {
        setActiveIdx(parseInt(el.dataset.i));
      });
    });

    activeIdx = -1;
    openDropdown();
  }

  // ── Navegación teclado ────────────────────────────────────────
  function setActiveIdx(i) {
    var els = dropdown.querySelectorAll('.suggestion');
    els.forEach(function (el) { el.classList.remove('bg-zinc-800/60'); });
    activeIdx = i;
    if (i >= 0 && i < els.length) {
      els[i].classList.add('bg-zinc-800/60');
      els[i].scrollIntoView({ block: 'nearest' });
    }
  }

  function moveActive(dir) {
    var els = dropdown.querySelectorAll('.suggestion');
    if (!els.length) return;
    var next = (activeIdx + dir + els.length) % els.length;
    setActiveIdx(next);
  }

  function confirmActive() {
    if (activeIdx >= 0 && suggestions[activeIdx]) addFilter(suggestions[activeIdx]);
  }

  // ── Dropdown visibility ───────────────────────────────────────
  function openDropdown()  { dropdown.classList.remove('hidden'); }
  function closeDropdown() { dropdown.classList.add('hidden'); activeIdx = -1; }

  // ── Gestión de filtros ────────────────────────────────────────
  function addFilter(item) {
    if (activeFilters.some(function (f) { return f.id === item.id; })) {
      clearInput(); return;
    }
    activeFilters.push(item);
    renderTags();
    applyFilters();
    clearInput();
  }

  function removeFilter(id) {
    activeFilters = activeFilters.filter(function (f) { return f.id !== id; });
    renderTags();
    applyFilters();
    updatePills();
  }

  function clearInput() {
    input.value = '';
    closeDropdown();
    input.focus();
  }

  // ── Quick filter pills ────────────────────────────────────────
  function addQuickFilter(key, label) {
    if (activeFilters.some(function (f) { return f.id === key; })) {
      removeFilter(key); return;
    }
    var pks;
    if (key.startsWith('sem:')) {
      var sem = parseInt(key.split(':')[1]);
      pks = DATA.filter(function (s) { return s.sem === sem; }).map(function (s) { return s.pk; });
    } else if (key.startsWith('tipo:')) {
      var tg = key.split(':')[1];
      pks = DATA.filter(function (s) { return s.tg === tg; }).map(function (s) { return s.pk; });
    } else {
      pks = [];
    }
    activeFilters.push({ id: key, type: 'quick', label: label, pks: pks });
    renderTags();
    applyFilters();
    updatePills();
  }

  // ── Tags ──────────────────────────────────────────────────────
  var TAG_CLS = {
    asignatura: 'bg-blue-900/50 border-blue-700/60 text-blue-300',
    profesor:   'bg-violet-900/50 border-violet-700/60 text-violet-300',
    aula:       'bg-amber-900/50 border-amber-700/60 text-amber-300',
    quick:      'bg-zinc-800 border-zinc-700 text-zinc-300',
  };

  function renderTags() {
    // Limpiar tags anteriores (hijos antes del input)
    inputBox.querySelectorAll('._sf-tag').forEach(function (t) { t.remove(); });

    activeFilters.forEach(function (f) {
      var cls = TAG_CLS[f.type] || TAG_CLS.quick;
      var tag = document.createElement('span');
      tag.className = '_sf-tag inline-flex items-center gap-1 pl-2 pr-1 py-0.5 rounded-full border text-xs font-medium leading-none ' + cls;
      tag.innerHTML = esc(f.label) +
        '<button class="_sf-tag-x ml-0.5 p-0.5 rounded-full opacity-50 hover:opacity-100 hover:bg-white/10 transition-opacity" data-id="' + esc(f.id) + '" title="Quitar filtro">' +
          '<svg class="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"/></svg>' +
        '</button>';
      tag.querySelector('._sf-tag-x').addEventListener('click', function () {
        removeFilter(f.id);
      });
      inputBox.insertBefore(tag, input);
    });

    // Placeholder dinámico
    input.placeholder = activeFilters.length ? '' : 'Buscar asignatura, profesor o aula…';
  }

  // ── Pills activas ─────────────────────────────────────────────
  function updatePills() {
    document.querySelectorAll('[data-qf]').forEach(function (btn) {
      var on = activeFilters.some(function (f) { return f.id === btn.dataset.qf; });
      btn.classList.toggle('_qf-on', on);
    });
  }

  // ── Aplicar filtros al grid ───────────────────────────────────
  function applyFilters() {
    var cards = document.querySelectorAll('.session-card[data-sesion-id]');

    if (!activeFilters.length) {
      cards.forEach(function (c) { c.classList.remove('_sf-dim'); });
      _removeNoResults();
      return;
    }

    var sets = activeFilters.map(function (f) { return new Set(f.pks || []); });

    cards.forEach(function (c) {
      var pk = parseInt(c.dataset.sesionId);
      var match = sets.every(function (s) { return s.has(pk); });
      c.classList.toggle('_sf-dim', !match);
    });

    // Mensaje sin resultados
    var visible = document.querySelectorAll('.session-card[data-sesion-id]:not(._sf-dim)').length;
    if (visible === 0) {
      _showNoResults();
    } else {
      _removeNoResults();
    }
  }

  function _showNoResults() {
    if (document.getElementById('_sf-nores')) return;
    var el = document.createElement('div');
    el.id = '_sf-nores';
    el.className = 'my-3 px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-xl text-xs text-zinc-500 text-center';
    el.textContent = 'Ninguna sesión coincide con los filtros activos.';
    var layout = document.getElementById('horario-layout');
    if (layout) layout.before(el);
  }

  function _removeNoResults() {
    var el = document.getElementById('_sf-nores');
    if (el) el.remove();
  }

  // Exponer para _reloadGrid
  window.reapplySearch = applyFilters;

  // ── CSS dinámico ──────────────────────────────────────────────
  (function () {
    var s = document.createElement('style');
    s.textContent = [
      '._sf-dim{opacity:.1;filter:grayscale(1);pointer-events:none;transition:opacity .18s,filter .18s;}',
      '._qf-on{background:rgba(220,38,38,.18)!important;border-color:rgba(220,38,38,.55)!important;color:#fca5a5!important;}',
    ].join('');
    document.head.appendChild(s);
  })();

  // ── Eventos input ─────────────────────────────────────────────
  var _debouncedSearch = US.debounce(function (q) {
    var res = doSearch(q);
    if (res) renderDropdown(res, q);
  }, 300);

  input.addEventListener('input', function () {
    var q = input.value.trim();
    if (!q) { closeDropdown(); return; }
    _debouncedSearch(q);
  });

  input.addEventListener('keydown', function (e) {
    var open = !dropdown.classList.contains('hidden');
    if (e.key === 'ArrowDown')  { e.preventDefault(); if (open) moveActive(1);  else if (input.value.trim()) input.dispatchEvent(new Event('input')); }
    else if (e.key === 'ArrowUp')   { e.preventDefault(); moveActive(-1); }
    else if (e.key === 'Enter')     { e.preventDefault(); confirmActive(); }
    else if (e.key === 'Escape')    { closeDropdown(); input.blur(); }
    else if (e.key === 'Backspace' && !input.value && activeFilters.length) {
      removeFilter(activeFilters[activeFilters.length - 1].id);
    }
  });

  input.addEventListener('focus', function () {
    var q = input.value.trim();
    if (q) { var res = doSearch(q); if (res) renderDropdown(res, q); }
  });

  // Clic en el wrap enfoca el input
  inputBox.addEventListener('click', function (e) {
    if (!e.target.closest('._sf-tag')) input.focus();
  });

  // Clic fuera cierra dropdown
  document.addEventListener('click', function (e) {
    var root = document.getElementById('schedule-search');
    if (root && !root.contains(e.target)) closeDropdown();
  });

  // ── Quick filter pills ────────────────────────────────────────
  document.querySelectorAll('[data-qf]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      addQuickFilter(btn.dataset.qf, btn.textContent.trim());
    });
  });

})();
