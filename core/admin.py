from django.contrib import admin
from .models import (
    Titulacion, CursoAcademico, NivelCurso,
    Asignatura, AsignaturaTitulacion,
    AsignacionProfesor, DisponibilidadProfesor,
    Matricula, Aula, FranjaHoraria,
    Horario, Sesion, AuditoriaHorario, Notificacion,
)


@admin.register(Titulacion)
class TitulacionAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'codigo', 'tipo', 'duracion_anios', 'permite_maniana', 'activa')
    list_filter   = ('tipo', 'activa')
    search_fields = ('nombre', 'codigo')


@admin.register(CursoAcademico)
class CursoAcademicoAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'matriculacion_abierta')
    list_filter   = ('estado', 'matriculacion_abierta')
    search_fields = ('nombre',)


@admin.register(NivelCurso)
class NivelCursoAdmin(admin.ModelAdmin):
    list_display  = ('titulacion', 'anio', 'es_ultimo')
    list_filter   = ('titulacion', 'es_ultimo')


@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display  = ('codigo', 'nombre', 'tipo_grupo', 'semestre', 'sesiones_semanales', 'duracion_sesion_h', 'es_transversal')
    list_filter   = ('tipo_grupo', 'semestre', 'es_transversal')
    search_fields = ('codigo', 'nombre')


@admin.register(AsignaturaTitulacion)
class AsignaturaTitulacionAdmin(admin.ModelAdmin):
    list_display  = ('asignatura', 'titulacion', 'nivel', 'es_optativa')
    list_filter   = ('titulacion', 'es_optativa')
    search_fields = ('asignatura__nombre', 'asignatura__codigo')


@admin.register(AsignacionProfesor)
class AsignacionProfesorAdmin(admin.ModelAdmin):
    list_display  = ('profesor', 'asignatura', 'curso_academico', 'tipo')
    list_filter   = ('tipo', 'curso_academico')
    search_fields = ('profesor__usuario__email', 'asignatura__nombre')


@admin.register(DisponibilidadProfesor)
class DisponibilidadProfesorAdmin(admin.ModelAdmin):
    list_display  = ('profesor', 'dia_semana', 'hora_inicio', 'hora_fin', 'tipo', 'curso_academico')
    list_filter   = ('tipo', 'dia_semana', 'curso_academico')
    search_fields = ('profesor__usuario__email',)


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display  = ('alumno', 'asignatura', 'curso_academico', 'fecha_matricula', 'tiene_conflicto')
    list_filter   = ('curso_academico', 'tiene_conflicto')
    search_fields = ('alumno__usuario__email', 'asignatura__nombre')


@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display  = ('codigo', 'nombre', 'capacidad', 'tipo', 'activa')
    list_filter   = ('tipo', 'activa')
    search_fields = ('codigo', 'nombre')


@admin.register(FranjaHoraria)
class FranjaHorariaAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'dia_semana', 'hora_inicio', 'hora_fin', 'turno', 'activa')
    list_filter   = ('turno', 'dia_semana', 'activa')


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display  = ('titulacion', 'nivel', 'curso_academico', 'estado', 'creado_por', 'aprobado_por', 'fecha_creacion')
    list_filter   = ('estado', 'curso_academico', 'titulacion')
    search_fields = ('titulacion__nombre', 'creado_por__email')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display  = ('asignatura', 'profesor', 'aula', 'franja', 'horario', 'grupo')
    list_filter   = ('horario__curso_academico', 'horario__titulacion', 'aula')
    search_fields = ('asignatura__nombre', 'profesor__usuario__email')


@admin.register(AuditoriaHorario)
class AuditoriaHorarioAdmin(admin.ModelAdmin):
    list_display  = ('timestamp', 'usuario', 'accion', 'severidad', 'modelo_afectado', 'objeto_id')
    list_filter   = ('accion', 'severidad')
    search_fields = ('usuario__email', 'modelo_afectado', 'descripcion')
    readonly_fields = ('timestamp', 'usuario', 'accion', 'severidad', 'modelo_afectado',
                       'objeto_id', 'valor_anterior', 'valor_nuevo', 'descripcion', 'codigo_error')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display  = ('titulo', 'destinatario', 'tipo', 'motivo', 'leida', 'fecha_creacion')
    list_filter   = ('tipo', 'motivo', 'leida')
    search_fields = ('titulo', 'destinatario__email')
    readonly_fields = ('fecha_creacion',)
