from mpi4py import MPI
from time import time
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

deb = time()

# Dimension du problème (peut-être changé)
dim = 1200

# Initialisation de la matrice
if rank == 0:
    A = np.array([ [(i+j)%dim+1. for i in range(dim)] for j in range(dim) ])
    #print(f"A = {A}")

# Initialisation du vecteur u
u = np.array([i+1. for i in range(dim)])
#print(f"u = {u}")

# Répartition des lignes de la matrice A
local_n = dim//size
local_A = np.zeros((local_n, dim))
if rank == 0:
    for i in range(1, size):
        comm.Send(A[local_n*i:local_n*(i+1)], dest=i)
    local_A=A[:local_n]
else:
    comm.Recv(local_A)

# Produit matrice-vecteur local
local_v = local_A.dot(u)

# Allocation de l'espace pour le résultat final

if rank == 0 : 
    v = np.zeros(dim)
else : 
    v = None
# Gather pour obtenir le résultat final sur chaque processus
comm.Gather(local_v, v, root=0)
#comm.Alltoall(local_v,)

#print(f"v = {v}")

fin = time()
print(f"Temps de calcul en ligne : {fin-deb} pour dimension {dim}")