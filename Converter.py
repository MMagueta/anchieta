import otf2 as otf2
from otf2.events import *
import networkx as nx

def create_graph(extract):
    G = nx.MultiDiGraph()

    identifier = 0
    for link in extract:
        if link['sender'] not in G:
            G.add_node(link['sender'])
        if link['receiver'] not in G:
            G.add_node(link['receiver'])

        #Sym relation, therefore using python magical comparator (min, max with strings)
        G.add_edge(link['sender'], link['receiver'], start=float(link['time']), end=float(link['end']), label=str(link['sender'])+"_"+str(link['receiver']), id=identifier)
        identifier += 1

    nx.write_gexf(G, 'out.gexf')

    return G

def filter_links(graph):
    sends = list(filter(lambda elem: elem['link_type'] == 'MpiSend', graph))
    receives = list(filter(lambda elem: elem['link_type'] == 'MpiRecv', graph))
    normalize_send = sends[0]['time']
    normalize_receive = False
    if len(sends) != len(receives):
        return "ERROR: Links cannot be formed because of asymmetrical connections."
    for s in sends:
        r = filter(lambda elem: elem['sender'] == s['sender'] and elem['receiver'] == s['receiver'], receives).__next__()
        receives.pop(receives.index(r))
        sends[sends.index(s)]['time'] -= normalize_send
        
        sends[sends.index(s)]['end'] = r['time'] - normalize_send
        if normalize_receive == False:
            normalize_receive = r['time'] - normalize_send
        sends[sends.index(s)]['time'] /= normalize_receive
        sends[sends.index(s)]['end'] /= normalize_receive
    return sends

with otf2.reader.open("/storage/magueta-storage/n-body/scorep_4/traces.otf2") as trace:
    graph = []
    enter_leave = []
    for item in trace.events:

    if item[1].__class__.__name__ == 'MpiSend':
        graph.append({'time': item[1].time, 'sender': int(item[0].group.name.split(" ")[-1]), 'receiver': item[1].receiver, 'link_type': item[1].__class__.__name__})
        #print(graph)
    elif item[1].__class__.__name__ == 'MpiRecv':
        graph.append({'time': item[1].time, 'sender': item[1].sender, 'receiver': int(item[0].group.name.split(" ")[-1]), 'link_type': item[1].__class__.__name__})
    #elif (item[1].__class__.__name__ == 'Enter' or item[1].__class__.__name__ == 'Leave') and (item[1].region.name == "MPI_Send" or item[1].region.name == "MPI_Recv"):
    #    enter_leave.append({"container": item[1].__class__.__name__, "time": item[1].time, "rank": item[0].group.name.split(" ")[-1], "type": item[1].region.name})
    
    print("finish")
    #print((filter(lambda g: (g["receiver"] == enter_leave[0]["rank"]) and (g["time"] >= enter_leave[0]["time"]), graph)).__next__())
    graph = filter_links(sorted(graph, key=lambda  x: x['time']))
    #print(graph)
    create_graph(graph)