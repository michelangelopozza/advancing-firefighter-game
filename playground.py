import numpy as np
import networkx as nx
import src.utils as utils
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

t_min = np.ones(len(V))*len(V)
for i in V:
    for j in F:
        t_min[i] = min(distances[i][j], t_min[i])

for i in V:
    for t in range(round(t_min[i])):
        b[i, t].ub = 0
        

print(distances)