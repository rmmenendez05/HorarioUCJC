from django.db import models
from django.utils.translation import gettext_lazy as _


# TITULACIONES Y ESTRUCTURA ACADÉMICA

class Titulacion(models.Model):
    """
    Representa un grado/titulación (RF-01, RD-17, RD-18).
    Ej: Ingeniería Informática, Doble Grado Informática+Robótica
    """
    class TipoTitulacion(models.TextChoices):
        GRADO       = 'GRADO',       _('Grado')
        DOBLE_GRADO = 'DOBLE_GRADO', _('Doble Grado')

    nombre          = models.CharField(max_length=150, unique=True)
    codigo          = models.CharField(max_length=20, unique=True)
    tipo            = models.CharField(max_length=15, choices=TipoTitulacion.choices, default=TipoTitulacion.GRADO)
    duracion_anios  = models.PositiveSmallIntegerField(default=4)
    permite_maniana = models.BooleanField(default=False)   # RD-18.1: Doble Grado puede tener mañana
    activa          = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Titulación'
        verbose_name_plural = 'Titulaciones'

    def __str__(self):
        return self.nombre


class CursoAcademico(models.Model):
    """
    Año académico (ej. 2025-2026).
    Los horarios deben estar definidos antes de la matriculación (RD-15).
    """
    class Estado(models.TextChoices):
        PLANIFICACION = 'PLANIFICACION', _('En planificación')
        ACTIVO        = 'ACTIVO',        _('Activo')
        CERRADO       = 'CERRADO',       _('Cerrado')

    nombre               = models.CharField(max_length=20, unique=True)   # "2025-2026"
    fecha_inicio         = models.DateField()
    fecha_fin            = models.DateField()
    estado               = models.CharField(max_length=15, choices=Estado.choices, default=Estado.PLANIFICACION)
    matriculacion_abierta = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Curso Académico'
        verbose_name_plural = 'Cursos Académicos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.nombre


class NivelCurso(models.Model):
    """
    Año dentro de una titulación (1º, 2º, 3º, 4º, 5º).
    RD-18: En grados individuales las clases se imparten por la tarde.
    """
    titulacion = models.ForeignKey(Titulacion, on_delete=models.CASCADE, related_name='niveles')
    anio       = models.PositiveSmallIntegerField()    # 1, 2, 3, 4, 5
    es_ultimo  = models.BooleanField(default=False)    # RD-18: último año → solo tarde

    class Meta:
        verbose_name = 'Nivel de Curso'
        verbose_name_plural = 'Niveles de Curso'
        unique_together = ('titulacion', 'anio')
        ordering = ['titulacion', 'anio']

    def __str__(self):
        return f"{self.titulacion} — {self.anio}º"


# ASIGNATURAS

class Asignatura(models.Model):
    """
    Asignatura del plan de estudios.
    Cada asignatura tiene 2 sesiones/semana de 2h cada una (RD-01).
    Puede ser compartida entre titulaciones (RF-13, RD-10).
    """
    class TipoGrupo(models.TextChoices):
        TEORIA      = 'TEORIA',      _('Teoría')
        PRACTICAS   = 'PRACTICAS',   _('Prácticas')
        LABORATORIO = 'LABORATORIO', _('Laboratorio')

    codigo             = models.CharField(max_length=20, unique=True)
    nombre             = models.CharField(max_length=150)
    titulaciones       = models.ManyToManyField(Titulacion, through='AsignaturaTitulacion', related_name='asignaturas')
    sesiones_semanales = models.PositiveSmallIntegerField(default=2)   # RD-01: n=2
    duracion_sesion_h  = models.PositiveSmallIntegerField(default=2)   # RD-01: h=2
    tipo_grupo         = models.CharField(max_length=15, choices=TipoGrupo.choices, default=TipoGrupo.TEORIA)
    es_transversal     = models.BooleanField(default=False)            # RF-13: compartida entre titulaciones
    semestre           = models.PositiveSmallIntegerField(choices=[(1, 'Primero'), (2, 'Segundo')])

    class Meta:
        verbose_name = 'Asignatura'
        verbose_name_plural = 'Asignaturas'
        ordering = ['codigo']

    def __str__(self):
        return f"[{self.codigo}] {self.nombre}"


class AsignaturaTitulacion(models.Model):
    """
    Tabla intermedia entre Asignatura y Titulacion.
    Permite saber en qué año de cada titulación se imparte (RF-01).
    """
    asignatura  = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    titulacion  = models.ForeignKey(Titulacion, on_delete=models.CASCADE)
    nivel       = models.ForeignKey(NivelCurso, on_delete=models.CASCADE)
    es_optativa = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Asignatura por Titulación'
        unique_together = ('asignatura', 'titulacion', 'nivel')

    def __str__(self):
        return f"{self.asignatura} → {self.titulacion} ({self.nivel.anio}º)"


class AsignacionProfesor(models.Model):
    """
    Vincula un profesor a una asignatura (RF-06, RD-07: cada asignatura tiene un único profesor).
    """
    class TipoAsignacion(models.TextChoices):
        TITULAR  = 'TITULAR',  _('Titular')
        SUPLENTE = 'SUPLENTE', _('Suplente')

    profesor        = models.ForeignKey('login.PerfilProfesor', on_delete=models.CASCADE)
    asignatura      = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    curso_academico = models.ForeignKey(CursoAcademico, on_delete=models.CASCADE)
    tipo            = models.CharField(max_length=10, choices=TipoAsignacion.choices, default=TipoAsignacion.TITULAR)

    class Meta:
        verbose_name = 'Asignación Profesor'
        unique_together = ('profesor', 'asignatura', 'curso_academico')

    def __str__(self):
        return f"{self.profesor} → {self.asignatura} ({self.tipo})"


class DisponibilidadProfesor(models.Model):
    """
    Franjas de disponibilidad/indisponibilidad del profesor (RF-08, RF-08.1, RF-08.2, RD-08).
    """
    class TipoDisponibilidad(models.TextChoices):
        PREFERENTE   = 'PREFERENTE',   _('Disponibilidad preferente')
        DISPONIBLE   = 'DISPONIBLE',   _('Disponible')
        INDISPONIBLE = 'INDISPONIBLE', _('Bloqueo / Indisponible')

    class Periodo(models.TextChoices):
        T1    = 'T1',    _('Solo Trimestre 1')
        T2    = 'T2',    _('Solo Trimestre 2')
        ANUAL = 'ANUAL', _('Anual (todo el curso)')

    DIAS_SEMANA = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'),
        (3, 'Jueves'), (4, 'Viernes'),
    ]

    profesor           = models.ForeignKey('login.PerfilProfesor', on_delete=models.CASCADE, related_name='disponibilidades')
    curso_academico    = models.ForeignKey(CursoAcademico, on_delete=models.CASCADE)
    dia_semana         = models.PositiveSmallIntegerField(choices=DIAS_SEMANA)
    hora_inicio        = models.TimeField()
    hora_fin           = models.TimeField()
    tipo               = models.CharField(max_length=15, choices=TipoDisponibilidad.choices, default=TipoDisponibilidad.DISPONIBLE)
    # Restricción trimestral: una indisponibilidad de T1 no aplica a asignaturas de S2
    periodo            = models.CharField(max_length=5, choices=Periodo.choices, default=Periodo.ANUAL)
    fecha_modificacion = models.DateTimeField(auto_now=True)   # RF-08.2: historial de cambios

    class Meta:
        verbose_name = 'Disponibilidad Profesor'
        verbose_name_plural = 'Disponibilidades Profesores'

    def aplica_a_semestre(self, semestre: int) -> bool:
        """
        Devuelve False si la restricción es T1-only y la asignatura es de S2.
        En ese caso la indisponibilidad ha expirado antes de que comience S2.
        """
        if self.tipo == self.TipoDisponibilidad.INDISPONIBLE and self.periodo == self.Periodo.T1 and semestre == 2:
            return False
        return True

    def __str__(self):
        return f"{self.profesor} — {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin} ({self.tipo}/{self.periodo})"


class Matricula(models.Model):
    """
    Matrícula de un alumno en una asignatura (RF-11, RF-14).
    Permite detectar solapamientos inter-niveles (RD-09).
    """
    alumno          = models.ForeignKey('login.PerfilAlumno', on_delete=models.CASCADE)
    asignatura      = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    curso_academico = models.ForeignKey(CursoAcademico, on_delete=models.CASCADE)
    fecha_matricula = models.DateTimeField(auto_now_add=True)
    tiene_conflicto = models.BooleanField(default=False)   # RF-14.1: marcador de conflicto

    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = ('alumno', 'asignatura', 'curso_academico')

    def __str__(self):
        return f"{self.alumno} → {self.asignatura}"


# AULAS

class Aula(models.Model):
    """
    Aula física disponible (RD-11, RD-12).
    """
    class TipoAula(models.TextChoices):
        TEORIA      = 'TEORIA',      _('Aula de Teoría')
        LABORATORIO = 'LABORATORIO', _('Laboratorio')
        SEMINARIO   = 'SEMINARIO',   _('Seminario')

    codigo    = models.CharField(max_length=20, unique=True)
    nombre    = models.CharField(max_length=100)
    capacidad = models.PositiveSmallIntegerField()
    tipo      = models.CharField(max_length=15, choices=TipoAula.choices, default=TipoAula.TEORIA)
    activa    = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'

    def __str__(self):
        return f"{self.codigo} — {self.nombre} (cap. {self.capacidad})"


# FRANJAS HORARIAS

class FranjaHoraria(models.Model):
    """
    Bloque temporal definido por el decano (RF-05, RD-17, RD-18).
    """
    class Turno(models.TextChoices):
        MANIANA = 'MANIANA', _('Mañana')
        TARDE   = 'TARDE',   _('Tarde')

    DIAS_SEMANA = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'),
        (3, 'Jueves'), (4, 'Viernes'),
    ]

    nombre      = models.CharField(max_length=50)
    dia_semana  = models.PositiveSmallIntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin    = models.TimeField()
    turno       = models.CharField(max_length=10, choices=Turno.choices)
    activa      = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Franja Horaria'
        verbose_name_plural = 'Franjas Horarias'
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ('dia_semana', 'hora_inicio', 'hora_fin')

    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin} ({self.get_turno_display()})"


# HORARIO (con workflow de estados — RF-04)

class Horario(models.Model):
    """
    Horario generado para una titulación, nivel y curso académico.
    Incluye el workflow: Borrador → Revisión → Aprobado/Rechazado (RF-04).
    """
    class Estado(models.TextChoices):
        BORRADOR  = 'BORRADOR',  _('Borrador')
        REVISION  = 'REVISION',  _('En Revisión')
        APROBADO  = 'APROBADO',  _('Aprobado')
        RECHAZADO = 'RECHAZADO', _('Rechazado')

    titulacion          = models.ForeignKey(Titulacion, on_delete=models.CASCADE, related_name='horarios')
    nivel               = models.ForeignKey(NivelCurso, on_delete=models.CASCADE)
    curso_academico     = models.ForeignKey(CursoAcademico, on_delete=models.CASCADE)
    estado              = models.CharField(max_length=10, choices=Estado.choices, default=Estado.BORRADOR)
    creado_por          = models.ForeignKey('login.Usuario', on_delete=models.SET_NULL, null=True, related_name='horarios_creados')
    aprobado_por        = models.ForeignKey('login.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='horarios_aprobados')
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    motivo_rechazo      = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        unique_together = ('titulacion', 'nivel', 'curso_academico')

    def __str__(self):
        return f"Horario {self.titulacion} {self.nivel.anio}º — {self.curso_academico} [{self.get_estado_display()}]"


class Sesion(models.Model):
    """
    Sesión concreta dentro de un horario (RF-09.1, RF-09.2, RD-05, RD-12).
    Una sesión ocupa una franja en un aula para una asignatura con un profesor.
    """
    horario    = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='sesiones')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    profesor   = models.ForeignKey('login.PerfilProfesor', on_delete=models.CASCADE)
    aula       = models.ForeignKey(Aula, on_delete=models.CASCADE)
    franja     = models.ForeignKey(FranjaHoraria, on_delete=models.CASCADE)
    grupo      = models.CharField(max_length=20, blank=True)   # RF-09.2: grupo/subgrupo

    class Meta:
        verbose_name = 'Sesión'
        verbose_name_plural = 'Sesiones'
        # RD-05: ningún profesor puede dar dos clases a la vez
        # RD-12: ningún aula puede tener dos clases a la vez
        unique_together = [
            ('aula', 'franja', 'horario'),   # RD-12: aula no puede tener dos clases simultáneas
        ]

    def __str__(self):
        return f"{self.asignatura} | {self.profesor} | {self.aula} | {self.franja}"


# AUDITORÍA Y LOGS (RNF-06, RNF-14)

class AuditoriaHorario(models.Model):
    """
    Registro inalterable de cambios en horarios (RNF-06, RNF-14).
    """
    class TipoAccion(models.TextChoices):
        CREACION   = 'CREACION',   _('Creación')
        EDICION    = 'EDICION',    _('Edición')
        BORRADO    = 'BORRADO',    _('Borrado')
        APROBACION = 'APROBACION', _('Aprobación')
        RECHAZO    = 'RECHAZO',    _('Rechazo')
        ESTADO     = 'ESTADO',     _('Cambio de Estado')

    class Severidad(models.TextChoices):
        INFO     = 'INFO',     _('Información')
        WARN     = 'WARN',     _('Advertencia')
        ERROR    = 'ERROR',    _('Error')
        CRITICAL = 'CRITICAL', _('Crítico')

    timestamp       = models.DateTimeField(auto_now_add=True)              # RNF-14.1
    usuario         = models.ForeignKey('login.Usuario', on_delete=models.SET_NULL, null=True)
    accion          = models.CharField(max_length=15, choices=TipoAccion.choices)
    severidad       = models.CharField(max_length=10, choices=Severidad.choices, default=Severidad.INFO)
    modelo_afectado = models.CharField(max_length=50)
    objeto_id       = models.PositiveIntegerField(null=True, blank=True)
    valor_anterior  = models.JSONField(null=True, blank=True)
    valor_nuevo     = models.JSONField(null=True, blank=True)
    descripcion     = models.TextField(blank=True)
    codigo_error    = models.CharField(max_length=20, blank=True)          # RNF-14.1

    class Meta:
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.accion} por {self.usuario} — {self.modelo_afectado}#{self.objeto_id}"


# NOTIFICACIONES (RF-10, RF-12, RNF-09)

class Notificacion(models.Model):
    """
    Notificaciones in-app para profesores y alumnos (RF-10.1, RF-12, RNF-09).
    """
    class Tipo(models.TextChoices):
        INFO        = 'INFO',        _('Informativa')
        ADVERTENCIA = 'ADVERTENCIA', _('Advertencia')
        ERROR       = 'ERROR',       _('Error')
        EXITO       = 'EXITO',       _('Éxito')

    class Motivo(models.TextChoices):
        CAMBIO_AULA     = 'CAMBIO_AULA',     _('Cambio de aula')
        CAMBIO_HORARIO  = 'CAMBIO_HORARIO',  _('Cambio de horario')
        CAMBIO_PROFESOR = 'CAMBIO_PROFESOR', _('Cambio de profesor')
        CONFLICTO       = 'CONFLICTO',       _('Conflicto detectado')
        APROBACION      = 'APROBACION',      _('Horario aprobado')
        RECHAZO         = 'RECHAZO',         _('Horario rechazado')

    destinatario    = models.ForeignKey('login.Usuario', on_delete=models.CASCADE, related_name='notificaciones')
    tipo            = models.CharField(max_length=15, choices=Tipo.choices, default=Tipo.INFO)
    motivo          = models.CharField(max_length=20, choices=Motivo.choices)
    titulo          = models.CharField(max_length=150)
    mensaje         = models.TextField()
    leida           = models.BooleanField(default=False)
    fecha_creacion  = models.DateTimeField(auto_now_add=True)
    sesion_afectada = models.ForeignKey(Sesion, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"[{self.tipo}] {self.titulo} → {self.destinatario}"


# RESTRICCIONES PERSONALIZADAS DEL DECANO

class RestriccionPersonalizada(models.Model):
    """
    Restricciones adicionales definidas por el Decano para un horario concreto.
    El motor de generación (GA) las lee y penaliza los cromosomas que las incumplan.
    """
    class Tipo(models.TextChoices):
        FRANJA_BLOQUEADA    = 'FRANJA_BLOQUEADA',    _('Bloquear franja horaria completa')
        ASIG_DIA_EXCLUIDO   = 'ASIG_DIA_EXCLUIDO',  _('Excluir asignatura de un día')
        ASIG_DIA_PREFERIDO  = 'ASIG_DIA_PREFERIDO', _('Día preferido para asignatura')

    DIAS_SEMANA = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'),
        (1, 'Lunes'), (2, 'Martes'), (3, 'Miércoles'), (4, 'Jueves'), (5, 'Viernes'),
    ]

    horario     = models.ForeignKey('Horario', on_delete=models.CASCADE,
                                    related_name='restricciones_personalizadas')
    tipo        = models.CharField(max_length=25, choices=Tipo.choices)
    descripcion = models.CharField(max_length=200, blank=True,
                                   help_text='Etiqueta descriptiva (opcional)')
    # Para FRANJA_BLOQUEADA
    franja      = models.ForeignKey('FranjaHoraria', on_delete=models.CASCADE,
                                    null=True, blank=True)
    # Para ASIG_DIA_EXCLUIDO / ASIG_DIA_PREFERIDO
    asignatura  = models.ForeignKey('Asignatura', on_delete=models.CASCADE,
                                    null=True, blank=True)
    dia_semana  = models.PositiveSmallIntegerField(null=True, blank=True)
    activa      = models.BooleanField(default=True)
    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Restricción personalizada'
        verbose_name_plural = 'Restricciones personalizadas'
        ordering = ['tipo', 'creado_en']

    def __str__(self):
        return f"[{self.tipo}] {self.descripcion or self.pk} — {self.horario}"
