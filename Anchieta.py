import networkx as nx
import statistics
import numpy as np

#import numpy as np
from AX import Parse

def degrees():
    from time import sleep
    temporal = np.array([])
    G = nx.read_gexf('out.gexf')
    print(len(G.edges(data=True)))
    timestamps = sorted(list(map(lambda item: item[2]['start'], G.edges(data=True))), key=lambda  x: x)
    print("Timestamps sorted: {}".format(len(timestamps)))
    for t in timestamps:
        #filtered_edges = map(lambda x: (x[0], x[1], int(x[2]['id'])), filter(lambda item: item[2]['start'] <= t and item[2]['end'] >= t, G.edges(data=True)))
        #print(G.edges)
        filtered_edges = map(lambda x: (x[0], x[1], int(x[2]['id'])), (item for item in G.edges(data=True) if (item[2]['start'] <= t and item[2]['end'] >= t)))
        H = G.edge_subgraph(list(filtered_edges))
        H = nx.Graph(H)
        H.add_nodes_from(G.nodes())
        np.append(temporal, np.mean(np.array(list(nx.average_neighbor_degree(H).values()))))
        #temporal.append(statistics.mean([val for (node, val) in H.degree()]))
    return temporal

def convert_dynamic_graph():
    temporal = np.array([])
    G = nx.read_gexf('out.gexf')
    timestamps = numpy.sort(np.fromiter(map(lambda item: item[2]['start'], G.edges(data=True)), dtype=np.float))
    for t in timestamps:
        filtered_edges = map(lambda x: (x[0], x[1], int(x[2]['id'])), (item for item in G.edges(data=True) if (item[2]['start'] <= t and item[2]['end'] >= t)))
        H = G.edge_subgraph(list(filtered_edges))
        H = nx.Graph(H)
        H.add_nodes_from(G.nodes())
        np.append(temporal, np.mean(np.array(list(nx.average_neighbor_degree(H).values()))))
    ##TO-DO: Make it multithreaded
    return temporal

if __name__=="__main__":
    #print(degrees())
    Parse()
