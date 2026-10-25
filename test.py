import gurobipy as gp
from gurobipy import GRB	

import numpy as np

import matplotlib.pyplot as plt
from src.graph_generation import getPoints, DelaunayGraph, GabrielGraph
import src.utils as utils
from src.models import IP1

"""
    Implementation of the paper   
    "Advancing firefighter games: novel integer programming formulations and the cost-value model"

    In the following script are present different formulation of the same Firefighter Game 
    problem:
        - Classical Firefigher Game formulation (CFG)
        - Classical Firefighter Game + Time bounds (CFGTB)
        - Variation 1 of Classical Firefighter Game (CFG1)
        - Variation 2 of Classical Firefighter Game (CFG2)
        - Cost Value Firefighter Game (CVFG)
        - Cost Value Firefighter Game + Time bounds (CVFGTB)
        - Variation 1 of Cost Value Firefighter Game (CVF1)
        - Variation 2 of Cost Value Firefighter Game (CVF2)
        
"""

PLOTS = False
SEED = 57

PLOT_PATH = "figures"

""" Classical Firefighter formulation """

# Number of generated points on the graph
n_points = 10
# Max T in the classical formulation corresponds to the number of points
T_max = n_points
# Number of simulation per configuration
N_SIM = 5


n_firefighters = 1
n_fire = 1

info_G = []
info_D = []

for i in range(N_SIM):
    # generate n_points random points in the plane [0,10]^2 as described in the data generation part
    points = utils.getPoints(n_points)

    T = T_max 

    # given the points generate its Gabriel and Delaunay Graph
    G = GabrielGraph(points)
    D = DelaunayGraph(points)

    # get the F set
    F_G = utils.getF(G, n_fire)
    F_D = utils.getF(D, n_fire)

    if PLOTS:
        fig, ax = plt.subplots(figsize=(8,8))
        plot_graph(ax, G, points, "Gabriel Graph")
        plt.show()

        fig, ax = plt.subplots(figsize=(8,8))
        plot_graph(ax, D, points, "Delaunay Graph")
        plt.show()

    V_G = list(G.nodes())
    V_D = list(D.nodes())


    m_G, b_G, d_G = IP1(G, T, n_firefighters, F_G)
    m_D, b_D, d_D = IP1(D, T, n_firefighters, F_D)

    T_opt_G = utils.get_T_opt(b_G, V_G, T)

    #graph_animation(f"{PLOT_PATH}/Gabriel_IP1.gif", points, G, V_G, F_G, T_opt_G, b_G, d_G)

    T_opt_D = utils.get_T_opt(b_D, V_D, T)

    #graph_animation(f"{PLOT_PATH}/Delaunay_IP1.gif", points, D, V_D, F_D, T_opt_D, b_D, d_D)

    info_G.append(utils.results_single_graph_vocabulary(G, V_G, T, m_G, b_G, d_G, "Gabriel"))
    info_D.append(utils.results_single_graph_vocabulary(D, V_D, T, m_D, b_D, d_D, "Delaunay"))

total_info_G = utils.compute_mean_graph_vocabulary(info_G, N_SIM, "Gabriel")
total_info_D = utils.compute_mean_graph_vocabulary(info_D, N_SIM, "Delaunay")

info = utils.test_information_vocabulary(n_points, n_fire, n_firefighters, total_info_G, total_info_D)

print(info)