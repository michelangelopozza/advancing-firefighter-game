import networkx as nx
import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt

MAX_COORD = 10
MIN_COORD = 0

n_points = 100

def getPoints(n_points):
    
    return np.column_stack((
        np.random.uniform(MIN_COORD, MAX_COORD, n_points),
        np.random.uniform(MIN_COORD, MAX_COORD, n_points)
    ))


def DelaunayGraph(points):
    
    # SciPy function to get Delaunay tessellation
    tri = Delaunay(points)
    G = nx.Graph()
    
    # tuple of two ndarrays of int; (indptr, indices)
    indptr = tri.vertex_neighbor_vertices[0]
    indices = tri.vertex_neighbor_vertices[1]
    
    # for every index i, its neighboors are indices[indptr[i]:indptr[i+1]]
    for i in range(len(points)):
        for j in indices[indptr[i]:indptr[i+1]]:
            # to avoid adding two times the same edge
            if i < j:
                G.add_edge(i, j)
                
    return G

def GabrielViaDelaunay(points):
    G = DelaunayGraph(points)
    
    # edges is like (0, 91), (0, 62), (0, 41), ..., (39, 79), (39, 99), ...
    for e in G.edges():
    
        # nodes contains the 100 indeces of the nodes
        for other in G.nodes():
            
            # if the chosen node is not in the selected edge, compute the disc that contains 
            # p1 and p2 and check if p3 (the other node) lies inside this circumference.
            # If it lies inside remove the edge
            # If not don't do anything
            if other not in e:
                p1 = points[e[0]]
                p2 = points[e[1]]
                p3 = points[other]
                center = 0.5*(p1+p2)
                radius = 0.5*np.linalg.norm(p2-p1)
                if (np.linalg.norm(p3-center)<=radius):
                    G.remove_edge(e[0], e[1])
                    break
    
    return G

def plotGraphs(G1, G2, points, title1, title2):
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    graphs = [
        (G1, title1),
        (G2, title2)
    ]

    for ax, (G, title) in zip(axes, graphs):

        pos = {i: points[i] for i in range(len(points))}

        nx.draw_networkx_edges(
            G,
            pos=pos,
            ax=ax,
            width=1.5
        )

        ax.scatter(
            points[:, 0],
            points[:, 1],
            s=50,
            zorder=2
        )

        for i, (x, y) in enumerate(points):
            ax.text(
                x,
                y,
                str(i),
                fontsize=10,
                ha="right",
                va="bottom"
            )

        ax.set_xlim(MIN_COORD, MAX_COORD)
        ax.set_ylim(MIN_COORD, MAX_COORD)

        ax.set_xticks(np.arange(MIN_COORD, MAX_COORD + 1, 1))
        ax.set_yticks(np.arange(MIN_COORD, MAX_COORD + 1, 1))

        ax.grid(True, linestyle="--", linewidth=0.5)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title(title)

        ax.set_aspect("equal")

    plt.tight_layout()
    plt.show()

points = getPoints(n_points)


G_Delaunay = DelaunayGraph(points)

G_Gabriel = GabrielViaDelaunay(points)

plotGraphs(G_Delaunay, G_Gabriel, points, "Delaunay", "Gabriel")