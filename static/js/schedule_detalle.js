// =============================================================
//  schedule_detalle.js — Drag-and-Drop v2
//  Arquitectura de un solo punto de drop (td[data-franja-id]).
//  Los .drop-zone son sólo decorativos; los eventos burbujean
//  al td sin necesidad de listeners duplicados.
// =============================================================

// ── CSRF / utilidades ─────────────────────────────────────────

function _getCsrf() {
  var m = document.querySelector('meta[name="csrf-token"]');
  if (m) return m.content;
  var i = document.querySelector('[name=csrfmiddlewaretoken]');
  return i ? i.value : '';
}

function _dndToast(msg, ok) {
  if (window.toast) window.toast(msg, ok ? 'success' : 'error');
}

var ERROR_MSGS = {
  'Conflicto de profesor: ya tiene clase en esa franja.':  'El profesor ya tiene otra clase en esa franja.',
  'Conflicto de aula: ya está ocupada en esa franja.':     'El aula ya está ocupada en esa franja.',
  'Solo se pueden editar sesiones en estado Borrador.':    'El horario no está en estado Borrador.',
  'franja_id requerido.':                                  'No se recibió la franja de destino.',
  'Método no permitido.':                                  'Acción no permitida.',
};
function _tradError(msg) { return ERROR_MSGS[msg] || msg || 'No se pudo completar la operación.'; }

// ── Estilos globales (inyectados una sola vez) ─────────────────

(function () {
  if (document.getElementById('_dnd-styles')) return;
  var s = document.createElement('style');
  s.id = '_dnd-styles';
  s.textContent = [
    '@keyframes _dndPulse{',
      'from{border-color:rgba(34,197,94,.35);background:rgba(20,83,45,.12)}',
      'to  {border-color:rgba(34,197,94,.85);background:rgba(20,83,45,.35)}',
    '}',
    '@keyframes _dndShake{',
      '0%,100%{transform:translateX(0)}',
      '20%,60%{transform:translateX(-6px)}',
      '40%,80%{transform:translateX(6px)}',
    '}',
    '._dnd-shake{animation:_dndShake 340ms ease-in-out!important;}',
    // Mientras hay drag activo: suprimir hover visual del drop-zone decorativo
    // y fijar el cursor en toda la página
    'body._dnd-active .drop-zone{pointer-events:none!important;border-color:transparent!important;}',
    'body._dnd-active{cursor:grabbing!important;}',
    'body._dnd-active *{cursor:grabbing!important;}',
  ].join('');
  document.head.appendChild(s);
})();

// ── Estado central del drag ────────────────────────────────────

var DnD = {
  active:         false,
  card:           null,     // .session-card en arrastre
  sesionId:       null,
  conflictos:     {},       // franjaId(int) → razon(str)
  fetchDone:      false,
  hoveredTd:      null,
};

// ── Fábrica de overlays ────────────────────────────────────────

var _WARN_PATH = 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z';

function _makeDim() {
  var d = document.createElement('div');
  d.className = '_dnd-ov _dnd-dim';
  d.style.cssText =
    'position:absolute;inset:0;z-index:20;pointer-events:none;' +
    'background:rgba(0,0,0,0.58);border-radius:inherit;';
  return d;
}

function _makeConflict(razon) {
  var d = document.createElement('div');
  d.className = '_dnd-ov _dnd-conflict';
  d.style.cssText =
    'position:absolute;inset:0;z-index:20;pointer-events:none;' +
    'background:rgba(113,47,12,0.82);border:2px solid rgba(217,119,6,0.85);' +
    'border-radius:10px;display:flex;flex-direction:column;' +
    'align-items:center;justify-content:center;gap:7px;padding:8px 10px;' +
    'backdrop-filter:blur(3px);';
  d.innerHTML =
    '<svg style="width:26px;height:26px;flex-shrink:0" fill="none" stroke="#fbbf24" stroke-width="2" viewBox="0 0 24 24">' +
      '<path stroke-linecap="round" stroke-linejoin="round" d="' + _WARN_PATH + '"/>' +
    '</svg>' +
    '<span style="font-size:10px;color:#fde68a;font-weight:600;text-align:center;' +
      'line-height:1.35;word-break:break-word;max-width:100%;">' + razon + '</span>';
  return d;
}

function _makeHover() {
  var d = document.createElement('div');
  d.className = '_dnd-ov _dnd-hover';
  d.style.cssText =
    'position:absolute;inset:3px;z-index:21;pointer-events:none;' +
    'border:2px dashed rgba(34,197,94,0.7);border-radius:10px;' +
    'background:rgba(20,83,45,0.22);' +
    'animation:_dndPulse 700ms ease-in-out infinite alternate;';
  return d;
}

// ── Gestión de overlays ────────────────────────────────────────

function _applyOverlaysAll() {
  document.querySelectorAll('td[data-franja-id]').forEach(function (td) {
    var fpk = parseInt(td.dataset.franjaId);
    // Eliminar overlays anteriores de esta td
    td.querySelectorAll('._dnd-ov:not(._dnd-hover)').forEach(function (o) { o.remove(); });
    td.style.position = 'relative';
    td.appendChild(DnD.conflictos[fpk] ? _makeConflict(DnD.conflictos[fpk]) : _makeDim());
  });
}

function _removeAllOverlays() {
  document.querySelectorAll('._dnd-ov').forEach(function (o) { o.remove(); });
  document.querySelectorAll('td[data-franja-id]').forEach(function (td) {
    td.style.position = '';
  });
}

function _setHover(td, on) {
  if (!td) return;
  td.querySelectorAll('._dnd-hover').forEach(function (o) { o.remove(); });
  if (on) {
    td.style.position = 'relative';
    td.appendChild(_makeHover());
  }
}

// ── Shake de la card dragging ──────────────────────────────────

function _shake(card) {
  if (!card) return;
  card.classList.remove('_dnd-shake');
  void card.offsetWidth;                          // force reflow
  card.classList.add('_dnd-shake');
  setTimeout(function () { card.classList.remove('_dnd-shake'); }, 360);
}

// ── API de movimiento ──────────────────────────────────────────

function _moveSession(sesionId, franjaId) {
  return fetch('/schedule/sesiones/' + sesionId + '/mover/', {
    method:  'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': _getCsrf() },
    body:    'franja_id=' + franjaId,
  }).then(function (r) {
    if (!r.ok) return r.text().then(function (t) { throw new Error('HTTP ' + r.status); });
    return r.json();
  });
}

function _reloadGrid() {
  return fetch(window.location.pathname + '?partial=grid')
    .then(function (r) { return r.text(); })
    .then(function (html) {
      var tmp = document.createElement('div');
      tmp.innerHTML = html;
      document.getElementById('horario-layout').replaceWith(tmp.firstElementChild);
      _initDnD();
      if (window.reapplySearch) window.reapplySearch();
    })
    .catch(function () { window.location.reload(); });
}

// ── Limpieza de estado global ──────────────────────────────────

function _resetDnD() {
  if (DnD.card) {
    DnD.card.style.opacity = '';
    DnD.card.style.filter  = '';
  }
  document.body.classList.remove('_dnd-active');
  _setHover(DnD.hoveredTd, false);
  _removeAllOverlays();
  DnD.active     = false;
  DnD.card       = null;
  DnD.sesionId   = null;
  DnD.conflictos = {};
  DnD.fetchDone  = false;
  DnD.hoveredTd  = null;
}

// ── Inicialización del DnD ─────────────────────────────────────

function _initDnD() {

  // ──────────────────────────────────────────────────────────────
  //  Tarjetas arrastrables
  // ──────────────────────────────────────────────────────────────
  document.querySelectorAll('.session-card[draggable="true"]').forEach(function (card) {

    card.addEventListener('dragstart', function (e) {
      DnD.active   = true;
      DnD.card     = card;
      DnD.sesionId = card.dataset.sesionId;
      DnD.conflictos = {};
      DnD.fetchDone  = false;
      DnD.hoveredTd  = null;

      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', DnD.sesionId);

      // Ghost limpio: clon sin overlays, posicionado fuera de pantalla
      var ghost = card.cloneNode(true);
      ghost.querySelectorAll('._dnd-ov').forEach(function (o) { o.remove(); });
      ghost.style.cssText =
        'position:fixed;top:-9999px;left:-9999px;' +
        'width:' + card.offsetWidth + 'px;opacity:.92;pointer-events:none;';
      document.body.appendChild(ghost);
      e.dataTransfer.setDragImage(ghost, 24, 24);
      requestAnimationFrame(function () { ghost.remove(); });

      // Fade de la tarjeta origen después de que el ghost se haya capturado
      requestAnimationFrame(function () {
        card.style.opacity = '0.25';
        card.style.filter  = 'grayscale(0.5)';
        document.body.classList.add('_dnd-active');
        _applyOverlaysAll();   // dim inmediato en todas las celdas
      });

      // Fetch de conflictos asíncrono
      fetch('/schedule/sesiones/' + DnD.sesionId + '/conflictos/')
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (!DnD.active) return;   // drag ya terminó
          (data.conflictos || []).forEach(function (c) {
            DnD.conflictos[c.franja_pk] = c.razon;
          });
          DnD.fetchDone = true;
          _applyOverlaysAll();       // reemplaza dim por conflicto donde aplique

          // Si ya hay hover activo sobre una celda conflictiva, quitar hover
          if (DnD.hoveredTd) {
            var fpk = parseInt(DnD.hoveredTd.dataset.franjaId);
            if (DnD.conflictos[fpk]) _setHover(DnD.hoveredTd, false);
          }
        })
        .catch(function () { DnD.fetchDone = true; });
    });

    card.addEventListener('dragend', function () {
      _resetDnD();
    });
  });

  // ──────────────────────────────────────────────────────────────
  //  Celdas destino — único punto de drop (td[data-franja-id]).
  //  Los .drop-zone son hijos decorativos; sus eventos burbujean aquí.
  // ──────────────────────────────────────────────────────────────
  document.querySelectorAll('td[data-franja-id]').forEach(function (td) {

    td.addEventListener('dragenter', function (e) {
      if (!DnD.active) return;
      e.preventDefault();
      if (DnD.hoveredTd && DnD.hoveredTd !== td) _setHover(DnD.hoveredTd, false);
      DnD.hoveredTd = td;
      var fpk = parseInt(td.dataset.franjaId);
      var isConflict = DnD.fetchDone && DnD.conflictos[fpk];
      e.dataTransfer.dropEffect = isConflict ? 'none' : 'move';
      if (!isConflict) _setHover(td, true);
    });

    td.addEventListener('dragover', function (e) {
      if (!DnD.active) return;
      e.preventDefault();
      var fpk = parseInt(td.dataset.franjaId);
      e.dataTransfer.dropEffect = (DnD.fetchDone && DnD.conflictos[fpk]) ? 'none' : 'move';
    });

    td.addEventListener('dragleave', function (e) {
      if (!DnD.active) return;
      // Ignorar si el puntero entra en un hijo
      if (e.relatedTarget && td.contains(e.relatedTarget)) return;
      if (DnD.hoveredTd === td) {
        _setHover(td, false);
        DnD.hoveredTd = null;
      }
    });

    td.addEventListener('drop', function (e) {
      e.preventDefault();
      if (!DnD.active) return;

      var sesionId = e.dataTransfer.getData('text/plain') || DnD.sesionId;
      var franjaId = td.dataset.franjaId;
      var fpk      = parseInt(franjaId);

      // Bloqueo cliente si los conflictos ya están cargados
      if (DnD.fetchDone && DnD.conflictos[fpk]) {
        _dndToast('No se puede mover: ' + _tradError(DnD.conflictos[fpk]), false);
        _shake(DnD.card);
        return;
      }

      // Referencia a la card para el shake en error (DnD se reseteará en dragend)
      var cardRef = DnD.card;

      _moveSession(sesionId, franjaId)
        .then(function (data) {
          if (data.ok) {
            _dndToast('Sesión movida correctamente.', true);
            _reloadGrid();
          } else {
            _dndToast(_tradError(data.error), false);
            _shake(cardRef);
          }
        })
        .catch(function () {
          _dndToast('Error de comunicación con el servidor.', false);
          _shake(cardRef);
        });
    });
  });
}

_initDnD();
