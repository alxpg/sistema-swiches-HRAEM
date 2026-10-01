from django.shortcuts import render, get_object_or_404
# pyright: reportMissingModuleSource=false
from django.db.models import Q
from .models import Nivel, IDF, Switch, Puerto, Nodo


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


# Vista parcial para los selects encadenados (HTMX)
def opciones_idf(request):
    nivel_id = request.GET.get("nivel")
    idfs = IDF.objects.filter(nivel_id=nivel_id) if nivel_id else IDF.objects.all()
    return render(request, "inventario/_opciones_idf.html", {"idfs": idfs})


def opciones_switch(request):
    idf_id = request.GET.get("idf")
    switches = Switch.objects.filter(idf_id=idf_id) if idf_id else Switch.objects.all()
    return render(request, "inventario/_opciones_switch.html", {"switches": switches})


def opciones_puerto(request):
    switch_id = request.GET.get("switch")
    puertos = Puerto.objects.filter(switch_id=switch_id).order_by("numero") if switch_id else []
    return render(request, "inventario/_opciones_puerto.html", {"puertos": puertos})