import gurobipy as gp
from gurobipy import GRB
import src.utils as utils	
import math

def IP1(G, T, n_firefighters, F):

    V = list(G.nodes())

    m = gp.Model("IP1")

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
        (b[i, t] + d[i, t] <= 1 for i in V for t in range(1, T+1)),
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

    return m, b, d


def IP1_bis(G, T, n_firefighters, F, alpha, relax="defense"):

    assert 0 <= alpha <= 1, "alpha must be in [0,1]"
    assert relax == "defense" or relax == "fires", "relax must be equal to defense or fires"

    V = list(G.nodes())

    m = gp.Model("IP1")

    vtype_b = GRB.BINARY
    vtype_d = GRB.BINARY

    if relax == "defense":
        vtype_d = GRB.CONTINUOUS
    elif relax == "fires":
        vtype_b = GRB.CONTINUOUS

    b = m.addVars(V, range(T+1), vtype=vtype_b, name="b")
    d = m.addVars(V, range(T+1), vtype=vtype_d, name="d")


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
        (b[i, t] + d[i, t] <= 1 for i in V for t in range(math.ceil(alpha*(T+1)))),
        name="3.1e_alpha"
    )

    m.addConstrs(
        (gp.quicksum(d[i, t] for i in V) <= n_firefighters*t for t in range(1, T+1)),
        name="3.2"
    )

    m.addConstrs(
        (b[i, t] <= gp.quicksum(b[j, t-1] for j in utils.get_N(i, G)) for i in V if i not in F for t in range(1, T+1)),
        name="3.3"
    )

    for i in V:
        if i in F:
            b[i, 0].lb = 1
            b[i, 0].ub = 1
        else:
            b[i, 0].lb = 0
            b[i, 0].ub = 0
        
    b = utils.preprocessing_b(G, V, F, T, b)

    m.setObjective(gp.quicksum(b[i, T] for i in V), GRB.MINIMIZE)

    m.optimize()

    return m, b, d