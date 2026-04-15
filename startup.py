import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biblioteca_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from biblioteca.models import Libro, Autor, Categoria

User = get_user_model()

# Crear superusuario con credenciales seguras (cambiar en producción)
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser(
        "admin", "admin@biblioteca.com", os.environ.get("ADMIN_PASSWORD", "admin123")
    )
    print('[STARTUP] Superusuario "admin" creado')
else:
    print('[STARTUP] Superusuario "admin" ya existe')

# Precargar libros de ejemplo si la BD está vacía
if not Libro.objects.exists():
    print("[STARTUP] Cargando libros de ejemplo...")

    libros_ejemplo = [
        {
            "titulo": "Cien Años de Soledad",
            "ISBN": "978-0060883287",
            "descripcion": "La saga de la familia Buendía en Macondo, una obra maestra del realismo mágico.",
            "autores": ["Gabriel García Márquez"],
            "categorias": ["Ficción", "Clásico"],
            "portada_url": "https://covers.openlibrary.org/b/isbn/9780060883287-L.jpg",
        },
        {
            "titulo": "Don Quijote de la Mancha",
            "ISBN": "978-8420412146",
            "descripcion": "La aventura del Caballero de la Triste Figura y su escudero Sancho Panza.",
            "autores": ["Miguel de Cervantes"],
            "categorias": ["Clásico", "Aventura"],
            "portada_url": "https://covers.openlibrary.org/b/isbn/9788420412146-L.jpg",
        },
        {
            "titulo": "El Principito",
            "ISBN": "978-0156012195",
            "descripcion": "Un piloto encuentra a un príncipe en el desierto, una fábula sobre la vida.",
            "autores": ["Antoine de Saint-Exupéry"],
            "categorias": ["Ficción", "Fábula"],
            "portada_url": "https://covers.openlibrary.org/b/isbn/9780156012195-L.jpg",
        },
        {
            "titulo": "1984",
            "ISBN": "978-0451524935",
            "descripcion": "Una sociedad controlada por un régimen totalitario en un futuro sombrío.",
            "autores": ["George Orwell"],
            "categorias": ["Ciencia Ficción", "Distopía"],
            "portada_url": "https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg",
        },
        {
            "titulo": "El Hobbit",
            "ISBN": "978-0547928227",
            "descripcion": "Bilbo Bolsón emprende un viaje hacia la Montaña Solitaria.",
            "autores": ["J.R.R. Tolkien"],
            "categorias": ["Fantasía", "Aventura"],
            "portada_url": "https://covers.openlibrary.org/b/isbn/9780547928227-L.jpg",
        },
        {
            "titulo": "Orgullo y Prejuicio",
            "ISBN": "978-0141439518",
            "descripcion": "Las relaciones amorosas entre la familia Bennet y el Sr. Darcy.",
            "autores": ["Jane Austen"],
            "categorias": ["Romance", "Clásico"],
            "portada_url": "https://covers.openlibrary.org/b/isbn/9780141439518-L.jpg",
        },
        {
            "titulo": "El Código Da Vinci",
            "ISBN": "978-0307474278",
            "descripcion": "Un symbologist revela un misterio religioso en el Louvre.",
            "autores": ["Dan Brown"],
            "categorias": ["Misterio", "Thriller"],
            "portada_url": "https://covers.openlibrary.org/b/isbn/9780307474278-L.jpg",
        },
        {
            "titulo": "Harry Potter y la Piedra Filosofal",
            "ISBN": "978-0590353427",
            "descripcion": "Un joven mago descubre su herencia mágica en Hogwarts.",
            "autores": ["J.K. Rowling"],
            "categorias": ["Fantasía", "Aventura"],
            "portada_url": "https://covers.openlibrary.org/b/isbn/9780590353427-L.jpg",
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
            portada_url=data.get("portada_url", ""),
        )
        libro.autores.set(autores)
        libro.categorias.set(categorias)

    print(f"[STARTUP] {len(libros_ejemplo)} libros de ejemplo cargados")
else:
    print("[STARTUP] La base de datos ya tiene libros")
