"""
Página Streamlit - Requerimiento 3: Análisis de Palabras Clave
"""

import streamlit as st
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import re
import bibtexparser
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
from collections import Counter

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.title("📊 Requerimiento 3: Análisis de Palabras Clave")

st.markdown("""
### Descripción
Este módulo analiza:
- **Frecuencia de palabras asociadas** a "Concepts of Generative AI in Education"
- **Generación de nuevas palabras clave** usando TF-IDF
- **Evaluación de precisión** de las nuevas palabras
""")

st.markdown("---")

# Palabras asociadas iniciales
PALABRAS_ASOCIADAS = [
    "generative models", "prompting", "machine learning", "multimodality",
    "fine-tuning", "training data", "algorithmic bias", "explainability",
    "transparency", "ethics", "privacy", "personalization",
    "human-ai interaction", "ai literacy", "co-creation"
]

# Cargar datos
BIB_PATH = BASE_DIR / "Requerimiento1" / "ArchivosFiltrados" / "articulosOptimos_limpio.bib"
ABSTRACTS_CSV = BASE_DIR / "Requerimiento3" / "DatosProcesados" / "abstracts_limpios.csv"

if not BIB_PATH.exists():
    st.error("❌ No se encontró el archivo BibTeX. Por favor, ejecuta el Requerimiento 1 primero.")
    st.stop()

# Función para limpiar texto
def limpiar_texto(texto: str) -> str:
    if not texto:
        return ""
    texto = re.sub(r'<[^>]+>', ' ', texto)
    texto = texto.lower()
    texto = re.sub(r'[^a-záéíóúüñ\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# Cargar abstracts
@st.cache_data
def cargar_abstracts():
    """Carga abstracts desde el archivo BibTeX."""
    try:
        with open(BIB_PATH, encoding="utf-8") as bibfile:
            bib_database = bibtexparser.load(bibfile)
        
        abstracts = []
        for entry in bib_database.entries:
            abstract = entry.get("abstract", "")
            if abstract:
                abstracts.append(limpiar_texto(abstract))
        return abstracts
    except Exception as e:
        st.error(f"Error al cargar archivo: {e}")
        return []

abstracts = cargar_abstracts()

if not abstracts:
    st.error("No se encontraron abstracts en el archivo.")
    st.stop()

st.success(f"✅ Se cargaron {len(abstracts)} abstracts")

# Análisis de frecuencia
st.subheader("📈 Frecuencia de Palabras Asociadas")

if st.button("🔍 Analizar Frecuencia", type="primary"):
    with st.spinner("Analizando frecuencias..."):
        texto_completo = " ".join(abstracts).lower()
        
        resultados = []
        for palabra in PALABRAS_ASOCIADAS:
            # Buscar la palabra (puede estar como palabra completa o parte de otra)
            patron = r'\b' + re.escape(palabra.lower()) + r'\b'
            frecuencia = len(re.findall(patron, texto_completo))
            resultados.append({
                "Palabra": palabra,
                "Frecuencia": frecuencia
            })
        
        df_freq = pd.DataFrame(resultados)
        df_freq = df_freq.sort_values("Frecuencia", ascending=False)
        
        # Mostrar tabla
        st.dataframe(df_freq, use_container_width=True)
        
        # Gráfico
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(df_freq["Palabra"], df_freq["Frecuencia"], color='steelblue')
        ax.set_xlabel("Frecuencia", fontsize=12)
        ax.set_title("Frecuencia de Palabras Asociadas", fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)

st.markdown("---")

# Generación de nuevas palabras
st.subheader("🆕 Generación de Nuevas Palabras Clave (TF-IDF)")

num_palabras = st.slider("Número de palabras clave a generar", 5, 50, 15)

if st.button("🔍 Generar Nuevas Palabras", type="primary"):
    with st.spinner("Generando palabras clave..."):
        try:
            # Vectorizar con TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),  # Unigramas y bigramas
                min_df=2,  # Mínimo 2 documentos
                max_df=0.95  # Máximo 95% de documentos
            )
            
            X = vectorizer.fit_transform(abstracts)
            features = vectorizer.get_feature_names_out()
            scores = np.array(X.mean(axis=0)).flatten()
            
            # Obtener top palabras
            top_indices = scores.argsort()[-num_palabras:][::-1]
            nuevas_palabras = []
            
            for idx in top_indices:
                nuevas_palabras.append({
                    "Palabra": features[idx],
                    "Score TF-IDF": f"{scores[idx]:.4f}",
                    "Valor": scores[idx]
                })
            
            df_nuevas = pd.DataFrame(nuevas_palabras)
            
            # Mostrar resultados
            st.dataframe(df_nuevas[["Palabra", "Score TF-IDF"]], use_container_width=True)
            
            # Gráfico
            fig, ax = plt.subplots(figsize=(10, 8))
            palabras = df_nuevas["Palabra"].tolist()
            valores = df_nuevas["Valor"].tolist()
            ax.barh(palabras, valores, color='coral')
            ax.set_xlabel("Score TF-IDF", fontsize=12)
            ax.set_title(f"Top {num_palabras} Nuevas Palabras Clave", fontsize=14, fontweight='bold')
            ax.invert_yaxis()
            plt.tight_layout()
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error al generar palabras: {e}")

st.markdown("---")

# Información adicional
st.info("""
💡 **Nota**: 
- Las palabras asociadas son las definidas en el requerimiento
- Las nuevas palabras se generan usando TF-IDF sobre todos los abstracts
- El score TF-IDF indica la importancia de cada palabra en el corpus
""")

# Verificar si existen archivos procesados
if ABSTRACTS_CSV.exists():
    st.markdown("---")
    st.subheader("📁 Archivos Procesados")
    
    try:
        df_procesado = pd.read_csv(ABSTRACTS_CSV)
        st.success(f"✅ Archivo de abstracts procesados encontrado: {len(df_procesado)} registros")
        
        with st.expander("Ver muestra de datos procesados"):
            st.dataframe(df_procesado.head(10))
    except Exception as e:
        st.warning(f"No se pudo leer el archivo procesado: {e}")

