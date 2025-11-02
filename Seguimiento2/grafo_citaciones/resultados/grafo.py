# grafo_graphviz.py
import json
import networkx as nx
from networkx.drawing.nx_pydot import write_dot
import matplotlib.pyplot as plt

# Cargar JSON
json_file = "grafo_citaciones.json"
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Crear grafo dirigido
G = nx.DiGraph()

# Agregar nodos
for nodo_id in data.get("nodos", {}):
    G.add_node(nodo_id)

# Agregar aristas
for origen, destinos in data.get("aristas", {}).items():
    for destino, peso in destinos.items():
        if peso == {}:
            peso = 1
        G.add_edge(origen, destino, weight=peso)

# Guardar grafo en formato DOT (Graphviz)
write_dot(G, "grafo.dot")
print("Archivo DOT generado: grafo.dot")

# Opcional: dibujar usando Graphviz layout de matplotlib
pos = nx.nx_pydot.graphviz_layout(G, prog="dot")  # Puedes cambiar prog a "neato" o "fdp"
plt.figure(figsize=(12, 12))
nx.draw(G, pos, node_size=30, node_color="skyblue", arrowsize=10, edge_color="gray", alpha=0.5)
plt.title("Grafo de citaciones (Graphviz layout)")
plt.axis("off")
plt.show()
