from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    nacionalidad = models.CharField(max_length=100, default="Desconocida")
    biografia = models.TextField(blank=True)
    foto = models.ImageField(upload_to="autores/", blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name_plural = "Autores"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#3B82F6")  # Código hexadecimal

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"


class Libro(models.Model):
    ESTADOS = [
        ("Disponible", "Disponible"),
        ("Prestado", "Prestado"),
        ("En reparación", "En reparación"),
    ]

    titulo = models.CharField(max_length=200)
    ISBN = models.CharField(max_length=20, blank=True)
    autores = models.ManyToManyField(Autor)
    categorias = models.ManyToManyField(Categoria)
    descripcion = models.TextField(max_length=1000, blank=True, default="")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="Disponible")
    stock = models.IntegerField(default=1)
    portada = models.ImageField(upload_to="portadas/", blank=True, null=True)
    portada_url = models.URLField(
        blank=True, max_length=500, default=""
    )  # NUEVO: Guardar URL original
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse("detalle_libro", kwargs={"id": self.pk})

    def get_portada_url(self):
        """Returns cover URL: local first, then external URL, then placeholder"""
        if self.portada:
            return self.portada.url
        elif self.portada_url:
            return self.portada_url
        else:
            return "https://via.placeholder.com/200x300/e2e8f0/64748b?text=No+Cover"

    class Meta:
        verbose_name_plural = "Libros"


class Prestamo(models.Model):
    ESTADOS_PRESTAMO = [
        ("Activo", "Activo"),
        ("Devuelto", "Devuelto"),
        ("Vencido", "Vencido"),
    ]

    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PRESTAMO, default="Activo")

    def __str__(self):
        return f"{self.libro} - {self.usuario}"

    class Meta:
        verbose_name_plural = "Préstamos"


class Resena(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.usuario} para {self.libro}"

    class Meta:
        verbose_name_plural = "Reseñas"
