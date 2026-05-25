const _TOAST_CFG = {
  success: { border:'border-green-500',  bg:'bg-green-950/90',  text:'text-green-200',  bar:'bg-green-500',  icon:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>' },
  error:   { border:'border-red-500',    bg:'bg-red-950/90',    text:'text-red-200',    bar:'bg-red-500',    icon:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>' },
  warning: { border:'border-amber-500',  bg:'bg-amber-950/90',  text:'text-amber-200',  bar:'bg-amber-500',  icon:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v3m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>' },
  info:    { border:'border-zinc-600',   bg:'bg-zinc-900/95',   text:'text-zinc-200',   bar:'bg-zinc-500',   icon:'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>' },
};

function showToast(msg, type) {
  type = type || 'info';
  const c  = _TOAST_CFG[type] || _TOAST_CFG.info;
  const el = document.createElement('div');
  el.className = 'pointer-events-auto relative overflow-hidden rounded-xl border ' + c.border + ' ' + c.bg + ' shadow-2xl backdrop-blur-sm toast-in';
  el.style.fontFamily = "Inter, system-ui, sans-serif";
  el.innerHTML =
    '<div class="flex items-start gap-3 px-4 py-3.5">' +
      '<svg class="w-4 h-4 mt-0.5 shrink-0 ' + c.text + '" fill="none" stroke="currentColor" viewBox="0 0 24 24">' + c.icon + '</svg>' +
      '<p class="text-sm ' + c.text + ' flex-1 leading-snug">' + msg + '</p>' +
      '<button data-dismiss class="shrink-0 ' + c.text + ' opacity-40 hover:opacity-100 transition-opacity -mr-1 -mt-0.5 p-1 rounded">' +
        '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">' +
          '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>' +
        '</svg>' +
      '</button>' +
    '</div>' +
    '<div class="h-0.5 ' + c.bar + ' toast-bar opacity-40"></div>';
  el.querySelector('[data-dismiss]').addEventListener('click', function () { dismissToast(el); });
  var container = document.getElementById('toast-container');
  if (container) container.appendChild(el);
  el._timer = setTimeout(function () { dismissToast(el); }, 4500);
}

function dismissToast(el) {
  if (!el) return;
  clearTimeout(el._timer);
  el.classList.remove('toast-in');
  el.classList.add('toast-out');
  setTimeout(function () { el.remove(); }, 300);
}
