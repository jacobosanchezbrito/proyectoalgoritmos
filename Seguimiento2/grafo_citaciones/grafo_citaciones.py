import os
import heapq
import bibtexparser
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Set, Any, Optional
import numpy as np

# Importar el módulo de similitud
from similitud import calcular_similitud_articulos

class GrafoCitaciones:
    """
    Clase que representa un grafo dirigido de citaciones entre artículos científicos.
    """
    
    def __init__(self):
        """
        Inicializa un grafo vacío.
        """
        self.nodos = {}  # Diccionario de nodos (artículos)
        self.aristas = {}  # Diccionario de aristas (citaciones)
    
    def agregar_nodo(self, id_articulo, datos_articulo):
        """
        Agrega un nodo (artículo) al grafo.
        
        Args:
            id_articulo: Identificador único del artículo
            datos_articulo: Diccionario con los datos del artículo
        """
        self.nodos[id_articulo] = datos_articulo
        if id_articulo not in self.aristas:
            self.aristas[id_articulo] = {}
    
    def agregar_arista(self, id_origen, id_destino, peso=1.0):
        """
        Agrega una arista dirigida (citación) entre dos artículos.
        
        Args:
            id_origen: ID del artículo que cita
            id_destino: ID del artículo citado
            peso: Peso de la arista (por defecto 1.0)
        """
        if id_origen not in self.nodos or id_destino not in self.nodos:
            raise ValueError("Los nodos deben existir en el grafo")
        
        if id_origen not in self.aristas:
            self.aristas[id_origen] = {}
        
        self.aristas[id_origen][id_destino] = peso
    
    def cargar_articulos_desde_bibtex(self, ruta_archivo):
        """
        Carga artículos desde un archivo BibTeX y los agrega como nodos al grafo.
        
        Args:
            ruta_archivo: Ruta al archivo BibTeX
        """
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"El archivo {ruta_archivo} no existe")
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as bibtex_file:
                parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                bib_database = parser.parse_file(bibtex_file)
                
                for entrada in bib_database.entries:
                    # Usar el ID de la entrada como identificador único
                    id_articulo = entrada.get('ID', '')
                    if not id_articulo:
                        continue
                    
                    # Extraer datos relevantes
                    datos_articulo = {
                        'titulo': entrada.get('title', ''),
                        'autores': self._extraer_autores(entrada.get('author', '')),
                        'año': entrada.get('year', ''),
                        'journal': entrada.get('journal', ''),
                        'abstract': entrada.get('abstract', ''),
                        'keywords': entrada.get('keywords', ''),
                        'doi': entrada.get('doi', ''),
                        'entrada_completa': entrada
                    }
                    
                    # Agregar el artículo como nodo
                    self.agregar_nodo(id_articulo, datos_articulo)
                
                print(f"Se cargaron {len(bib_database.entries)} artículos desde {ruta_archivo}")
                return len(bib_database.entries)
        except Exception as e:
            print(f"Error al cargar el archivo BibTeX: {e}")
            return 0
    
    def _extraer_autores(self, autor_str: str) -> List[str]:
        """
        Extrae la lista de autores desde una cadena de texto.
        
        Args:
            autor_str: Cadena con los autores separados por 'and'
            
        Returns:
            Lista de nombres de autores
        """
        if not autor_str:
            return []
        
        # Dividir por 'and' y limpiar espacios
        return [autor.strip() for autor in autor_str.split(' and ') if autor.strip()]
    
    def inferir_relaciones_por_similitud(self, umbral=0.7, max_comparaciones=None, usar_filtro_previo=True):
        """
        Infiere relaciones de citación entre artículos basándose en su similitud.
        
        Args:
            umbral: Umbral mínimo de similitud para establecer una relación
            max_comparaciones: Número máximo de comparaciones a realizar (None para todas)
            usar_filtro_previo: Si es True, aplica un filtro previo para reducir comparaciones
            
        Returns:
            Número de relaciones inferidas
        """
        if len(self.nodos) < 2:
            return 0
        
        relaciones_inferidas = 0
        ids_articulos = list(self.nodos.keys())
        
        # Crear pares de comparación
        pares_comparacion = []
        
        if usar_filtro_previo:
            # Agrupar artículos por año para comparar solo los cercanos en tiempo
            articulos_por_año = defaultdict(list)
            for id_articulo in ids_articulos:
                año = int(self.nodos[id_articulo].get('año', '0') or '0')
                articulos_por_año[año].append(id_articulo)
            
            # Crear pares de comparación solo entre artículos con años cercanos (±3 años)
            for año, articulos_año in articulos_por_año.items():
                # Comparar artículos del mismo año entre sí
                for i in range(len(articulos_año)):
                    for j in range(i + 1, len(articulos_año)):
                        pares_comparacion.append((articulos_año[i], articulos_año[j]))
                
                # Comparar con artículos de años cercanos
                for año_cercano in range(año - 3, año + 4):
                    if año_cercano != año and año_cercano in articulos_por_año:
                        for id1 in articulos_año:
                            for id2 in articulos_por_año[año_cercano]:
                                pares_comparacion.append((id1, id2))
        else:
            # Comparar todos los pares posibles
            for i in range(len(ids_articulos)):
                for j in range(i + 1, len(ids_articulos)):
                    pares_comparacion.append((ids_articulos[i], ids_articulos[j]))
        
        # Limitar el número de comparaciones si se especifica
        if max_comparaciones and len(pares_comparacion) > max_comparaciones:
            import random
            random.shuffle(pares_comparacion)
            pares_comparacion = pares_comparacion[:max_comparaciones]
        
        total_comparaciones = len(pares_comparacion)
        comparaciones_realizadas = 0
        ultimo_porcentaje = 0
        
        print(f"Total de comparaciones a realizar: {total_comparaciones}")
        
        # Comparar pares de artículos
        for id1, id2 in pares_comparacion:
            # Actualizar y mostrar progreso
            comparaciones_realizadas += 1
            porcentaje_actual = int((comparaciones_realizadas / total_comparaciones) * 100)
            if porcentaje_actual > ultimo_porcentaje and porcentaje_actual % 5 == 0:
                print(f"   Progreso: {porcentaje_actual}% ({comparaciones_realizadas}/{total_comparaciones})")
                ultimo_porcentaje = porcentaje_actual
            
            # Calcular similitud entre los artículos
            similitud = calcular_similitud_articulos(self.nodos[id1], self.nodos[id2])
            
            # Si la similitud combinada supera el umbral, inferir relación
            if similitud['combinada'] >= umbral:
                # Determinar dirección basada en el año de publicación
                año1 = int(self.nodos[id1].get('año', '0') or '0')
                año2 = int(self.nodos[id2].get('año', '0') or '0')
                
                # El artículo más reciente cita al más antiguo
                if año1 > año2:
                    self.agregar_arista(id1, id2, peso=similitud['combinada'])
                    relaciones_inferidas += 1
                elif año2 > año1:
                    self.agregar_arista(id2, id1, peso=similitud['combinada'])
                    relaciones_inferidas += 1
                else:
                    # Si son del mismo año, crear relación bidireccional con menor peso
                    self.agregar_arista(id1, id2, peso=similitud['combinada'] * 0.8)
                    self.agregar_arista(id2, id1, peso=similitud['combinada'] * 0.8)
                    relaciones_inferidas += 2
        
        print(f"Se infirieron {relaciones_inferidas} relaciones de citación")
        return relaciones_inferidas
    
    def calcular_camino_minimo_dijkstra(self, id_origen, id_destino):
        """
        Calcula el camino mínimo entre dos artículos usando el algoritmo de Dijkstra.
        
        Args:
            id_origen: ID del artículo de origen
            id_destino: ID del artículo de destino
            
        Returns:
            Tupla con (distancia, camino) donde camino es una lista de IDs de artículos
        """
        if id_origen not in self.nodos or id_destino not in self.nodos:
            raise ValueError("Los nodos de origen y destino deben existir en el grafo")
        
        # Inicialización
        distancias = {nodo: float('infinity') for nodo in self.nodos}
        distancias[id_origen] = 0
        predecesores = {nodo: None for nodo in self.nodos}
        visitados = set()
        
        # Cola de prioridad para Dijkstra
        cola_prioridad = [(0, id_origen)]
        
        while cola_prioridad:
            # Obtener el nodo con menor distancia
            dist_actual, nodo_actual = heapq.heappop(cola_prioridad)
            
            # Si ya llegamos al destino, terminar
            if nodo_actual == id_destino:
                break
            
            # Si ya visitamos este nodo, continuar
            if nodo_actual in visitados:
                continue
            
            # Marcar como visitado
            visitados.add(nodo_actual)
            
            # Explorar vecinos
            for vecino, peso in self.aristas.get(nodo_actual, {}).items():
                # Calcular nueva distancia
                nueva_distancia = dist_actual + (1 / peso)  # Invertir el peso para que mayor similitud = menor distancia
                
                # Si encontramos un camino más corto
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    predecesores[vecino] = nodo_actual
                    heapq.heappush(cola_prioridad, (nueva_distancia, vecino))
        
        # Reconstruir el camino
        if distancias[id_destino] == float('infinity'):
            return float('infinity'), []  # No hay camino
        
        camino = []
        nodo_actual = id_destino
        while nodo_actual is not None:
            camino.append(nodo_actual)
            nodo_actual = predecesores[nodo_actual]
        
        # Invertir el camino para que vaya desde el origen al destino
        camino.reverse()
        
        return distancias[id_destino], camino
    
    def identificar_componentes_fuertemente_conexas(self):
        """
        Identifica componentes fuertemente conexas en el grafo usando el algoritmo de Kosaraju.
        
        Returns:
            Lista de componentes, donde cada componente es una lista de IDs de artículos
        """
        # Paso 1: Realizar DFS y almacenar el orden de finalización
        visitados = set()
        orden_finalizacion = []
        
        def dfs_primera_pasada(nodo):
            visitados.add(nodo)
            for vecino in self.aristas.get(nodo, {}):
                if vecino not in visitados:
                    dfs_primera_pasada(vecino)
            orden_finalizacion.append(nodo)
        
        # Primera pasada DFS
        for nodo in self.nodos:
            if nodo not in visitados:
                dfs_primera_pasada(nodo)
        
        # Paso 2: Transponer el grafo (invertir aristas)
        grafo_transpuesto = defaultdict(dict)
        for origen, destinos in self.aristas.items():
            for destino, peso in destinos.items():
                grafo_transpuesto[destino][origen] = peso
        
        # Paso 3: Realizar DFS en el grafo transpuesto siguiendo el orden de finalización
        visitados.clear()
        componentes = []
        
        def dfs_segunda_pasada(nodo, componente_actual):
            visitados.add(nodo)
            componente_actual.append(nodo)
            for vecino in grafo_transpuesto.get(nodo, {}):
                if vecino not in visitados:
                    dfs_segunda_pasada(vecino, componente_actual)
        
        # Segunda pasada DFS
        for nodo in reversed(orden_finalizacion):
            if nodo not in visitados:
                componente_actual = []
                dfs_segunda_pasada(nodo, componente_actual)
                if componente_actual:  # Solo agregar componentes no vacías
                    componentes.append(componente_actual)
        
        return componentes
    
    def guardar_grafo(self, ruta_archivo):
        """
        Guarda la estructura del grafo en un archivo para su posterior análisis.
        
        Args:
            ruta_archivo: Ruta donde guardar el archivo
        """
        try:
            import json
            
            # Crear diccionario con la estructura del grafo
            grafo_dict = {
                'nodos': {k: {
                    'titulo': v.get('titulo', ''),
                    'autores': v.get('autores', []),
                    'año': v.get('año', ''),
                    'journal': v.get('journal', ''),
                    'doi': v.get('doi', '')
                } for k, v in self.nodos.items()},
                'aristas': self.aristas
            }
            
            # Guardar como JSON
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(grafo_dict, f, ensure_ascii=False, indent=2)
                
            print(f"Grafo guardado en {ruta_archivo}")
            return True
        except Exception as e:
            print(f"Error al guardar el grafo: {e}")
            return False
    
    def estadisticas_grafo(self):
        """
        Calcula estadísticas básicas del grafo.
        
        Returns:
            Diccionario con estadísticas del grafo
        """
        num_nodos = len(self.nodos)
        num_aristas = sum(len(destinos) for destinos in self.aristas.values())
        
        # Calcular grado de entrada y salida para cada nodo
        grado_entrada = defaultdict(int)
        for origen, destinos in self.aristas.items():
            for destino in destinos:
                grado_entrada[destino] += 1
        
        grado_salida = {nodo: len(destinos) for nodo, destinos in self.aristas.items()}
        
        # Nodos con mayor grado de entrada (más citados)
        nodos_mas_citados = sorted(
            [(nodo, grado) for nodo, grado in grado_entrada.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Nodos con mayor grado de salida (más citan)
        nodos_mas_citan = sorted(
            [(nodo, grado_salida.get(nodo, 0)) for nodo in self.nodos],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Componentes fuertemente conexas
        componentes = self.identificar_componentes_fuertemente_conexas()
        
        return {
            'num_nodos': num_nodos,
            'num_aristas': num_aristas,
            'densidad': num_aristas / (num_nodos * (num_nodos - 1)) if num_nodos > 1 else 0,
            'nodos_mas_citados': nodos_mas_citados,
            'nodos_mas_citan': nodos_mas_citan,
            'num_componentes': len(componentes),
            'tamaño_componente_mayor': max([len(c) for c in componentes]) if componentes else 0
        }