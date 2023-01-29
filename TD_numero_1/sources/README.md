
# TD1

`pandoc -s --toc README.md --css=./github-pandoc.css -o README.html`





## lscpu

```
Architecture :                          x86_64
Mode(s) opératoire(s) des processeurs : 32-bit, 64-bit
Boutisme :                              Little Endian
Address sizes:                          39 bits physical, 48 bits virtual
Processeur(s) :                         8
Liste de processeur(s) en ligne :       0-7
Thread(s) par cœur :                    2
Cœur(s) par socket :                    4
Socket(s) :                             1
Nœud(s) NUMA :                          1


Nom de modèle :                         Intel(R) Core(TM) i5-9300H CPU @ 2.40GHz

Vitesse du processeur en MHz :          2400.000
Vitesse maximale du processeur en MHz : 4100,0000
Vitesse minimale du processeur en MHz : 800,0000

Cache L1d :                             128 KiB
Cache L1i :                             128 KiB
Cache L2 :                              1 MiB
Cache L3 :                              8 MiB
Nœud NUMA 0 de processeur(s) :          0-7

```

*Des infos utiles s'y trouvent : nb core, taille de cache*



## Produit matrice-matrice



### Permutation des boucles

*Expliquer comment est compilé le code (ligne de make ou de gcc) : on aura besoin de savoir l'optim, les paramètres, etc.

`g++ -o TestProduct.exe -O2 TestProductMatrix.cpp ProdMatMat.cpp Matrix.cpp`


Q1. 

n   |  time   | MFlops  |
----|---------|---------|
1023| 1.28021 | 1672.53 |
1024| 2.38371 | 900.901 |
1025| 1.28071 | 1681.7  |


  ordre           | time    | MFlops (n=1024) | MFlops(n=2048) 
------------------|---------|-----------------|----------------
i,j,k (origine)   | 2.38371 |     900.901     |    197.899
j,i,k             | 2.61509 |     821.19      |    177.277
i,k,j             | 12.8625 |     166.956     |    38.6809
k,i,j             | 12.1458 |     176.808     |    57.3487
j,k,i             | 0.68483 |     3135.79     |    2604.57
k,j,i             | 0.75663 |     2838.2      |    1772.93


*Discussion des résultats*

j,k,i meilleure boucle


### OMP sur la meilleure boucle 

`make TestProduct.exe && OMP_NUM_THREADS=8 ./TestProduct.exe 1024`

```sh
#!/bin/bash

for omp_num in {1..8}
do
	export OMP_NUM_THREADS=$omp_num
	echo "Nombre de threads : $OMP_NUM_THREADS"
	for n in 1024 2048 512 4096
	do
		echo "n = $n"
		./TestProduct.exe $n
	done
done
```
avec "pragma omp parallel for sur les 3 boucles
  OMP_NUM   | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------|---------|----------------|----------------|---------------
1           |  1111   | 1479           | 693            | 1897
2           |  1899   | 2691           | 1350           | 3309
3           |  3018   | 4096           | 1905           | 4564
4           |  3612   | 4991           | 2356           | 5716 
5           |  3248   | 4420           | 1876           | 4884
6           |  3485   | 4986           | 2107           | 5207
7           |  3493   | 4761           | 2061           | 6036
8           |  3856   | 5337           | 2375           | 5969

avec "pragma omp parallel for sur la 1e boucle
  OMP_NUM   | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096) |
------------|---------|----------------|----------------|----------------|
1           |  3195   | 2851           | 2914           | 2769           |
2           |  5888   | 5334           | 5558           | 4901           |
3           |  7611   | 7210           | 6967           | 6369           |
4           |  7444   | 7502           | 7601           | 7358           |
5           |  7320   | 7316           | 8154           | 6326           |
6           |  9175   | 6563           | 8789           | 6085           |
7           |  9864   | 8524           | 7797           | 7579           |
8           |  9018   | 9832           | 5903           | 7339           |


  SANS OMP  | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------|---------|----------------|----------------|---------------
 sans omp   |  3157   | 2897           | 3384           | 2748
 
Cela permet de calculer le speedup
 
  OMP_NUM   | speedup | speedup(n=2048) | speedup(n=512) | speedup(n=4096)| speedup moyen |
------------|---------|-----------------|----------------|----------------|---------------|
1           |  1.01   | 0.98            | 0.86           | 1              | 0.96          |
2           |  1.87   | 1.84            | 1.64           | 1.78           | 1.78          |
3           |  2.41   | 2.49            | 2.06           | 2.32           | 2.32          |
4           |  2.36   | 2.59            | 2.25           | 2.68           | 2.47          |
5           |  2.32   | 2.53            | 2.41           | 2.30           | 2.39          |
6           |  2.91   | 2.27            | 2.60           | 2.21           | 2.50          |
7           |  3.12   | 2.94            | 2.30           | 2.76           | 2.78          |
8           |  2.86   | 3.40            | 1.74           | 2.67           | 2.67          |



### Produit par blocs

`make TestProduct.exe && ./TestProduct.exe 1024`

Les prochaines mesures sont sans OMP

  szBlock         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
origine(=max)     |  3157   | 2897           | 3384           | 2748
32                |  2336   | 2351           | 2410           | 1919
64                |  2523   | 2535           | 2560           | 2148
128               |  2714   | 2654           | 2641           | 2458
256               |  2820   | 2822           | 2742           | 2524
512               |  2994   | 2764           | 2887           | 2460
1024              |  2644   | 2416           | 2835           | 2269




### Bloc + OMP

#pragma omp parallel for avant la boucle principale dans prodSubblocks et pas dans operator*

  szBlock      | OMP_NUM | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)|
---------------|---------|---------|----------------|----------------|---------------|
A.nbCols       |  1      | 9501    | 9502           | 5910           | 8342          |
512            |  8      | 11102   | 10701          | 7848           | 11510         |
---------------|---------|---------|----------------|----------------|---------------|
Speed-up       |         | 1.17    | 1.13           | 1.33           | 1.38          |
---------------|---------|---------|----------------|----------------|---------------|



### Comparaison with BLAS

  BLAS  | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
--------|---------|----------------|----------------|---------------
  blas  |  14580  | 15298          | 8985           | 15571

Le produit en utilisant blas est beaucoup plus rapide.

# Tips 

```
	env 
	OMP_NUM_THREADS=4 ./produitMatriceMatrice.exe
```

```
    $ for i in $(seq 1 4); do elap=$(OMP_NUM_THREADS=$i ./TestProductOmp.exe|grep "Temps CPU"|cut -d " " -f 7); echo -e "$i\t$elap"; done > timers.out
```
