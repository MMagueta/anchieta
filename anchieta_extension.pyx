#!python
#cython: language_level=3, boundscheck=False

from cython.parallel import parallel, prange
from libc.stdlib cimport abort, malloc, free
from libc.stdio cimport stdout, fprintf
cimport openmp

def degrees():
	cdef int i
	cdef unsigned int n = 10000000
	cdef int * vet

	with nogil,parallel(num_threads=4): #Test
		vet = <int *> malloc(sizeof(int) * n)
		for i in prange(n):
			vet[i] = i
			fprintf(stdout, "%d %d\n", openmp.omp_get_thread_num(), vet[i])
		free(vet)