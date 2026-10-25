import numpy as np
import networkx as nx
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from src.graph_generation import getPoints, DelaunayGraph, GabrielGraph
from src.graph_status import Status

MAX_COORD = 10
MIN_COORD = 0


def getF(G, f):
    """
        getF(G: Graph, f: number) -> list
        
        Given a graph and the number of initially burning nodes, compute the average degree of the nodes
        and create an ordered list depending on the distance of the degree with respect to the average.
        Then, the first f nodes are picked and returned
    """
    degrees = dict(G.degree())
    avg_degree = sum(degrees.values())/len(degrees)

    sorted_nodes = sorted(
        G.nodes(),
        key=lambda v: (abs(degrees[v]-avg_degree), v)
    )
    
    return sorted_nodes[:f]

def burnNodes(G, F):
    
    for i in F:
        G.nodes[i]["status"] = Status.BURNING
    
    return G

def setDefenders(G, D):
    
    for i in D:
        G.nodes[i]["status"] = Status.DEFENDED
        
    return G

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
    anim.save(f"{path}/graph.gif", writer="pillow", fps=1) 

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
        
        color = 'black'
        
        if G.nodes[i]['status'].value == 'defended':
            color = 'darkblue'
        elif G.nodes[i]['status'].value == 'burning':
            color = 'red'  
        
        ax.scatter(
            points[i, 0],
            points[i, 1],
            c=color
        )


    for i, (x, y) in enumerate(points):
        ax.text(
            x+0.1,
            y-0.2,
            str(i),
            fontsize=10,
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