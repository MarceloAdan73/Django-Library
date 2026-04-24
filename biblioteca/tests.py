from django.test import TestCase
from django.contrib.auth import get_user_model
from biblioteca.models import Libro, Autor, Categoria, Prestamo, Resena
from unittest.mock import patch, MagicMock


User = get_user_model()


class ModeloAutorTestCase(TestCase):
    def setUp(self):
        self.autor = Autor.objects.create(
            nombre="Gabriel",
            apellido="Garcia Marquez",
            nacionalidad="Colombiano",
            biografia="Nobel de Literatura"
        )

    def test_autor_str(self):
        self.assertEqual(str(self.autor), "Gabriel Garcia Marquez")

    def test_autor_verbose_name_plural(self):
        self.assertEqual(Autor._meta.verbose_name_plural, "Autores")

    def test_autor_create(self):
        self.assertEqual(Autor.objects.count(), 1)


class ModeloCategoriaTestCase(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nombre="Ficcion",
            descripcion="Libros de ficcion",
            color="#FF0000"
        )

    def test_categoria_str(self):
        self.assertEqual(str(self.categoria), "Ficcion")

    def test_categoria_verbose_name_plural(self):
        self.assertEqual(Categoria._meta.verbose_name_plural, "Categorías")

    def test_categoria_default_color(self):
        cat = Categoria.objects.create(nombre="Test")
        self.assertEqual(cat.color, "#3B82F6")


class ModeloLibroTestCase(TestCase):
    def setUp(self):
        self.autor = Autor.objects.create(nombre="Autor", apellido="Test")
        self.categoria = Categoria.objects.create(nombre="Categoria Test")
        self.libro = Libro.objects.create(
            titulo="Test Book",
            ISBN="978-3-16-148410-0",
            descripcion="Test description",
            estado="Disponible",
            stock=3
        )
        self.libro.autores.add(self.autor)
        self.libro.categorias.add(self.categoria)

    def test_libro_str(self):
        self.assertEqual(str(self.libro), "Test Book")

    def test_libro_verbose_name_plural(self):
        self.assertEqual(Libro._meta.verbose_name_plural, "Libros")

    def test_libro_get_portada_url(self):
        url = self.libro.get_portada_url()
        self.assertIsInstance(url, str)

    def test_libro_get_portada_url_con_portada(self):
        self.libro.portada_url = "https://example.com/cover.jpg"
        self.libro.save()
        url = self.libro.get_portada_url()
        self.assertEqual(url, "https://example.com/cover.jpg")

    def test_libro_get_portada_url_sin_portada(self):
        url = self.libro.get_portada_url()
        self.assertIn("via.placeholder.com", url)

    def test_libro_estados(self):
        self.assertEqual(Libro.ESTADOS[0], ("Disponible", "Disponible"))
        self.assertEqual(Libro.ESTADOS[1], ("Prestado", "Prestado"))

    def test_libro_stock_default(self):
        nuevo_libro = Libro.objects.create(titulo="Nuevo")
        self.assertEqual(nuevo_libro.stock, 1)

    def test_libro_relaciones_m2m(self):
        self.assertEqual(self.libro.autores.count(), 1)
        self.assertEqual(self.libro.categorias.count(), 1)


class VistaIndexTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.autor = Autor.objects.create(nombre="Test Author")
        self.categoria = Categoria.objects.create(nombre="Test Category")

    def test_index_sin_libros(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_libros", response.context)
        self.assertEqual(response.context["total_libros"], 0)

    def test_index_con_libros(self):
        Libro.objects.create(titulo="Book 1", estado="Disponible", stock=1)
        response = self.client.get("/")
        self.assertEqual(response.context["total_libros"], 1)
        self.assertEqual(response.context["total_disponibles"], 1)


class VistaLibroListTestCase(TestCase):
    def setUp(self):
        self.autor = Autor.objects.create(nombre="Test Author")
        self.categoria = Categoria.objects.create(nombre="Test Category")
        Libro.objects.create(titulo="Book 1", estado="Disponible", stock=1)
        Libro.objects.create(titulo="Book 2", estado="Prestado", stock=0)

    def test_libro_list(self):
        response = self.client.get("/libros/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["libros"]), 2)

    def test_libro_list_incluye_categorias(self):
        response = self.client.get("/libros/")
        self.assertIn("categorias", response.context)


class VistaLibroDetailTestCase(TestCase):
    def setUp(self):
        self.autor = Autor.objects.create(nombre="Test Author")
        self.libro = Libro.objects.create(titulo="Test Book", stock=1)

    def test_libro_detail(self):
        response = self.client.get(f"/libros/{self.libro.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["libro"], self.libro)

    def test_libro_detail_404(self):
        response = self.client.get("/libros/99999/")
        self.assertEqual(response.status_code, 404)


class VistaLoginTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_login_get(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_login_post_valido(self):
        response = self.client.post("/accounts/login/", {
            "username": "testuser",
            "password": "testpass"
        })
        self.assertRedirects(response, "/")

    def test_login_post_invalido(self):
        response = self.client.post("/accounts/login/", {
            "username": "wrong",
            "password": "wrong"
        })
        self.assertEqual(response.status_code, 200)


class GoogleBooksAPITestCase(TestCase):
    @patch("biblioteca.google_books.requests.Session")
    def test_buscar_libros_exito(self, mock_session_class):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {"volumeInfo": {"title": "Test Book", "authors": ["Author"]}}
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        from biblioteca.google_books import GoogleBooksAPI
        api = GoogleBooksAPI()
        result = api.buscar_libros("test")

        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 1)

    @patch("biblioteca.google_books.requests.Session")
    def test_buscar_libros_vacio(self, mock_session_class):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        from biblioteca.google_books import GoogleBooksAPI
        api = GoogleBooksAPI()
        result = api.buscar_libros("empty")

        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 0)

    @patch("biblioteca.google_books.requests.Session")
    def test_buscar_libros_timeout(self, mock_session_class):
        import requests
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.Timeout()
        mock_session_class.return_value = mock_session

        from biblioteca.google_books import GoogleBooksAPI
        api = GoogleBooksAPI()
        result = api.buscar_libros("test")

        self.assertIn("error", result)
        self.assertIn("Timeout", result["error"])

    def test_importar_libro_desde_api(self):
        from biblioteca.google_books import GoogleBooksAPI
        api = GoogleBooksAPI()

        book_data = {
            "volumeInfo": {
                "title": "Test Book",
                "authors": ["Test Author"],
                "categories": ["Ficcion"],
                "description": "Test description",
                "industryIdentifiers": [
                    {"type": "ISBN_13", "identifier": "978-3-16-148410-0"}
                ],
                "imageLinks": {
                    "thumbnail": "https://example.com/cover.jpg"
                }
            }
        }

        libro = api.importar_libro_desde_api(book_data)

        self.assertIsNotNone(libro)
        self.assertEqual(libro.titulo, "Test Book")
        self.assertEqual(libro.ISBN, "978-3-16-148410-0")
        self.assertEqual(libro.autores.count(), 1)
        self.assertEqual(libro.categorias.count(), 1)

    def test_importar_libro_sin_titulo(self):
        from biblioteca.google_books import GoogleBooksAPI
        api = GoogleBooksAPI()

        book_data = {"volumeInfo": {}}
        libro = api.importar_libro_desde_api(book_data)

        self.assertIsNone(libro)

    def test_importar_libro_dublicado(self):
        from biblioteca.google_books import GoogleBooksAPI
        api = GoogleBooksAPI()

        book_data = {
            "volumeInfo": {
                "title": "Duplicate Book",
                "authors": ["Author"],
                "categories": ["Ficcion"],
                "industryIdentifiers": [
                    {"type": "ISBN_13", "identifier": "978-3-16-148410-0"}
                ],
                "imageLinks": {
                    "thumbnail": "https://example.com/cover.jpg"
                }
            }
        }

        api.importar_libro_desde_api(book_data)
        libro2 = api.importar_libro_desde_api(book_data)

        self.assertIsNone(libro2)

    def test_generar_color_aleatorio(self):
        from biblioteca.google_books import GoogleBooksAPI
        api = GoogleBooksAPI()
        color = api._generar_color_aleatorio()

        self.assertIn(color, ["#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899"])