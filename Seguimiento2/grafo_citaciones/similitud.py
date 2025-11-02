"""
Módulo de funciones de similitud para inferir relaciones entre artículos.
"""

import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Set, Dict, Any

def jaccard_similitud(a: str, b: str) -> float:
    """
    Calcula la similitud de Jaccard entre dos textos.
    Jaccard(A,B) = |A ∩ B| / |A ∪ B|
    """
    if not a or not b:
        return 0.0
        
    # Tokenización simple
    A = set(re.findall(r'\w+', a.lower()))
    B = set(re.findall(r'\w+', b.lower()))
    
    # Cálculo de Jaccard
    interseccion = len(A.intersection(B))
    union = len(A.union(B))
    
    return interseccion / union if union > 0 else 0.0

def coseno_similitud(textos: List[str]) -> np.ndarray:
    """
    Calcula la similitud del coseno entre múltiples textos usando TF-IDF.
    
    Args:
        textos: Lista de textos a comparar
        
    Returns:
        Matriz de similitud donde matriz[i][j] es la similitud entre textos[i] y textos[j]
    """
    if not textos or all(not texto for texto in textos):
        return np.zeros((len(textos), len(textos)))
    
    # Vectorización TF-IDF
    vectorizer = TfidfVectorizer(lowercase=True, analyzer='word')
    try:
        tfidf_matrix = vectorizer.fit_transform(textos)
        # Cálculo de similitud del coseno
        return cosine_similarity(tfidf_matrix)
    except:
        # En caso de error, devolver matriz de ceros
        return np.zeros((len(textos), len(textos)))

def similitud_autores(autores1: List[str], autores2: List[str]) -> float:
    """
    Calcula la similitud entre dos listas de autores.
    
    Args:
        autores1: Primera lista de autores
        autores2: Segunda lista de autores
        
    Returns:
        Valor de similitud entre 0 y 1
    """
    if not autores1 or not autores2:
        return 0.0
    
    # Normalizar nombres de autores
    set1 = {autor.lower().strip() for autor in autores1}
    set2 = {autor.lower().strip() for autor in autores2}
    
    # Calcular similitud como proporción de autores compartidos
    interseccion = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return interseccion / union if union > 0 else 0.0

def similitud_keywords(keywords1: str, keywords2: str) -> float:
    """
    Calcula la similitud entre dos conjuntos de palabras clave.
    
    Args:
        keywords1: Primer conjunto de palabras clave (como string)
        keywords2: Segundo conjunto de palabras clave (como string)
        
    Returns:
        Valor de similitud entre 0 y 1
    """
    # Extraer palabras clave individuales
    kw1 = {k.strip().lower() for k in keywords1.split(',') if k.strip()}
    kw2 = {k.strip().lower() for k in keywords2.split(',') if k.strip()}
    
    if not kw1 or not kw2:
        return 0.0
    
    # Calcular similitud de Jaccard
    interseccion = len(kw1.intersection(kw2))
    union = len(kw1.union(kw2))
    
    return interseccion / union if union > 0 else 0.0

def calcular_similitud_articulos(articulo1: Dict[str, Any], articulo2: Dict[str, Any]) -> Dict[str, float]:
    """
    Calcula diferentes métricas de similitud entre dos artículos.
    
    Args:
        articulo1: Diccionario con metadatos del primer artículo
        articulo2: Diccionario con metadatos del segundo artículo
        
    Returns:
        Diccionario con diferentes métricas de similitud
    """
    # Extraer datos relevantes
    titulo1 = articulo1.get('titulo', '')
    titulo2 = articulo2.get('titulo', '')
    
    autores1 = articulo1.get('autores', [])
    autores2 = articulo2.get('autores', [])
    
    keywords1 = articulo1.get('keywords', '')
    keywords2 = articulo2.get('keywords', '')
    
    abstract1 = articulo1.get('abstract', '')
    abstract2 = articulo2.get('abstract', '')
    
    # Calcular similitudes
    sim_titulo = jaccard_similitud(titulo1, titulo2)
    sim_autores = similitud_autores(autores1, autores2)
    sim_keywords = similitud_keywords(keywords1, keywords2)
    
    # Similitud de abstracts (si están disponibles)
    sim_abstract = 0.0
    if abstract1 and abstract2:
        matriz_sim = coseno_similitud([abstract1, abstract2])
        sim_abstract = matriz_sim[0, 1]
    
    return {
        'titulo': sim_titulo,
        'autores': sim_autores,
        'keywords': sim_keywords,
        'abstract': sim_abstract,
        # Similitud combinada (promedio ponderado)
        #'combinada': 0.5 * sim_titulo + 0.2 * sim_autores + 
        #            0.2 * sim_keywords + 0.1 * sim_abstract
        'combinada': sim_titulo
    }