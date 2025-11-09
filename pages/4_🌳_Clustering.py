"""
Página Streamlit - Requerimiento 4: Clustering Jerárquico
"""

import streamlit as st
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import linkage, dendrogram, cophenet, fcluster
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.title("🌳 Requerimiento 4: Clustering Jerárquico")

st.markdown("""
### Descripción
Este módulo implementa **3 algoritmos de agrupamiento jerárquico**:
1. **Single Linkage** - Enlace simple (mínima distancia)
2. **Complete Linkage** - Enlace completo (máxima distancia)
3. **Average Linkage** - Enlace promedio (distancia promedio)

Cada algoritmo genera un dendrograma que representa la similitud entre abstracts científicos.
""")

st.markdown("---")

# Cargar datos
ABSTRACTS_CSV = BASE_DIR / "Requerimiento3" / "DatosProcesados" / "abstracts_limpios.csv"
BIB_PATH = BASE_DIR / "Requerimiento1" / "ArchivosFiltrados" / "articulosOptimos_limpio.bib"

if not ABSTRACTS_CSV.exists():
    st.warning("⚠️ No se encontró el archivo de abstracts procesados.")
    st.info("💡 Ejecuta el Requerimiento 3 primero para procesar los abstracts.")
    
    # Opción alternativa: procesar desde BibTeX
    if BIB_PATH.exists():
        st.markdown("### Procesar desde BibTeX")
        if st.button("Procesar abstracts ahora"):
            with st.spinner("Procesando abstracts..."):
                # Aquí iría la lógica de procesamiento
                st.info("Esta funcionalidad requiere ejecutar el script de preparación de datos.")
    st.stop()

# Cargar datos
@st.cache_data
def cargar_datos():
    """Carga los abstracts procesados."""
    try:
        df = pd.read_csv(ABSTRACTS_CSV)
        if 'abstract_limpio' not in df.columns:
            st.error("El archivo CSV no tiene la columna 'abstract_limpio'")
            return None
        
        df = df.dropna(subset=['abstract_limpio']).drop_duplicates(subset=['abstract_limpio']).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return None

df = cargar_datos()

if df is None:
    st.stop()

st.success(f"✅ Se cargaron {len(df)} abstracts procesados")

# Configuración
st.subheader("⚙️ Configuración")

max_abstracts = st.slider(
    "Número máximo de abstracts a analizar",
    min_value=50,
    max_value=min(500, len(df)),
    value=min(200, len(df)),
    step=50
)

metodos = st.multiselect(
    "Seleccionar métodos de clustering",
    ['single', 'complete', 'average'],
    default=['single', 'complete', 'average']
)

# Procesar
if st.button("🌳 Generar Dendrogramas", type="primary"):
    with st.spinner("Procesando clustering..."):
        # Tomar muestra
        df_sample = df.head(max_abstracts).copy()
        abstracts = df_sample['abstract_limpio'].tolist()
        
        # Vectorizar
        st.info("Vectorizando abstracts con TF-IDF...")
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X = vectorizer.fit_transform(abstracts).toarray()
        
        # Eliminar filas con vectores cero
        filas_validas = np.any(X != 0, axis=1)
        X = X[filas_validas]
        df_sample = df_sample[filas_validas].reset_index(drop=True)
        
        st.success(f"✅ {len(df_sample)} abstracts válidos para clustering")
        
        # Calcular distancias
        st.info("Calculando matriz de distancias...")
        dist_matrix = pdist(X, 'cosine')
        
        resultados_cophenetic = []
        
        # Generar dendrogramas
        for metodo in metodos:
            st.info(f"Procesando método: {metodo}...")
            
            try:
                # Aplicar clustering
                Z = linkage(dist_matrix, method=metodo)
                coph_corr, _ = cophenet(Z, dist_matrix)
                resultados_cophenetic.append({
                    "Método": metodo.upper(),
                    "Correlación Cophenética": f"{coph_corr:.4f}",
                    "Valor": coph_corr
                })
                
                # Generar dendrograma
                fig, ax = plt.subplots(figsize=(14, 8))
                dendrogram(
                    Z,
                    leaf_rotation=90,
                    leaf_font_size=8,
                    color_threshold=0.7,
                    above_threshold_color='gray',
                    truncate_mode='level',
                    p=10
                )
                ax.set_title(f"Dendrograma - {metodo.upper()} Linkage\nCorrelación Cophenética: {coph_corr:.4f}", 
                           fontsize=14, fontweight='bold')
                ax.set_xlabel("Abstracts", fontsize=12)
                ax.set_ylabel("Distancia", fontsize=12)
                plt.tight_layout()
                
                st.pyplot(fig)
                plt.close()
                
            except Exception as e:
                st.error(f"Error al procesar método {metodo}: {e}")
        
        # Mostrar comparación
        if resultados_cophenetic:
            st.markdown("---")
            st.subheader("📊 Comparación de Métodos")
            
            df_comparacion = pd.DataFrame(resultados_cophenetic)
            df_comparacion = df_comparacion.sort_values("Valor", ascending=False)
            
            st.dataframe(df_comparacion[["Método", "Correlación Cophenética"]], use_container_width=True)
            
            # Gráfico de comparación
            fig, ax = plt.subplots(figsize=(10, 6))
            metodos_nombres = df_comparacion["Método"].tolist()
            valores = df_comparacion["Valor"].tolist()
            bars = ax.bar(metodos_nombres, valores, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
            ax.set_ylabel("Correlación Cophenética", fontsize=12)
            ax.set_title("Comparación de Métodos de Clustering", fontsize=14, fontweight='bold')
            ax.set_ylim(0, 1)
            
            # Agregar valores en las barras
            for bar, val in zip(bars, valores):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{val:.4f}', ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Mejor método
            mejor_metodo = df_comparacion.iloc[0]
            st.success(f"🏆 Mejor método: **{mejor_metodo['Método']}** con correlación cophenética de **{mejor_metodo['Correlación Cophenética']}**")
            
            st.info("""
            💡 **Interpretación**: 
            - La correlación cophenética mide qué tan bien el dendrograma preserva las distancias originales
            - Un valor más alto indica mejor preservación de la estructura de datos
            - El mejor método es el que tiene la mayor correlación cophenética
            """)

st.markdown("---")

# Información adicional
with st.expander("📖 Explicación de los Métodos"):
    st.markdown("""
    **Single Linkage (Enlace Simple)**:
    - Usa la mínima distancia entre clusters
    - Tiende a crear clusters largos y delgados
    - Sensible a outliers
    
    **Complete Linkage (Enlace Completo)**:
    - Usa la máxima distancia entre clusters
    - Tiende a crear clusters compactos y esféricos
    - Menos sensible a outliers
    
    **Average Linkage (Enlace Promedio)**:
    - Usa la distancia promedio entre clusters
    - Balance entre single y complete
    - Generalmente produce resultados equilibrados
    """)

