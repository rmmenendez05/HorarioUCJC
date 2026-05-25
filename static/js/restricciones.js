(function () {
  var tipo       = document.getElementById('id_tipo_restriccion');
  var campoFranja = document.getElementById('campo-franja');
  var campoAsig   = document.getElementById('campo-asignatura');
  var campoDia    = document.getElementById('campo-dia');

  function actualizar() {
    var v = tipo ? tipo.value : '';
    campoFranja.classList.toggle('hidden', v !== 'FRANJA_BLOQUEADA');
    campoAsig.classList.toggle('hidden',   v === 'FRANJA_BLOQUEADA' || v === '');
    campoDia.classList.toggle('hidden',    v === 'FRANJA_BLOQUEADA' || v === '');
  }

  if (tipo) {
    tipo.addEventListener('change', actualizar);
    actualizar();
  }
})();
