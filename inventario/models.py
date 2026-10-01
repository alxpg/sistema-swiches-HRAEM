# pyright: reportMissingModuleSource=false
from django.db import models


class Nivel(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return self.nombre


class IDF(models.Model):
    TIPO_CHOICES = [
        ("INTERIOR", "Interior"),
        ("EXTERIOR", "Exterior"),
        ("CORE", "Core"),
    ]
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="INTERIOR")
    nivel = models.ForeignKey(Nivel, on_delete=models.SET_NULL, null=True, blank=True)
    ubicacion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.nombre


class Switch(models.Model):
    idf = models.ForeignKey(IDF, on_delete=models.CASCADE, related_name="switches")
    marca = models.CharField(max_length=80, blank=True)
    modelo = models.CharField(max_length=150)
    ip = models.GenericIPAddressField(null=True, blank=True)
    total_puertos = models.PositiveIntegerField(default=24)
    orden = models.PositiveIntegerField(default=0)
    notas = models.TextField(blank=True)

    class Meta:
        ordering = ["idf", "orden"]
        verbose_name_plural = "Switches"

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.ip or 'sin IP'})"


class VLAN(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    nombre = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.numero} - {self.nombre}"


class Puerto(models.Model):
    ESTADO_CHOICES = [
        ("ACTIVO", "Activo"),
        ("INACTIVO", "Inactivo"),
        ("DAÑADO", "Dañado"),
        ("INHABILITADO", "Inhabilitado"),
    ]
    switch = models.ForeignKey(Switch, on_delete=models.CASCADE, related_name="puertos")
    numero = models.PositiveIntegerField()
    vlans = models.ManyToManyField(VLAN, blank=True, related_name="puertos")

    class Meta:
        unique_together = ("switch", "numero")
        ordering = ["switch", "numero"]

    def __str__(self):
        return f"{self.switch} - Puerto {self.numero}"


class Nodo(models.Model):
    ESTADO_CHOICES = [
        ("ACTIVO", "Activo"),
        ("INACTIVO", "Inactivo"),
        ("INHABILITADO", "Inhabilitado"),
    ]
    TIPO_CHOICES = [
        ("Computadora", "Computadora"),
        ("Impresora", "Impresora"),
        ("Camara", "Cámara"),
        ("Telefono", "Teléfono"),
        ("WiFi", "Access Point WiFi"),
        ("Switch", "Switch (Cascada)"),
        ("Biomedico", "Equipo Biomédico"),
        ("Copiadora", "Copiadora"),
        ("Reloj Checador", "Reloj Checador"),
        ("Otro", "Otro"),
    ]
    nombre = models.CharField(max_length=100, db_index=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="ACTIVO")
    tipo = models.CharField(max_length=40, choices=TIPO_CHOICES, blank=True)
    ip = models.CharField(max_length=80, blank=True)
    nombre_equipo = models.CharField(max_length=200, blank=True)
    ubicacion = models.CharField(max_length=200, blank=True)
    observacion = models.TextField(blank=True)
    puerto = models.OneToOneField(
        Puerto, on_delete=models.SET_NULL, null=True, blank=True, related_name="nodo"
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.tipo or 'sin tipo'})"