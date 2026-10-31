import gurobipy as gp
from gurobipy import GRB
import src.utils as utils	
import math

def CFG(G, T, n_firefighters, F):

    V = utils.get_V(G)

    m = gp.Model("CFG")

    # 3.1i
    b = m.addVars(V, range(T+1), vtype=GRB.BINARY, name="b")
    d = m.addVars(V, range(T+1), vtype=GRB.BINARY, name="d")

    m.addConstrs(
        (b[i, t-1] <= b[i, t] for i in V for t in range(1, T+1)),
        name="3.1b"
    )

    m.addConstrs(
        (d[i, t-1] <= d[i, t] for i in V for t in range(1, T+1)),
        name="3.1c"
    )

    m.addConstrs(
        (b[i, t-1] <= b[j, t] + d[j, t] for i in V for j in utils.get_N(i, G) for t in range(1, T+1)),
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

    # 3.1g, 3.1h
    for i in V:
        # fix nodes in F to burn in t=0 (3.1g)
        if i in F:
            b[i, 0].lb = 1
            b[i, 0].ub = 1
        # fix defense to 0 for t=0 (3.1h)
        d[i, 0].lb = 0
        d[i, 0].ub = 0
        
    # 3.1a
    m.setObjective(gp.quicksum(b[i, T] for i in V), GRB.MINIMIZE)

    m.optimize()

    return m, b, d


def CFG_improved(G, T, n_firefighters, F, alpha, relax="defense"):

    assert 0 <= alpha <= 1, "alpha must be in [0,1]"
    # add none to not relax both
    assert relax == "defense" or relax == "fires", "relax must be equal to defense or fires"

    V = utils.get_V(G)

    m = gp.Model("CFG_improved")

    vtype_b = GRB.BINARY
    vtype_d = GRB.BINARY

    # relax none or one of the variables
    if relax == "defense":
        vtype_d = GRB.CONTINUOUS
    elif relax == "fires":
        vtype_b = GRB.CONTINUOUS

    # 3.1i
    b = m.addVars(V, range(T+1), vtype=vtype_b, lb=0, ub=1, name="b")
    d = m.addVars(V, range(T+1), vtype=vtype_d, lb=0, ub=1, name="d")


    m.addConstrs(
        (b[i, t-1] <= b[i, t] for i in V for t in range(1, T+1)),
        name="3.1b"
    )

    m.addConstrs(
        (d[i, t-1] <= d[i, t] for i in V for t in range(1, T+1)),
        name="3.1c"
    )

    m.addConstrs(
        (b[i, t-1] <= b[j, t] + d[j, t] for i in V for j in utils.get_N(i, G) for t in range(1, T+1)),
        name="3.1d"
    )

    m.addConstrs(
        (b[i, t] + d[i, t] <= 1 for i in V for t in range(1, math.ceil(alpha*T)+1)),
        name="3.1e_alpha"
    )

    m.addConstrs(
        (gp.quicksum(d[i, t] for i in V) <= n_firefighters*t for t in range(1, T+1)),
        name="3.2"
    )

    for i in F:
        # 3.1g
        b[i, 0].lb = 1
        b[i, 0].ub = 1
        
    # preprocessing
    b = utils.preprocessing_b(G, V, F, T, b)

    m.setObjective(gp.quicksum(b[i, T] for i in V), GRB.MINIMIZE)

    m.optimize()

    return m, b, d

def CF1(G, T, n_firefighters, F):

    V = list(G.nodes())

    m = gp.Model("CF1")

    b_hat = m.addVars(V, range(T+1), vtype=GRB.BINARY, name="b_hat")
    d_hat = m.addVars(V, range(T+1), vtype=GRB.BINARY, name="d_hat")


    m.addConstrs(
        (gp.quicksum(d_hat[i, t] for i in V) <= n_firefighters for t in range(1, T+1)),
        name="3.5b"
    )

    m.addConstrs(
        (gp.quicksum(b_hat[i, r] for r in range(0, t)) <= gp.quicksum(b_hat[j, r] 
        for r in range(0, t+1)) + gp.quicksum(d_hat[j, r] for r in range(1, t+1)) 
        for i in V for j in utils.get_N(i, G) for t in range(1, T+1)),
        name="3.5c"
    )

    for i in V:
        if i in F:
            b_hat[i, 0].lb = 1
            b_hat[i, 0].ub = 1
        else:
            b_hat[i, 0].lb = 0
            b_hat[i, 0].ub = 0
        d_hat[i, 0].lb = 0
        d_hat[i, 0].ub = 0

    m.setObjective(gp.quicksum(gp.quicksum(b_hat[i, t] for t in range(0, T+1)) for i in V), GRB.MINIMIZE)

    m.optimize()

    return m, b_hat, d_hat

def CF1_improved(G, T, n_firefighters, F, alpha=0.3, relax="none"):

    assert 0 <= alpha <= 1, "alpha must be in [0,1]"
    assert relax == "defense" or relax == "fires" or relax == "none", "relax must be equal to defense, fires or none"

    V = list(G.nodes())

    m = gp.Model("CF1_improved")

    vtype_b_hat = GRB.BINARY
    vtype_d_hat = GRB.BINARY

    if relax == "defense":
        vtype_d_hat = GRB.CONTINUOUS
    elif relax == "fires":
        vtype_b_hat = GRB.CONTINUOUS

    b_hat = m.addVars(V, range(T+1), vtype=vtype_b_hat, name="b_hat")
    d_hat = m.addVars(V, range(T+1), vtype=vtype_d_hat, name="d_hat")

    m.addConstrs(
        (gp.quicksum(b_hat[i, r] for r in range(0, t)) <= gp.quicksum(b_hat[j, r] 
        for r in range(0, t+1)) + gp.quicksum(d_hat[j, r] for r in range(1, t+1)) 
        for i in V for j in utils.get_N(i, G) for t in range(1, T+1)),
        name="3.5c"
    )

    m.addConstrs(
        (gp.quicksum(gp.quicksum(d_hat[i, r] for r in range(1, t+1)) for i in V) <= t*n_firefighters for t in range(1, T+1)),
        name="3.6"
    )

    m.addConstrs(
        (gp.quicksum(b_hat[i, r] for r in range(0, t+1)) <= 1 for i in V for t in range(0, math.ceil(alpha*(T+1)))),
        name="alpha3.7_1"
    )

    m.addConstrs(
        (gp.quicksum(d_hat[i, r] for r in range(1, t+1)) <= 1 for i in V for t in range(1, math.ceil(alpha*(T+1)))),
        name="alpha3.7_2"
    )

    m.addConstrs(
        (gp.quicksum(b_hat[i, r] for r in range(0, t+1)) + gp.quicksum(d_hat[i, r] for r in range(1, t+1)) <= 1 for i in V for t in range(0, math.ceil(alpha*(T+1)))),
        name="alpha3.8"
    )

    for i in V:
        if i in F:
            b_hat[i, 0].lb = 1
            b_hat[i, 0].ub = 1
        else:
            b_hat[i, 0].lb = 0
            b_hat[i, 0].ub = 0
        d_hat[i, 0].lb = 0
        d_hat[i, 0].ub = 0

    b_hat = utils.preprocessing_b(G, V, F, T, b_hat)

    m.setObjective(gp.quicksum(gp.quicksum(b_hat[i, t] for t in range(0, T+1)) for i in V), GRB.MINIMIZE)

    m.optimize()

    return m, b_hat, d_hat

optimization_problems = {
    "CFG": CFG,
    "CFG_improved": CFG_improved
}

relax_availables = ["defense", "fires", "none"]