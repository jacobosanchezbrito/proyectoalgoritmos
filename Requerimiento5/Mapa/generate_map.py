# generate_map.py
import os
import re
from pathlib import Path
from urllib.request import urlretrieve
import geopandas as gpd
import matplotlib.pyplot as plt
import bibtexparser
from collections import Counter

# === CONFIGURACIÓN DE RUTAS ===
BASE_DIR = Path(__file__).resolve().parents[2]  # Subir dos niveles desde Requerimiento5/Mapa
BIB_PATH = BASE_DIR / "Requerimiento1" / "ArchivosFiltrados" / "articulosOptimos_limpio.bib"
OUTPUT_DIR = Path(__file__).resolve().parent  # Carpeta actual (Mapa)
MAP_PATH = OUTPUT_DIR / "mapa_articulos_por_pais.jpg"

# === VERIFICAR EXISTENCIA DEL ARCHIVO ===
if not BIB_PATH.exists():
    print(f"❌ Archivo no encontrado: {BIB_PATH}")
    exit()

# === DESCARGAR MAPA BASE SI NO EXISTE ===
geojson_path = OUTPUT_DIR / "ne_110m_admin_0_countries.geojson"
if not geojson_path.exists():
    print("🌍 Descargando mapa base desde Natural Earth (GitHub)...")
    url = "https://github.com/nvkelso/natural-earth-vector/raw/master/geojson/ne_110m_admin_0_countries.geojson"
    urlretrieve(url, geojson_path)

# === CARGAR MAPA BASE ===
world = gpd.read_file(geojson_path)

# === LEER ARCHIVO BIBTEX ===
with open(BIB_PATH, encoding="utf-8") as bib_file:
    bib_database = bibtexparser.load(bib_file)

entries = bib_database.entries

# === LISTA DE PAÍSES (ISO + nombre común) ===
countries = {
    "Argentina": "ARG", "Australia": "AUS", "Austria": "AUT", "Belgium": "BEL", "Brazil": "BRA",
    "Canada": "CAN", "Chile": "CHL", "China": "CHN", "Colombia": "COL", "Czech Republic": "CZE",
    "Denmark": "DNK", "Egypt": "EGY", "Finland": "FIN", "France": "FRA", "Germany": "DEU",
    "Greece": "GRC", "Hungary": "HUN", "India": "IND", "Indonesia": "IDN", "Iran": "IRN",
    "Ireland": "IRL", "Israel": "ISR", "Italy": "ITA", "Japan": "JPN", "Kenya": "KEN",
    "Mexico": "MEX", "Netherlands": "NLD", "New Zealand": "NZL", "Nigeria": "NGA", "Norway": "NOR",
    "Pakistan": "PAK", "Peru": "PER", "Philippines": "PHL", "Poland": "POL", "Portugal": "PRT",
    "Russia": "RUS", "Saudi Arabia": "SAU", "Singapore": "SGP", "South Africa": "ZAF", "South Korea": "KOR",
    "Spain": "ESP", "Sweden": "SWE", "Switzerland": "CHE", "Thailand": "THA", "Turkey": "TUR",
    "Ukraine": "UKR", "United Arab Emirates": "ARE", "United Kingdom": "GBR", "United States": "USA",
    "Venezuela": "VEN", "Vietnam": "VNM"
}

# === DETECCIÓN HEURÍSTICA DE PAÍSES ===
country_counts = Counter()
for entry in entries:
    text = ""
    for key in ["author", "affiliation", "institution", "organization"]:
        if key in entry:
            text += " " + entry[key]
    for name, code in countries.items():
        if re.search(rf"\b{name}\b", text, flags=re.IGNORECASE):
            country_counts[code] += 1

# === IMPRIMIR RESULTADOS ===
if country_counts:
    print("\n🌎 Conteo de artículos por país:")
    for code, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
        country_name = next((n for n, c in countries.items() if c == code), code)
        print(f"  {country_name} ({code}): {count}")
else:
    print("⚠️ No se detectaron países en las afiliaciones o autores del archivo BibTeX.")

# === UNIR CON MAPA BASE ===
world["article_count"] = world["ADM0_A3"].map(country_counts)
world["article_count"] = world["article_count"].fillna(0)

# === DIBUJAR Y GUARDAR MAPA ===
fig, ax = plt.subplots(figsize=(12, 7))
world.plot(column="article_count", cmap="OrRd", linewidth=0.5, edgecolor="gray", legend=True, ax=ax)
ax.set_title("Distribución de artículos científicos por país", fontsize=14, fontweight="bold")
ax.axis("off")
plt.tight_layout()
plt.savefig(MAP_PATH, dpi=300)
print(f"\n🗺️ Mapa generado y guardado en: {MAP_PATH}")
plt.show()
