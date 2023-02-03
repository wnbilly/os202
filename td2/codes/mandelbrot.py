# Calcul de l'ensemble de Mandelbrot en python
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
import matplotlib.cm
from mpi4py import MPI


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius : float = 2.0

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c:complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c,smooth)/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex,  smooth=False) :
        z    : complex
        iter : int

        # On vérifie dans un premier temps si le complexe
        # n'appartient pas à une zone de convergence connue :
        #   1. Appartenance aux disques  C0{(0,0),1/4} et C1{(-1,0),1/4}
        if c.real*c.real+c.imag*c.imag < 0.0625 :
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        #  2.  Appartenance à la cardioïde {(1/4,0),1/2(1-cos(theta))}    
        if (c.real > -0.75) and (c.real < 0.5) :
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2,1.E-14)):
                return self.max_iterations
        # Sinon on itère 
        z=0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

# On peut changer les paramètres des deux prochaines lignes
mandelbrot_set = MandelbrotSet(max_iterations=50,escape_radius=10)
width, height = 800, 600

# Répartition des lignes par processus
pcs_height = height // size

scaleX = 3./width
scaleY = 2.25/height
convergence = np.empty((width,pcs_height),dtype=np.double)

# Calcul de l'ensemble de mandelbrot :
deb = time()
range_beg = rank*pcs_height
range_end = (rank+1)*pcs_height

for y in range(range_beg, range_end):
    for x in range(width):
        c = complex(-2. + scaleX*x, -1.125 + scaleY * (y))
        convergence[x,y-range_beg] = mandelbrot_set.convergence(c,smooth=True)
fin = time()
print(f"{rank} - Temps du calcul de l'ensemble de Mandelbrot via répartition uniforme des lignes : {fin-deb}\n shape : {convergence.shape}")

# image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence.T)*255))
# image.show()

total_convergence = None
if rank == 0 : 
    total_convergence = np.empty((size, width, pcs_height),dtype=np.double)

comm.Gather(sendbuf=convergence, recvbuf=total_convergence, root=0)

# Constitution de l'image résultante :
if rank == 0 :
    deb = time()
    image = np.empty((width, height),dtype=np.double)

    # Recreate image as Gather returns garbage
    for i in range(size):
        image[:, i*pcs_height:(i+1)*pcs_height] = total_convergence[i, :, :]
    #ATTENTION : Convergence.T
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(image.T)*255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.show()
