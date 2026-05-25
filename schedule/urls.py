from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    # Router
    path("", views.schedule_home, name="home"),

    # RF-01: Horarios CRUD
    path("horarios/", views.horarios_list, name="horarios_list"),
    path("horarios/crear/", views.horario_create, name="horario_create"),
    path("horarios/<int:pk>/", views.horario_detalle, name="horario_detalle"),
    path("horarios/<int:pk>/eliminar/", views.horario_eliminar, name="horario_eliminar"),

    # RF-04: Workflow
    path("horarios/<int:pk>/workflow/", views.horario_workflow, name="horario_workflow"),

    # RF-02: Generación automática
    path("horarios/<int:pk>/generar/", views.horario_generar, name="horario_generar"),
    path("horarios/<int:pk>/log/",     views.horario_log,     name="horario_log"),

    # RF-02.0: Hoja de restricciones previa a la generación
    path("horarios/<int:pk>/restricciones/",                              views.horario_restricciones,           name="horario_restricciones"),
    path("horarios/<int:pk>/restricciones/eliminar/<int:rpk>/",           views.restriccion_eliminar,            name="restriccion_eliminar"),

    # Conflictos para drag-and-drop
    path("sesiones/<int:pk>/conflictos/",  views.sesion_conflictos,  name="sesion_conflictos"),

    # RF-07: Edición manual de sesiones
    path("horarios/<int:horario_pk>/sesion/crear/", views.sesion_crear, name="sesion_crear"),
    path("sesiones/<int:pk>/eliminar/", views.sesion_eliminar, name="sesion_eliminar"),
    path("sesiones/<int:pk>/mover/",    views.sesion_mover,    name="sesion_mover"),

    # RF-08: Disponibilidad de profesores
    path("disponibilidad/", views.disponibilidad, name="disponibilidad"),
    path("disponibilidad/<int:pk>/eliminar/", views.disponibilidad_eliminar, name="disponibilidad_eliminar"),

    # RF-09, RF-11: Horario personal
    path("mi-horario/", views.mi_horario, name="mi_horario"),

    # RF-10, RF-12, RNF-09: Notificaciones
    path("notificaciones/", views.notificaciones, name="notificaciones"),
    path("notificaciones/<int:pk>/leer/", views.notificacion_leer, name="notificacion_leer"),
    path("notificaciones/leer-todas/", views.notificaciones_leer_todas, name="notificaciones_leer_todas"),
    path("notificaciones/<int:pk>/eliminar/", views.notificacion_eliminar, name="notificacion_eliminar"),
    path("notificaciones/eliminar-todas/", views.notificaciones_eliminar_todas, name="notificaciones_eliminar_todas"),

    # RF-05: Configuración
    path("config/", views.config_view, name="config"),
    path("config/franja/<int:pk>/toggle/", views.franja_toggle, name="franja_toggle"),
    path("config/franja/<int:pk>/eliminar/", views.franja_eliminar, name="franja_eliminar"),

    # RNF-06/14: Auditoría
    path("audit/", views.audit_view, name="audit"),

    # RF-03: Informes y exportación
    path("informes/", views.informes, name="informes"),
    path("horarios/<int:pk>/export/pdf/",   views.horario_export_pdf,   name="horario_export_pdf"),
    path("horarios/<int:pk>/export/excel/", views.horario_export_excel, name="horario_export_excel"),

    # Curriculum: Titulaciones y Asignaturas (solo Decano)
    path("curriculum/", views.curriculum_view, name="curriculum"),
    path("curriculum/titulacion/crear/", views.titulacion_crear, name="titulacion_crear"),
    path("curriculum/titulacion/<int:pk>/", views.titulacion_detalle, name="titulacion_detalle"),
    path("curriculum/titulacion/<int:pk>/editar/", views.titulacion_editar, name="titulacion_editar"),
    path("curriculum/titulacion/<int:pk>/eliminar/", views.titulacion_eliminar, name="titulacion_eliminar"),
    path("curriculum/titulacion/<int:tit_pk>/asignatura/crear/", views.asignatura_crear, name="asignatura_crear"),
    path("curriculum/asignatura/<int:pk>/editar/", views.asignatura_editar, name="asignatura_editar"),
    path("curriculum/asignatura/<int:pk>/eliminar/", views.asignatura_eliminar, name="asignatura_eliminar"),
]
