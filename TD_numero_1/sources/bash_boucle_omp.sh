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
