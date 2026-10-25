import gurobipy as gp
from gurobipy import GRB	

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

    return m, b, d