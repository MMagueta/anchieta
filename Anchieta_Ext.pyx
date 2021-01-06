#!python
#cython: language_level=3, boundscheck=False

from cython.parallel import parallel, prange
from libc.stdlib cimport abort, malloc, free
from libc.stdio cimport stdout, fprintf
cimport openmp
import cynetworkx as cnx
import numpy as np

def Parse():
	# cdef int i
	# cdef unsigned int n = 10000000
	# cdef int * vet

	# with nogil, parallel(num_threads=4): #Test
	# 	vet = <int *> malloc(sizeof(int) * n)
	# 	for i in prange(n):
	# 		vet[i] = i
	# 		fprintf(stdout, "%d %d\n", openmp.omp_get_thread_num(), vet[i])
	# 	free(vet)

	cpdef G = cnx.read_gexf('out.gexf')
	cdef int number_edges = G.number_of_edges()
	cdef float * timestamps
	cdef int i
	cdef sorted_edges = np.sort(np.fromiter(map(lambda item: item[2]['start'], G.edges(data=True)), dtype=np.float))
	cdef temporal = np.array([], dtype=np.object)
	cpdef filtered_edges
	cpdef edges = list(G.edges(data=True))
	cpdef H
	timestamps = <float *> malloc(sizeof(float) * number_edges)
	for i in range(number_edges):
		timestamps[i] = sorted_edges[i]

	for i in range(0, number_edges):
		filtered_edges = []
		for j in range(0, number_edges):
			if (edges[j][2]['start'] <= timestamps[i] and edges[j][2]['end'] >= timestamps[i]):
				filtered_edges.append((edges[j][0], edges[j][1], edges[j][2]['id']))
		print(filtered_edges)
	free(timestamps)
	return temporal