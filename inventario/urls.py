from django.urls import path  # type: ignore[reportMissingModuleSource]
from . import views

app_name = "inventario"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("buscar/", views.buscar, name="buscar"),
    path("ajax/idf/", views.opciones_idf, name="opciones_idf"),
    path("ajax/switch/", views.opciones_switch, name="opciones_switch"),
    path("ajax/puerto/", views.opciones_puerto, name="opciones_puerto"),
    path("asignar/", views.asignar_nodo, name="asignar_nodo"),
    path("liberar-puerto/<int:puerto_id>/", views.liberar_puerto, name="liberar_puerto"),
]