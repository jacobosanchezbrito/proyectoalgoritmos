# Proyecto/Requerimiento3/frecuenciaPalabras.py
import pandas as pd
from pathlib import Path
import re
import matplotlib.pyplot as plt
from collections import Counter

# === CONFIGURACIÓN DE RUTAS ===
BASE_DIR = Path(__file__).resolve().parent
IN_FILE = BASE_DIR / "DatosProcesados" / "abstracts_limpios.csv"

# Nueva carpeta de salida
OUT_DIR = BASE_DIR / "FrecuenciaPalabras"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "frecuencias_palabras_asociadas.csv"
OUT_PLOT = OUT_DIR / "frecuencias_palabras_asociadas.png"

print("📘 Iniciando análisis de frecuencias específicas...")
print("Ruta esperada del archivo:", IN_FILE)
print("Los resultados se guardarán en:", OUT_DIR)

if not IN_FILE.exists():
    raise FileNotFoundError(f"❌ No se encontró el archivo: {IN_FILE}")

# === LECTURA DE DATOS ===
df = pd.read_csv(IN_FILE, encoding='utf-8')
print("✅ Archivo CSV cargado correctamente.")

if "abstract_limpio" not in df.columns:
    raise KeyError("La columna 'abstract_limpio' no existe en el CSV. Revisa el archivo generado en el requerimiento 2.")

# === LISTA DE PALABRAS ASOCIADAS ===
palabras_asociadas = [
    "generative models",
    "prompting",
    "machine learning",
    "multimodality",
    "fine-tuning",
    "training data",
    "algorithmic bias",
    "explainability",
    "transparency",
    "ethics",
    "privacy",
    "personalization",
    "human-ai interaction",
    "ai literacy",
    "co-creation"
]

# Normalizamos las palabras (todo minúscula, sin espacios extra)
palabras_asociadas = [p.lower().strip() for p in palabras_asociadas]

# === COMBINAR TODOS LOS ABSTRACTS LIMPIOS ===
print("🔍 Unificando texto de todos los abstracts...")
texto_total = " ".join(df["abstract_limpio"].astype(str).fillna(" ")).lower()

# === FUNCIÓN PARA CONTAR OCURRENCIAS ===
def contar_ocurrencias(texto, palabra):
    """
    Cuenta ocurrencias exactas de una palabra o frase dentro de un texto.
    Usa regex con límites de palabra (\b) y espacios.
    """
    patron = re.escape(palabra)
    if " " in palabra:
        matches = re.findall(patron, texto)
    else:
        matches = re.findall(rf"\b{patron}\b", texto)
    return len(matches)

# === CALCULAR FRECUENCIAS ===
print("📊 Calculando frecuencias de palabras/frases asociadas...")
resultados = []

for palabra in palabras_asociadas:
    frecuencia = contar_ocurrencias(texto_total, palabra)
    resultados.append({"palabra_asociada": palabra, "frecuencia_total": frecuencia})

df_resultados = pd.DataFrame(resultados)
df_resultados = df_resultados.sort_values(by="frecuencia_total", ascending=False)

# === GUARDAR RESULTADOS ===
df_resultados.to_csv(OUT_FILE, index=False, encoding="utf-8")
print(f"✅ Resultados guardados en: {OUT_FILE}")

# === MOSTRAR RESULTADOS EN CONSOLA ===
print("\n📋 Frecuencia de palabras asociadas:\n")
print(df_resultados.to_string(index=False))

# === GRAFICAR ===
try:
    plt.figure(figsize=(10, 6))
    plt.barh(df_resultados["palabra_asociada"], df_resultados["frecuencia_total"], color="#4A90E2")
    plt.gca().invert_yaxis()
    plt.title("Frecuencia de palabras asociadas - Generative AI in Education")
    plt.xlabel("Frecuencia total en abstracts")
    plt.ylabel("Palabra/Frase asociada")
    plt.tight_layout()
    plt.savefig(OUT_PLOT, dpi=150)
    plt.close()
    print(f"📈 Gráfica guardada en: {OUT_PLOT}")
except Exception as e:
    print("⚠️ Ocurrió un error al generar la gráfica:", e)

print("\n🔚 Análisis completado correctamente.")
