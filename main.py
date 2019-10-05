import networkx as nx

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
			G.add_edge(line[7], line[8], start=float(line[3])*10000.0, end=float(line[4])*10000.0, label=line[7]+"_"+line[8], id=identifier, duration=float(line[5])*10000.0)
			identifier += 1

		nx.write_gexf(G, 'out.gexf')
	except: #In case it has the last line in file (\n)
		print("Error parsing graph from extract")
	return G

if __name__=="__main__":
	raw = read_extract("./Traces/hpcg.extract")
	G = create_graph(raw)
