
# Rendu TD1


## -lscpu

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



## Ex 1 - Produit matrice-matrice



### Permutation des boucles

Ma ligne de commande de compilatio nest la suivante :

`g++ -o TestProduct.exe -O2 TestProductMatrix.cpp ProdMatMat.cpp Matrix.cpp`


### Mesure du temps de calcul pour n=1024

n   |  time   | MFlops  |
----|---------|---------|
1023| 1.28021 | 1672.53 |
1024| 2.38371 | 900.901 |
1025| 1.28071 | 1681.7  |


### Première optimisation par permutation de boucles

  ordre           | time    | MFlops (n=1024) | MFlops(n=2048) 
------------------|---------|-----------------|----------------
i,j,k (origine)   | 2.38371 |     900.901     |    197.899
j,i,k             | 2.61509 |     821.19      |    177.277
i,k,j             | 12.8625 |     166.956     |    38.6809
k,i,j             | 12.1458 |     176.808     |    57.3487
j,k,i             | 0.68483 |     3135.79     |    2604.57
k,j,i             | 0.75663 |     2838.2      |    1772.93



On trouve que j,k,i est le meilleur ordre pour les boucles talonnée de près par k,j,i. Cela est logique car la mémoire est chargée en cache de façon contigüe et que C++ stocke les matrices suivant les lignes. 
Ainsi, avoir i en dernière boucle permet d'itérer sur plusieurs valeurs de suite dans les lignes de A (car i est la valeur d'itération sur les lignes de A) sans avoir à charger de la mémoire en cache en provenance de la mémoire ram.


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

avec "pragma omp parallel for sur les 3 boucles, ce qui s'est révélé inefficace, probablement car tous les processus ont un même modèle d'accès mémoire, ce qui rend la parallélisation peu efficace.
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

avec "pragma omp parallel for sur la 1e boucle uniquement
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
 
Ce dernier tableau permet de calculer le speedup.
 
OMP_NUM_THREADS  | speedup | speedup(n=2048) | speedup(n=512) | speedup(n=4096)| speedup moyen |
-----------------|---------|-----------------|----------------|----------------|---------------|
1                |  1.01   | 0.98            | 0.86           | 1              | 0.96          |
2                |  1.87   | 1.84            | 1.64           | 1.78           | 1.78          |
3                |  2.41   | 2.49            | 2.06           | 2.32           | 2.32          |
4                |  2.36   | 2.59            | 2.25           | 2.68           | 2.47          |
5                |  2.32   | 2.53            | 2.41           | 2.30           | 2.39          |
6                |  2.91   | 2.27            | 2.60           | 2.21           | 2.50          |
7                |  3.12   | 2.94            | 2.30           | 2.76           | 2.78          |
8                |  2.86   | 3.40            | 1.74           | 2.67           | 2.67          |

On remarque que globalement plus on augmente le nombre de threads alloués à cette tâche, plus les performances augmentent. Cela n'est plus vrai après OMP_NUM_THREADs = 7 probablement car d'autres programmes tournent déjà en parallèle sur le PC et nécessitent également du temps d'exécution.

De plus, entre OMP_NUM_THREADS=1 et OMP_NUM_THREADS=X, on ne remarque pas un speedup de X car la multiplication de matrices requiert beaucoup d'appel à la mémoire hors cache. Ceci est cohérent vaec la loi d'Amdahl.

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


Je pense devoir observer une amélioration en utilisant le produit par blocs mais la version la plus efficace dans mon cas est la version scalaire.

Cependant, je pense que l'optimum devrait se trouver lorsque le cache (à déterminer lequel) peut tenir entièrement une ligne de A.


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


# 2 - Parallélisation MPI

## 2.1 - Circulation d'un jeton

*cf. ex21.py*


## 2.2 - Calcul très approché de pi

*cf. ex22.py et ex22_mpi.py*

Pour ex22.py et ex22_mpi.py, il faut préciser le nombre de points en argument lors du lancement dans la ligne de commande.

J'obtenais de meilleurs résultats en utilisant une parallélisation via 4 processus.

Ma commande d'exécution était donc `mpiexec -n 4 python3 ex22_mpi.py 10000`

Voici les résultats obtenus en temps d'exécution en secondes en fonction du nombre de points :

  MPI    |    10⁴    |    10⁵    |    10⁶    |    10⁷    |
---------|-----------|-----------|-----------|-----------|
  Non    |  0.0135   |  0.1346   | 1.3036    | 12.901    |
  Oui    |  0.0276   |  0.0341   | 0.3600    | 3.6992    |
 Speedup |  0.49     |  3.95     | 3.62      | 3.43
  
 
 
On remarque déjà que le temps d'exécution semble linéaire par rapport au nombre de points, ce qui est cohérent avec la structure de boucles simples du code dans le cas sans mpi.

Hormis pour le cas avec 10⁴ points, on trouve un speed up s'approchant de 4, ce qui est cohérent car j'ai utilisé 4 threads pour réaliser le calcul avec MPI contre 1 sans MPI. Le speedup n'est pas de 4 car d'autres programmes tournent sur mon PC et requièrent du temps de calcul.

