from functools import wraps
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from login.models import Usuario, PerfilAlumno
from .forms import AlumnoGradoForm


def decano_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.rol != 'DECANO':
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def render_dashboard(request):
    context = {}
    if request.user.rol == 'DECANO':
        context['stats'] = {
            'total_users': Usuario.objects.count(),
            'decanos':     Usuario.objects.filter(rol='DECANO').count(),
            'profesores':  Usuario.objects.filter(rol='PROFESOR').count(),
            'alumnos':     Usuario.objects.filter(rol='ALUMNO').count(),
            'it':          Usuario.objects.filter(rol='IT').count(),
            'horarios':    0,
        }
    return render(request, "core/dashboard.html", context)


@decano_required
def user_management(request):
    import json
    from login.models import PerfilProfesor

    rol_filter = request.GET.get('rol', '')
    qs = Usuario.objects.all().order_by('rol', 'last_name', 'first_name')
    if rol_filter:
        qs = qs.filter(rol=rol_filter)
    users = list(qs)

    # Build profile lookups in 2 queries (no N+1)
    prof_map = {
        p.usuario_id: p
        for p in PerfilProfesor.objects.prefetch_related('asignaturas').all()
    }
    alumno_map = {
        a.usuario_id: a
        for a in PerfilAlumno.objects.select_related('titulacion', 'nivel').all()
    }

    # Client-side search data island
    search_data = []
    for u in users:
        item = {
            'pk':    u.pk,
            'name':  u.get_full_name(),
            'email': u.email,
            'rol':   u.rol,
            'id':    str(u.pk),
            'area':  '',
            'asignaturas': '',
            'titulacion':  '',
            'nivel':       '',
        }
        prof = prof_map.get(u.pk)
        if prof:
            item['area'] = prof.area_conocimiento
            item['asignaturas'] = ' '.join(a.nombre for a in prof.asignaturas.all())
        alumno = alumno_map.get(u.pk)
        if alumno:
            item['titulacion'] = str(alumno.titulacion) if alumno.titulacion else ''
            item['nivel'] = f"{alumno.nivel.anio}º" if alumno.nivel else ''
        search_data.append(item)

    context = {
        'users':           users,
        'rol_filter':      rol_filter,
        'rol_choices':     Usuario.Rol.choices,
        'search_data_json': json.dumps(search_data, ensure_ascii=False),
        'stats': {
            'total':      Usuario.objects.count(),
            'decanos':    Usuario.objects.filter(rol='DECANO').count(),
            'profesores': Usuario.objects.filter(rol='PROFESOR').count(),
            'alumnos':    Usuario.objects.filter(rol='ALUMNO').count(),
        },
    }
    return render(request, "core/user_management.html", context)


@decano_required
def alumno_update_grado(request, pk):
    """Permite al Decano asignar o cambiar la titulación/nivel de un alumno."""
    usuario = get_object_or_404(Usuario, pk=pk, rol='ALUMNO')
    # Crear perfil si no existe
    perfil, _ = PerfilAlumno.objects.get_or_create(usuario=usuario)

    if request.method == 'POST':
        form = AlumnoGradoForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Grado actualizado para {usuario.get_full_name() or usuario.email}.',
            )
            return redirect('user_management')
    else:
        form = AlumnoGradoForm(instance=perfil)

    return render(request, 'core/alumno_grado_form.html', {
        'form':    form,
        'usuario': usuario,
        'perfil':  perfil,
    })


@decano_required
def user_update_rol(request, pk):
    if request.method != 'POST':
        return redirect('user_management')
    nuevo_rol = request.POST.get('rol', '')
    roles_validos = [r for r, _ in Usuario.Rol.choices]
    if nuevo_rol not in roles_validos:
        return redirect('user_management')
    try:
        usuario = Usuario.objects.get(pk=pk)
        if usuario != request.user:
            usuario.rol = nuevo_rol
            usuario.save(update_fields=['rol'])
    except Usuario.DoesNotExist:
        pass
    return redirect('user_management')