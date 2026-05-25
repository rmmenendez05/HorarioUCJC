"""
RNF-06 / RNF-14: Módulo de auditoría inalterable.
Registra cualquier modificación en horarios o configuraciones.
Cada entrada incluye: timestamp, usuario, acción, valor_anterior, valor_nuevo.
"""
from core.models import AuditoriaHorario


def log(usuario, accion, modelo, objeto_id=None,
        valor_anterior=None, valor_nuevo=None,
        descripcion='', severidad='INFO', codigo_error=''):
    """
    Registra una entrada de auditoría (RNF-14.1).
    """
    AuditoriaHorario.objects.create(
        usuario=usuario,
        accion=accion,
        severidad=severidad,
        modelo_afectado=modelo,
        objeto_id=objeto_id,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        descripcion=descripcion,
        codigo_error=codigo_error,
    )


def log_workflow(usuario, horario, estado_anterior, estado_nuevo, motivo=''):
    log(
        usuario=usuario,
        accion='ESTADO',
        modelo='Horario',
        objeto_id=horario.pk,
        valor_anterior={'estado': estado_anterior},
        valor_nuevo={'estado': estado_nuevo, 'motivo': motivo},
        descripcion=f"Cambio de estado: {estado_anterior} → {estado_nuevo}",
        severidad='INFO' if estado_nuevo != 'RECHAZADO' else 'WARN',
    )


def log_sesion_create(usuario, sesion):
    log(
        usuario=usuario,
        accion='CREACION',
        modelo='Sesion',
        objeto_id=sesion.pk,
        valor_nuevo={
            'asignatura': str(sesion.asignatura),
            'franja': str(sesion.franja),
            'aula': str(sesion.aula),
            'grupo': sesion.grupo,
        },
        descripcion=f"Sesión creada en horario #{sesion.horario.pk}",
    )


def log_sesion_delete(usuario, sesion_id, descripcion=''):
    log(
        usuario=usuario,
        accion='BORRADO',
        modelo='Sesion',
        objeto_id=sesion_id,
        descripcion=descripcion or f"Sesión #{sesion_id} eliminada",
        severidad='WARN',
    )


def log_generacion(usuario, horario, n_sesiones, errores):
    sev = 'INFO' if not errores else 'WARN'
    log(
        usuario=usuario,
        accion='CREACION',
        modelo='Horario',
        objeto_id=horario.pk,
        valor_nuevo={'sesiones_generadas': n_sesiones, 'errores': errores},
        descripcion=f"Generación automática: {n_sesiones} sesiones, {len(errores)} advertencias",
        severidad=sev,
    )
