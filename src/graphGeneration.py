import networkx as nx
import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from enum import Enum

MAX_COORD = 10
MIN_COORD = 0

class Status(Enum):
    BURNING = "burning"
    DEFENDED = "defended"
    NONE = "none"

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
    
    for i in range(len(points)):
        G.add_node(i, status=Status.NONE)
    
    # for every index i, its neighboors are indices[indptr[i]:indptr[i+1]]
    for i in range(len(points)):
        for j in indices[indptr[i]:indptr[i+1]]:
            # to avoid adding two times the same edge
            if i < j:
                G.add_edge(i, j)
        
    return G

def GabrielGraph(points):
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

def plotGraph(G, points):
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))

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

    ax.set_xlim(MIN_COORD, MAX_COORD)
    ax.set_ylim(MIN_COORD, MAX_COORD)

    ax.set_xticks(np.arange(MIN_COORD, MAX_COORD+1, 1))
    ax.set_yticks(np.arange(MIN_COORD, MAX_COORD+1, 1))

    ax.grid(True, linestyle="--", linewidth=0.5)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Graph")

    ax.set_aspect("equal")

    plt.tight_layout()
    plt.show()

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

# n_points = 10

# points = getPoints(n_points)

# G = DelaunayGraph(points)

# F = getF(G, 3)
# D = [0,1]

# G = burnNodes(G, F)
# G = setDefenders(G, D)

# plotGraphWithFire(G, points)

# for node in G.nodes():
#     print(node, G.nodes[node]['status'].value)