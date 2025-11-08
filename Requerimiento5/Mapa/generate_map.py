# generate_map.py
import os
import re
import pycountry
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
from urllib.request import urlretrieve
from collections import Counter

BASE_DIR = Path(__file__).resolve().parents[2]
BIB_PATH = BASE_DIR / "Requerimiento1" / "ArchivosFiltrados" / "articulosOptimos_limpio.bib"
OUTPUT_DIR = BASE_DIR / "Requerimiento5" / "Mapa"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- Descarga del mapa base ----
geojson_path = OUTPUT_DIR / "ne_110m_admin_0_countries.geojson"
if not geojson_path.exists():
    print("Descargando mapa base desde Natural Earth (GitHub)...")
    url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
    urlretrieve(url, geojson_path)

# ---- Cargar mapa ----
world = gpd.read_file(geojson_path)

# ---- Inferencia heurística de país por apellido ----
surname_country_map = {
    # Ejemplos representativos
    "Wang": "China", "Li": "China", "Zhang": "China",
    "Kim": "South Korea", "Park": "South Korea", "Lee": "South Korea",
    "Singh": "India", "Kumar": "India", "Patel": "India",
    "Garcia": "Spain", "Martinez": "Spain", "Lopez": "Spain", "Gonzalez": "Spain",
    "Silva": "Brazil", "Santos": "Brazil", "Oliveira": "Brazil",
    "Smith": "United Kingdom", "Jones": "United Kingdom",
    "Brown": "United States", "Johnson": "United States",
    "Nguyen": "Vietnam", "Tran": "Vietnam",
    "Mohamed": "Egypt", "Hassan": "Egypt",
    "Kowalski": "Poland", "Nowak": "Poland",
    "Ivanov": "Russia", "Petrov": "Russia",
    "Yamamoto": "Japan", "Tanaka": "Japan",
    "Schmidt": "Germany", "Müller": "Germany", "Mueller": "Germany",
    "Rossi": "Italy", "Bianchi": "Italy", "Esposito": "Italy",
    "Dupont": "France", "Lefevre": "France",
    "Andersson": "Sweden", "Johansson": "Sweden",
    "Nielsen": "Denmark", "Hansen": "Denmark",
    "Olsen": "Norway", "Larsen": "Norway"
}

def infer_country_from_author(author_name: str) -> str:
    """Inferir país probable según el apellido del primer autor."""
    if not author_name:
        return None
    surname = author_name.split(",")[0].strip()
    for key, country in surname_country_map.items():
        if surname.lower() == key.lower():
            return country
    return None

# ---- Cargar archivo .bib ----
if not BIB_PATH.exists():
    print(f"❌ Archivo no encontrado: {BIB_PATH}")
    exit(1)

with open(BIB_PATH, "r", encoding="utf-8") as f:
    bib_content = f.read()

entries = re.split(r"@article", bib_content)[1:]  # dividir en artículos

country_counts = Counter()
no_country = 0

for entry in entries:
    # Buscar autor principal
    match = re.search(r"author\s*=\s*[{\"]([^}\"]+)[}\"]", entry)
    author = match.group(1).split(" and ")[0] if match else None
    country = infer_country_from_author(author)
    if country:
        country_counts[country] += 1
    else:
        no_country += 1

# ---- Mostrar conteos ----
print("\n🌍 Países detectados:")
for c, n in country_counts.most_common():
    print(f"  {c}: {n}")
print(f"Entradas sin país detectado: {no_country}")

# ---- Convertir nombres a códigos ISO alpha3 ----
country_alpha3_counts = {}
for name, count in country_counts.items():
    try:
        country_alpha3_counts[pycountry.countries.lookup(name).alpha_3] = count
    except:
        print(f"⚠️ No se pudo convertir {name} a código alpha3")

# ---- Generar mapa ----
world["count"] = world["ADM0_A3"].map(country_alpha3_counts).fillna(0)

fig, ax = plt.subplots(figsize=(14, 8))
world.plot(column="count", cmap="OrRd", linewidth=0.8, ax=ax, edgecolor="0.8", legend=True)
ax.set_title("Distribución aproximada de autores por país (heurística por apellido)", fontsize=14)
ax.axis("off")

# Guardar
jpg_path = OUTPUT_DIR / "mapa_autores_heuristico.jpg"
pdf_path = OUTPUT_DIR / "mapa_autores_heuristico.pdf"
plt.savefig(jpg_path, dpi=300, bbox_inches="tight")
plt.savefig(pdf_path, dpi=300, bbox_inches="tight")

print(f"\n✅ Mapa generado y guardado como:\n - {jpg_path}\n - {pdf_path}")
