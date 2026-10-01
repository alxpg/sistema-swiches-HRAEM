# pyright: reportMissingModuleSource=false
from django.contrib import admin
from .models import Nivel, IDF, Switch, VLAN, Puerto, Nodo


@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden")


@admin.register(IDF)
class IDFAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "nivel")
    list_filter = ("tipo", "nivel")


@admin.register(Switch)
class SwitchAdmin(admin.ModelAdmin):
    list_display = ("marca", "modelo", "ip", "idf", "total_puertos")
    list_filter = ("idf", "marca")
    search_fields = ("modelo", "ip")


@admin.register(VLAN)
class VLANAdmin(admin.ModelAdmin):
    list_display = ("numero", "nombre")


@admin.register(Puerto)
class PuertoAdmin(admin.ModelAdmin):
    list_display = ("switch", "numero")
    list_filter = ("switch",)
    filter_horizontal = ("vlans",)
    search_fields = ("switch__modelo", "switch__ip", "numero")


@admin.register(Nodo)
class NodoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "estado", "ip", "puerto")
    list_filter = ("estado", "tipo")
    search_fields = ("nombre", "ip", "nombre_equipo", "ubicacion")
    #autocomplete_fields = ("puerto",)

#@admin.register(Dispositivo)
#class DispositivoAdmin(admin.ModelAdmin):
 #   list_display = ("nombre", "tipo", "estado", "ip", "puerto")
  #  list_filter = ("estado", "tipo")
   # search_fields = ("nombre", "ip", "nombre_equipo", "ubicacion")