import gurobipy as gp
from gurobipy import GRB	

import argparse
import numpy as np
import os

import matplotlib.pyplot as plt
from src.graph_generation import getPoints, DelaunayGraph, GabrielGraph
import src.utils as utils
from src.models import optimization_problems, relax_availables, CFG, CFG_improved

from src.configurations import CONFIGURATIONS

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
# Number of simulation per configuration
N_SIM = 5

PLOT_PATH = "figures"
RESULTS_PATH = "results"

""" Classical Firefighter formulation """
test_name = "test_CFG"
def perform_full_test():
    for idx, config in enumerate(CONFIGURATIONS):
        
        # Number of generated points on the graph
        n_points = config["n_points"]
        # Max T in the classical formulation corresponds to the number of points
        T_max = n_points



        n_firefighters = config["n_firefighters"]
        n_fires = config["n_fires"]

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
            F_G = utils.getF(G, n_fires)
            F_D = utils.getF(D, n_fires)

            if PLOTS:
                fig, ax = plt.subplots(figsize=(8,8))
                plot_graph(ax, G, points, "Gabriel Graph")
                plt.show()

                fig, ax = plt.subplots(figsize=(8,8))
                plot_graph(ax, D, points, "Delaunay Graph")
                plt.show()

            V_G = list(G.nodes())
            V_D = list(D.nodes())


            m_G, b_G, d_G = CFG(G, T, n_firefighters, F_G)
            m_D, b_D, d_D = CFG(D, T, n_firefighters, F_D)

            T_opt_G = utils.get_T_opt(b_G, V_G, T)

            #graph_animation(f"{PLOT_PATH}/Gabriel_IP1.gif", points, G, V_G, F_G, T_opt_G, b_G, d_G)

            T_opt_D = utils.get_T_opt(b_D, V_D, T)

            #graph_animation(f"{PLOT_PATH}/Delaunay_IP1.gif", points, D, V_D, F_D, T_opt_D, b_D, d_D)

            info_G.append(utils.results_single_graph_vocabulary(G, V_G, T, m_G, b_G, d_G, "Gabriel"))
            info_D.append(utils.results_single_graph_vocabulary(D, V_D, T, m_D, b_D, d_D, "Delaunay"))

        total_info_G = utils.compute_mean_graph_vocabulary(info_G, N_SIM, "Gabriel")
        total_info_D = utils.compute_mean_graph_vocabulary(info_D, N_SIM, "Delaunay")

        info = utils.test_information_vocabulary(n_points, n_fires, n_firefighters, total_info_G, total_info_D)

        utils.append_to_csv(info, f"{RESULTS_PATH}/{test_name}.csv")

    utils.from_csv_to_pdf(f"{RESULTS_PATH}/{test_name}.csv", f"{RESULTS_PATH}/{test_name}.pdf")

def perform_simple_graphic_test(n_points, seed, type_opt, n_fires, n_firefighters, alpha, relax):
    save_path = f"{PLOT_PATH}/simple_test_{type_opt}"
    os.makedirs(save_path, exist_ok=True)

    opt = optimization_problems[type_opt]
    
    points = utils.getPoints(n_points, seed)

    T_max = n_points
    T = T_max 

    # given the points generate its Gabriel and Delaunay Graph
    G = GabrielGraph(points)
    D = DelaunayGraph(points)

    # get the F set
    F_G = utils.getF(G, n_fires)
    F_D = utils.getF(D, n_fires)

    V_G = list(G.nodes())
    V_D = list(D.nodes())

    if type_opt == "CFG_improved":
        m_G, b_G, d_G = opt(G, T, n_firefighters, F_G, alpha, relax)
        m_D, b_D, d_D = opt(D, T, n_firefighters, F_D, alpha, relax)
    else:
        m_G, b_G, d_G = opt(G, T, n_firefighters, F_G)
        m_D, b_D, d_D = opt(D, T, n_firefighters, F_D) 

    T_opt_G = utils.get_T_opt(b_G, V_G, T)
    T_opt_D = utils.get_T_opt(b_D, V_D, T)

    utils.graph_animation(f"{save_path}/Gabriel_animation.gif", points, G, V_G, F_G, T_opt_G, b_G, d_G)
    utils.graph_animation(f"{save_path}/Delaunay_animation.gif", points, D, V_D, F_D, T_opt_D, b_D, d_D)
    
    fig, ax = plt.subplots(figsize=(8,8))
    utils.plot_graph(ax, G, points, "Gabriel Graph")
    plt.savefig(f"{save_path}/Gabriel.png")

    fig, ax = plt.subplots(figsize=(8,8))
    utils.plot_graph(ax, D, points, "Delaunay Graph")
    plt.savefig(f"{save_path}/Delaunay.png")

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--test", type=str, default="simple")
    parser.add_argument("--opt", type=str, default="CFG")
    parser.add_argument("-n", type=int, default=10)
    parser.add_argument("-f", type=int, default=1)
    parser.add_argument("-d", type=int, default=1)
    parser.add_argument("-alpha", type=float, default=0.3)
    parser.add_argument("-relax", type=str, default="none")

    args = parser.parse_args()
    
    test = args.test
    type_opt = args.opt
    n_points = args.n
    n_fires = args.f
    n_firefighters = args.d
    alpha = args.alpha
    relax = args.relax

    if type_opt not in optimization_problems:
        opt_available = ", ".join(optimization_problems.keys())
        parser.error(f"Test '{type_opt}' does not exist. Use one of: {opt_available}")

    if alpha < 0.0 or alpha > 1.0:
        parser.error(f"Alpha '{alpha}' is out of bounds. Use alpha in [0.0, 1.0]")

    if relax not in relax_availables:
        parser.error(f"Relax '{relax}' is not defined. Use one of the following relaxations: {relax_availables}")

    if test == "simple":
        perform_simple_graphic_test(n_points, SEED, type_opt, n_fires, n_firefighters, alpha, relax)
                