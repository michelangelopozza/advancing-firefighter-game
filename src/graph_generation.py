import networkx as nx
import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from src.graph_status import Status


MAX_COORD = 10
MIN_COORD = 0

def getPoints(n_points, seed=None):
    if seed != None:
        np.random.seed(seed)
    
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