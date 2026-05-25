from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilDecano, PerfilProfesor, PerfilAlumno


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ('email', 'username', 'get_full_name', 'rol', 'is_active', 'is_staff')
    list_filter   = ('rol', 'is_active', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering      = ('email',)

    fieldsets = UserAdmin.fieldsets + (
        ('Rol RBAC', {'fields': ('rol',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rol RBAC', {'fields': ('rol',)}),
    )


@admin.register(PerfilDecano)
class PerfilDecanoAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'departamento', 'puede_aprobar')
    search_fields = ('usuario__email', 'usuario__first_name', 'usuario__last_name')


@admin.register(PerfilProfesor)
class PerfilProfesorAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'area_conocimiento', 'es_suplente')
    list_filter   = ('es_suplente',)
    search_fields = ('usuario__email', 'usuario__first_name', 'area_conocimiento')


@admin.register(PerfilAlumno)
class PerfilAlumnoAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'titulacion', 'nivel', 'curso_academico')
    list_filter   = ('titulacion', 'curso_academico')
    search_fields = ('usuario__email', 'usuario__first_name', 'usuario__last_name')
