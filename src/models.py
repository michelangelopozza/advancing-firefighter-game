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


def CFG_improved(G, T, n_firefighters, F, alpha=0.7, relax="none"):

    assert 0 <= alpha <= 1, "alpha must be in [0,1]"
    assert relax == "defense" or relax == "fires" or relax == "none", "relax must be equal to defense, fires or none"

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

    V = utils.get_V(G)

    m = gp.Model("CF1")

    b_hat = m.addVars(V, range(T+1), vtype=GRB.BINARY, name="b_hat")
    d_hat = m.addVars(V, range(T+1), vtype=GRB.BINARY, name="d_hat")

    # max n_firefighters set each time step
    m.addConstrs(
        (gp.quicksum(d_hat[i, t] for i in V) <= n_firefighters for t in range(1, T+1)),
        name="3.5b"
    )

    # vertex j adjacent to i burning at t-1 must be defended or burn at time t
    m.addConstrs(
        (gp.quicksum(b_hat[i, r] for r in range(0, t)) <= gp.quicksum(b_hat[j, r] 
        for r in range(0, t+1)) + gp.quicksum(d_hat[j, r] for r in range(1, t+1)) 
        for i in V for j in utils.get_N(i, G) for t in range(1, T+1)),
        name="3.5c"
    )

    # 3.5d -> set vertices in F to burn at t=0
    for i in F:
        b_hat[i, 0].lb = 1
        b_hat[i, 0].ub = 1

    # 3.5a -> minimize the sum of vertices that starts burning at t for all t and for all i in V
    m.setObjective(gp.quicksum(gp.quicksum(b_hat[i, t] for t in range(0, T+1)) for i in V), GRB.MINIMIZE)

    m.optimize()

    return m, b_hat, d_hat

def CF1_improved(G, T, n_firefighters, F, alpha=0.7, relax="none"):

    assert 0 <= alpha <= 1, "alpha must be in [0,1]"
    assert relax == "defense" or relax == "fires" or relax == "none", "relax must be equal to defense, fires or none"

    V = utils.get_V(G)

    m = gp.Model("CF1_improved")

    vtype_b_hat = GRB.BINARY
    vtype_d_hat = GRB.BINARY

    # relax none or one of the variables
    if relax == "defense":
        vtype_d_hat = GRB.CONTINUOUS
    elif relax == "fires":
        vtype_b_hat = GRB.CONTINUOUS

    b_hat = m.addVars(V, range(T+1), vtype=vtype_b_hat, lb=0, ub=1, name="b_hat")
    d_hat = m.addVars(V, range(T+1), vtype=vtype_d_hat, lb=0, ub=1, name="d_hat")

    # vertex j adjacent to i burning at t-1 must be defended or burn at time t
    m.addConstrs(
        (gp.quicksum(b_hat[i, r] for r in range(0, t)) <= gp.quicksum(b_hat[j, r] 
        for r in range(0, t+1)) + gp.quicksum(d_hat[j, r] for r in range(1, t+1)) 
        for i in V for j in utils.get_N(i, G) for t in range(1, T+1)),
        name="3.5c"
    )

    # aggregate constraint for the maximum number of defenders per time step
    m.addConstrs(
        (gp.quicksum(gp.quicksum(d_hat[i, r] for r in range(1, t+1)) for i in V) <= t*n_firefighters for t in range(1, T+1)),
        name="3.6"
    )

    # # a vertex can burn for the first time only at one t (alpha formulation to reduce the total number of inequalities)
    # m.addConstrs(
    #     (gp.quicksum(b_hat[i, r] for r in range(0, t+1)) <= 1 for i in V for t in range(0, math.ceil(alpha*(T))+1)),
    #     name="alpha3.7_1"
    # )
    
    # # a vertex can be defended for the first time only at one t (alpha formulation to reduce the total number of inequalities)
    # m.addConstrs(
    #     (gp.quicksum(d_hat[i, r] for r in range(1, t+1)) <= 1 for i in V for t in range(1, math.ceil(alpha*(T))+1)),
    #     name="alpha3.7_2"
    # )

    # a vertex can be defended or burn, not both for each time t (alpha formulation to reduce the total number of inequalities)
    m.addConstrs(
        (gp.quicksum(b_hat[i, r] for r in range(0, t+1)) + gp.quicksum(d_hat[i, r] for r in range(1, t+1)) <= 1 for i in V for t in range(0, math.ceil(alpha*(T))+1)),
        name="alpha3.8"
    )

    # 3.5d -> set vertices in F to burn at t=0
    for i in F:
        b_hat[i, 0].lb = 1
        b_hat[i, 0].ub = 1
    
    # preprocessing -> set b[i, t]=0 for t<dist(i,j) where j in F
    b_hat = utils.preprocessing_b(G, V, F, T, b_hat)

    # 3.5a -> minimize the sum of vertices that starts burning at t for all t and for all i in V
    m.setObjective(gp.quicksum(gp.quicksum(b_hat[i, t] for t in range(0, T+1)) for i in V), GRB.MINIMIZE)

    m.optimize()

    return m, b_hat, d_hat

def CF2(G, T, n_firefighters, F):

    V = utils.get_V(G)

    m = gp.Model("CF2")

    # x_ij^t is 1 if the fire spreads from vertex i to j at time t
    x = m.addVars(((i, j, t) for i in V for j in utils.get_N(i, G) for t in range(1, T+1)), 
    vtype=GRB.BINARY, name="x")
    d = m.addVars(V, range(T+1), vtype=GRB.BINARY, name="d")

    m.addConstrs(
        (d[i, t-1] <= d[i, t] for i in V for t in range(1, T+1)),
        name="3.1c"
    )

    m.addConstrs(
        (gp.quicksum(d[i, t] - d[i, t-1] for i in V) <= n_firefighters for t in range(1, T+1)),
        name="3.1f"
    )

    # 3.1h
    for i in V:
        # fix defense to 0 for t=0 (3.1h)
        d[i, 0].lb = 0
        d[i, 0].ub = 0

    # case for t=1: vertices adjacent to F must be defended at t=1 or the fire will burn them
    m.addConstrs(
        (1 <= d[i, 1] + gp.quicksum(x[k, i, 1] for k in (set(utils.get_N(i, G)) & set(F))) for i in (set(utils.get_N_set(F, G))-set(F))),
        name="3.11b"
    )

    # case for t>=2: 
        # -take all the nodes not in F, compute their neighborhood N(i)
        # -if the fire reaches i at time t-1
            # -then at t the fires spread to j (neighbors of i)
            # -or the node is already defended (d_j^t)
            # -or it has been already burned by others nodes (neighbors of the neighbors of i)
    m.addConstrs(
        (gp.quicksum(x[k, i, t-1] for k in set(utils.get_N(i, G)) - {j}) <= x[i, j, t] + d[j, t] + 
        gp.quicksum(gp.quicksum(x[k, j, r] for k in (set(utils.get_N(j, G))-set({i}))) 
        for r in range(max(1, t-2),t+1)) for i in (set(V)-set(F)) 
        for j in utils.get_N(i, G) for t in range(2, T+1)),
        name="3.11c"
    )

    # 3.11d -> no spontaneous ignition constraint
    for i in (set(V)-set(F)):
        for j in utils.get_N(i, G):
            x[i, j, 1].ub = 0
            x[i, j, 1].lb = 0

    # 3.11e -> no spontaneous ignition constraint
    m.addConstrs(
        (x[i, j, t] <= gp.quicksum(x[k, i, t-1] for k in (set(utils.get_N(i, G))-set({j}))) 
        for i in (set(V)-set(F)) for j in utils.get_N(i, G) for t in range(2, T+1)),
        name="3.11e"
    )

    # 3.11a -> minimize the number of vertices the fire spreads to
    m.setObjective(gp.quicksum(gp.quicksum(gp.quicksum(x[i, j, t] for t in range(1, T+1)) for j in utils.get_N(i, G)) for i in V), GRB.MINIMIZE)

    m.optimize()

    return m, x, d

def CF2_improved(G, T, n_firefighters, F, alpha=0.7, beta=0.5):

    assert 0 <= alpha <= 1, "alpha must be in [0,1]"
    assert 0 <= beta <= 1, "beta must be in [0,1]"

    V = utils.get_V(G)

    m = gp.Model("CF2_improved")

    # x_ij^t is 1 if the fire spreads from vertex i to j at time t
    x = m.addVars(((i, j, t) for i in V for j in utils.get_N(i, G) for t in range(1, T+1)), 
    vtype=GRB.BINARY, name="x")
    d = m.addVars(V, range(T+1), vtype=GRB.BINARY, name="d")

    m.addConstrs(
        (d[i, t-1] <= d[i, t] for i in V for t in range(1, T+1)),
        name="3.1c"
    )

    # substitute 3.1f
    m.addConstrs(
        (gp.quicksum(d[i, t] for i in V) <= n_firefighters*t for t in range(1, T+1)),
        name="3.2"
    )

    # 3.1h
    for i in V:
        # fix defense to 0 for t=0 (3.1h)
        d[i, 0].lb = 0
        d[i, 0].ub = 0

    # case for t=1: vertices adjacent to F must be defended at t=1 or the fire will burn them
    m.addConstrs(
        (1 <= d[i, 1] + gp.quicksum(x[k, i, 1] for k in (set(utils.get_N(i, G)) & set(F))) for i in (set(utils.get_N_set(F, G))-set(F))),
        name="3.11b"
    )

    # case for t>=2: 
        # -take all the nodes not in F, compute their neighborhood N(i)
        # -if the fire reaches i at time t-1
            # -then at t the fires spread to j (neighbors of i)
            # -or the node is already defended (d_j^t)
            # -or it has been already burned by others nodes (neighbors of the neighbors of i)
    m.addConstrs(
        (gp.quicksum(x[k, i, t-1] for k in set(utils.get_N(i, G)) - {j}) <= x[i, j, t] + d[j, t] + 
        gp.quicksum(gp.quicksum(x[k, j, r] for k in (set(utils.get_N(j, G))-set({i}))) 
        for r in range(max(1, t-2),t+1)) for i in (set(V)-set(F)) 
        for j in utils.get_N(i, G) for t in range(2, T+1)),
        name="3.11c"
    )

    # 3.11d -> no spontaneous ignition constraint
    for i in (set(V)-set(F)):
        for j in utils.get_N(i, G):
            x[i, j, 1].ub = 0
            x[i, j, 1].lb = 0

    # 3.11e -> no spontaneous ignition constraint
    m.addConstrs(
        (x[i, j, t] <= gp.quicksum(x[k, i, t-1] for k in (set(utils.get_N(i, G))-set({j}))) 
        for i in (set(V)-set(F)) for j in utils.get_N(i, G) for t in range(2, T+1)),
        name="3.11e"
    )


    # add 3.12alpha
    m.addConstrs(
        (d[i, t] + gp.quicksum(gp.quicksum(x[k, i, r] for k in utils.get_N(i, G)) 
        for r in range(1, t+1)) <= 1 for i in V for t in range(1, math.ceil(alpha*T)+1)),
        name="3.12_alpha"
    )

    # add 3.14alpha
    m.addConstrs(
        (beta*d[i, t] + (1-beta)*d[j, t] + gp.quicksum(x[i, j, r] for r in range(1, t+1))
        + gp.quicksum(x[j, i, r] for r in range(1, t+1)) <= 1 for (i,j) in G.edges() 
        for t in range(1, math.ceil(alpha*T)+1)),
        name="3.14_alpha"
    )

    # preprocessing
    x = utils.preprocessing_x(G, V, F, T, x)



    # 3.11a -> minimize the number of vertices the fire spreads to
    m.setObjective(gp.quicksum(gp.quicksum(gp.quicksum(x[i, j, t] for t in range(1, T+1)) for j in utils.get_N(i, G)) for i in V), GRB.MINIMIZE)

    m.optimize()

    return m, x, d

def CVFG(G, T, F, c, v, B):
    V = utils.get_V(G)

    m = gp.Model("CVFG")

    # 4.1i
    b = m.addVars(V, range(0, T+1), vtype=GRB.BINARY, name="b")
    # 4.1j
    d = m.addVars(V, range(1, T+1), vtype=GRB.BINARY, name="d")
    # total amount of defense budget spent on vertex i up to and including time t
    # 4.1k
    s = m.addVars(V, range(0, T+1), vtype=GRB.CONTINUOUS, lb=0,
    ub={(i, t): c[i] for i in V for t in range(0, T+1)}, 
    name="s")

    m.addConstrs(
        (b[i, t-1] <= b[i, t] for i in V for t in range(1, T+1)),
        name="4.1b"
    )

    m.addConstrs(
        (d[i, t-1] <= d[i, t] for i in V for t in range(2, T+1)),
        name="4.1c"
    )

    m.addConstrs(
        (b[i, t-1] <= b[j, t] + d[j, t] for i in V for j in utils.get_N(i, G) for t in range(1, T+1)),
        name="4.1d"
    )

    # max B defensive budget per timestep
    m.addConstrs(
        (gp.quicksum(s[i, t] - s[i, t-1] for i in V) <= B for t in range(1, T+1)),
        name="4.1e"
    )

    # dsufficient defensive budget spent on the node
    m.addConstrs(
        (c[i]*d[i, t] <= s[i, t] for i in V for t in range(1, T+1)),
        name="4.1f"
    )

    # 4.1g -> no node starts with spent defensive budget
    for i in V:
        s[i, 0].ub = 0

    # 4.1h
    for i in F:
        b[i, 0].lb = 1
        b[i, 0].ub = 1

    # 4.1a -> minimize the value of burning vertices
    m.setObjective(gp.quicksum(v[i]*b[i, T] for i in V), GRB.MINIMIZE)

    m.optimize()

    return m, b, d, s

optimization_problems = {
    "CFG": CFG,
    "CFG_improved": CFG_improved,
    "CF1": CF1,
    "CF1_improved": CF1_improved,
    "CF2": CF2,
    "CF2_improved": CF2_improved,
    "CVFG": CVFG
}

relax_availables = ["defense", "fires", "none"]