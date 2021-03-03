import networkx as nx
import statistics
import numpy as np
from threading import Thread
from AX import Parse
from math import floor
import time
import sys

start = time.time()
#numbers = []
G = nx.read_gexf('gexfs/'+sys.argv[1]+'.gexf')
timestamps = sorted(set(list(map(lambda item: item[2]['start'], G.edges(data=True)))), key=lambda  x: x)
#print(set(timestamps))
temporal = np.zeros(len(timestamps))
print("Edges:", len(temporal))

def temporal_calculation(id, number_threads, fun):
    pieces = floor(len(timestamps)/number_threads)
    if id+1 != number_threads:
        thread_range = [pieces*id, pieces*(id+1)-1]
    else:
        thread_range = [pieces*id, len(timestamps)]

    print(id, thread_range)
    for t in range(thread_range[0]-1, thread_range[1]):
        if t > -1: #Must ignore the first because of the range initial state, eg.: [0-1=-1, 1] and [1-1=0, 2]
            #numbers.append(t)
            H = nx.Graph()
            filtered_edges = list(map(lambda x: (int(x[0]), int(x[1])), (item for item in G.edges(data=True) if (item[2]['start'] <= timestamps[t] and item[2]['end'] >= timestamps[t]))))
            #print(filtered_edges)
            H.add_nodes_from(G.nodes())
            H.add_edges_from(filtered_edges)
            temporal[t] = fun(H)
            #print(temporal[t])

if __name__=="__main__":
    #Parse()
    try:
        threads = []
        if len(temporal) < 56: #Number of cores
            N = len(temporal)-1
        else:
            N = 56
        print("N:", N)
        for i in range(N):
            #threads.append(Thread(target=temporal_calculation, args=( i, N, #lambda H: np.mean(np.array(list(nx.average_neighbor_degree(H).values()))) ))) #Degree
            #threads.append(Thread(target=temporal_calculation, args=( i, N, lambda H: np.mean(list(nx.average_neighbor_degree(H).values())) )))
            #threads.append(Thread(target=temporal_calculation, args=( i, N, lambda H: nx.average_shortest_path_length(H) )))
            threads.append(Thread(target=temporal_calculation, args=( i, N, lambda H: nx.density(H) )))
        for i in range(N):
            threads[i].start()
        for i in range(N):
            threads[i].join()
        #print(sorted(numbers))
        np.savetxt('temporal/densidade/'+sys.argv[1]+'.csv', temporal, delimiter=',')
        np.savetxt('temporal/densidade/T_'+sys.argv[1]+'.csv', timestamps, delimiter=',')
        print(time.time() - start)
    except Exception as e:
        print ("Unable to start thread: {}".format(str(e)))


"""

import networkx as nx
import statistics
import numpy as np
from threading import Thread
from AX import Parse
from math import floor
import time
import sys

start = time.time()
#numbers = []
G = nx.read_gexf('gexfs/'+sys.argv[1]+'.gexf')
timestamps = sorted(list(map(lambda item: item[2]['start'], G.edges(data=True))), key=lambda  x: x)
temporal = np.zeros(len(timestamps))
print("Edges:", len(temporal))

def temporal_calculation(id, number_threads, fun):
    pieces = floor(G.number_of_edges()/number_threads)
    if id+1 != number_threads:
        thread_range = [pieces*id, pieces*(id+1)-1]
    else:
        thread_range = [pieces*id, G.number_of_edges()]

    #print(id, thread_range)
    for t in range(thread_range[0]-1, thread_range[1]):
        if t > -1: #Must ignore the first because of the range initial state, eg.: [0-1=-1, 1] and [1-1=0, 2]
            #numbers.append(t)
            H = nx.Graph()
            filtered_edges = list(map(lambda x: (int(x[0]), int(x[1])), (item for item in G.edges(data=True) if (item[2]['start'] <= timestamps[t] and item[2]['end'] >= timestamps[t]))))
            #print(filtered_edges)
            H.add_nodes_from(G.nodes())
            H.add_edges_from(filtered_edges)
            temporal[t] = fun(H)
            #print(temporal[t])

if __name__=="__main__":
    #Parse()
    try:
        threads = []
        if len(temporal) < 48: #Number of cores
            N = len(temporal)-1
        else:
            N = 48
        print("N:", N)
        for i in range(N):
            #threads.append(Thread(target=temporal_calculation, args=( i, N, lambda H: np.mean(np.array(list(nx.average_neighbor_degree(H).values()))) ))) #Degree
            threads.append(Thread(target=temporal_calculation, args=( i, N, lambda H: nx.density(H) )))#np.mean(list(nx.average_neighbor_degree(H).values())) )))
        for i in range(N):
            threads[i].start()
        for i in range(N):
            threads[i].join()
        #print(sorted(numbers))
        np.savetxt('temporal/densidade/'+sys.argv[1]+'.csv', temporal, delimiter=',')
        print(time.time() - start)
    except Exception as e:
        print ("Unable to start thread: {}".format(str(e)))

"""