import numpy as np
import networkx as nx
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from src.graphGeneration import getPoints, DelaunayGraph, GabrielGraph, getF, plotGraph, setDefenders, burnNodes

MAX_COORD = 10
MIN_COORD = 0


def get_T_opt(b, V, T):
    for t in range(T + 1):
        finished = True
        for i in V:
            if (round(b[i, t].X) == 1) != (round(b[i, T].X) == 1):
                finished = False   
        if finished:
            return t
    return T

def graph_animation(path, points, G, V, F, T, b, d):

    fig, ax = plt.subplots(figsize=(8,8))

    
    
    anim = animation.FuncAnimation(
        fig, 
        update_graph_frame, 
        fargs=(ax, points, G, V, F, b, d),
        frames = 2*(T+1), interval = 1000) 
    anim.save(f"{path}/graph.gif", fps=1, writer="Pillow") 

    plt.close(fig)


def plot_graph(ax, G, points, title):

    ax.clear()

    ax.set_xlim(MIN_COORD, MAX_COORD)
    ax.set_ylim(MIN_COORD, MAX_COORD)

    ax.set_xticks(np.arange(MIN_COORD, MAX_COORD+1, 1))
    ax.set_yticks(np.arange(MIN_COORD, MAX_COORD+1, 1))

    ax.grid(True, linestyle="--", linewidth=0.5)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title(title)

    ax.set_aspect("equal")

    n_points = len(points)

    keys = np.zeros(n_points).astype(int)
    for i in range(n_points):
        keys[i] = i
    
    pos = dict(zip(keys, points))

    nx.draw_networkx_edges(
        G,
        pos=pos,
        ax=ax,
        edge_color='g',
        width=1.5
    )

    for i in range(n_points):
        
        color = 'tab:gray'
        
        if G.nodes[i]['status'].value == 'defended':
            color = 'tab:blue'
        elif G.nodes[i]['status'].value == 'burning':
            color = 'tab:red'  
        
        ax.scatter(
            points[i, 0],
            points[i, 1],
            c=color
        )


    for i, (x, y) in enumerate(points):
        ax.text(
            x,
            y+0.2,
            str(i),
            fontsize=15,
            color='black'
        )

def update_graph_frame(frame, ax, points, G, V, F, b, d):
        
    if frame == 0:
        burnNodes(G, F)
        plot_graph(ax, G, points, "t0")
    elif frame % 2 != 0:
        t = round((frame+1)/2)
        D = []
        for i in V:
            if round(d[i, t].X) == 1:
                D.append(i)
        setDefenders(G, D)
        plot_graph(ax, G, points, f"t={t}: set defenders")
    else:
        t = round(frame/2)
        F_prime = []
        for i in V:
            if round(b[i, t].X) == 1:
                F_prime.append(i)
        burnNodes(G, F_prime)
        plot_graph(ax, G, points, f"t={t}: burning nodes")
    
    

    


def provide_results(burned_nodes, T_opt):
    return 