from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Usuario(AbstractUser):
    """
    Extiende AbstractUser con el sistema de roles RBAC.
    Roles: DECANO, PROFESOR, ALUMNO, IT
    """
    class Rol(models.TextChoices):
        DECANO   = 'DECANO',   _('Decano / Dirección')
        PROFESOR = 'PROFESOR', _('Profesor')
        ALUMNO   = 'ALUMNO',   _('Alumno')
        IT       = 'IT',       _('Departamento IT')

    rol = models.CharField(
        max_length=10,
        choices=Rol.choices,
        default=Rol.ALUMNO,
    )
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"


class PerfilDecano(models.Model):
    """
    Perfil extendido para el rol de Decano/Dirección.
    RF-01, RF-04, RF-07: gestión y aprobación de horarios.
    """
    usuario       = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_decano')
    departamento  = models.CharField(max_length=100, blank=True)
    puede_aprobar = models.BooleanField(default=True)   # RF-04: solo Decanato puede aprobar

    class Meta:
        verbose_name = 'Perfil Decano'

    def __str__(self):
        return f"Decano: {self.usuario.get_full_name()}"


class PerfilProfesor(models.Model):
    """
    Perfil extendido para el rol de Profesor.
    RF-08, RF-09, RD-05, RD-06, RD-07.
    """
    usuario           = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_profesor')
    area_conocimiento = models.CharField(max_length=100)
    es_suplente       = models.BooleanField(default=False)    # RF-06: suplentes por área
    asignaturas       = models.ManyToManyField(
        'core.Asignatura',
        through='core.AsignacionProfesor',
        related_name='profesores',
    )

    class Meta:
        verbose_name = 'Perfil Profesor'
        verbose_name_plural = 'Perfiles Profesores'

    def __str__(self):
        return f"Prof. {self.usuario.get_full_name()}"


class PerfilAlumno(models.Model):
    """
    Perfil extendido para el rol de Alumno.
    RF-11, RF-12, RF-14, RD-08, RD-09.
    """
    usuario         = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_alumno')
    titulacion      = models.ForeignKey('core.Titulacion', on_delete=models.SET_NULL, null=True, related_name='alumnos')
    nivel           = models.ForeignKey('core.NivelCurso', on_delete=models.SET_NULL, null=True)
    curso_academico = models.ForeignKey('core.CursoAcademico', on_delete=models.SET_NULL, null=True)
    matriculas      = models.ManyToManyField(
        'core.Asignatura',
        through='core.Matricula',
        related_name='alumnos',
    )

    class Meta:
        verbose_name = 'Perfil Alumno'
        verbose_name_plural = 'Perfiles Alumnos'

    def __str__(self):
        return f"Alumno: {self.usuario.get_full_name()} — {self.titulacion} {self.nivel}"
