import requests
import json
from django.core.files.base import ContentFile
from biblioteca.models import Libro, Autor, Categoria
import os
from django.conf import settings
import uuid

class GoogleBooksAPI:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def __init__(self):
        self.session = requests.Session()
        self.timeout = 30
    
    def buscar_libros(self, query, max_results=10):
        # ... (mantener código existente igual) ...
        params = {
            'q': query,
            'maxResults': max_results,
            'printType': 'books'
        }
        
        try:
            print(f"Buscando libros: {query}")
            response = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if 'items' not in data or not data['items']:
                print("No se encontraron resultados")
                return {'items': []}
                
            print(f"Encontrados {len(data['items'])} resultados")
            return data
            
        except requests.exceptions.Timeout:
            print("Timeout en la API de Google Books")
            return {'error': 'Timeout en la busqueda'}
        except Exception as e:
            print(f"Error: {e}")
            return {'error': f'Error: {e}'}
    
    def importar_libro_desde_api(self, book_data):
        try:
            volume_info = book_data.get('volumeInfo', {})
            
            if not volume_info.get('title'):
                print("Libro sin titulo, saltando...")
                return None
            
            # Verificar si el libro ya existe por ISBN
            isbns = volume_info.get('industryIdentifiers', [])
            for isbn_info in isbns:
                if isbn_info.get('type') in ['ISBN_13', 'ISBN_10']:
                    isbn = isbn_info.get('identifier')
                    if Libro.objects.filter(ISBN=isbn).exists():
                        print(f"Libro con ISBN {isbn} ya existe")
                        return None
            
            # Crear o obtener autores (mantener igual)
            autores = []
            author_names = volume_info.get('authors', ['Autor Desconocido'])
            for author_name in author_names:
                if author_name:
                    autor, created = Autor.objects.get_or_create(
                        nombre=author_name,
                        defaults={
                            'nacionalidad': 'Desconocida',
                            'biografia': f'Autor del libro "{volume_info.get("title", "")}"'
                        }
                    )
                    autores.append(autor)
            
            if not autores:
                autor, _ = Autor.objects.get_or_create(
                    nombre='Autor Desconocido',
                    defaults={'nacionalidad': 'Desconocida'}
                )
                autores.append(autor)
            
            # Crear o obtener categorías (mantener igual)
            categorias = []
            category_names = volume_info.get('categories', ['General'])
            for category_name in category_names:
                if category_name:
                    categoria, created = Categoria.objects.get_or_create(
                        nombre=category_name[:50],
                        defaults={
                            'descripcion': f'Libros de {category_name}',
                            'color': self._generar_color_aleatorio()
                        }
                    )
                    categorias.append(categoria)
            
            if not categorias:
                categoria, _ = Categoria.objects.get_or_create(
                    nombre='General',
                    defaults={'descripcion': 'Libros generales', 'color': '#3B82F6'}
                )
                categorias.append(categoria)
            
            # Determinar ISBN (mantener igual)
            isbn = ""
            for isbn_info in isbns:
                if isbn_info.get('type') == 'ISBN_13':
                    isbn = isbn_info.get('identifier', '')
                    break
                elif isbn_info.get('type') == 'ISBN_10' and not isbn:
                    isbn = isbn_info.get('identifier', '')
            
            # Obtener URL de portada - SIEMPRE guardarla
            portada_url = None
            if volume_info.get('imageLinks') and volume_info.get('imageLinks').get('thumbnail'):
                portada_url = volume_info['imageLinks']['thumbnail']
            
            # CREAR LIBRO CON portada_url
            libro = Libro.objects.create(
                titulo=volume_info.get('title', 'Sin titulo')[:200],
                ISBN=isbn,
                descripcion=volume_info.get('description', 'Sin descripcion disponible.')[:1000],
                estado='Disponible',
                stock=1,
                portada_url=portada_url,  # ← NUEVO: Guardar URL siempre
            )
            
            # Agregar relaciones ManyToMany
            libro.autores.set(autores)
            libro.categorias.set(categorias)
            
            # DESCARGAR PORTADA SOLO EN DESARROLLO
            if portada_url and settings.DEBUG:
                try:
                    print(f"Descargando portada localmente: {portada_url}")
                    response = requests.get(portada_url, timeout=10)
                    if response.status_code == 200:
                        filename = f"portada_{uuid.uuid4().hex[:8]}.jpg"
                        libro.portada.save(filename, ContentFile(response.content), save=True)
                        print(f"[OK] Portada guardada localmente: {filename}")
                    else:
                        print(f"[FAIL] No se pudo descargar portada: {response.status_code}")
                except Exception as e:
                    print(f"[FAIL] Error descargando portada: {e}")
            
            libro.save()
            print(f"[OK] Libro importado exitosamente: {libro.titulo}")
            return libro
            
        except Exception as e:
            print(f"[ERROR] Error importando libro: {e}")
            return None
    
    def _generar_color_aleatorio(self):
        import random
        colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899']
        return random.choice(colors)
