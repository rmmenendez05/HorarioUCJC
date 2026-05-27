from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Crea el usuario decano por defecto si no existe.'

    def handle(self, *args, **options):
        from login.models import Usuario, PerfilDecano

        with transaction.atomic():
            u, created = Usuario.objects.get_or_create(
                email='decano@ucjc.edu',
                defaults={
                    'username':     'decano',
                    'first_name':   'Decano',
                    'last_name':    'UCJC',
                    'rol':          'DECANO',
                    'is_staff':     True,
                    'is_superuser': True,
                },
            )
            if created:
                u.set_password('ucjc2025!')
                u.save(update_fields=['password'])
                self.stdout.write(self.style.SUCCESS('Decano creado: decano@ucjc.edu / ucjc2025!'))
            else:
                self.stdout.write('Decano ya existía, no se modificó.')

            PerfilDecano.objects.get_or_create(usuario=u)
