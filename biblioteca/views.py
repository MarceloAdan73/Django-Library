from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.utils import timezone
from .models import Libro, Categoria, Prestamo
from .google_books import GoogleBooksAPI


def index(request):
    libros_destacados = Libro.objects.filter(estado="Disponible")[:6]
    total_libros = Libro.objects.count()
    total_disponibles = Libro.objects.filter(estado="Disponible").count()

    context = {
        "libros_destacados": libros_destacados,
        "total_libros": total_libros,
        "total_disponibles": total_disponibles,
        "user": request.user,
    }
    return render(request, "biblioteca/index.html", context)


def libro_list(request):
    libros = Libro.objects.all()
    categorias = Categoria.objects.all()

    context = {
        "libros": libros,
        "categorias": categorias,
        "user": request.user,
    }
    return render(request, "biblioteca/libro_list.html", context)


def libro_detail(request, id):
    libro = get_object_or_404(Libro, id=id)
    context = {
        "libro": libro,
        "user": request.user,
    }
    return render(request, "biblioteca/libro_detail.html", context)


def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect("/")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


def custom_logout(request):
    auth_logout(request)
    return redirect("/")


@login_required
def importar_libros(request):
    resultados = None
    query_actual = ""

    # SOLO manejar POST
    if request.method == "POST":
        query = request.POST.get("q", "").strip()
        max_results = int(request.POST.get("max_results", 10))
        accion = request.POST.get("accion")

        query_actual = query

        if query:
            api = GoogleBooksAPI()
            resultados = api.buscar_libros(query, max_results)

            # Si se solicita importar
            if accion == "importar" and resultados and "items" in resultados:
                libros_importados = 0
                for item in resultados["items"][:max_results]:
                    libro = api.importar_libro_desde_api(item)
                    if libro:
                        libros_importados += 1

                if libros_importados > 0:
                    messages.success(
                        request, f"{libros_importados} books imported successfully"
                    )
                    return redirect("libro_list")
                else:
                    messages.info(
                        request,
                        "No new books could be imported (possibly already exist)",
                    )

            # Si hay error en la API
            if "error" in resultados:
                messages.error(request, f"Search error: {resultados['error']}")

    context = {
        "resultados": resultados,
        "query_actual": query_actual,
        "user": request.user,
    }
    return render(request, "biblioteca/importar_libros.html", context)


@login_required
def reservar_libro(request, id):
    libro = get_object_or_404(Libro, id=id)

    if libro.estado != "Disponible" or libro.stock < 1:
        messages.error(request, "This book is not available for reservation")
        return redirect("libro_detail", id=id)

    reserva_existente = Prestamo.objects.filter(
        usuario=request.user, libro=libro, estado="Activo"
    ).exists()

    if reserva_existente:
        messages.warning(
            request, "You already have an active reservation for this book"
        )
        return redirect("libro_detail", id=id)

    Prestamo.objects.create(libro=libro, usuario=request.user, estado="Activo")

    libro.stock -= 1
    if libro.stock == 0:
        libro.estado = "Prestado"
    libro.save()

    messages.success(request, f'Book "{libro.titulo}" reserved successfully!')
    return redirect("mis_reservas")


@login_required
def mis_reservas(request):
    reservas = Prestamo.objects.filter(usuario=request.user, estado="Activo")

    context = {
        "reservas": reservas,
        "user": request.user,
    }
    return render(request, "biblioteca/mis_reservas.html", context)


@login_required
def cancelar_reserva(request, id):
    reserva = get_object_or_404(Prestamo, id=id, usuario=request.user, estado="Activo")
    libro = reserva.libro

    # Restaurar stock del libro
    libro.stock += 1
    if libro.estado == "Prestado":
        libro.estado = "Disponible"
    libro.save()

    # Cambiar estado de la reserva
    reserva.estado = "Devuelto"
    reserva.save()

    messages.success(
        request, f'Reservation for "{libro.titulo}" cancelled successfully'
    )
    return redirect("mis_reservas")


def register_demo(request):
    """Demo registration view that redirects to login"""
    if request.method == "POST":
        messages.info(request, "This is a demo version. Use the provided credentials.")
        return redirect("login")

    return render(request, "biblioteca/register.html")


def demo_login(request):
    """Demo login - authenticate admin user directly"""
    from django.contrib.auth import authenticate
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        admin_user = User.objects.get(username="admin")
        auth_login(request, admin_user)
        messages.success(request, "Welcome to the demo!")
    except User.DoesNotExist:
        messages.error(request, "Admin user not found. Run startup.py first.")

    return redirect("/")
