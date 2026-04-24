import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Resetea la base de datos para modo demo (borra prestamos y limpia datos de usuarios)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Fuerza el reset sin verificar la última fecha",
        )

    def handle(self, *args, **options):
        from biblioteca.models import Prestamo, Libro
        from django.utils import timezone
        from datetime import timedelta
        import os

        # Verificar si es seguro hacer reset (cada 24h)
        last_reset_file = "/tmp/.demo_reset_lock"

        if not options["force"]:
            if os.path.exists(last_reset_file):
                last_reset = os.path.getmtime(last_reset_file)
                if timezone.now().timestamp() - last_reset < 86400:  # 24 horas
                    self.stdout.write(
                        self.style.WARNING(
                            "Reset automático omitido (menos de 24h desde el último)"
                        )
                    )
                    return

        # Contar antes
        prestamos_count = Prestamo.objects.count()
        libros_no_disponibles = Libro.objects.exclude(estado="Disponible").count()

        # Liberar todos los préstamos
        Prestamo.objects.all().delete()

        # Restaurar estado de libros
        for libro in Libro.objects.all():
            libro.estado = "Disponible"
            libro.stock = 1
            libro.save()

        # Marcar tiempo de reset
        with open(last_reset_file, "w") as f:
            f.write(str(timezone.now().timestamp()))

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Reset completado: {prestamos_count} préstamos eliminados, {libros_no_disponibles} libros restaurados"
            )
        )
