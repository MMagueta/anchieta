import otf2 as otf2
from otf2.events import *
import networkx as nx
from itertools import permutations

def create_graph(extract, name):
    G = nx.MultiDiGraph()
    identifier = 0
    for link in extract:
        if link['sender'] not in G:
            G.add_node(link['sender'])
        if link['receiver'] not in G:
            G.add_node(link['receiver'])
        G.add_edge(link['sender'], link['receiver'], start=float(link['time']), end=float(link['end']), label=str(link['sender'])+"_"+str(link['receiver']), id=identifier)
        identifier += 1
    nx.write_gexf(G, name + '.gexf')
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
        #if normalize == True:
        #    normalize = r['time']
        #sends[sends.index(s)]['time'] /= normalize
        #sends[sends.index(s)]['end'] /= normalize
    return sends

with otf2.reader.open("/storage/magueta-storage/n-body/BH/py/scorep_16_128@100/traces.otf2") as trace:
    send_receives = []
    collectives = []
    average_allreduce = 7.12*(10**(-6))
    average_gatherv = 9.15*(10**(-6))
    average_scatter = 13350.15*(10**(-6))
    average_gather = 22410.37*(10**(-6))
    average_broadcast = 6477.11*(10**(-6))
    average_barrier = 1912813.09*(10**(-6))
    OPTION_BARRIER = False
    OPTION_ALLREDUCE = False

    for item in trace.events:
        if item[1].__class__.__name__ == 'MpiSend' or item[1].__class__.__name__ == 'MpiIsend':
            send_receives.append({'time': item[1].time-trace.definitions.clock_properties.global_offset, 'sender': int(item[0].group.name.split(" ")[-1]), 'receiver': item[1].receiver, 'link_type': "MpiSend"})
        elif item[1].__class__.__name__ == 'MpiRecv':
            send_receives.append({'time': item[1].time-trace.definitions.clock_properties.global_offset, 'sender': item[1].sender, 'receiver': int(item[0].group.name.split(" ")[-1]), 'link_type': "MpiRecv"})
        elif item[1].__class__.__name__ == 'MpiCollectiveEnd':
            #print(item[0], item[1], item[1].communicator.group.members)
            if item[1].collective_op == otf2.CollectiveOp.ALLREDUCE and OPTION_ALLREDUCE:
                comm_permutation = permutations(map(lambda item: int(item.group.name.split(" ")[-1]), item[1].communicator.group.members), 2)
                for c1, c2 in comm_permutation:
                    collectives.append({'time': (item[1].time-trace.definitions.clock_properties.global_offset)-average_allreduce, 'end': item[1].time-trace.definitions.clock_properties.global_offset, 'sender': c1, 'receiver': c2, 'link_type': "MPIAllReduce"})
            elif item[1].collective_op == otf2.CollectiveOp.SCATTER:
                communicator = map(lambda item: int(item.group.name.split(" ")[-1]), item[1].communicator.group.members)
                for c in communicator:
                    if c != int(item[0].group.name.split(" ")[-1]):
                        collectives.append({'time': (item[1].time-trace.definitions.clock_properties.global_offset)-average_scatter, 'end': item[1].time-trace.definitions.clock_properties.global_offset, 'sender': int(item[0].group.name.split(" ")[-1]), 'receiver': c, 'link_type': "MPIScatter"})
            elif item[1].collective_op == otf2.CollectiveOp.GATHER or item[1].collective_op == otf2.CollectiveOp.GATHERV:
                communicator = map(lambda item: int(item.group.name.split(" ")[-1]), item[1].communicator.group.members)
                for c in communicator:
                    if c != int(item[0].group.name.split(" ")[-1]):
                        if item[1].collective_op == otf2.CollectiveOp.GATHERV:
                            collectives.append({'time': (item[1].time-trace.definitions.clock_properties.global_offset)-average_gatherv, 'end': item[1].time-trace.definitions.clock_properties.global_offset, 'sender': c, 'receiver': int(item[0].group.name.split(" ")[-1]), 'link_type': "MPIGatherv"})
                        else:
                            collectives.append({'time': (item[1].time-trace.definitions.clock_properties.global_offset)-average_gather, 'end': item[1].time-trace.definitions.clock_properties.global_offset, 'sender': c, 'receiver': int(item[0].group.name.split(" ")[-1]), 'link_type': "MPIGather"})
            elif item[1].collective_op == otf2.CollectiveOp.BARRIER and OPTION_BARRIER:
                comm_permutation = permutations(map(lambda item: int(item.group.name.split(" ")[-1]), item[1].communicator.group.members), 2)
                for c1, c2 in comm_permutation:
                    collectives.append({'time': (item[1].time-trace.definitions.clock_properties.global_offset)-average_barrier, 'end': item[1].time-trace.definitions.clock_properties.global_offset, 'sender': c1, 'receiver': c2, 'link_type': "MPIBarrier"})
    graph = (filter_links(sorted(send_receives, key=lambda  x: x['time'])) + collectives)
    create_graph(graph, "BH16")