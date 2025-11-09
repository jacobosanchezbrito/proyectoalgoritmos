"""
Página Streamlit - Requerimiento 1: Descarga y Unificación de Datos
"""

import streamlit as st
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.title("📥 Requerimiento 1: Descarga y Unificación de Datos")

st.markdown("""
### Descripción
Este módulo permite:
- Descargar artículos de múltiples bases de datos (ACM, SAGE, Elsevier)
- Unificar la información en un solo archivo
- Eliminar duplicados basados en DOI
- Generar archivos de artículos óptimos y descartados
""")

st.markdown("---")

# Información sobre el proceso
with st.expander("ℹ️ Información sobre el proceso"):
    st.markdown("""
    #### Proceso Automático:
    1. **Descarga**: Se descargan artículos de ACM, SAGE y Elsevier
    2. **Filtrado**: Se filtran artículos que:
       - Tienen DOI único
       - Tienen abstract disponible
    3. **Unificación**: Se crea un archivo único con todos los artículos válidos
    4. **Archivos generados**:
       - `articulosOptimos_limpio.bib`: Artículos válidos y limpios
       - `articulosDescartados.bib`: Artículos descartados (duplicados, sin abstract)
    """)

# Estado de archivos
st.subheader("📊 Estado de Archivos")

BIB_PATH = BASE_DIR / "Requerimiento1" / "ArchivosFiltrados" / "articulosOptimos_limpio.bib"
DESCARTADOS_PATH = BASE_DIR / "Requerimiento1" / "ArchivosFiltrados" / "articulosDescartados.bib"

col1, col2 = st.columns(2)

with col1:
    if BIB_PATH.exists():
        st.success("✅ Archivo de artículos óptimos encontrado")
        # Contar artículos
        try:
            import bibtexparser
            with open(BIB_PATH, 'r', encoding='utf-8') as f:
                parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                bib_database = parser.parse_file(f)
                num_articulos = len(bib_database.entries)
                st.metric("Artículos óptimos", num_articulos)
        except Exception as e:
            st.warning(f"No se pudo leer el archivo: {e}")
    else:
        st.warning("⚠️ Archivo de artículos óptimos no encontrado")

with col2:
    if DESCARTADOS_PATH.exists():
        st.info("ℹ️ Archivo de artículos descartados encontrado")
        try:
            import bibtexparser
            with open(DESCARTADOS_PATH, 'r', encoding='utf-8') as f:
                parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                bib_database = parser.parse_file(f)
                num_descartados = len(bib_database.entries)
                st.metric("Artículos descartados", num_descartados)
        except Exception as e:
            st.warning(f"No se pudo leer el archivo: {e}")
    else:
        st.info("ℹ️ No hay archivo de descartados")

st.markdown("---")

# Opciones de ejecución
st.subheader("🚀 Ejecutar Proceso")

st.warning("""
⚠️ **Nota**: La descarga de artículos desde las APIs requiere:
- Claves API válidas
- Conexión a internet
- Tiempo de procesamiento (puede tardar varios minutos)

Para ejecutar el proceso completo, usa los scripts desde la terminal:
- `Requerimiento1/Descargaarchivos.py` - Descarga artículos
- `Requerimiento1/filtrararticulos.py` - Filtra y unifica
- `Requerimiento1/completarabstracts.py` - Completa abstracts faltantes
""")

# Mostrar archivos disponibles para descarga
if BIB_PATH.exists():
    st.subheader("📥 Descargar Archivos")
    
    with open(BIB_PATH, 'rb') as f:
        st.download_button(
            label="📄 Descargar artículos óptimos (BibTeX)",
            data=f.read(),
            file_name="articulosOptimos_limpio.bib",
            mime="application/x-bibtex"
        )

if DESCARTADOS_PATH.exists():
    with open(DESCARTADOS_PATH, 'rb') as f:
        st.download_button(
            label="📄 Descargar artículos descartados (BibTeX)",
            data=f.read(),
            file_name="articulosDescartados.bib",
            mime="application/x-bibtex"
        )

# Información adicional
st.markdown("---")
st.subheader("📖 Documentación")

with st.expander("Ver estructura de archivos"):
    st.code("""
Requerimiento1/
├── Descargaarchivos.py      # Script de descarga
├── filtrararticulos.py      # Script de filtrado
├── completarabstracts.py    # Script de completar abstracts
└── ArchivosFiltrados/
    ├── articulosOptimos_limpio.bib
    └── articulosDescartados.bib
    """)

st.info("""
💡 **Siguiente paso**: Una vez que tengas el archivo `articulosOptimos_limpio.bib`,
puedes usar los demás requerimientos para analizar los datos.
""")

