import networkx as nx
from random import randint as random
import numpy as np
import matplotlib.pyplot as plt
from functools import reduce

def HungarianAlgorithm(G):
    lines = np.zeros_like(G)
    def colorir(i, j, maximo, num_linhas):
        if lines[i][j] == 2:
            return num_linhas
        if maximo > 0 and lines[i][j] == 1:
            return num_linhas
        if maximo <= 0 and lines[i][j] == -1:
            return num_linhas
        for pos in range(len(G)):
            if maximo > 0:
                if lines[pos][j] == -1 or lines[pos][j] == 2:
                    lines[pos][j] = 2
                else:
                    lines[pos][j] = 1
            else:
                if lines[i][pos] == -1 or lines[i][pos] == 2:
                    lines[i][pos] = 2
                else:
                    lines[i][pos] = -1
        return num_linhas + 1
         
    def optimal_assignment(M):
        brute_force = [0 for _ in range(len(M))]
        line_control = [0 for _ in range(len(M))]
        def choose(i):
            if i == len(line_control):
                return True
            for j in range(len(M)):
                if M[i][j] == 0 and brute_force[j] == 0:
                    line_control[i] = j
                    brute_force[j] = 1
                    if choose(i + 1):
                        return list(map(lambda x: (line_control.index(x), x), line_control))
                    brute_force[j] = 0
            return False

        temp = 0
        maximum = lambda i,j: reduce(lambda a, b : a + b, [1 if M[control][j] == 0 else (-1 if M[i][control] == 0 else 0) for control in range(len(M))])
        for i in range(len(M)):
            for j in range(len(M)):
                if 0 == M[i][j]:
                    temp = colorir(i, j, maximum(i, j), temp)
        if temp > 2:
            return choose(0)
        else:
            return False

    reduction = lambda matrix: list(map(lambda x: list(map(lambda y: y-min(x), x)), matrix))
    G = reduction(G)
    print(G)
    G = np.transpose(reduction(np.transpose(G)))
    print(G)
    G = G.tolist()
    print(optimal_assignment(G))
    #print(np.transpose(G))

def Print_Graph(G, M, N):
    X, Y = nx.bipartite.sets(G)
    pos = dict()
    pos.update((n, (1, i)) for i, n in enumerate(X))
    pos.update((n, (2, i)) for i, n in enumerate(Y))
    nx.draw_networkx(G, pos = pos, edges = G.edges, node_color=["#A5B0E6" for _ in range(M)] + ["#A3481B" for _ in range(N)])
    plt.show()

if __name__=="__main__":
    M, N = 3, 3
    G = nx.DiGraph()
    G = nx.bipartite_random_graph(M, N, 1.0, seed=None, directed=False)
    #print(G.size(), G.edges)
    attributes = {}
    for e in G.edges():
        G[e[0]][e[1]]['weight'] = random(0, 10)
    matrix = [[] for _ in range(M)]
    
    for i in range(M):
        for j in range(M, N+M):
            try:
                #print(i, j, G[i][j])
                matrix[i].append(G[i][j]["weight"])
            except:
                pass
            #matrix[i].append(j)

    print(matrix)
    HungarianAlgorithm(matrix)
    #Print_Graph(G, M, N)
    #print(nx.adjacency_matrix(G))