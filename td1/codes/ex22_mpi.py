from mpi4py import MPI
import numpy as np
import sys
import random
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

start = time.time()
random.seed(start)

def generate_random_point():
    return [random.uniform(-1,1), random.uniform(-1,1)]

def is_in_circle(pt):
    if pt[0]**2+pt[1]**2 <= 1:
        return True
    else : 
        return False

# Nombre de points total tiré d'un argument en ligne de commande
nb_pts = int(sys.argv[1])

# Nombre de points par processus
proc_nb_pts = nb_pts // size

points = np.zeros((proc_nb_pts,2))

for i in range(proc_nb_pts):
    points[i] = generate_random_point()

# Initialize area_estimation and the factor necessary to estimate pi
area_estimation = 0

for pt in points:
    if is_in_circle(pt):
        area_estimation+=1

total_area_estimation = comm.reduce(area_estimation, op=MPI.SUM, root=0)

if rank == 0:
    pi_estimation = total_area_estimation * 4/nb_pts
    end = time.time()
    print("Estimation de pi à",nb_pts,"points :", pi_estimation)
    print(f"Temps d'exécution : {end-start:.4f} seconds")