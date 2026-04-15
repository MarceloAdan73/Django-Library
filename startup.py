import os
import django
import secrets
import string

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biblioteca_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from biblioteca.models import Libro, Autor, Categoria

User = get_user_model()

CREDENTIALS_FILE = ".admin_credentials"


def generate_secure_password(length=16):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def save_credentials(username, password):
    """Save credentials to a local file (not tracked by git)."""
    with open(CREDENTIALS_FILE, "w") as f:
        f.write(f"USERNAME={username}\n")
        f.write(f"PASSWORD={password}\n")
    print(f"[STARTUP] Credentials saved to {CREDENTIALS_FILE}")


def load_credentials():
    """Load credentials from file if exists."""
    if os.path.exists(CREDENTIALS_FILE):
        creds = {}
        with open(CREDENTIALS_FILE, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    creds[key] = value
        return creds.get("USERNAME"), creds.get("PASSWORD")
    return None, None


def create_admin_user():
    """Create admin user with secure credentials."""
    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@biblioteca.com")
    admin_password_env = os.environ.get("ADMIN_PASSWORD")
    admin_password_file, _ = load_credentials()

    if not User.objects.filter(username=admin_username).exists():
        if admin_password_env:
            password = admin_password_env
            print("[STARTUP] Using admin password from environment variable")
        elif admin_password_file:
            password = admin_password_file
            print("[STARTUP] Using admin password from credentials file")
        else:
            password = generate_secure_password()
            print("[STARTUP] Generated new secure password")
            print("[STARTUP] IMPORTANT: Save these credentials!")
            save_credentials(admin_username, password)

        User.objects.create_superuser(admin_username, admin_email, password)
        print(f'[STARTUP] Admin user "{admin_username}" created')
    else:
        print("[STARTUP] Admin user already exists")


def load_sample_books():
    """Load sample books - always ensures they exist."""
    print("[STARTUP] Loading sample books...")

    libros_ejemplo = [
            {
                "titulo": "Cien Años de Soledad",
                "ISBN": "978-0060883287",
                "descripcion": "La saga de la familia Buendía en Macondo.",
                "autores": ["Gabriel García Márquez"],
                "categorias": ["Ficción", "Clásico"],
                "portada_url": "https://covers.openlibrary.org/b/isbn/9780060883287-L.jpg",
            },
            {
                "titulo": "Don Quijote de la Mancha",
                "ISBN": "978-8420412146",
                "descripcion": "La aventura del Caballero de la Triste Figura.",
                "autores": ["Miguel de Cervantes"],
                "categorias": ["Clásico", "Aventura"],
                "portada_url": "https://covers.openlibrary.org/b/isbn/9780142437230-L.jpg",
            },
            {
                "titulo": "El Principito",
                "ISBN": "978-0156012195",
                "descripcion": "Un piloto encuentra a un príncipe en el desierto.",
                "autores": ["Antoine de Saint-Exupéry"],
                "categorias": ["Ficción", "Fábula"],
                "portada_url": "https://covers.openlibrary.org/b/isbn/9780156012195-L.jpg",
            },
            {
                "titulo": "1984",
                "ISBN": "978-0451524935",
                "descripcion": "Una sociedad controlada por un régimen totalitario.",
                "autores": ["George Orwell"],
                "categorias": ["Ciencia Ficción", "Distopía"],
                "portada_url": "https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg",
            },
            {
                "titulo": "El Hobbit",
                "ISBN": "978-0547928227",
                "descripcion": "Bilbo Bolsón emprende un viaje épico.",
                "autores": ["J.R.R. Tolkien"],
                "categorias": ["Fantasía", "Aventura"],
                "portada_url": "https://covers.openlibrary.org/b/isbn/9780547928227-L.jpg",
            },
            {
                "titulo": "Orgullo y Prejuicio",
                "ISBN": "978-0141439518",
                "descripcion": "Las relaciones amorosas entre la familia Bennet.",
                "autores": ["Jane Austen"],
                "categorias": ["Romance", "Clásico"],
                "portada_url": "https://covers.openlibrary.org/b/isbn/9780141439518-L.jpg",
            },
            {
                "titulo": "El Código Da Vinci",
                "ISBN": "978-0307474278",
                "descripcion": "Un symbologist revela un misterio religioso.",
                "autores": ["Dan Brown"],
                "categorias": ["Misterio", "Thriller"],
                "portada_url": "https://covers.openlibrary.org/b/isbn/9780307474278-L.jpg",
            },
            {
                "titulo": "Harry Potter y la Piedra Filosofal",
                "ISBN": "978-0590353427",
                "descripcion": "Un joven mago descubre su herencia mágica.",
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

            libro, created = Libro.objects.get_or_create(
                ISBN=data["ISBN"],
                defaults={
                    "titulo": data["titulo"],
                    "descripcion": data["descripcion"],
                    "estado": "Disponible",
                    "stock": 1,
                    "portada_url": data.get("portada_url", ""),
                },
            )
            libro.autores.set(autores)
            libro.categorias.set(categorias)

        print(f"[STARTUP] {len(libros_ejemplo)} sample books ready")
    else:
        print("[STARTUP] Sample books already exist")


if __name__ == "__main__":
    print("=" * 50)
    print("Digital Library - Setup")
    print("=" * 50)
    create_admin_user()
    load_sample_books()
    print("=" * 50)
    print("Setup complete!")
    print("=" * 50)
