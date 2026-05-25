"""
Comando de inicialización de datos reales de la Escuela Politécnica UCJC.
Crea titulaciones, niveles, asignaturas y franjas horarias.
Idempotente: usa get_or_create en todos los pasos.

Uso:
    python manage.py seed_politecnica
    python manage.py seed_politecnica --flush   # borra datos previos
"""
import datetime
from django.core.management.base import BaseCommand
from core.models import (
    Titulacion, NivelCurso, Asignatura, AsignaturaTitulacion,
    CursoAcademico, FranjaHoraria, Aula,
)


# ── Titulaciones ──────────────────────────────────────────────────────────────

TITULACIONES = [
    {
        'nombre':         'Grado en Ingeniería Informática',
        'codigo':         'GII',
        'tipo':           'GRADO',
        'duracion_anios': 4,
        'permite_maniana': False,
    },
    {
        'nombre':         'Grado en Ingeniería Telemática',
        'codigo':         'GIT',
        'tipo':           'GRADO',
        'duracion_anios': 4,
        'permite_maniana': False,
    },
    {
        'nombre':         'Grado en Ingeniería Robótica e Inteligencia Artificial',
        'codigo':         'GRIA',
        'tipo':           'GRADO',
        'duracion_anios': 4,
        'permite_maniana': False,
    },
    {
        'nombre':         'Grado en Empresa y Tecnología',
        'codigo':         'GET',
        'tipo':           'GRADO',
        'duracion_anios': 4,
        'permite_maniana': False,
    },
]


# ── Plan de estudios: {codigo_tit: {anio: {semestre: [(cod, nombre, tipo)]}}} ─

PLAN = {

    'GII': {
        1: {
            1: [
                ('GII-1-1-1', 'Fundamentos de Programación',          'TEORIA'),
                ('GII-1-1-2', 'Álgebra Lineal y Matemática Discreta', 'TEORIA'),
                ('GII-1-1-3', 'Cálculo I',                            'TEORIA'),
                ('GII-1-1-4', 'Fundamentos de Computadores',          'TEORIA'),
                ('GII-1-1-5', 'Lógica para Informática',              'TEORIA'),
            ],
            2: [
                ('GII-1-2-1', 'Programación Orientada a Objetos',          'TEORIA'),
                ('GII-1-2-2', 'Cálculo II y Estadística',                  'TEORIA'),
                ('GII-1-2-3', 'Estructura de Computadores',                'TEORIA'),
                ('GII-1-2-4', 'Inglés para Ingeniería I',                  'TEORIA'),
                ('GII-1-2-5', 'Metodología y Tecnología de Programación',  'LABORATORIO'),
            ],
        },
        2: {
            1: [
                ('GII-2-1-1', 'Estructura de Datos y Algoritmos', 'TEORIA'),
                ('GII-2-1-2', 'Sistemas Operativos',              'TEORIA'),
                ('GII-2-1-3', 'Redes de Computadores',            'TEORIA'),
                ('GII-2-1-4', 'Bases de Datos I',                 'TEORIA'),
                ('GII-2-1-5', 'Diseño de Software',               'PRACTICAS'),
            ],
            2: [
                ('GII-2-2-1', 'Ingeniería del Software I',                 'TEORIA'),
                ('GII-2-2-2', 'Bases de Datos II',                         'LABORATORIO'),
                ('GII-2-2-3', 'Arquitectura de Computadores',              'TEORIA'),
                ('GII-2-2-4', 'Probabilidad y Estadística Informática',    'TEORIA'),
                ('GII-2-2-5', 'Programación Concurrente y Distribuida',    'PRACTICAS'),
            ],
        },
        3: {
            1: [
                ('GII-3-1-1', 'Ingeniería del Software II',  'TEORIA'),
                ('GII-3-1-2', 'Inteligencia Artificial',     'TEORIA'),
                ('GII-3-1-3', 'Sistemas Distribuidos',       'TEORIA'),
                ('GII-3-1-4', 'Seguridad Informática',       'TEORIA'),
                ('GII-3-1-5', 'Compiladores e Intérpretes',  'PRACTICAS'),
            ],
            2: [
                ('GII-3-2-1', 'Aprendizaje Automático',                    'TEORIA'),
                ('GII-3-2-2', 'Interacción Persona-Computador',            'TEORIA'),
                ('GII-3-2-3', 'Administración de Sistemas y Redes',        'LABORATORIO'),
                ('GII-3-2-4', 'Gestión de Proyectos Software',             'TEORIA'),
                ('GII-3-2-5', 'Inglés para Ingeniería II',                 'TEORIA'),
            ],
        },
        4: {
            1: [
                ('GII-4-1-1', 'Computación en la Nube y Big Data', 'TEORIA'),
                ('GII-4-1-2', 'Ciberseguridad Avanzada',           'TEORIA'),
                ('GII-4-1-3', 'Desarrollo de Aplicaciones Web',    'LABORATORIO'),
                ('GII-4-1-4', 'Ética y Legislación Informática',   'TEORIA'),
                ('GII-4-1-5', 'Trabajo Fin de Grado I',            'PRACTICAS'),
            ],
            2: [
                ('GII-4-2-1', 'Sistemas de Información Empresarial', 'TEORIA'),
                ('GII-4-2-2', 'Computación Cuántica',               'TEORIA'),
                ('GII-4-2-3', 'Emprendimiento Tecnológico',         'TEORIA'),
                ('GII-4-2-4', 'Visión Artificial',                  'LABORATORIO'),
                ('GII-4-2-5', 'Trabajo Fin de Grado II',            'PRACTICAS'),
            ],
        },
    },

    'GIT': {
        1: {
            1: [
                ('GIT-1-1-1', 'Fundamentos de Programación Telemática', 'TEORIA'),
                ('GIT-1-1-2', 'Álgebra Lineal',                         'TEORIA'),
                ('GIT-1-1-3', 'Cálculo I',                              'TEORIA'),
                ('GIT-1-1-4', 'Física I: Electromagnetismo',            'TEORIA'),
                ('GIT-1-1-5', 'Teoría de Circuitos Lineales',           'TEORIA'),
            ],
            2: [
                ('GIT-1-2-1', 'Programación de Aplicaciones',   'LABORATORIO'),
                ('GIT-1-2-2', 'Cálculo II y Ecuaciones Dif.',   'TEORIA'),
                ('GIT-1-2-3', 'Física II: Ondas y Óptica',      'TEORIA'),
                ('GIT-1-2-4', 'Electrónica Analógica',          'TEORIA'),
                ('GIT-1-2-5', 'Inglés para Ingeniería I',       'TEORIA'),
            ],
        },
        2: {
            1: [
                ('GIT-2-1-1', 'Redes Telemáticas I',      'TEORIA'),
                ('GIT-2-1-2', 'Sistemas Operativos',      'TEORIA'),
                ('GIT-2-1-3', 'Señales y Sistemas',       'TEORIA'),
                ('GIT-2-1-4', 'Electrónica Digital',      'LABORATORIO'),
                ('GIT-2-1-5', 'Microprocesadores',        'LABORATORIO'),
            ],
            2: [
                ('GIT-2-2-1', 'Redes Telemáticas II',         'TEORIA'),
                ('GIT-2-2-2', 'Teoría de la Comunicación',    'TEORIA'),
                ('GIT-2-2-3', 'Comunicaciones Digitales',     'TEORIA'),
                ('GIT-2-2-4', 'Sistemas Embebidos',           'LABORATORIO'),
                ('GIT-2-2-5', 'Estadística y Probabilidad',   'TEORIA'),
            ],
        },
        3: {
            1: [
                ('GIT-3-1-1', 'Seguridad en Redes',                   'TEORIA'),
                ('GIT-3-1-2', 'Gestión y Administración de Redes',    'TEORIA'),
                ('GIT-3-1-3', 'Ingeniería del Software Telemático',   'TEORIA'),
                ('GIT-3-1-4', 'Virtualización y Centros de Datos',    'LABORATORIO'),
                ('GIT-3-1-5', 'Protocolos de Red Avanzados',          'TEORIA'),
            ],
            2: [
                ('GIT-3-2-1', 'Ciberseguridad y Hacking Ético',   'LABORATORIO'),
                ('GIT-3-2-2', 'Redes SDN y NFV',                  'TEORIA'),
                ('GIT-3-2-3', 'Computación en la Nube',           'TEORIA'),
                ('GIT-3-2-4', 'Redes Inalámbricas y Móviles',     'TEORIA'),
                ('GIT-3-2-5', 'Gestión de Proyectos TIC',         'TEORIA'),
            ],
        },
        4: {
            1: [
                ('GIT-4-1-1', 'Análisis de Tráfico y QoS',              'TEORIA'),
                ('GIT-4-1-2', 'Internet de las Cosas (IoT)',             'LABORATORIO'),
                ('GIT-4-1-3', 'Procesado Digital de Señales',           'TEORIA'),
                ('GIT-4-1-4', 'Ética y Regulación en Telecomunicaciones','TEORIA'),
                ('GIT-4-1-5', 'Trabajo Fin de Grado I',                 'PRACTICAS'),
            ],
            2: [
                ('GIT-4-2-1', 'Servicios Telemáticos Avanzados',    'TEORIA'),
                ('GIT-4-2-2', 'Arquitecturas de Red Emergentes',    'TEORIA'),
                ('GIT-4-2-3', 'Innovación y Emprendimiento TIC',    'TEORIA'),
                ('GIT-4-2-4', 'Inglés para Ingeniería II',          'TEORIA'),
                ('GIT-4-2-5', 'Trabajo Fin de Grado II',            'PRACTICAS'),
            ],
        },
    },

    'GRIA': {
        1: {
            1: [
                ('GRIA-1-1-1', 'Fundamentos de Programación para Robótica', 'TEORIA'),
                ('GRIA-1-1-2', 'Álgebra Lineal y Geometría',               'TEORIA'),
                ('GRIA-1-1-3', 'Cálculo I',                                'TEORIA'),
                ('GRIA-1-1-4', 'Física I: Mecánica',                       'TEORIA'),
                ('GRIA-1-1-5', 'Introducción a la Robótica',               'LABORATORIO'),
            ],
            2: [
                ('GRIA-1-2-1', 'Programación Avanzada (Python/C++)',  'LABORATORIO'),
                ('GRIA-1-2-2', 'Cálculo II',                          'TEORIA'),
                ('GRIA-1-2-3', 'Física II: Electrónica y Energía',   'TEORIA'),
                ('GRIA-1-2-4', 'Electrónica para Robótica',           'LABORATORIO'),
                ('GRIA-1-2-5', 'Inglés para Ingeniería I',            'TEORIA'),
            ],
        },
        2: {
            1: [
                ('GRIA-2-1-1', 'Cinemática y Dinámica de Robots',   'TEORIA'),
                ('GRIA-2-1-2', 'Sistemas Operativos para Robótica', 'TEORIA'),
                ('GRIA-2-1-3', 'Percepción y Sensores',             'LABORATORIO'),
                ('GRIA-2-1-4', 'Inteligencia Artificial I',         'TEORIA'),
                ('GRIA-2-1-5', 'Electrónica de Potencia y Actuadores','LABORATORIO'),
            ],
            2: [
                ('GRIA-2-2-1', 'Planificación de Movimiento',       'TEORIA'),
                ('GRIA-2-2-2', 'Visión por Computador',             'LABORATORIO'),
                ('GRIA-2-2-3', 'Control de Robots',                 'TEORIA'),
                ('GRIA-2-2-4', 'Inteligencia Artificial II',        'TEORIA'),
                ('GRIA-2-2-5', 'Estadística y Probabilidad',        'TEORIA'),
            ],
        },
        3: {
            1: [
                ('GRIA-3-1-1', 'Aprendizaje Automático para Robótica',     'TEORIA'),
                ('GRIA-3-1-2', 'Robots Colaborativos (Cobots)',             'LABORATORIO'),
                ('GRIA-3-1-3', 'Sistemas de Control Avanzado',             'TEORIA'),
                ('GRIA-3-1-4', 'Integración de Sistemas Robóticos',        'PRACTICAS'),
                ('GRIA-3-1-5', 'ROS (Robot Operating System)',             'LABORATORIO'),
            ],
            2: [
                ('GRIA-3-2-1', 'Procesado del Lenguaje Natural',   'TEORIA'),
                ('GRIA-3-2-2', 'Robótica Autónoma y Navegación',  'LABORATORIO'),
                ('GRIA-3-2-3', 'Aprendizaje por Refuerzo',         'TEORIA'),
                ('GRIA-3-2-4', 'Ética en IA y Robótica',           'TEORIA'),
                ('GRIA-3-2-5', 'Gestión de Proyectos Robóticos',   'TEORIA'),
            ],
        },
        4: {
            1: [
                ('GRIA-4-1-1', 'Gemelos Digitales y Simulación',       'LABORATORIO'),
                ('GRIA-4-1-2', 'Edge AI y Computación Embebida',       'TEORIA'),
                ('GRIA-4-1-3', 'Robótica Industrial Avanzada',         'LABORATORIO'),
                ('GRIA-4-1-4', 'Interacción Humano-Robot (HRI)',        'TEORIA'),
                ('GRIA-4-1-5', 'Trabajo Fin de Grado I',               'PRACTICAS'),
            ],
            2: [
                ('GRIA-4-2-1', 'Robótica Médica y Asistencial',        'TEORIA'),
                ('GRIA-4-2-2', 'Drones y Sistemas Aéreos Autónomos',   'LABORATORIO'),
                ('GRIA-4-2-3', 'Innovación y Emprendimiento Tech',     'TEORIA'),
                ('GRIA-4-2-4', 'Inglés para Ingeniería II',            'TEORIA'),
                ('GRIA-4-2-5', 'Trabajo Fin de Grado II',              'PRACTICAS'),
            ],
        },
    },

    'GET': {
        1: {
            1: [
                ('GET-1-1-1', 'Fundamentos de Programación',      'TEORIA'),
                ('GET-1-1-2', 'Matemáticas Empresariales',        'TEORIA'),
                ('GET-1-1-3', 'Introducción a la Economía',       'TEORIA'),
                ('GET-1-1-4', 'Fundamentos de Empresa',           'TEORIA'),
                ('GET-1-1-5', 'Contabilidad Financiera I',        'TEORIA'),
            ],
            2: [
                ('GET-1-2-1', 'Bases de Datos para Empresas',    'LABORATORIO'),
                ('GET-1-2-2', 'Estadística Empresarial',          'TEORIA'),
                ('GET-1-2-3', 'Microeconomía',                    'TEORIA'),
                ('GET-1-2-4', 'Marketing Digital',                'TEORIA'),
                ('GET-1-2-5', 'Inglés para Negocios I',           'TEORIA'),
            ],
        },
        2: {
            1: [
                ('GET-2-1-1', 'Sistemas de Información Empresarial', 'TEORIA'),
                ('GET-2-1-2', 'Gestión Financiera',                  'TEORIA'),
                ('GET-2-1-3', 'Derecho Mercantil y Digital',         'TEORIA'),
                ('GET-2-1-4', 'Análisis y Visualización de Datos',   'LABORATORIO'),
                ('GET-2-1-5', 'Programación para Negocios',          'PRACTICAS'),
            ],
            2: [
                ('GET-2-2-1', 'Comercio Electrónico',                'TEORIA'),
                ('GET-2-2-2', 'Gestión de Recursos Humanos',         'TEORIA'),
                ('GET-2-2-3', 'Estrategia Empresarial',              'TEORIA'),
                ('GET-2-2-4', 'Inteligencia de Negocio (BI)',        'LABORATORIO'),
                ('GET-2-2-5', 'Fiscalidad y Contabilidad II',        'TEORIA'),
            ],
        },
        3: {
            1: [
                ('GET-3-1-1', 'Transformación Digital de Empresas',   'TEORIA'),
                ('GET-3-1-2', 'Gestión de Proyectos Tecnológicos',    'TEORIA'),
                ('GET-3-1-3', 'Ciberseguridad Empresarial',           'TEORIA'),
                ('GET-3-1-4', 'Marketing Tecnológico y Growth',       'TEORIA'),
                ('GET-3-1-5', 'Innovación y Modelos de Negocio',      'PRACTICAS'),
            ],
            2: [
                ('GET-3-2-1', 'Big Data y Analítica Empresarial',         'LABORATORIO'),
                ('GET-3-2-2', 'Logística y Supply Chain Digital',          'TEORIA'),
                ('GET-3-2-3', 'Economía Digital y Plataformas',            'TEORIA'),
                ('GET-3-2-4', 'Gestión del Talento en Empresas Tech',      'TEORIA'),
                ('GET-3-2-5', 'Inglés para Negocios II',                   'TEORIA'),
            ],
        },
        4: {
            1: [
                ('GET-4-1-1', 'Dirección Estratégica de TI',                'TEORIA'),
                ('GET-4-1-2', 'Emprendimiento y Startups Tecnológicas',     'PRACTICAS'),
                ('GET-4-1-3', 'Responsabilidad Social Corporativa Digital', 'TEORIA'),
                ('GET-4-1-4', 'Auditoría y Gobernanza de Sistemas',         'TEORIA'),
                ('GET-4-1-5', 'Trabajo Fin de Grado I',                     'PRACTICAS'),
            ],
            2: [
                ('GET-4-2-1', 'Fintech e Innovación Financiera',             'TEORIA'),
                ('GET-4-2-2', 'Consultoría Tecnológica',                     'PRACTICAS'),
                ('GET-4-2-3', 'Liderazgo y Transformación Organizacional',   'TEORIA'),
                ('GET-4-2-4', 'Internacionalización Digital',                'TEORIA'),
                ('GET-4-2-5', 'Trabajo Fin de Grado II',                     'PRACTICAS'),
            ],
        },
    },
}


# ── Franjas horarias (tarde: 15:00-21:00 en bloques de 2h) ───────────────────

DIAS = [0, 1, 2, 3, 4]  # lunes-viernes
FRANJAS_TARDE = [
    ('15:00', '17:00'),
    ('17:00', '19:00'),
    ('19:00', '21:00'),
]

AULAS_INICIALES = [
    {'codigo': 'A-101', 'nombre': 'Aula 101',       'capacidad': 60, 'tipo': 'TEORIA'},
    {'codigo': 'A-102', 'nombre': 'Aula 102',       'capacidad': 60, 'tipo': 'TEORIA'},
    {'codigo': 'A-103', 'nombre': 'Aula 103',       'capacidad': 60, 'tipo': 'TEORIA'},
    {'codigo': 'A-201', 'nombre': 'Aula 201',       'capacidad': 60, 'tipo': 'TEORIA'},
    {'codigo': 'A-202', 'nombre': 'Aula 202',       'capacidad': 40, 'tipo': 'TEORIA'},
    {'codigo': 'L-101', 'nombre': 'Lab Informática 1', 'capacidad': 30, 'tipo': 'LABORATORIO'},
    {'codigo': 'L-102', 'nombre': 'Lab Informática 2', 'capacidad': 30, 'tipo': 'LABORATORIO'},
    {'codigo': 'L-201', 'nombre': 'Lab Robótica',      'capacidad': 20, 'tipo': 'LABORATORIO'},
    {'codigo': 'L-202', 'nombre': 'Lab Redes',         'capacidad': 24, 'tipo': 'LABORATORIO'},
    {'codigo': 'S-101', 'nombre': 'Seminario 1',       'capacidad': 20, 'tipo': 'SEMINARIO'},
]

DIAS_NOMBRES = {0: 'Lun', 1: 'Mar', 2: 'Mié', 3: 'Jue', 4: 'Vie'}


class Command(BaseCommand):
    help = 'Carga el plan de estudios real de la Escuela Politécnica UCJC'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Elimina titulaciones, asignaturas y franjas antes de crear',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('Eliminando datos previos...')
            AsignaturaTitulacion.objects.all().delete()
            Asignatura.objects.all().delete()
            NivelCurso.objects.all().delete()
            Titulacion.objects.all().delete()
            FranjaHoraria.objects.all().delete()
            Aula.objects.all().delete()

        self._seed_curso_academico()
        self._seed_franjas()
        self._seed_aulas()
        self._seed_titulaciones()
        self.stdout.write(self.style.SUCCESS('Datos de la Escuela Politécnica cargados correctamente.'))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _seed_curso_academico(self):
        ca, created = CursoAcademico.objects.get_or_create(
            nombre='2025-2026',
            defaults={
                'fecha_inicio': datetime.date(2025, 9, 1),
                'fecha_fin':    datetime.date(2026, 6, 30),
                'estado':       'ACTIVO',
                'matriculacion_abierta': True,
            },
        )
        verb = 'Creado' if created else 'Ya existe'
        self.stdout.write(f'  {verb}: Curso académico {ca}')

    def _seed_franjas(self):
        n = 0
        for dia in DIAS:
            for hora_ini, hora_fin in FRANJAS_TARDE:
                hi = datetime.time(*map(int, hora_ini.split(':')))
                hf = datetime.time(*map(int, hora_fin.split(':')))
                nombre = f'Tarde-{DIAS_NOMBRES[dia]}-{hora_ini[:2]}h'
                _, created = FranjaHoraria.objects.get_or_create(
                    dia_semana=dia,
                    hora_inicio=hi,
                    hora_fin=hf,
                    defaults={'nombre': nombre, 'turno': 'TARDE', 'activa': True},
                )
                if created:
                    n += 1
        self.stdout.write(f'  Franjas creadas: {n} (tarde, L-V)')

    def _seed_aulas(self):
        n = 0
        for a in AULAS_INICIALES:
            _, created = Aula.objects.get_or_create(
                codigo=a['codigo'],
                defaults={
                    'nombre':    a['nombre'],
                    'capacidad': a['capacidad'],
                    'tipo':      a['tipo'],
                    'activa':    True,
                },
            )
            if created:
                n += 1
        self.stdout.write(f'  Aulas creadas: {n}')

    def _seed_titulaciones(self):
        for tit_data in TITULACIONES:
            tit, created = Titulacion.objects.get_or_create(
                codigo=tit_data['codigo'],
                defaults={
                    'nombre':          tit_data['nombre'],
                    'tipo':            tit_data['tipo'],
                    'duracion_anios':  tit_data['duracion_anios'],
                    'permite_maniana': tit_data['permite_maniana'],
                    'activa':          True,
                },
            )
            verb = 'Creada' if created else 'Ya existe'
            self.stdout.write(f'\n  {verb}: {tit.nombre}')

            # Niveles (1º–4º)
            for anio in range(1, tit_data['duracion_anios'] + 1):
                nivel, _ = NivelCurso.objects.get_or_create(
                    titulacion=tit,
                    anio=anio,
                    defaults={'es_ultimo': anio == tit_data['duracion_anios']},
                )

            # Asignaturas
            plan_tit = PLAN.get(tit_data['codigo'], {})
            total_asig = 0
            for anio, semestres in plan_tit.items():
                nivel = NivelCurso.objects.get(titulacion=tit, anio=anio)
                for semestre, asigs in semestres.items():
                    for cod, nombre, tipo in asigs:
                        asig, _ = Asignatura.objects.get_or_create(
                            codigo=cod,
                            defaults={
                                'nombre':             nombre,
                                'sesiones_semanales': 2,
                                'duracion_sesion_h':  2,
                                'tipo_grupo':         tipo,
                                'es_transversal':     False,
                                'semestre':           semestre,
                            },
                        )
                        AsignaturaTitulacion.objects.get_or_create(
                            asignatura=asig,
                            titulacion=tit,
                            nivel=nivel,
                        )
                        total_asig += 1

            self.stdout.write(f'    Asignaturas vinculadas: {total_asig}')
