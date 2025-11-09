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

# Inicializar session state para artículos seleccionados
if 'articulos_seleccionados' not in st.session_state:
    st.session_state['articulos_seleccionados'] = [0, 1]  # Dos artículos por defecto

# Mostrar artículos seleccionados
st.write("**Artículos seleccionados:**")

# Crear selectores dinámicos para cada artículo
for idx in range(len(st.session_state['articulos_seleccionados'])):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        # Permitir seleccionar cualquier artículo
        art_idx_actual = st.session_state['articulos_seleccionados'][idx]
        
        nuevo_idx = st.selectbox(
            f"Artículo {idx + 1}",
            range(len(df)),
            index=art_idx_actual,
            key=f"articulo_select_{idx}",
            format_func=lambda x: f"{df.iloc[x]['titulo'][:60]}..." if len(df.iloc[x]['titulo']) > 60 else df.iloc[x]['titulo']
        )
        
        # Actualizar el índice
        st.session_state['articulos_seleccionados'][idx] = nuevo_idx
        
        # Mostrar advertencia si hay duplicados
        seleccionados = st.session_state['articulos_seleccionados']
        if seleccionados.count(nuevo_idx) > 1:
            st.warning(f"⚠️ Este artículo ya está seleccionado en otra posición")
    
    with col2:
        # Botón para eliminar (solo si hay más de 2 artículos)
        if len(st.session_state['articulos_seleccionados']) > 2:
            if st.button("🗑️", key=f"eliminar_{idx}", help="Eliminar este artículo"):
                st.session_state['articulos_seleccionados'].pop(idx)
                st.rerun()
        else:
            st.write("")  # Espacio vacío para mantener alineación

# Botón para agregar artículo
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("➕ Agregar Artículo", type="primary"):
        # Agregar el primer artículo disponible (o el primero si todos están seleccionados)
        seleccionados = st.session_state['articulos_seleccionados']
        disponibles = [i for i in range(len(df)) if i not in seleccionados]
        if disponibles:
            st.session_state['articulos_seleccionados'].append(disponibles[0])
        else:
            # Si todos están seleccionados, agregar el primero de todos modos
            st.session_state['articulos_seleccionados'].append(0)
            st.info("ℹ️ Se agregó el artículo 1 (ya estaba seleccionado, pero puedes cambiarlo)")
        st.rerun()

# Obtener índices finales
indices_seleccionados = st.session_state['articulos_seleccionados']

# Mostrar información de artículos seleccionados
st.markdown("---")
st.subheader("📄 Información de Artículos Seleccionados")

# Mostrar información de cada artículo
for idx, art_idx in enumerate(indices_seleccionados):
    with st.expander(f"Artículo {idx + 1}: {df.iloc[art_idx]['titulo'][:80]}..."):
        art = df.iloc[art_idx]
        st.write(f"**Título:** {art['titulo']}")
        st.write(f"**Año:** {art['year']}")
        st.write(f"**Autor:** {art['autor'][:100]}..." if len(art['autor']) > 100 else f"**Autor:** {art['autor']}")
        st.write(f"**Abstract:** {art['abstract'][:500]}...")

# Calcular similitudes
st.markdown("---")
st.subheader("📊 Resultados de Similitud")

if len(indices_seleccionados) < 2:
    st.warning("⚠️ Debes seleccionar al menos 2 artículos para comparar")
else:
    if st.button("🔍 Calcular Similitud", type="primary"):
        with st.spinner("Calculando similitudes entre todos los artículos..."):
            # Obtener abstracts de los artículos seleccionados
            abstracts_seleccionados = [df.iloc[idx]['abstract'] for idx in indices_seleccionados]
            titulos_seleccionados = [df.iloc[idx]['titulo'][:50] + "..." if len(df.iloc[idx]['titulo']) > 50 
                                    else df.iloc[idx]['titulo'] for idx in indices_seleccionados]
            
            # Lista de algoritmos a calcular
            algoritmos = ['Jaccard', 'Coseno (TF-IDF)', 'Levenshtein', 'N-gramas']
            if distilbert_model is not None:
                algoritmos.append('DistilBERT')
            if sbert_model is not None:
                algoritmos.append('Sentence-BERT')
            
            # Calcular matrices de similitud para cada algoritmo
            matrices_resultados = {}
            
            n = len(abstracts_seleccionados)
            
            # Jaccard
            matriz_jaccard = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    if i == j:
                        matriz_jaccard[i, j] = 1.0
                    else:
                        matriz_jaccard[i, j] = jaccard_similarity(abstracts_seleccionados[i], abstracts_seleccionados[j])
            matrices_resultados['Jaccard'] = matriz_jaccard
            
            # Coseno TF-IDF
            vectorizer = TfidfVectorizer().fit(abstracts_seleccionados)
            tfidf_matrix = vectorizer.transform(abstracts_seleccionados)
            matrices_resultados['Coseno (TF-IDF)'] = cosine_similarity(tfidf_matrix)
            
            # Levenshtein
            matriz_lev = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    if i == j:
                        matriz_lev[i, j] = 1.0
                    else:
                        matriz_lev[i, j] = levenshtein_similarity(abstracts_seleccionados[i], abstracts_seleccionados[j])
            matrices_resultados['Levenshtein'] = matriz_lev
            
            # N-gramas
            matriz_ng = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    if i == j:
                        matriz_ng[i, j] = 1.0
                    else:
                        matriz_ng[i, j] = ngram_overlap_similarity(abstracts_seleccionados[i], abstracts_seleccionados[j])
            matrices_resultados['N-gramas'] = matriz_ng
            
            # DistilBERT
            if distilbert_model is not None:
                try:
                    embeddings_distil = distilbert_model.encode(abstracts_seleccionados)
                    matrices_resultados['DistilBERT'] = cosine_similarity(embeddings_distil)
                except Exception as e:
                    st.warning(f"Error con DistilBERT: {e}")
            
            # Sentence-BERT
            if sbert_model is not None:
                try:
                    embeddings_sbert = sbert_model.encode(abstracts_seleccionados)
                    matrices_resultados['Sentence-BERT'] = cosine_similarity(embeddings_sbert)
                except Exception as e:
                    st.warning(f"Error con Sentence-BERT: {e}")
            
            # Mostrar resultados
            st.success(f"✅ Similitud calculada para {n} artículos")
            
            # Mostrar matrices de similitud
            st.markdown("### 📊 Matrices de Similitud")
            
            for algo_name, matriz in matrices_resultados.items():
                st.markdown(f"#### {algo_name}")
                
                # Crear DataFrame con la matriz
                df_matriz = pd.DataFrame(
                    matriz,
                    index=[f"Art {i+1}" for i in range(n)],
                    columns=[f"Art {i+1}" for i in range(n)]
                )
                
                # Mostrar matriz
                st.dataframe(df_matriz.style.format("{:.4f}").background_gradient(cmap='viridis', vmin=0, vmax=1), 
                           use_container_width=True)
                
                # Visualización de heatmap
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(matriz, annot=True, fmt='.3f', cmap='viridis', 
                           xticklabels=[f"Art {i+1}" for i in range(n)],
                           yticklabels=[f"Art {i+1}" for i in range(n)],
                           vmin=0, vmax=1, ax=ax, cbar_kws={'label': 'Similitud'})
                ax.set_title(f"Matriz de Similitud - {algo_name}", fontsize=14, fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            
            # Comparación de algoritmos (promedio de similitudes)
            st.markdown("### 📈 Comparación de Algoritmos")
            
            # Calcular promedios (excluyendo diagonal)
            promedios = {}
            for algo_name, matriz in matrices_resultados.items():
                # Obtener solo la parte superior (sin diagonal)
                mask = np.triu(np.ones_like(matriz, dtype=bool), k=1)
                valores = matriz[mask]
                promedios[algo_name] = np.mean(valores) if len(valores) > 0 else 0
            
            df_promedios = pd.DataFrame([
                {"Algoritmo": k, "Promedio": f"{v:.4f}", "Valor": v}
                for k, v in promedios.items()
            ])
            df_promedios = df_promedios.sort_values("Valor", ascending=False)
            
            st.dataframe(df_promedios[["Algoritmo", "Promedio"]], use_container_width=True)
            
            # Gráfico de barras de promedios
            fig, ax = plt.subplots(figsize=(10, 6))
            algoritmos_ordenados = df_promedios["Algoritmo"].tolist()
            valores_promedios = df_promedios["Valor"].tolist()
            
            bars = ax.barh(algoritmos_ordenados, valores_promedios, color=sns.color_palette("viridis", len(algoritmos_ordenados)))
            ax.set_xlabel("Similitud Promedio", fontsize=12)
            ax.set_title("Comparación de Algoritmos - Promedio de Similitud", fontsize=14, fontweight='bold')
            ax.set_xlim(0, 1)
            
            # Agregar valores en las barras
            for bar, val in zip(bars, valores_promedios):
                ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
                       f'{val:.4f}', ha='left', va='center', fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
            
            # Explicación
            with st.expander("📖 Explicación de los Algoritmos"):
                st.markdown("""
                **Jaccard**: Mide el solapamiento de conjuntos de palabras. Fórmula: |A ∩ B| / |A ∪ B|
                
                **Coseno (TF-IDF)**: Calcula la similitud del coseno entre vectores TF-IDF de los textos.
                
                **Levenshtein**: Mide la distancia de edición (caracteres a cambiar). Normalizada a 0-1.
                
                **N-gramas**: Compara secuencias de n caracteres. Mide solapamiento de n-gramas.
                
                **DistilBERT**: Modelo de IA basado en BERT que captura similitud semántica.
                
                **Sentence-BERT**: Modelo optimizado para similitud semántica entre oraciones.
                
                **Nota**: Los valores en la diagonal son 1.0 (similitud consigo mismo). 
                La matriz es simétrica (similitud(A,B) = similitud(B,A)).
                """)

st.markdown("---")
st.info("💡 **Nota**: Los modelos de IA pueden tardar en cargar la primera vez. Se cargan automáticamente al iniciar la aplicación.")

