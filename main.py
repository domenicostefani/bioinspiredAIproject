#! /usr/bin/python3

#  Main test module to verify feasibility of the application of genetic
#  computation and evolutionary algorithms to Conway's game of life
#
#  Author:  Domenico Stefani
#  Created: 04 nov 2019

import numpy as np
import os
import life

# Grid size
N = 100
# Genotypes
glider = np.zeros(25)

#set grid size
life.set_grid_size(N)

"""
 * Run life and evaluate maximum automata size
"""
# print("Max size is " + str(automata_maxsize(genotype)))

"""
 * Run life and evaluate of the number of cells that are born and die
"""
life.display(life.genotype_to_grid(glider))
[cb,cd] = life.automata_cellscount(genotype)
print("cellsborn: " + str(cb))
print("cellsdead: " + str(cd))
