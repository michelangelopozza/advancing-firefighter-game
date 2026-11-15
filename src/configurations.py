from itertools import product


GRID = {
    "n_points":       [10, 20, 30],
    "n_fires":        [1, 2],
    "n_firefighters": [1, 2],
}

CONFIGURATIONS = [
    dict(zip(GRID.keys(), values))
    for values in product(*GRID.values())
]

grid_2 = {
    "T_max": [0, 1, 2, 3, 4],
    "n_points": [10, 20, 30]
}

config_test_2 = [
    dict(zip(grid_2.keys(), values))
    for values in product(*grid_2.values())
]

grid_params_2 = {
    "n_fires":        [1, 2],
    "n_firefighters": [1, 2]
}

params_test_2 = [
    dict(zip(grid_params_2.keys(), values))
    for values in product(*grid_params_2.values())
]

config_test_3 = ["none", "fires", "defense"]

grid_params_3 = {
    "n_points": [10, 20, 30],
    "n_fires": [1, 2, 3],
    "n_firefighters": [1]
}

params_test_3 = [
    dict(zip(grid_params_3.keys(), values))
    for values in product(*grid_params_3.values())
]

grid_test_4 = {
    "preprocessing": [False, True],
    "alpha": [0.1],
    "defense": ["3.1f", "3.2"],
    "other_constraints": [[], ["3.1e"], ["3.4"], ["3.1e_alpha"]]
}

config_test_4 = [
    dict(zip(grid_test_4.keys(), values))
    for values in product(*grid_test_4.values())
]

grid_params_4 = {
    "n_points": [10, 20, 30],
    "n_fires": [1, 2, 3],
    "n_firefighters": [1]
}

params_test_4 = [
    dict(zip(grid_params_4.keys(), values))
    for values in product(*grid_params_4.values())
]

grid_test_5 = {
    "preprocessing": [True],
    "alpha": [0.1],
    "defense": ["3.5b", "3.6"],
    "other_constraints": [[], ["3.7"], ["3.7_alpha"], ["3.8"], ["3.8_alpha"], ["3.9"], ["3.10"]]
}

config_test_5_a = [{"preprocessing": False, "alpha": 0.1, "defense": "3.5b", "other_constraints": []}]

config_test_5_b = [
    dict(zip(grid_test_5.keys(), values))
    for values in product(*grid_test_5.values())
]

config_test_5 = config_test_5_a + config_test_5_b

grid_params_5 = {
    "n_points": [10, 20, 30],
    "n_fires": [1, 2, 3],
    "n_firefighters": [1]
}

params_test_5 = [
    dict(zip(grid_params_5.keys(), values))
    for values in product(*grid_params_5.values())
]

grid_test_6 = {
    "preprocessing": [False, True],
    "alpha": [0.1],
    "defense": ["3.1f", "3.2"],
    "other_constraints": [[], ["3.13"], ["3.15"], ["3.13", "3.15"], ["3.12_alpha"]]
}

config_test_6 = [
    dict(zip(grid_test_6.keys(), values))
    for values in product(*grid_test_6.values())
]

grid_params_6 = {
    "n_points": [10, 20, 30],
    "n_fires": [1, 2, 3],
    "n_firefighters": [1]
}

params_test_6 = [
    dict(zip(grid_params_6.keys(), values))
    for values in product(*grid_params_6.values())
]