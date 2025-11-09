"""
Página Streamlit - Requerimiento 2: Análisis de Similitud Textual
"""

import streamlit as st
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import re
import bibtexparser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein
from sentence_transformers import SentenceTransformer
import matplotlib.pyplot as plt
import seaborn as sns

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.title("🔍 Requerimiento 2: Análisis de Similitud Textual")

st.markdown("""
### Descripción
Este módulo implementa **6 algoritmos de similitud textual**:
1. **Jaccard** - Coeficiente de Jaccard
2. **Coseno (TF-IDF)** - Similitud del coseno con vectorización TF-IDF
3. **Levenshtein** - Distancia de edición
4. **N-gramas** - Coincidencia de n-gramas
5. **DistilBERT** - Modelo de IA basado en BERT
6. **Sentence-BERT** - Modelo de IA para similitud semántica
""")

st.markdown("---")

# Cargar datos
BIB_PATH = BASE_DIR / "Requerimiento1" / "ArchivosFiltrados" / "articulosOptimos_limpio.bib"

if not BIB_PATH.exists():
    st.error("❌ No se encontró el archivo BibTeX. Por favor, ejecuta el Requerimiento 1 primero.")
    st.stop()

# Cargar artículos
@st.cache_data
def cargar_articulos():
    """Carga artículos desde el archivo BibTeX."""
    try:
        with open(BIB_PATH, encoding="utf-8") as bibfile:
            bib_database = bibtexparser.load(bibfile)
        
        data = []
        for entry in bib_database.entries:
            title = entry.get("title", "Sin título").replace("\n", " ").strip()
            abstract = entry.get("abstract", "").replace("\n", " ").strip()
            if abstract:
                data.append({
                    "ID": entry.get("ID", ""),
                    "titulo": title,
                    "abstract": abstract,
                    "autor": entry.get("author", ""),
                    "year": entry.get("year", "")
                })
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error al cargar archivo: {e}")
        return None

df = cargar_articulos()

if df is None or df.empty:
    st.error("No se encontraron artículos con abstracts en el archivo.")
    st.stop()

st.success(f"✅ Se cargaron {len(df)} artículos con abstracts")

# Funciones de similitud
def jaccard_similarity(a: str, b: str) -> float:
    A = set(re.findall(r'\w+', a.lower()))
    B = set(re.findall(r'\w+', b.lower()))
    return len(A & B) / len(A | B) if (A | B) else 0.0

def cosine_tfidf_similarity(a: str, b: str) -> float:
    vectorizer = TfidfVectorizer().fit([a, b])
    tfidf = vectorizer.transform([a, b])
    return float(cosine_similarity(tfidf[0], tfidf[1])[0][0])

def levenshtein_similarity(a: str, b: str) -> float:
    dist = Levenshtein.distance(a, b)
    return 1 - dist / max(len(a), len(b)) if max(len(a), len(b)) > 0 else 0

def ngram_overlap_similarity(a: str, b: str, n=3) -> float:
    def ngrams(text, n):
        text = re.sub(r'\s+', ' ', text.lower())
        return {text[i:i+n] for i in range(len(text) - n + 1)}
    A = ngrams(a, n)
    B = ngrams(b, n)
    return len(A & B) / len(A | B) if (A | B) else 0.0

# Modelos de IA (cargar una vez)
@st.cache_resource
def cargar_modelos():
    """Carga los modelos de IA."""
    try:
        # Usar los mismos modelos que el script original
        distilbert = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
        sbert = SentenceTransformer('all-MiniLM-L6-v2')
        return distilbert, sbert
    except Exception as e:
        st.warning(f"Error al cargar modelos de IA: {e}")
        st.info("💡 Los modelos de IA se descargarán la primera vez. Esto puede tardar varios minutos.")
        return None, None

distilbert_model, sbert_model = cargar_modelos()

def distilbert_similarity(a: str, b: str, model) -> float:
    if model is None:
        return 0.0
    embeddings = model.encode([a, b])
    return float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])

def sbert_similarity(a: str, b: str, model) -> float:
    if model is None:
        return 0.0
    embeddings = model.encode([a, b])
    return float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])

# Interfaz de usuario
st.subheader("📋 Seleccionar Artículos para Comparar")

# Selector de artículos
col1, col2 = st.columns(2)

with col1:
    articulo1_idx = st.selectbox(
        "Seleccionar primer artículo",
        range(len(df)),
        format_func=lambda x: f"{df.iloc[x]['titulo'][:60]}..." if len(df.iloc[x]['titulo']) > 60 else df.iloc[x]['titulo']
    )

with col2:
    # Filtrar para no permitir seleccionar el mismo artículo
    opciones_art2 = [i for i in range(len(df)) if i != articulo1_idx]
    articulo2_idx = st.selectbox(
        "Seleccionar segundo artículo",
        opciones_art2,
        format_func=lambda x: f"{df.iloc[x]['titulo'][:60]}..." if len(df.iloc[x]['titulo']) > 60 else df.iloc[x]['titulo']
    )

# Mostrar artículos seleccionados
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Artículo 1")
    art1 = df.iloc[articulo1_idx]
    st.write(f"**Título:** {art1['titulo']}")
    st.write(f"**Año:** {art1['year']}")
    st.write(f"**Abstract:** {art1['abstract'][:300]}...")

with col2:
    st.subheader("Artículo 2")
    art2 = df.iloc[articulo2_idx]
    st.write(f"**Título:** {art2['titulo']}")
    st.write(f"**Año:** {art2['year']}")
    st.write(f"**Abstract:** {art2['abstract'][:300]}...")

# Calcular similitudes
st.markdown("---")
st.subheader("📊 Resultados de Similitud")

if st.button("🔍 Calcular Similitud", type="primary"):
    with st.spinner("Calculando similitudes..."):
        abstract1 = art1['abstract']
        abstract2 = art2['abstract']
        
        resultados = {}
        
        # Algoritmos clásicos
        resultados['Jaccard'] = jaccard_similarity(abstract1, abstract2)
        resultados['Coseno (TF-IDF)'] = cosine_tfidf_similarity(abstract1, abstract2)
        resultados['Levenshtein'] = levenshtein_similarity(abstract1, abstract2)
        resultados['N-gramas'] = ngram_overlap_similarity(abstract1, abstract2)
        
        # Modelos de IA
        if distilbert_model is not None:
            try:
                resultados['DistilBERT'] = distilbert_similarity(abstract1, abstract2, distilbert_model)
            except Exception as e:
                st.warning(f"Error con DistilBERT: {e}")
                resultados['DistilBERT'] = None
        else:
            resultados['DistilBERT'] = None
            
        if sbert_model is not None:
            try:
                resultados['Sentence-BERT'] = sbert_similarity(abstract1, abstract2, sbert_model)
            except Exception as e:
                st.warning(f"Error con Sentence-BERT: {e}")
                resultados['Sentence-BERT'] = None
        else:
            resultados['Sentence-BERT'] = None
        
        # Mostrar resultados
        df_resultados = pd.DataFrame([
            {"Algoritmo": k, "Similitud": f"{v:.4f}" if v is not None else "N/A", "Valor": v if v is not None else 0}
            for k, v in resultados.items()
        ])
        
        st.dataframe(df_resultados[["Algoritmo", "Similitud"]], use_container_width=True)
        
        # Gráfico de barras
        fig, ax = plt.subplots(figsize=(10, 6))
        algoritmos = [k for k, v in resultados.items() if v is not None]
        valores = [v for k, v in resultados.items() if v is not None]
        
        bars = ax.barh(algoritmos, valores, color=sns.color_palette("viridis", len(algoritmos)))
        ax.set_xlabel("Similitud", fontsize=12)
        ax.set_title("Comparación de Algoritmos de Similitud", fontsize=14, fontweight='bold')
        ax.set_xlim(0, 1)
        
        # Agregar valores en las barras
        for i, (bar, val) in enumerate(zip(bars, valores)):
            ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                   f'{val:.4f}', va='center', fontsize=10)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Explicación
        with st.expander("📖 Explicación de los Algoritmos"):
            st.markdown("""
            **Jaccard**: Mide el solapamiento de conjuntos de palabras. Fórmula: |A ∩ B| / |A ∪ B|
            
            **Coseno (TF-IDF)**: Calcula la similitud del coseno entre vectores TF-IDF de los textos.
            
            **Levenshtein**: Mide la distancia de edición (caracteres a cambiar). Normalizada a 0-1.
            
            **N-gramas**: Compara secuencias de n caracteres. Mide solapamiento de n-gramas.
            
            **DistilBERT**: Modelo de IA basado en BERT que captura similitud semántica.
            
            **Sentence-BERT**: Modelo optimizado para similitud semántica entre oraciones.
            """)

st.markdown("---")
st.info("💡 **Nota**: Los modelos de IA pueden tardar en cargar la primera vez. Se cargan automáticamente al iniciar la aplicación.")

