#! /usr/bin/python3

#  Main test module to verify feasibility of the application of genetic
#  computation and evolutionary algorithms to Conway's game of life
#
#  Author:  Domenico Stefani
#  Created: 04 nov 2019

import numpy as np
import os
import life

MAX_ITERATIONS = 1000
TARGET = (-4,-4)


# Grid size
N = 20
# Genotypes
glider = np.array([1,4,
                     2,5,
                     3,3,
                     3,4,
                     3,5,
                     -1,-1,
                     -1,-1,
                     -1,-1,
                     -1,-1,
                     -1,-1,
                     -1,-1,
                     -1,-1])
line3 = np.array([4,4,
                  4,5,
                  4,6,
                  -1,-1,
                  -1,-1,
                  -1,-1,
                  -1,-1,
                  -1,-1,
                  -1,-1,
                  -1,-1,
                  -1,-1,
                  -1,-1])
dot = np.array([4,4,
                -1,-1,
                -1,-1,
               -1,-1,
               -1,-1,
               -1,-1,
               -1,-1,
               -1,-1,
               -1,-1,
               -1,-1,
               -1,-1,
               -1,-1])

#Set the genotype
genotype = glider
# genotype = glider
#set grid size
life.set_grid_size(N)

"""
 * Run life and evaluate maximum automata size
"""
# print("Max size is " + str(automata_maxsize(genotype)))

"""
 * Run life and evaluate of the number of cells that are born and die
"""
life.display(life.genotype_to_grid(genotype))
distance, size, iterations = life.compute_fitness(genotype,MAX_ITERATIONS,TARGET)