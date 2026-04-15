from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("libros/", views.libro_list, name="libro_list"),
    path("libros/<int:id>/", views.libro_detail, name="libro_detail"),
    path("accounts/login/", views.custom_login, name="login"),
    path("accounts/logout/", views.custom_logout, name="logout"),
    path(
        "accounts/register/", views.register_demo, name="register"
    ),  # Cambiado a vista demo
    path("importar-libros/", views.importar_libros, name="importar_libros"),
    path("reservar/<int:id>/", views.reservar_libro, name="reservar_libro"),
    path("mis-reservas/", views.mis_reservas, name="mis_reservas"),
    path("cancelar-reserva/<int:id>/", views.cancelar_reserva, name="cancelar_reserva"),
    path("demo-login/", views.demo_login, name="demo_login"),
]
