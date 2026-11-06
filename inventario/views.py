from django.shortcuts import render, get_object_or_404, redirect
# pyright: reportMissingModuleSource=false
from django.db.models import Q
from django.contrib import messages
from .forms import AsignarNodoForm
from .models import Nivel, IDF, Switch, Puerto, Nodo
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def es_administrador(user):
    # Retorna True si es superusuario o si pertenece al grupo "Administradores"
    return user.is_superuser or user.groups.filter(name="Administradores").exists()

@login_required
def dashboard(request):
    nivel_id = request.GET.get("nivel")
    idf_id = request.GET.get("idf")
    switch_id = request.GET.get("switch")
    puerto_num = request.GET.get("puerto")

    niveles = Nivel.objects.all()
    idfs = IDF.objects.all()
    switches = Switch.objects.all()
    puertos = Puerto.objects.none()

    if nivel_id:
        idfs = idfs.filter(nivel_id=nivel_id)
        switches = switches.filter(idf__nivel_id=nivel_id)
    if idf_id:
        switches = switches.filter(idf_id=idf_id)
    if switch_id:
        puertos = Puerto.objects.filter(switch_id=switch_id).order_by("numero")

    puerto = None
    nodo = None
    if switch_id and puerto_num:
        puerto = Puerto.objects.filter(switch_id=switch_id, numero=puerto_num).first()
        if puerto:
            nodo = getattr(puerto, "nodo", None)

    context = {
        "niveles": niveles,
        "idfs": idfs,
        "switches": switches,
        "puertos": puertos,
        "puerto": puerto,
        "nodo": nodo,
        "sel": {
            "nivel": nivel_id,
            "idf": idf_id,
            "switch": switch_id,
            "puerto": puerto_num,
        },
    }
    return render(request, "inventario/dashboard.html", context)
pass

@login_required
def buscar(request):
    q = request.GET.get("q", "").strip()
    resultados = []
    if q:
        nodos = Nodo.objects.filter(
            Q(nombre__icontains=q)
            | Q(ip__icontains=q)
            | Q(nombre_equipo__icontains=q)
            | Q(ubicacion__icontains=q)
        ).select_related("puerto__switch__idf__nivel")
        for n in nodos:
            item = {
                "nodo": n,
                "puerto": n.puerto,
                "switch": n.puerto.switch if n.puerto else None,
                "idf": n.puerto.switch.idf if n.puerto else None,
                "nivel": n.puerto.switch.idf.nivel if n.puerto else None,
                "vlans": list(n.puerto.vlans.all()) if n.puerto else [],
            }
            resultados.append(item)
    return render(request, "inventario/buscar.html", {"q": q, "resultados": resultados})

pass
# Vista parcial para los selects encadenados (HTMX)
@login_required
def opciones_idf(request):
    nivel_id = request.GET.get("nivel")
    idfs = IDF.objects.filter(nivel_id=nivel_id) if nivel_id else IDF.objects.all()
    return render(request, "inventario/_opciones_idf.html", {"idfs": idfs})

pass
@login_required
def opciones_switch(request):
    idf_id = request.GET.get("idf")
    switches = Switch.objects.filter(idf_id=idf_id) if idf_id else Switch.objects.all()
    return render(request, "inventario/_opciones_switch.html", {"switches": switches})
pass
@login_required
def opciones_puerto(request):
    switch_id = request.GET.get("switch")
    puertos = Puerto.objects.filter(switch_id=switch_id).order_by("numero") if switch_id else []
    return render(request, "inventario/_opciones_puerto.html", {"puertos": puertos})
pass
login_required
def asignar_nodo(request):
    niveles = Nivel.objects.all()
    
    # Obtener filtros de la URL
    nivel_id = request.GET.get("nivel")
    switch_id = request.GET.get("switch")
    puerto_num = request.GET.get("puerto")

    switches = Switch.objects.all()
    puertos = Puerto.objects.none()
    puerto_actual = None
    nodo_actual = None

    if nivel_id:
        switches = switches.filter(idf__nivel_id=nivel_id)
    if switch_id:
        puertos = Puerto.objects.filter(switch_id=switch_id).order_by("numero")
    
    if switch_id and puerto_num:
        puerto_actual = Puerto.objects.filter(switch_id=switch_id, numero=puerto_num).first()
        if puerto_actual:
            nodo_actual = getattr(puerto_actual, "nodo", None)

    # Manejo del formulario (POST)
    if request.method == "POST":
        puerto_id = request.POST.get("puerto_id")
        puerto_obj = get_object_or_404(Puerto, id=puerto_id)
        
        # Si el puerto ya tiene un nodo, lo estamos editando
        nodo_obj = getattr(puerto_obj, "nodo", None)
        
        form = AsignarNodoForm(request.POST, instance=nodo_obj)
        if form.is_valid():
            nodo = form.save(commit=False)
            nodo.puerto = puerto_obj
            nodo.save()
            messages.success(request, f"Nodo '{nodo.nombre}' guardado correctamente en el puerto {puerto_obj.numero}.")
            return redirect(f"/asignar/?switch={puerto_obj.switch.id}&puerto={puerto_obj.numero}")
    else:
        # Si ya hay un nodo, precargamos el form. Si no, form vacío.
        form = AsignarNodoForm(instance=nodo_actual)

    context = {
        "niveles": niveles,
        "switches": switches,
        "puertos": puertos,
        "puerto_actual": puerto_actual,
        "nodo_actual": nodo_actual,
        "form": form,
        "sel": {
            "nivel": nivel_id or "",
            "switch": switch_id or "",
            "puerto": puerto_num or "",
        }
    }
    return render(request, "inventario/asignar_nodo.html", context)
pass

@login_required
def liberar_puerto(request, puerto_id):
    puerto = get_object_or_404(Puerto, id=puerto_id)
    nodo = getattr(puerto, "nodo", None)
    if nodo:
        nombre = nodo.nombre
        nodo.delete()
        messages.warning(request, f"El nodo '{nombre}' fue eliminado y el puerto {puerto.numero} quedó libre.")
    return redirect(f"/asignar/?switch={puerto.switch.id}&puerto={puerto.numero}")