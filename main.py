import networkx as nx
import HungarianAlgorithm as ha

def read_extract(path):
	with open(path, 'r')as file:
		return file.read()

def create_graph(raw_extract):
	G = nx.MultiDiGraph()
	try:
		identifier = 0
		for line in raw_extract.split("\n"):
			line = line.split(", ")
			if line[7] not in G:
				G.add_node(line[7])
			if line[8] not in G:
				G.add_node(line[8])
			#Sym relation, therefore using python magical comparator (min, max with strings)
			#G.add_edge(min(line[7], line[8]), max(line[7], line[8]), start=line[3], end=line[4], label=min(line[7], line[8])+"_"+max(line[7], line[8]))
			G.add_edge(line[7], line[8], start=float(line[3])*10000.0, end=float(line[4])*10000.0, label=line[7]+"_"+line[8], id=identifier, weight=float(line[5])*10000.0)
			identifier += 1

		nx.write_gexf(G, 'out.gexf')
	except: #In case it has the last line in file (\n)
		print("Error parsing graph from extract")
	return G

if __name__=="__main__":
	raw = read_extract("./traces/MC32_LINK.extract")
	G = create_graph(raw)
	
	W = [x[2]["weight"] for x in G.edges(data=True) if x[0] == "rank0"]
	M, H = ha.Generate_DiBipartite(30, 30, W) #sqrt(900) = 30
	print(ha.HungarianAlgorithm(M))