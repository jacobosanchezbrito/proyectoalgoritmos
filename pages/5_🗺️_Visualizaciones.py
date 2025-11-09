"""
Página Streamlit - Requerimiento 5: Visualizaciones
"""

import streamlit as st
import sys
from pathlib import Path

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.title("🗺️ Requerimiento 5: Análisis Visual de Producción Científica")

st.markdown("""
### Descripción
Este módulo genera tres visualizaciones principales:
1. **Mapa de Calor** - Distribución geográfica según primer autor
2. **Nube de Palabras** - Términos más frecuentes en abstracts y keywords
3. **Línea Temporal** - Publicaciones por año y por revista

Todas las visualizaciones se pueden exportar a PDF.
""")

st.markdown("---")

# Verificar archivo BibTeX
BIB_PATH = BASE_DIR / "Requerimiento1" / "ArchivosFiltrados" / "articulosOptimos_limpio.bib"

if not BIB_PATH.exists():
    st.error("❌ No se encontró el archivo BibTeX. Por favor, ejecuta el Requerimiento 1 primero.")
    st.stop()

# Verificar dependencias
try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    st.error("""
    ❌ **geopandas no está instalado**
    
    El mapa de calor requiere geopandas. Para instalarlo:
    
    **Opción 1 (Recomendada) - Usar Conda:**
    ```bash
    conda install -c conda-forge geopandas
    ```
    
    **Opción 2 - Usar pip (puede ser complicado en Windows):**
    ```bash
    pip install geopandas
    ```
    
    Ver el README del Requerimiento 5 para más detalles.
    """)

# Importar funciones del Requerimiento 5
try:
    sys.path.insert(0, str(BASE_DIR / "Requerimiento5"))
    from requerimiento5_completo import (
        cargar_articulos_desde_bib,
        generar_mapa_calor,
        generar_nube_palabras,
        generar_linea_temporal,
        exportar_a_pdf
    )
    FUNCIONES_DISPONIBLES = True
except ImportError as e:
    FUNCIONES_DISPONIBLES = False
    st.warning(f"No se pudieron importar las funciones del Requerimiento 5: {e}")

if not FUNCIONES_DISPONIBLES:
    st.stop()

# Directorio de salida
OUTPUT_DIR = BASE_DIR / "Requerimiento5" / "Resultados"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cargar artículos
st.subheader("📖 Cargar Datos")

if st.button("📥 Cargar Artículos", type="primary"):
    with st.spinner("Cargando artículos..."):
        try:
            articulos = cargar_articulos_desde_bib(BIB_PATH)
            st.session_state['articulos'] = articulos
            st.success(f"✅ Se cargaron {len(articulos)} artículos")
        except Exception as e:
            st.error(f"Error al cargar artículos: {e}")

if 'articulos' not in st.session_state:
    st.info("💡 Haz clic en 'Cargar Artículos' para comenzar")
    st.stop()

articulos = st.session_state['articulos']

st.markdown("---")

# Generar visualizaciones
st.subheader("🎨 Generar Visualizaciones")

col1, col2, col3 = st.columns(3)

with col1:
    generar_mapa = st.button("🗺️ Generar Mapa de Calor", type="primary", disabled=not GEOPANDAS_AVAILABLE)

with col2:
    generar_nube = st.button("☁️ Generar Nube de Palabras", type="primary")

with col3:
    generar_temporal = st.button("📅 Generar Línea Temporal", type="primary")

# Mapa de calor
if generar_mapa:
    if not GEOPANDAS_AVAILABLE:
        st.error("geopandas no está disponible")
    else:
        with st.spinner("Generando mapa de calor..."):
            try:
                mapa_path = generar_mapa_calor(articulos, OUTPUT_DIR)
                if mapa_path and mapa_path.exists():
                    st.success("✅ Mapa de calor generado")
                    st.image(str(mapa_path), use_container_width=True)
                    
                    # Descargar
                    with open(mapa_path, 'rb') as f:
                        st.download_button(
                            "📥 Descargar Mapa de Calor",
                            f.read(),
                            file_name="mapa_calor_distribucion.png",
                            mime="image/png"
                        )
            except Exception as e:
                st.error(f"Error al generar mapa: {e}")

# Nube de palabras
if generar_nube:
    with st.spinner("Generando nube de palabras..."):
        try:
            nube_path = generar_nube_palabras(articulos, OUTPUT_DIR)
            if nube_path and nube_path.exists():
                st.success("✅ Nube de palabras generada")
                st.image(str(nube_path), use_container_width=True)
                
                # Descargar
                with open(nube_path, 'rb') as f:
                    st.download_button(
                        "📥 Descargar Nube de Palabras",
                        f.read(),
                        file_name="nube_palabras.png",
                        mime="image/png"
                    )
        except Exception as e:
            st.error(f"Error al generar nube de palabras: {e}")

# Línea temporal
if generar_temporal:
    with st.spinner("Generando línea temporal..."):
        try:
            temporal_path = generar_linea_temporal(articulos, OUTPUT_DIR)
            if temporal_path and temporal_path.exists():
                st.success("✅ Línea temporal generada")
                st.image(str(temporal_path), use_container_width=True)
                
                # Descargar
                with open(temporal_path, 'rb') as f:
                    st.download_button(
                        "📥 Descargar Línea Temporal",
                        f.read(),
                        file_name="linea_temporal.png",
                        mime="image/png"
                    )
        except Exception as e:
            st.error(f"Error al generar línea temporal: {e}")

st.markdown("---")

# Exportar a PDF
st.subheader("📄 Exportar a PDF")

if st.button("📥 Generar PDF con Todas las Visualizaciones", type="primary"):
    with st.spinner("Generando PDF..."):
        try:
            mapa_path = OUTPUT_DIR / "mapa_calor_distribucion.png"
            nube_path = OUTPUT_DIR / "nube_palabras.png"
            temporal_path = OUTPUT_DIR / "linea_temporal.png"
            
            # Verificar que existan las visualizaciones
            archivos_faltantes = []
            if not mapa_path.exists():
                archivos_faltantes.append("Mapa de calor")
            if not nube_path.exists():
                archivos_faltantes.append("Nube de palabras")
            if not temporal_path.exists():
                archivos_faltantes.append("Línea temporal")
            
            if archivos_faltantes:
                st.warning(f"⚠️ Faltan las siguientes visualizaciones: {', '.join(archivos_faltantes)}")
                st.info("💡 Genera todas las visualizaciones primero antes de exportar a PDF")
            else:
                pdf_path = exportar_a_pdf(mapa_path, nube_path, temporal_path, OUTPUT_DIR)
                if pdf_path and pdf_path.exists():
                    st.success("✅ PDF generado exitosamente")
                    
                    # Descargar
                    with open(pdf_path, 'rb') as f:
                        st.download_button(
                            "📥 Descargar PDF",
                            f.read(),
                            file_name="requerimiento5_visualizaciones.pdf",
                            mime="application/pdf"
                        )
        except Exception as e:
            st.error(f"Error al generar PDF: {e}")

st.markdown("---")

# Información adicional
st.info("""
💡 **Notas**:
- El mapa de calor requiere geopandas (ver instrucciones arriba)
- Las visualizaciones se guardan en `Requerimiento5/Resultados/`
- El PDF incluye las tres visualizaciones en un solo documento
- El proceso puede tardar varios minutos dependiendo del número de artículos
""")

# Verificar archivos existentes
st.markdown("---")
st.subheader("📁 Archivos Generados")

archivos = list(OUTPUT_DIR.glob("*.png")) + list(OUTPUT_DIR.glob("*.pdf"))
if archivos:
    for archivo in archivos:
        st.write(f"✅ {archivo.name}")
else:
    st.info("ℹ️ Aún no se han generado archivos")

