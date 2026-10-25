import gurobipy as gp
from gurobipy import GRB	

import matplotlib.pyplot as plt
from src.graph_generation import getPoints, DelaunayGraph, GabrielGraph
from src.utils import get_T_opt, graph_animation, plot_graph, getF
from src.models import IP1

PLOTS = False
SEED = 57

"""
    Implementation of the paper: .....
    In the following script are presents different formulation of the same Firefighter Game problem:
        - Classical Firefigher formulantion
        
"""

""" Classical Firefighter formulation """

# Number of generated points on the graph
n_points = 50
# Max T in the classical formulation corresponds to the number of points
T_max = n_points


n_firefighters = 1
n_fire = 1

# generate n_points random points in the plane [0,10]^2 as described in the data generation part
points = getPoints(n_points, SEED)

# given the points generate its Gabriel Graph
G = GabrielGraph(points)

# get the F set
F = getF(G, n_fire)

if PLOTS:
    fig, ax = plt.subplots(figsize=(8,8))
    plot_graph(ax, G, points, "Gabriel Graph")
    plt.show()


V = list(G.nodes())
T = T_max 

m, b, d = IP1(G, T, n_firefighters, F)

if m.Status == GRB.OPTIMAL:
    print("Obiettivo:", m.ObjVal)
elif m.Status == GRB.INFEASIBLE:
    m.computeIIS()
    m.write("model.ilp")

T_opt = get_T_opt(b, V, T)
print("T_opt trovato:", T_opt)
print("Vertici bruciati:", sum(1 for i in V if b[i, T].X > 0.5))

graph_animation("figures", points, G, V, F, T_opt, b, d)