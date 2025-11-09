"""
Aplicación Streamlit - Análisis Bibliométrico
Integra todos los requerimientos del proyecto
"""

import streamlit as st
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Análisis Bibliométrico",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📚 Análisis Bibliométrico de Producción Científica")
st.markdown("---")
st.markdown("""
### Bienvenido al Sistema de Análisis Bibliométrico

Esta aplicación integra todos los módulos de análisis para la producción científica:

- **Requerimiento 1**: Descarga y unificación de datos de bases de datos científicas
- **Requerimiento 2**: Análisis de similitud textual con múltiples algoritmos
- **Requerimiento 3**: Análisis de palabras clave y frecuencias
- **Requerimiento 4**: Clustering jerárquico y dendrogramas
- **Requerimiento 5**: Visualizaciones (mapa de calor, nube de palabras, línea temporal)

Usa el menú lateral para navegar entre los diferentes módulos.
""")

# Información sobre el proyecto
with st.expander("ℹ️ Información del Proyecto"):
    st.markdown("""
    ### Descripción
    
    Este sistema permite realizar un análisis completo de la producción científica
    en el área de "Concepts of Generative AI in Education", incluyendo:
    
    - Descarga automatizada de artículos de múltiples bases de datos
    - Análisis de similitud entre documentos
    - Extracción y análisis de palabras clave
    - Agrupamiento de documentos similares
    - Visualización de resultados geográficos y temporales
    
    ### Requisitos
    
    - Archivo BibTeX con los artículos científicos
    - Dependencias instaladas (ver requirements.txt)
    - Para el Requerimiento 5, se requiere geopandas (ver README)
    """)

# Estado del sistema
st.sidebar.title("📊 Estado del Sistema")

# Verificar archivos importantes
BASE_DIR = Path(__file__).resolve().parent
BIB_PATH = BASE_DIR / "Requerimiento1" / "ArchivosFiltrados" / "articulosOptimos_limpio.bib"

if BIB_PATH.exists():
    st.sidebar.success("✅ Archivo BibTeX encontrado")
    st.sidebar.info(f"📄 {BIB_PATH.name}")
else:
    st.sidebar.warning("⚠️ Archivo BibTeX no encontrado")
    st.sidebar.info("Ejecuta el Requerimiento 1 para generar los datos")

# Información adicional
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Navegación")
st.sidebar.markdown("""
Usa el menú superior para acceder a:
- 📥 Descarga de Datos
- 🔍 Similitud Textual
- 📊 Palabras Clave
- 🌳 Clustering
- 🗺️ Visualizaciones
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Despliegue")
st.sidebar.markdown("""
Esta aplicación está diseñada para desplegarse en:
- Streamlit Cloud (recomendado)
- Servidor local
- Docker
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Sistema de Análisis Bibliométrico - Proyecto Algoritmos</p>
</div>
""", unsafe_allow_html=True)

