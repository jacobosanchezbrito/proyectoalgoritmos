# Proyecto/Requerimiento3/GenerarYEvaluarNuevasTFIDF.py
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from collections import Counter

# -----------------------
# Rutas
# -----------------------
BASE_DIR = Path(__file__).resolve().parent
IN_FILE = BASE_DIR / "DatosProcesados" / "abstracts_limpios.csv"
OUT_DIR = BASE_DIR  / "ResultadosNuevasPalabras"
OUT_TFIDF = OUT_DIR / "nuevas_palabras_tfidf.csv"
OUT_FREQ = OUT_DIR / "frecuencias_nuevas_palabras.csv"
OUT_EVAL = OUT_DIR / "evaluacion_simple_nuevas_palabras.csv"

# -----------------------
# Lista original (las 15 del requerimiento)
# -----------------------
palabras_iniciales = [
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
palabras_iniciales = [p.lower().strip() for p in palabras_iniciales]

# -----------------------
# Comprobaciones y lectura
# -----------------------
print("📘 Leyendo abstracts limpios desde:", IN_FILE)
if not IN_FILE.exists():
    raise FileNotFoundError(f"No se encontró {IN_FILE}. Ejecuta la preparación de datos primero.")

df = pd.read_csv(IN_FILE, encoding='utf-8')
if 'abstract_limpio' not in df.columns:
    raise KeyError("La columna 'abstract_limpio' no existe en el CSV de entrada.")

textos = df['abstract_limpio'].astype(str).fillna("").tolist()

# -----------------------
# TF-IDF (unigrams) para obtener top-15
# -----------------------
print("🔬 Calculando TF-IDF (unigrams)...")
vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words='english',  # cambiar a 'spanish' si tu corpus es principalmente en español
    ngram_range=(1,1)
)
X = vectorizer.fit_transform(textos)
features = vectorizer.get_feature_names_out()
# score promedio por término (media por columna)
scores = X.mean(axis=0).A1

tfidf_df = pd.DataFrame({'palabra': features, 'score_promedio': scores})
top15 = tfidf_df.sort_values('score_promedio', ascending=False).head(15).reset_index(drop=True)

# Guardar top15 TF-IDF
top15.to_csv(OUT_TFIDF, index=False, encoding='utf-8')
print(f"✅ Guardado TF-IDF top15 en: {OUT_TFIDF}")
print("\nTop 15 TF-IDF:\n", top15)

# -----------------------
# Para cada top palabra: calcular frecuencia absoluta y n_docs
# -----------------------
print("\n📊 Calculando frecuencias y presencia por documento...")

# Preparamos texto_total y lista tokenizada por documento
texto_total = " ".join(textos).lower()
docs = [t.lower() for t in textos]

def contar_en_texto(texto, termino):
    # Si termino tiene espacios (phrase), buscamo exacto; si no, usamos \b
    pattern = re.escape(termino)
    if " " in termino:
        return len(re.findall(pattern, texto))
    else:
        return len(re.findall(rf"\b{pattern}\b", texto))

def n_docs_con_termino(docs_list, termino):
    cnt = 0
    for d in docs_list:
        if " " in termino:
            if re.search(re.escape(termino), d):
                cnt += 1
        else:
            if re.search(rf"\b{re.escape(termino)}\b", d):
                cnt += 1
    return cnt

freq_rows = []
for _, row in top15.iterrows():
    termino = row['palabra'].lower()
    score = float(row['score_promedio'])
    freq_total = contar_en_texto(texto_total, termino)
    docs_count = n_docs_con_termino(docs, termino)
    freq_rows.append({
        'palabra': termino,
        'score_promedio_tfidf': score,
        'frecuencia_total': int(freq_total),
        'n_docs_con_palabra': int(docs_count)
    })

df_freq = pd.DataFrame(freq_rows).sort_values('frecuencia_total', ascending=False).reset_index(drop=True)
df_freq.to_csv(OUT_FREQ, index=False, encoding='utf-8')
print(f"✅ Frecuencias guardadas en: {OUT_FREQ}")
print("\nFrecuencias (primeras filas):\n", df_freq.head(15))

# -----------------------
# Evaluación simple: overlap lexical con lista inicial
# -----------------------
print("\n🧾 Evaluando coincidencia exacta con la lista inicial (overlap lexical)...")
eval_rows = []
for _, r in df_freq.iterrows():
    palabra = r['palabra']
    # Coincidencia exacta: palabra en lista inicial o matches if phrase in initial
    is_overlap = False
    # direct match
    if palabra in palabras_iniciales:
        is_overlap = True
    else:
        # check if palabra is part of any initial phrase or viceversa
        for init in palabras_iniciales:
            if palabra == init or palabra in init.split() or init in palabra.split():
                # this is a permissive lexical partial overlap
                is_overlap = True
                break
    eval_rows.append({
        'palabra': palabra,
        'score_promedio_tfidf': r['score_promedio_tfidf'],
        'frecuencia_total': r['frecuencia_total'],
        'n_docs_con_palabra': r['n_docs_con_palabra'],
        'overlap_lexical_con_iniciales': is_overlap
    })

df_eval = pd.DataFrame(eval_rows).sort_values('score_promedio_tfidf', ascending=False).reset_index(drop=True)
df_eval.to_csv(OUT_EVAL, index=False, encoding='utf-8')
print(f"✅ Evaluación simple guardada en: {OUT_EVAL}")
print("\nEvaluación (primeras filas):\n", df_eval.head(15))

print("\n🔚 Proceso completado. Archivos generados:")
print(" -", OUT_TFIDF)
print(" -", OUT_FREQ)
print(" -", OUT_EVAL)
