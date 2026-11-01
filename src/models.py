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


def CFG_improved(G, T, n_firefighters, F, alpha, relax="none"):

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

def CF1_improved(G, T, n_firefighters, F, alpha=0.3, relax="none"):

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

optimization_problems = {
    "CFG": CFG,
    "CFG_improved": CFG_improved,
    "CF1": CF1,
    "CF1_improved": CF1_improved
}

relax_availables = ["defense", "fires", "none"]