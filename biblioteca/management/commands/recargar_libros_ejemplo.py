import logging
from django.core.management.base import BaseCommand
from biblioteca.models import Libro, Autor, Categoria

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Precarga libros de ejemplo en la base de datos"

    def handle(self, *args, **options):
        if Libro.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Ya existen libros en la base de datos. Omitiendo precarga."
                )
            )
            return

        libros_ejemplo = [
            {
                "titulo": "Cien Años de Soledad",
                "ISBN": "978-0060883287",
                "descripcion": "La saga de la familia Buendía en Macondo, una obra maestra del realismo mágico.",
                "autores": ["Gabriel García Márquez"],
                "categorias": ["Ficción", "Clásico"],
            },
            {
                "titulo": "Don Quijote de la Mancha",
                "ISBN": "978-8420412146",
                "descripcion": "La aventura del Caballero de la Triste Figura y su escudero Sancho Panza.",
                "autores": ["Miguel de Cervantes"],
                "categorias": ["Clásico", "Aventura"],
            },
            {
                "titulo": "El Principito",
                "ISBN": "978-0156012195",
                "descripcion": "Un piloto encuentra a un principe en el desierto, una fábula sobre la vida.",
                "autores": ["Antoine de Saint-Exupéry"],
                "categorias": ["Ficción", "Fábula"],
            },
            {
                "titulo": "1984",
                "ISBN": "978-0451524935",
                "descripcion": "Una sociedad controlada por un régimen totalitario en un futuro sombrío.",
                "autores": ["George Orwell"],
                "categorias": ["Ciencia Ficción", "Distopía"],
            },
            {
                "titulo": "El Hobbit",
                "ISBN": "978-0547928227",
                "descripcion": "Bilbo Bolsón emprende un viaje hacia la Montaña Solitaria.",
                "autores": ["J.R.R. Tolkien"],
                "categorias": ["Fantasía", "Aventura"],
            },
            {
                "titulo": "Orgullo y Prejuicio",
                "ISBN": "978-0141439518",
                "descripcion": "Las relaciones amorosas entre la familia Bennet y el Sr. Darcy.",
                "autores": ["Jane Austen"],
                "categorias": ["Romance", "Clásico"],
            },
            {
                "titulo": "El Código Da Vinci",
                "ISBN": "978-0307474278",
                "descripcion": "Un symbologist revela un misterio religiosas en el Louvre.",
                "autores": ["Dan Brown"],
                "categorias": ["Misterio", "Thriller"],
            },
            {
                "titulo": "Harry Potter y la Piedra Filosofal",
                "ISBN": "978-0590353427",
                "descripcion": "Un joven mago descubre su herencia mágica en Hogwarts.",
                "autores": ["J.K. Rowling"],
                "categorias": ["Fantasía", "Aventura"],
            },
        ]

        colores = ["#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899"]

        for i, data in enumerate(libros_ejemplo):
            autores = []
            for nombre_autor in data["autores"]:
                autor, _ = Autor.objects.get_or_create(
                    nombre=nombre_autor,
                    defaults={
                        "nacionalidad": "Desconocida",
                        "biografia": f"Autor de {data['titulo']}",
                    },
                )
                autores.append(autor)

            categorias = []
            for nombre_cat in data["categorias"]:
                cat, _ = Categoria.objects.get_or_create(
                    nombre=nombre_cat,
                    defaults={
                        "descripcion": f"Libros de {nombre_cat}",
                        "color": colores[i % len(colores)],
                    },
                )
                categorias.append(cat)

            libro = Libro.objects.create(
                titulo=data["titulo"],
                ISBN=data["ISBN"],
                descripcion=data["descripcion"],
                estado="Disponible",
                stock=1,
            )
            libro.autores.set(autores)
            libro.categorias.set(categorias)

        self.stdout.write(
            self.style.SUCCESS(
                f"Se precargaron {len(libros_ejemplo)} libros de ejemplo"
            )
        )
