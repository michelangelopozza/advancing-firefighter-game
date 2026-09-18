import gurobipy as gb

item_weight = [2, 4, 6, 2, 5, 1]
item_preference = [0.3, 1.1, 2.3, 0.3, 5.1, 0.1]
max_weight = 8
n_items = len(item_weight)

knapsack = gb.Model()

x = knapsack.addVars([i for i in range(n_items)], vtype=gb.GRB.BINARY)

knapsack.addConstr(
    gb.quicksum(x[i] * item_weight[i] for i in range(n_items)) <= max_weight
)

knapsack.setObjective(
    gb.quicksum(x[i] * item_preference[i] for i in range(n_items)), sense=gb.GRB.MAXIMIZE
)

knapsack.optimize()

print(knapsack.objVal)
print(x)