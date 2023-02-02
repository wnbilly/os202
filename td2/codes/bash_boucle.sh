#!/bin/bash

for i in $(seq 1 8); 
	do elap=$( mpiexec -n $i python3 mandelbrot.py)
done
