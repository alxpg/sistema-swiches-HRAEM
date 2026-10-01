import re
from pathlib import Path
from django.core.management.base import BaseCommand  # pyright: ignore[reportMissingModuleSource]
import pandas as pd  # pyright: ignore[reportMissingModuleSource]
from inventario.models import Nivel, IDF, Switch, VLAN, Puerto, Nodo

EXCEL_PATH = Path("Ordenamiento Switches 2024.xlsx")

# Catálogos que irás afinando
NIVELES = {
    "SOTANO": ("Sótano", 0),
    "SÓTANO": ("Sótano", 0),
    "PB": ("Planta Baja", 1),
    "1N": ("1er Nivel", 2),
    "2N": ("2do Nivel", 3),
    "3N": ("3er Nivel", 4),
}

VLANS_BASE = {
    1: "Default",
    12: "Datos",
    13: "Biomedicos",
    14: "Voz",
    21: "Impresora",
    22: "HM_Wifi",
    26: "HM_Móvil",
    90: "Infinitum",
}


class Command(BaseCommand):
    help = "Importa el Excel de switches a la base de datos"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, default=str(EXCEL_PATH))

    def handle(self, *args, **options):
        # 1. Catálogos básicos
        self._crear_niveles()
        self._crear_vlans()

        path = options["file"]
        self.stdout.write(f"Leyendo {path}...")

        # 2. Importar la hoja resumen "Distribucion" que es la más limpia
        self._importar_distribucion(path)

        self.stdout.write(self.style.SUCCESS("Importación terminada."))

    # ---------- Catálogos ----------
    def _crear_niveles(self):
        for nombre, orden in NIVELES.values():
            Nivel.objects.get_or_create(nombre=nombre, defaults={"orden": orden})

    def _crear_vlans(self):
        for numero, nombre in VLANS_BASE.items():
            VLAN.objects.get_or_create(numero=numero, defaults={"nombre": nombre})

    # ---------- Hoja Distribución ----------
    def _importar_distribucion(self, path):
        df = pd.read_excel(path, sheet_name="Distribucion")
        df.columns = [c.strip().upper() for c in df.columns]
        df = df.ffill()  # rellenar nivel y ubicación combinados

        nivel_actual = None
        for _, row in df.iterrows():
            nivel_nombre = str(row.get("NIVEL", "")).strip().upper()
            ubicacion = str(row.get("UBICACIÓN", "")).strip().upper()
            modelo = str(row.get("DISTRIBUCIÓN DE RED HRAEM", "")).strip()
            ip = str(row.get("IP", "")).strip()
            puertos = row.get("PUERTO")

            if not modelo or modelo == "NAN":
                continue

            # Nivel
            nivel_key = next((k for k in NIVELES if k in nivel_nombre), None)
            if not nivel_key:
                # fallback por ubicación si el nivel viene vacío
                continue
            nivel, _ = Nivel.objects.get_or_create(
                nombre=NIVELES[nivel_key][0],
                defaults={"orden": NIVELES[nivel_key][1]},
            )

            # IDF: usamos "nivel + ubicacion" como nombre
            idf_nombre = f"IDF {nivel.nombre} - {ubicacion}" if ubicacion and ubicacion != "NAN" else f"IDF {nivel.nombre}"
            idf, _ = IDF.objects.get_or_create(
                nombre=idf_nombre,
                defaults={"tipo": "INTERIOR", "nivel": nivel},
            )

            # Marca/modelo
            marca, modelo_limpio = self._parsear_modelo(modelo)
            try:
                total_puertos = int(float(str(puertos).split("+")[0]))
            except (ValueError, TypeError):
                total_puertos = 24

            switch, _ = Switch.objects.get_or_create(
                idf=idf,
                modelo=modelo_limpio,
                ip=ip if ip and ip != "NAN" else None,
                defaults={"marca": marca, "total_puertos": total_puertos},
            )

            # Crear puertos vacíos
            for p in range(1, switch.total_puertos + 1):
                Puerto.objects.get_or_create(switch=switch, numero=p)

        self.stdout.write(self.style.SUCCESS(
            f"Distribución importada: {Switch.objects.count()} switches, "
            f"{Puerto.objects.count()} puertos."
        ))

    def _parsear_modelo(self, texto):
        texto = texto.strip()
        marcas = ["EXTREME", "ALCATEL", "CISCO", "CISCOC", "NORTEL", "D-LINK", "LINKSYS", "3COM", "SWITCH"]
        for m in marcas:
            if texto.upper().startswith(m):
                return m, texto
        partes = texto.split(" ", 1)
        return (partes[0], texto) if partes else ("", texto)