import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import linkage, dendrogram, cophenet, fcluster
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt

# ===============================================================
# FASE 1: Cargar y preparar los datos
# ===============================================================

RUTA_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RUTA_ARCHIVO = os.path.join(RUTA_BASE, 'Requerimiento3', 'DatosProcesados', 'abstracts_limpios.csv')

df = pd.read_csv(RUTA_ARCHIVO)

if 'abstract_limpio' not in df.columns:
    raise ValueError("El archivo CSV debe contener una columna llamada 'abstract_limpio'")

df = df.dropna(subset=['abstract_limpio']).drop_duplicates(subset=['abstract_limpio']).reset_index(drop=True)

print(f"[FASE 1] Abstracts cargados: {len(df)} registros válidos")

# ===============================================================
# FASE 2: Vectorización (TF-IDF)
# ===============================================================

vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
X = vectorizer.fit_transform(df['abstract_limpio']).toarray()

# ===============================================================
# ELIMINAR FILAS CON VECTORES CERO
# ===============================================================

filas_validas = np.any(X != 0, axis=1)
num_eliminados = np.sum(~filas_validas)
if num_eliminados > 0:
    print(f"[AVISO] Se eliminaron {num_eliminados} abstracts con vector TF-IDF vacío.")
X = X[filas_validas]
df = df[filas_validas].reset_index(drop=True)

print(f"[FASE 2] Matriz TF-IDF generada con forma: {X.shape}")

# ===============================================================
# FASE 3: Calcular similitudes y distancias
# ===============================================================

sim_matrix = cosine_similarity(X)
dist_matrix = 1 - sim_matrix

print(f"[FASE 3] Matriz de distancias generada con tamaño: {dist_matrix.shape}")

# ===============================================================
# FASE 4: Aplicar algoritmos jerárquicos y generar dendrogramas
# ===============================================================

metodos = ['single', 'complete', 'average']
resultados_cophenetic = []

OUT_DIR = os.path.join(os.path.dirname(__file__), 'resultados')
os.makedirs(OUT_DIR, exist_ok=True)

for metodo in metodos:
    print(f"[FASE 4] Procesando método: {metodo} ...")
    
    Z = linkage(pdist(X, 'cosine'), method=metodo)
    coph_corr, _ = cophenet(Z, pdist(X, 'cosine'))
    resultados_cophenetic.append((metodo, coph_corr))
    
    plt.figure(figsize=(12, 6))
    dendrogram(
        Z,
        leaf_rotation=90,
        leaf_font_size=6,
        color_threshold=0.7,
        above_threshold_color='gray',
        truncate_mode='level',
        p=10
    )
    plt.title(f'Dendrograma - Método {metodo.capitalize()}')
    plt.xlabel('Abstracts (muestra)')
    plt.ylabel('Distancia')
    plt.tight_layout()
    
    ruta_img = os.path.join(OUT_DIR, f'dendrograma_{metodo}.png')
    plt.savefig(ruta_img, dpi=300)
    plt.close()
    
    print(f"  → Dendrograma guardado en: {ruta_img}")
    print(f"  → Coeficiente cophenético: {coph_corr:.4f}")

# ===============================================================
# FASE 5: Evaluación y análisis de coherencia
# ===============================================================

ruta_cophenetic = os.path.join(OUT_DIR, 'comparacion_cophenetic.txt')
with open(ruta_cophenetic, 'w', encoding='utf-8') as f:
    f.write("Comparación de Coeficientes Cophenéticos:\n\n")
    for metodo, coph_corr in resultados_cophenetic:
        f.write(f"Método: {metodo:<10}  ->  Coeficiente: {coph_corr:.4f}\n")

print("\n[FASE 5] Evaluación completada.")
print(f"Archivo con resultados: {ruta_cophenetic}")

mejor_metodo, mejor_coph = max(resultados_cophenetic, key=lambda x: x[1])
print(f"\n🏁 Mejor método jerárquico: {mejor_metodo.upper()} (Coeficiente = {mejor_coph:.4f})")

# ===============================================================
# OPCIONAL: Exportar clusters finales (solo con el mejor método)
# ===============================================================

Z_best = linkage(pdist(X, 'cosine'), method=mejor_metodo)
clusters = fcluster(Z_best, t=10, criterion='maxclust')
df['cluster'] = clusters

ruta_clusters = os.path.join(OUT_DIR, 'clusters_agrupados.csv')
df.to_csv(ruta_clusters, index=False, encoding='utf-8')
print(f"Clusters exportados en: {ruta_clusters}")

print("\n✅ Requerimiento 4 completado correctamente.")
