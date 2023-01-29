import numpy as np
import sys
import random
import time


start = time.time()
random.seed(start)

def generate_random_point():
    return [random.uniform(-1,1), random.uniform(-1,1)]

def is_in_circle(pt):
    if pt[0]**2+pt[1]**2 <= 1:
        return True
    else : 
        return False

nb_pts = int(sys.argv[1])
points = np.zeros((nb_pts,2))


for i in range(nb_pts):
    points[i] = generate_random_point()

area_estimation = 0
factor = 4/nb_pts

for pt in points:
    if is_in_circle(pt):
        area_estimation+=1

end = time.time()
print("Estimation de pi à",nb_pts,"points :", area_estimation*factor )
print(f"Temps d'exécution : {end-start:.4f} seconds")