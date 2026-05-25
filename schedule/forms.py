from django import forms
from core.models import (
    Horario, Sesion, FranjaHoraria, DisponibilidadProfesor,
    Titulacion, CursoAcademico, NivelCurso, Aula, Asignatura,
    AsignaturaTitulacion, RestriccionPersonalizada,
)

_BASE = 'w-full bg-zinc-800 border border-zinc-700 text-white text-sm rounded-lg focus:outline-none focus:ring-1 focus:ring-red-600 focus:border-red-600 transition-colors'
_WS  = {'class': f'{_BASE} pl-3 pr-9 py-2.5 appearance-none cursor-pointer'}
_WI  = {'class': f'{_BASE} px-3 py-2.5 placeholder:text-zinc-500'}
_W   = {'class': f'{_BASE} px-3 py-2 placeholder:text-zinc-500'}
_WC  = {'class': 'form-checkbox h-4 w-4 rounded border-zinc-600 bg-zinc-800 text-red-600 focus:ring-red-600'}


class HorarioCreateForm(forms.ModelForm):
    class Meta:
        model  = Horario
        fields = ['titulacion', 'nivel', 'curso_academico']
        widgets = {
            'titulacion':      forms.Select(attrs=_WS),
            'nivel':           forms.Select(attrs=_WS),
            'curso_academico': forms.Select(attrs=_WS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titulacion'].queryset      = Titulacion.objects.filter(activa=True)
        self.fields['curso_academico'].queryset = CursoAcademico.objects.all()
        self.fields['nivel'].queryset           = NivelCurso.objects.select_related('titulacion')


class WorkflowForm(forms.Form):
    ACCIONES = [
        ('REVISION',  'Enviar a Revisión'),
        ('APROBADO',  'Aprobar horario'),
        ('RECHAZADO', 'Rechazar horario'),
        ('BORRADOR',  'Volver a Borrador'),
    ]
    accion = forms.ChoiceField(choices=ACCIONES, widget=forms.HiddenInput)
    motivo = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Motivo del rechazo (obligatorio al rechazar)…', 'style': 'resize:none; width:100%'}),
    )


class RestriccionPersonalizadaForm(forms.ModelForm):
    DIAS_CHOICES = [
        ('', '— Selecciona día —'),
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'),
    ]

    dia_semana = forms.ChoiceField(
        choices=DIAS_CHOICES,
        required=False,
        widget=forms.Select(attrs=_WS),
    )

    class Meta:
        model  = RestriccionPersonalizada
        fields = ['tipo', 'descripcion', 'franja', 'asignatura', 'dia_semana']
        widgets = {
            'tipo':        forms.Select(attrs={**_WS, 'id': 'id_tipo_restriccion'}),
            'descripcion': forms.TextInput(attrs={**_WI, 'placeholder': 'Descripción breve (opcional)'}),
            'franja':      forms.Select(attrs={**_WS, 'id': 'id_franja_restriccion'}),
            'asignatura':  forms.Select(attrs={**_WS, 'id': 'id_asignatura_restriccion'}),
        }

    def __init__(self, *args, horario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['franja'].required    = False
        self.fields['asignatura'].required = False
        self.fields['franja'].empty_label = '— Selecciona franja —'
        self.fields['asignatura'].empty_label = '— Selecciona asignatura —'
        self.fields['franja'].queryset = FranjaHoraria.objects.filter(activa=True).order_by('dia_semana', 'hora_inicio')
        if horario:
            self.fields['asignatura'].queryset = Asignatura.objects.filter(
                asignaturatitulacion__titulacion=horario.titulacion,
                asignaturatitulacion__nivel=horario.nivel,
            ).distinct().order_by('nombre')
        else:
            self.fields['asignatura'].queryset = Asignatura.objects.none()


class DisponibilidadForm(forms.ModelForm):
    class Meta:
        model  = DisponibilidadProfesor
        fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'tipo', 'periodo', 'curso_academico']
        widgets = {
            'dia_semana':      forms.Select(attrs=_WS),
            'hora_inicio':     forms.TimeInput(attrs={**_WI, 'type': 'time'}),
            'hora_fin':        forms.TimeInput(attrs={**_WI, 'type': 'time'}),
            'tipo':            forms.Select(attrs=_WS),
            'periodo':         forms.Select(attrs=_WS),
            'curso_academico': forms.Select(attrs=_WS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso_academico'].queryset = CursoAcademico.objects.all()
        self.fields['periodo'].help_text = (
            'Solo Trimestre 1: la restricción no afectará a asignaturas de 2.º semestre.'
        )


class SesionManualForm(forms.ModelForm):
    class Meta:
        model  = Sesion
        fields = ['asignatura', 'profesor', 'aula', 'franja', 'grupo']
        widgets = {
            'asignatura': forms.Select(attrs=_WS),
            'profesor':   forms.Select(attrs=_WS),
            'aula':       forms.Select(attrs=_WS),
            'franja':     forms.Select(attrs=_WS),
            'grupo':      forms.TextInput(attrs={**_WI, 'placeholder': 'T1, P2, L1…'}),
        }


class FranjaHorariaForm(forms.ModelForm):
    class Meta:
        model  = FranjaHoraria
        fields = ['nombre', 'dia_semana', 'hora_inicio', 'hora_fin', 'turno', 'activa']
        widgets = {
            'nombre':      forms.TextInput(attrs={**_WI, 'placeholder': 'Ej: Tarde-Lunes-1'}),
            'dia_semana':  forms.Select(attrs=_WS),
            'hora_inicio': forms.TimeInput(attrs={**_WI, 'type': 'time'}),
            'hora_fin':    forms.TimeInput(attrs={**_WI, 'type': 'time'}),
            'turno':       forms.Select(attrs=_WS),
            'activa':      forms.CheckboxInput(attrs=_WC),
        }


DIAS_CHOICES = [
    (1, 'Lunes'),
    (2, 'Martes'),
    (3, 'Miércoles'),
    (4, 'Jueves'),
    (5, 'Viernes'),
]

DURACION_CHOICES = [
    (60,  '1 hora'),
    (90,  '1 hora 30 min'),
    (120, '2 horas'),
]


class ConfigGeneracionForm(forms.Form):
    dias = forms.MultipleChoiceField(
        choices=DIAS_CHOICES,
        label='Días lectivos',
        widget=forms.CheckboxSelectMultiple,
        initial=[1, 2, 3, 4, 5],
    )
    hora_inicio = forms.TimeField(
        label='Hora de inicio',
        initial='15:00',
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )
    hora_fin = forms.TimeField(
        label='Hora de finalización',
        initial='21:00',
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )
    duracion_min = forms.ChoiceField(
        choices=DURACION_CHOICES,
        label='Duración de cada sesión',
        initial=90,
    )

    def clean(self):
        cleaned = super().clean()
        hi = cleaned.get('hora_inicio')
        hf = cleaned.get('hora_fin')
        dur = int(cleaned.get('duracion_min', 90))
        if hi and hf:
            from datetime import datetime, timedelta
            start = datetime.combine(datetime.today(), hi)
            end = datetime.combine(datetime.today(), hf)
            if end <= start:
                raise forms.ValidationError('La hora de fin debe ser posterior a la de inicio.')
            total_min = (end - start).seconds // 60
            if total_min < dur:
                raise forms.ValidationError(
                    f'El rango horario ({total_min} min) es menor que la duración de sesión ({dur} min).'
                )
        if not cleaned.get('dias'):
            raise forms.ValidationError('Selecciona al menos un día lectivo.')
        return cleaned


class FiltroHorarioAlumnoForm(forms.Form):
    titulacion = forms.ModelChoiceField(
        queryset=Titulacion.objects.filter(activa=True),
        required=False,
        empty_label="Todas las titulaciones",
        widget=forms.Select(attrs=_WS),
    )
    semestre = forms.ChoiceField(
        choices=[('', 'Ambos semestres'), ('1', 'Primer semestre'), ('2', 'Segundo semestre')],
        required=False,
        widget=forms.Select(attrs=_WS),
    )
    tipo_grupo = forms.ChoiceField(
        choices=[('', 'Todos los grupos'), ('TEORIA', 'Teoría'), ('PRACTICAS', 'Prácticas'), ('LABORATORIO', 'Laboratorio')],
        required=False,
        widget=forms.Select(attrs=_WS),
    )


class TitulacionForm(forms.ModelForm):
    class Meta:
        model  = Titulacion
        fields = ['nombre', 'codigo', 'tipo', 'duracion_anios', 'permite_maniana', 'activa']
        widgets = {
            'nombre':          forms.TextInput(attrs={**_WI, 'placeholder': 'Ej: Grado en Ingeniería Informática'}),
            'codigo':          forms.TextInput(attrs={**_WI, 'placeholder': 'Ej: GII'}),
            'tipo':            forms.Select(attrs=_WS),
            'duracion_anios':  forms.NumberInput(attrs={**_WI, 'min': 3, 'max': 6}),
            'permite_maniana': forms.CheckboxInput(attrs=_WC),
            'activa':          forms.CheckboxInput(attrs=_WC),
        }


class AsignaturaForm(forms.ModelForm):
    titulacion = forms.ModelChoiceField(
        queryset=Titulacion.objects.filter(activa=True),
        label='Titulación',
        widget=forms.Select(attrs=_WS),
    )
    anio = forms.ChoiceField(
        choices=[(i, f'{i}º') for i in range(1, 6)],
        label='Año',
        widget=forms.Select(attrs=_WS),
    )

    class Meta:
        model  = Asignatura
        fields = ['codigo', 'nombre', 'semestre', 'tipo_grupo',
                  'sesiones_semanales', 'duracion_sesion_h', 'es_transversal']
        widgets = {
            'codigo':             forms.TextInput(attrs={**_WI, 'placeholder': 'Ej: GII-1-1-1'}),
            'nombre':             forms.TextInput(attrs={**_WI, 'placeholder': 'Nombre de la asignatura'}),
            'semestre':           forms.Select(attrs=_WS, choices=[(1, 'Primer semestre'), (2, 'Segundo semestre')]),
            'tipo_grupo':         forms.Select(attrs=_WS),
            'sesiones_semanales': forms.NumberInput(attrs={**_WI, 'min': 1, 'max': 5}),
            'duracion_sesion_h':  forms.NumberInput(attrs={**_WI, 'min': 1, 'max': 4}),
            'es_transversal':     forms.CheckboxInput(attrs=_WC),
        }

    def __init__(self, *args, titulacion=None, **kwargs):
        super().__init__(*args, **kwargs)
        if titulacion:
            self.fields['titulacion'].initial = titulacion
