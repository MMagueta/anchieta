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

with otf2.reader.open("/home/mmagueta/Documents/barnes_hut_4/traces.otf2") as trace:
    graph = []
    enter_leave = []
    trace_events = filter(lambda item: item[1].__class__.__name__ == 'MpiSend' or item[1].__class__.__name__ == 'MpiRecv' or item[1].__class__.__name__ == 'MpiCollectiveBegin' or item[1].__class__.__name__ == 'MpiCollectiveEnd', trace.events)
    for item in trace_events:
        
        if item[1].__class__.__name__ == 'MpiSend':
            pass
            graph.append({'time': item[1].time, 'sender': int(item[0].group.name.split(" ")[-1]), 'receiver': item[1].receiver, 'link_type': item[1].__class__.__name__})
        elif item[1].__class__.__name__ == 'MpiRecv':
            pass
            graph.append({'time': item[1].time, 'sender': item[1].sender, 'receiver': int(item[0].group.name.split(" ")[-1]), 'link_type': item[1].__class__.__name__})
        elif item[1].__class__.__name__ == 'MpiCollectiveEnd':
            #print(item[1].communicator.group.members)
            #print(item[1])
            #print(item[1].root)
            if item[1].collective_op == otf2.CollectiveOp.ALLREDUCE:
                communicator = list(map(lambda item: int(item.group.name.split(" ")[-1]), item[1].communicator.group.members))
                for c1 in communicator:
                    for c2 in communicator:
                        if c1 != c2:
                            graph.append({'time': item[1].time, 'sender': c1, 'receiver': c2, 'link_type': "MPIAllReduce"})
            else:
                print(item[1].collective_op)

    graph = filter_links(sorted(graph, key=lambda  x: x['time']))
    create_graph(graph)