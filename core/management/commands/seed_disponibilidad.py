"""
Genera disponibilidad automática para todos los profesores.
Por defecto marca todas las franjas de tarde (L-V) como DISPONIBLE.
Opcionalmente introduce variabilidad: algunos profesores tienen
franjas PREFERENTE o INDISPONIBLE para que el GA tenga datos reales.

Uso:
    python manage.py seed_disponibilidad
    python manage.py seed_disponibilidad --flush   # borra y recrea
    python manage.py seed_disponibilidad --variado # añade preferentes e indisponibles
"""
import random
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import DisponibilidadProfesor, FranjaHoraria, CursoAcademico
from login.models import PerfilProfesor

# Semilla fija para reproducibilidad
SEED = 42


class Command(BaseCommand):
    help = 'Genera disponibilidad automática para todos los profesores'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true',
                            help='Elimina disponibilidades existentes antes de crear')
        parser.add_argument('--variado', action='store_true',
                            help='Introduce franjas preferentes e indisponibles realistas')

    def handle(self, *args, **options):
        curso = CursoAcademico.objects.filter(nombre='2025-2026').first()
        if not curso:
            self.stderr.write("CursoAcademico '2025-2026' no encontrado. Ejecuta seed_politecnica primero.")
            return

        franjas = list(FranjaHoraria.objects.filter(activa=True).order_by('dia_semana', 'hora_inicio'))
        if not franjas:
            self.stderr.write("No hay franjas horarias. Ejecuta seed_politecnica primero.")
            return

        profesores = list(PerfilProfesor.objects.select_related('usuario').all())
        if not profesores:
            self.stderr.write("No hay profesores. Ejecuta seed_profesores primero.")
            return

        if options['flush']:
            n, _ = DisponibilidadProfesor.objects.filter(curso_academico=curso).delete()
            self.stdout.write(f'Flush: {n} disponibilidades eliminadas.')

        rng = random.Random(SEED)

        with transaction.atomic():
            total = self._seed(profesores, franjas, curso, options['variado'], rng)

        self.stdout.write(self.style.SUCCESS(
            f'OK — {total} disponibilidades creadas para {len(profesores)} profesores.'
        ))

    def _seed(self, profesores, franjas, curso, variado, rng):
        total = 0

        for profesor in profesores:
            # Con --variado cada profesor bloquea 1-3 franjas al azar
            # y marca 2-4 como preferentes
            if variado:
                indisponibles = set(rng.sample(range(len(franjas)), k=rng.randint(1, 3)))
                preferentes   = set(rng.sample(
                    [i for i in range(len(franjas)) if i not in indisponibles],
                    k=min(rng.randint(2, 4), len(franjas) - len(indisponibles))
                ))
            else:
                indisponibles = set()
                preferentes   = set()

            for idx, franja in enumerate(franjas):
                if idx in indisponibles:
                    tipo = DisponibilidadProfesor.TipoDisponibilidad.INDISPONIBLE
                elif idx in preferentes:
                    tipo = DisponibilidadProfesor.TipoDisponibilidad.PREFERENTE
                else:
                    tipo = DisponibilidadProfesor.TipoDisponibilidad.DISPONIBLE

                _, created = DisponibilidadProfesor.objects.get_or_create(
                    profesor=profesor,
                    curso_academico=curso,
                    dia_semana=franja.dia_semana,
                    hora_inicio=franja.hora_inicio,
                    hora_fin=franja.hora_fin,
                    defaults={'tipo': tipo},
                )
                if created:
                    total += 1

            self.stdout.write(f'  {profesor.usuario.get_full_name() or profesor.usuario.email}')

        return total
