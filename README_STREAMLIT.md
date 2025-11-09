# 🚀 Guía de Despliegue - Aplicación Streamlit

Esta guía explica cómo desplegar la aplicación Streamlit en Streamlit Cloud.

## 📋 Requisitos Previos

1. **Repositorio en GitHub** (público o privado con acceso)
2. **Cuenta de GitHub**
3. **Cuenta de Streamlit Cloud** (gratis, se crea con GitHub)

## 🛠️ Instalación Local (Para Pruebas)

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar Localmente

```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

## ☁️ Despliegue en Streamlit Cloud

### Paso 1: Preparar el Repositorio

Asegúrate de que tu repositorio tenga:
- ✅ `app.py` (aplicación principal)
- ✅ `requirements.txt` (dependencias)
- ✅ Carpeta `pages/` con las páginas de la aplicación
- ✅ Archivos de datos necesarios (BibTeX, etc.)

### Paso 2: Subir a GitHub

```bash
git add .
git commit -m "Agregar aplicación Streamlit"
git push
```

### Paso 3: Conectar con Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en "New app"
4. Selecciona tu repositorio
5. Selecciona la rama (generalmente `main`)
6. Especifica el archivo principal: `app.py`
7. Haz clic en "Deploy"

### Paso 4: Configurar (Opcional)

Si necesitas variables de entorno o configuración especial:

1. Ve a la configuración de la app en Streamlit Cloud
2. Agrega variables de entorno si es necesario
3. La app se actualizará automáticamente

## 📁 Estructura del Proyecto

```
proyectoalgoritmos/
├── app.py                          # Aplicación principal
├── requirements.txt                # Dependencias
├── README_STREAMLIT.md            # Este archivo
├── pages/                          # Páginas de la app
│   ├── 1_📥_Descarga_Datos.py
│   ├── 2_🔍_Similitud_Textual.py
│   ├── 3_📊_Palabras_Clave.py
│   ├── 4_🌳_Clustering.py
│   └── 5_🗺️_Visualizaciones.py
├── Requerimiento1/                 # Módulos existentes
├── Requerimiento2/
├── Requerimiento3/
├── Requerimiento4/
└── Requerimiento5/
```

## ⚠️ Notas Importantes

### Geopandas en Streamlit Cloud

El Requerimiento 5 requiere `geopandas`, que puede ser complicado de instalar. Streamlit Cloud generalmente maneja esto bien, pero si hay problemas:

1. Asegúrate de que `geopandas` esté en `requirements.txt`
2. Streamlit Cloud instalará las dependencias automáticamente
3. Si falla, verifica los logs de despliegue

### Archivos de Datos

- Los archivos BibTeX deben estar en el repositorio o ser cargados por el usuario
- Los archivos generados se guardan temporalmente durante la sesión
- Para persistencia, considera usar almacenamiento externo (S3, etc.)

### Límites de Streamlit Cloud

- **Gratis**: Aplicaciones públicas ilimitadas
- **Memoria**: Limitada (suficiente para la mayoría de casos)
- **CPU**: Compartida (puede ser lenta con procesamientos pesados)
- **Tiempo de ejecución**: Limitado (timeout después de inactividad)

## 🔧 Solución de Problemas

### Error: "Module not found"

- Verifica que todas las dependencias estén en `requirements.txt`
- Revisa los logs de despliegue en Streamlit Cloud

### Error: "File not found"

- Verifica que los archivos de datos estén en el repositorio
- Asegúrate de que las rutas sean correctas (relativas al directorio raíz)

### Error: "Geopandas installation failed"

- Streamlit Cloud generalmente maneja geopandas bien
- Si falla, verifica la versión en `requirements.txt`
- Considera usar una versión específica: `geopandas==0.13.0`

### La aplicación es lenta

- Streamlit Cloud usa recursos compartidos
- Para procesamientos pesados, considera optimizar el código
- Usa `@st.cache_data` y `@st.cache_resource` para cachear resultados

## 📚 Recursos Adicionales

- [Documentación de Streamlit](https://docs.streamlit.io/)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Ejemplos de Streamlit](https://streamlit.io/gallery)

## 🎉 ¡Listo!

Una vez desplegado, tu aplicación estará disponible en:
`https://[tu-usuario]-[tu-app].streamlit.app`

Comparte este enlace para que otros puedan usar tu aplicación.

---

**Nota**: Esta aplicación está diseñada para análisis bibliométrico. Asegúrate de tener los datos necesarios antes de usar cada módulo.

