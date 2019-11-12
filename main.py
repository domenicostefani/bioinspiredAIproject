import numpy as np
import os
import life

# Grid
N = 10
# Genotype
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

genotype = line3
life.set_grid_size(N)

"""
 * Maximum automata size computation
"""
# print("Max size is " + str(automata_maxsize(genotype)))

"""
 * Computation of the number of cells that are born and die during life
"""
life.display(life.genotype_to_grid(genotype))
[cb,cd] = life.automata_cellscount(genotype)
print("cellsborn: " + str(cb))
print("cellsdead: " + str(cd))
