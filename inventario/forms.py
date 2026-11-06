from django import forms
from .models import Nodo, Puerto

class AsignarNodoForm(forms.ModelForm):
    class Meta:
        model = Nodo
        fields = ["nombre", "estado", "tipo", "ip", "nombre_equipo", "ubicacion", "observacion"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: V003, D023"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "ip": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 10.104.2.20"}),
            "nombre_equipo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del equipo en Windows"}),
            "ubicacion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Enfermería - Cama 3"}),
            "observacion": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }