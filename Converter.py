import otf2 as otf2
from otf2.events import *
import networkx as nx
from itertools import permutations

def create_graph(extract):
    G = nx.MultiDiGraph()
    identifier = 0
    for link in extract:
        if link['sender'] not in G:
            G.add_node(link['sender'])
        if link['receiver'] not in G:
            G.add_node(link['receiver'])
        G.add_edge(link['sender'], link['receiver'], start=float(link['time']), end=float(link['end']), label=str(link['sender'])+"_"+str(link['receiver']), id=identifier)
        identifier += 1
    nx.write_gexf(G, 'out.gexf')
    return G

def filter_links(graph):
    sends = list(filter(lambda elem: elem['link_type'] == 'MpiSend', graph))
    receives = list(filter(lambda elem: elem['link_type'] == 'MpiRecv', graph))
    normalize = True
    if len(sends) != len(receives):
        return "ERROR: Links cannot be formed because of asymmetrical connections."
    for s in sends:
        r = filter(lambda elem: elem['sender'] == s['sender'] and elem['receiver'] == s['receiver'], receives).__next__()
        receives.pop(receives.index(r))
        sends[sends.index(s)]['end'] = r['time']
        if normalize == True:
            normalize = r['time']
        sends[sends.index(s)]['time'] /= normalize
        sends[sends.index(s)]['end'] /= normalize
    return sends

with otf2.reader.open("/storage/magueta-storage/n-body/BH/py/scorep_4_128@100/traces.otf2") as trace:
    send_receives = []
    collectives = []
    average_allreduce = 4.17*(10**(-6))
    for item in trace.events:
        if item[1].__class__.__name__ == 'MpiSend':
            send_receives.append({'time': item[1].time-trace.definitions.clock_properties.global_offset, 'sender': int(item[0].group.name.split(" ")[-1]), 'receiver': item[1].receiver, 'link_type': item[1].__class__.__name__})
        elif item[1].__class__.__name__ == 'MpiRecv':
            send_receives.append({'time': item[1].time-trace.definitions.clock_properties.global_offset, 'sender': item[1].sender, 'receiver': int(item[0].group.name.split(" ")[-1]), 'link_type': item[1].__class__.__name__})
        elif item[1].__class__.__name__ == 'MpiCollectiveEnd':
            #print(item[0], item[1], item[1].communicator.group.members)
            if item[1].collective_op == otf2.CollectiveOp.ALLREDUCE:
                comm_permutation = permutations(map(lambda item: int(item.group.name.split(" ")[-1]), item[1].communicator.group.members), 2)
                for c1, c2 in comm_permutation:
                    collectives.append({'time': (item[1].time-trace.definitions.clock_properties.global_offset)-average_allreduce, 'end': item[1].time-trace.definitions.clock_properties.global_offset, 'sender': c1, 'receiver': c2, 'link_type': "MPIAllReduce"})

    graph = (filter_links(sorted(send_receives, key=lambda  x: x['time'])) + collectives)
    create_graph(graph)