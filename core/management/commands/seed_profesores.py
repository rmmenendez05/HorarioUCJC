"""
Genera cuentas de profesor inventadas y las asigna a las asignaturas del plan de estudios.
Cada asignatura recibe exactamente un profesor titular.
Los profesores se agrupan por área de conocimiento y cubren varias asignaturas afines.

Uso:
    python manage.py seed_profesores           # idempotente
    python manage.py seed_profesores --flush   # borra todo y recrea
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    Asignatura, AsignacionProfesor, CursoAcademico,
)
from login.models import Usuario, PerfilProfesor

PASSWORD = "ucjc2025!"

# (nombre, apellidos, area_conocimiento, palabras_clave_en_nombre_asignatura)
PROFESORES = [
    # Matemáticas / Estadística
    ("Ana",       "García López",      "Matemáticas y Estadística",
     ["álgebra", "cálculo", "estadística", "matemática", "probabilidad", "optimización"]),
    ("Carlos",    "Martínez Ruiz",     "Matemáticas y Estadística",
     ["matemática", "álgebra", "cálculo", "estadística", "modelos matemáticos"]),

    # Programación / Software
    ("Laura",     "Sánchez Pérez",     "Ingeniería del Software",
     ["programación", "software", "algoritmos", "compiladores", "intérpretes", "paradigmas"]),
    ("Javier",    "López Fernández",   "Ingeniería del Software",
     ["ingeniería del software", "pruebas", "metodologías", "gestión de proyectos", "desarrollo"]),
    ("María",     "González Torres",   "Ingeniería del Software",
     ["programación orientada", "estructuras de datos", "algorítmica"]),

    # Sistemas / Redes / Telecomunicaciones
    ("Pedro",     "Rodríguez Gómez",   "Redes y Telecomunicaciones",
     ["redes", "telecomunicaciones", "protocolos", "seguridad en red", "tráfico", "qos",
      "emergentes", "inalámbricas", "5g", "vpn", "routing"]),
    ("Lucía",     "Díaz Moreno",       "Redes y Telecomunicaciones",
     ["administración de sistemas", "sistemas operativos", "virtualización", "cloud",
      "servicios en la nube"]),
    ("Tomás",     "Fernández Jiménez", "Redes y Telecomunicaciones",
     ["ciberseguridad", "hacking", "seguridad", "criptografía", "auditoría"]),

    # Inteligencia Artificial / Machine Learning
    ("Sofía",     "Martín Álvarez",    "Inteligencia Artificial",
     ["inteligencia artificial", "machine learning", "aprendizaje automático",
      "aprendizaje profundo", "redes neuronales", "nlp", "lenguaje natural"]),
    ("Diego",     "Herrera Castillo",  "Inteligencia Artificial",
     ["aprendizaje por refuerzo", "visión por computador", "visión artificial",
      "reconocimiento", "deep learning"]),
    ("Elena",     "Ruiz Morales",      "Inteligencia Artificial",
     ["sistemas inteligentes", "lógica difusa", "agentes", "planificación automática",
      "big data", "analítica"]),

    # Robótica / Control
    ("Andrés",    "Vargas Palacios",   "Robótica e Ingeniería de Control",
     ["robótica", "robots", "cinemática", "dinámica", "control", "percepción",
      "sensores", "actuadores"]),
    ("Natalia",   "Blanco Serrano",    "Robótica e Ingeniería de Control",
     ["automatización", "sistemas de control", "electrónica", "microcontroladores",
      "programación de robots"]),

    # Bases de Datos / Sistemas de Información
    ("Alberto",   "Castro Delgado",    "Sistemas de Información",
     ["bases de datos", "sistemas de información", "data warehouse", "nosql",
      "minería de datos", "análisis de datos", "visualización"]),

    # Empresas / Gestión tecnológica
    ("Beatriz",   "Ortega Fuentes",    "Empresa y Tecnología",
     ["empresa", "gestión", "economía", "marketing", "comercio", "dirección",
      "emprendimiento", "estrategia", "gobernanza", "auditoría y gobernanza"]),
    ("Raúl",      "Iglesias Vega",     "Empresa y Tecnología",
     ["administración de empresas", "contabilidad", "finanzas", "erp",
      "transformación digital", "innovación"]),

    # Hardware / Arquitectura
    ("Carmen",    "Núñez Aguilar",     "Arquitectura de Computadores",
     ["arquitectura", "computadores", "hardware", "microprocesadores",
      "sistemas embebidos", "fpga"]),

    # Matemáticas discretas / Teoría
    ("Ignacio",   "Prieto Sanz",       "Fundamentos Teóricos",
     ["matemática discreta", "teoría de grafos", "lógica", "teoría de la computación",
      "computación", "cuántica", "fundamentos"]),

    # Interacción / UX / Web
    ("Silvia",    "Molina Gutiérrez",  "Tecnologías Web e Interacción",
     ["interfaces", "usabilidad", "ux", "diseño", "web", "frontend",
      "interacción", "multimedia"]),

    # Telecomunicaciones señales
    ("Hugo",      "Lozano Campos",     "Señales y Comunicaciones",
     ["señales", "comunicaciones", "transmisión", "antenas", "radio", "fibra",
      "procesamiento de señal"]),
]


def _slug(nombre, apellidos):
    """email-safe slug from name"""
    import unicodedata
    raw = f"{nombre}.{apellidos.split()[0]}".lower()
    nfkd = unicodedata.normalize("NFKD", raw)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).replace(" ", "")


def _matches(asig_nombre: str, keywords: list[str]) -> bool:
    name_lower = asig_nombre.lower()
    return any(kw in name_lower for kw in keywords)


class Command(BaseCommand):
    help = "Genera profesores inventados y los asigna a las asignaturas"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true",
                            help="Elimina profesores y asignaciones generadas antes de recrear")

    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()

        curso = CursoAcademico.objects.filter(nombre="2025-2026").first()
        if not curso:
            self.stderr.write("CursoAcademico '2025-2026' no encontrado. Ejecuta seed_politecnica primero.")
            return

        with transaction.atomic():
            perfiles = self._create_professors()
            self._assign_subjects(perfiles, curso)

        self.stdout.write(self.style.SUCCESS("OK Profesores generados y asignados correctamente."))

    def _flush(self):
        emails = [f"{_slug(n, a)}@ucjc.edu" for n, a, _, _ in PROFESORES]
        deleted, _ = Usuario.objects.filter(email__in=emails).delete()
        self.stdout.write(f"Flush: {deleted} usuarios eliminados.")

    def _create_professors(self):
        perfiles = []
        for nombre, apellidos, area, keywords in PROFESORES:
            email = f"{_slug(nombre, apellidos)}@ucjc.edu"
            usuario, created = Usuario.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": nombre,
                    "last_name": apellidos,
                    "rol": "PROFESOR",
                    "is_active": True,
                }
            )
            if created:
                usuario.set_password(PASSWORD)
                usuario.save()
                self.stdout.write(f"  + Creado: {nombre} {apellidos} <{email}>")
            else:
                self.stdout.write(f"  · Ya existe: {email}")

            perfil, _ = PerfilProfesor.objects.get_or_create(
                usuario=usuario,
                defaults={"area_conocimiento": area, "es_suplente": False}
            )
            perfiles.append((perfil, area, keywords))

        return perfiles

    def _assign_subjects(self, perfiles, curso):
        asignaturas = list(Asignatura.objects.all())
        assigned = set()
        total = 0

        # First pass: assign by keyword match
        for perfil, area, keywords in perfiles:
            for asig in asignaturas:
                if asig.pk in assigned:
                    continue
                if _matches(asig.nombre, keywords):
                    _, created = AsignacionProfesor.objects.get_or_create(
                        profesor=perfil,
                        asignatura=asig,
                        curso_academico=curso,
                        defaults={"tipo": "TITULAR"}
                    )
                    assigned.add(asig.pk)
                    if created:
                        total += 1

        # Second pass: round-robin for unassigned subjects
        unassigned = [a for a in asignaturas if a.pk not in assigned]
        if unassigned:
            self.stdout.write(f"  Asignando {len(unassigned)} asignaturas sin match por rotacion...")
            for i, asig in enumerate(unassigned):
                perfil, _, _ = perfiles[i % len(perfiles)]
                _, created = AsignacionProfesor.objects.get_or_create(
                    profesor=perfil,
                    asignatura=asig,
                    curso_academico=curso,
                    defaults={"tipo": "TITULAR"}
                )
                if created:
                    total += 1

        self.stdout.write(f"  Asignaciones creadas: {total}")
