from django import forms
from login.models import PerfilAlumno
from core.models import Titulacion, NivelCurso, CursoAcademico

_W = {
    'class': (
        'w-full bg-zinc-800 border border-zinc-700 text-white text-sm rounded-lg '
        'px-3 py-2 focus:outline-none focus:ring-1 focus:ring-red-600'
    )
}


class AlumnoGradoForm(forms.ModelForm):
    """Permite al Decano asignar la titulación, nivel y curso académico a un alumno."""

    class Meta:
        model  = PerfilAlumno
        fields = ['titulacion', 'nivel', 'curso_academico']
        widgets = {
            'titulacion':      forms.Select(attrs=_W),
            'nivel':           forms.Select(attrs=_W),
            'curso_academico': forms.Select(attrs=_W),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titulacion'].queryset      = Titulacion.objects.filter(activa=True)
        self.fields['nivel'].queryset           = NivelCurso.objects.select_related('titulacion').all()
        self.fields['curso_academico'].queryset = CursoAcademico.objects.all()
        self.fields['titulacion'].empty_label   = '— Sin titulación —'
        self.fields['nivel'].empty_label        = '— Sin nivel —'
        self.fields['curso_academico'].empty_label = '— Sin curso —'
        self.fields['titulacion'].required      = False
        self.fields['nivel'].required           = False
        self.fields['curso_academico'].required = False
