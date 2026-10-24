import gurobipy as gp
from gurobipy import GRB	
from src.graphGeneration import getPoints, DelaunayGraph, GabrielGraph, getF, plotGraph, setDefenders, burnNodes

n_points = 10
T_max = n_points
n_firefighters = 1
n_fire = 1

points = getPoints(n_points)

G = GabrielGraph(points)

F = getF(G, n_fire)

plotGraph(G, points)

# Create a new model
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
    
def get_T_opt(b, V, T):
    for t in range(T + 1):
        stable = all(
            (b[i, t].X > 0.5) == (b[i, T].X > 0.5)
            for i in V
        )
        if stable:
            return t
    return T

T_opt = get_T_opt(b, V, T)
print("T_opt trovato:", T_opt)
print("Vertici bruciati:", sum(1 for i in V if b[i, T].X > 0.5))

#burnedNodes = b[:, T]
#defendedNodes = d[:, T]

print(b[0, 1])

#G = burnNodes(G, )