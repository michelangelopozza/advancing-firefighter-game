import gurobipy as gp
from gurobipy import GRB	
from src.graphGeneration import getPoints, DelaunayGraph, GabrielGraph, getF, plotGraph, setDefenders, burnNodes
from src.utils import get_T_opt, graph_animation

PLOTS = False

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
points = getPoints(n_points)

# given the points generate its Gabriel Graph
G = GabrielGraph(points)

# get the F set
F = getF(G, n_fire)

if PLOTS:
    plotGraph(G, points)

# Mathematical model
m = gp.Model("IP1")

V = list(G.nodes())
T = T_max 

b = m.addVars(V, range(T+1), vtype=GRB.BINARY, name="b")
d = m.addVars(V, range(T+1), vtype=GRB.BINARY, name="d")


m.addConstrs(
    (b[i, t-1] <= b[i, t] for i in V for t in range(1, T+1)),
    name="perm_burning"
)

m.addConstrs(
    (d[i, t-1] <= d[i, t] for i in V for t in range(1, T+1)),
    name="perm_defense"
)

m.addConstrs(
    (b[i, t-1] <= b[j, t] + d[j, t] for i in V for j in G.neighbors(i) for t in range(1, T+1)),
    name="3.1d"
)

m.addConstrs(
    (b[i, t] + d[i, t] <= 1 for i in V for t in range(T+1)),
    name="3.1e"
)

m.addConstrs(
    (gp.quicksum(d[i, t] - d[i, t-1] for i in V) <= n_firefighters for t in range(1, T+1)),
    name="3.1f"
)


for i in V:
    if i in F:
        b[i, 0].lb = 1
        b[i, 0].ub = 1
    else:
        b[i, 0].lb = 0
        b[i, 0].ub = 0
    d[i, 0].lb = 0
    d[i, 0].ub = 0
    

m.setObjective(gp.quicksum(b[i, T] for i in V), GRB.MINIMIZE)

m.optimize()

if m.Status == GRB.OPTIMAL:
    print("Obiettivo:", m.ObjVal)
elif m.Status == GRB.INFEASIBLE:
    m.computeIIS()
    m.write("model.ilp")

T_opt = get_T_opt(b, V, T)
print("T_opt trovato:", T_opt)
print("Vertici bruciati:", sum(1 for i in V if b[i, T].X > 0.5))

graph_animation("figures", points, G, V, F, T_opt, b, d)

#burnedNodes = b[:, T]
#defendedNodes = d[:, T]
# burnNodes(G, F)
# plotGraph(G, points)
# for t in range(1, T_opt + 1):
#     D = []
#     F_prime = []
#     for i in V:
#         if round(d[i, t].X) == 1:
#             D.append(i)
#         if round(b[i, t].X) == 1:
#             F_prime.append(i)
#     setDefenders(G, D)
#     plotGraph(G, points)
#     burnNodes(G, F_prime)
#     plotGraph(G, points)