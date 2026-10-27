import numpy as np
import networkx as nx
import src.utils as utils
import matplotlib.pyplot as plt
import src.models as models
from src.graph_generation import getPoints, DelaunayGraph, GabrielGraph

vals = np.column_stack((
        np.random.uniform(0, 10, 10),
        np.random.uniform(0, 10, 10)
    ))

keys = np.zeros(10).astype(int)
for i in range(10):
    keys[i] = i

e = zip(keys, vals)
d = dict(e)
print(d)

points = getPoints(10, 45)
G = GabrielGraph(points)
V = list(G.nodes())
distances = dict(nx.all_pairs_shortest_path_length(G))
F = utils.getF(G, 1)
T = 10

# fig, ax = plt.subplots(figsize=(8,8))
# utils.plot_graph(ax, G, points, "Gabriel Graph")
# plt.show()

m, b, d = models.IP1_bis(G, T, 1, F, 0.4, "defense")