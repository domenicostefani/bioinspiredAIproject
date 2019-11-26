#! /usr/bin/python3

## @package life
#  Module that implements Conway's game of life and bridge with a genetic
#  notation
#
#  Author:  Domenico Stefani
#  Created: 04 nov 2019

import numpy as np
import math
import os

"""genotype mode"""
# GENOTYPE = "cardinal" # vector of cell coordinates
GENOTYPE = "matrix"   # matrix

if GENOTYPE == "cardinal":
    GENOTYPE_SIZE = 10
elif GENOTYPE == "matrix":
    GENOTYPExSIZE = 10
    GENOTYPEySIZE = 10
    PLACEMENT = (10,0)

""" Life iteration number """
max_iterations = 1000

""" Configuration files for c++ core """
CONFIGFILE = "./config/config.txt"
RESULTSFILE = "./result.txt"

# grid size
N = -1
min_bound = -1
max_bound = -1
## Set grid size
def set_grid_size(n):
    assert(n > 0)
    global N
    global min_bound
    global max_bound
    N = n+2
    min_bound = 1
    max_bound = N-1


## Print nicely the grid
#
#  Print in the console the whole grid in a compact way
def display(mgrid):
    for i in range(min_bound,max_bound):
        for j in range(min_bound,max_bound):
            if mgrid[i,j] == False:
                print("░░", end = '')
            else:
                print("██", end = '')
        print("")

def savegrid(grid,filename):
    f = open(filename,"w")
    for i in range(min_bound,max_bound):
        for j in range(min_bound,max_bound):
            f.write(str(int(grid[i,j])))
        f.write("\n")
    f.close


## Traduce genotypic description into an initial configuration for the grid
#
def cardinal_genotype_to_grid(genotype):
    grid = np.zeros((N,N),dtype=bool)
    for i in range(int(genotype.size / 2)):
        gen = genotype.reshape((int(genotype.size / 2),2))[i]
        if gen[0] != -1 and gen[1] != -1:
            grid[gen[0]+1,gen[1]+1] = True

    return grid

def matrix_genotype_to_grid(genotype):
    assert(genotype.shape == (GENOTYPEySIZE,GENOTYPExSIZE))
    assert(PLACEMENT[0] + GENOTYPExSIZE < N-2)
    assert(PLACEMENT[1] + GENOTYPEySIZE < N-2)
    assert(PLACEMENT[0] >= 0)
    assert(PLACEMENT[1] >= 0)
    grid = np.zeros((N,N),dtype=bool)

    grid[PLACEMENT[1]:PLACEMENT[1]+GENOTYPEySIZE,PLACEMENT[0]:PLACEMENT[0]+GENOTYPExSIZE] = genotype

    return grid

def genotype_to_grid(genotype):
    # The genotypic desciption is converted into a correct initial configuration
    # for Life.
    # Cardinal and matrix-form genotypes are treated differently, depending on
    # the chosen modality
    if GENOTYPE == "cardinal":
        automaton = cardinal_genotype_to_grid(genotype)
    elif GENOTYPE == "matrix":
        automaton = matrix_genotype_to_grid(genotype)
    return automaton

def readFileAsMatrix(file):
    with open(file) as f:
        lines = f.read().splitlines()
        matrix = []
        for line in lines:
            row = []
            for value in line.split():
                row.append(float(value.replace(',','.')))
            matrix.append(row)
        return matrix

def compute_fitness(genotype,max_it,target):
    distance = math.inf # inverse of proximity
    size = math.inf # inverse of compactness
    iterations = math.inf # inverse of speed
    reached = False

    automaton = genotype_to_grid(genotype)

    savegrid(automaton,CONFIGFILE)
    command = './lifecore ' + CONFIGFILE + ' ' + str(max_iterations) + ' ' +  str(target[0]) + ' ' + str(target[1]) + ' ' + RESULTSFILE
    output = os.system(command)

    if output is not 0:
        print("ERROR: bad results from c++ core")

    results = readFileAsMatrix(RESULTSFILE)
    distance = results[0][0]
    size = results[1][0]
    iterations = results[2][0]

    print("Distance: " + str(distance))
    print("Size: " + str(size))
    print("Iterations: " + str(iterations))

    return distance,size,iterations

















####### This is testing #######################################################
## try to run life for a number of epochs and return the number of
#  cells that are born and the ones that die
#
#   This includes a few stopping criteria
def automaton_cellscount(genotype):
    automaton = genotype_to_grid(genotype)
    cellsborn = 0
    cellsdead= 0
    previous_previous_automaton = np.zeros(automaton.shape, dtype=bool)
    previous_automaton = np.zeros(automaton.shape, dtype=bool)
    for i in range(max_iterations):
        previous_previous_automaton = previous_automaton
        previous_automaton = automaton
        [automaton,b,d] = update(automaton)
        cellsborn += b
        cellsdead += d

        if stopping(automaton,previous_automaton,previous_previous_automaton,i):
            break
    return [cellsborn,cellsdead]

def stopping(automaton,previous_automaton,previous_previous_automaton,iteration):
    """ Stopping criterion: automaton death """
    if np.sum(automaton.astype(int)) == 0 :
        print("# WARNING: Automata died at iteration " + str(iteration))
        return True
    """ Stopping criterion: static behaviour """
    if(np.array_equal(previous_automaton,automaton)):
        print("# WARNING: Automata became static at iteration " + str(iteration))
        return True
    """ Stopping criterion: repetitive behaviour """
    if(np.array_equal(previous_previous_automaton,automaton)):
        print("# WARNING: Automata became repetitive at iteration " + str(iteration))
        return True

    #
    # TODO: add other stopping criteria if required
    #

    return False


####### This is testing #######################################################
## try to run life for 1000 epochs and return the maximum number of
#  cells obtained in one epoch
def automaton_maxsize(genotype):
    automaton = cardinal_genotype_to_grid(genotype)
    maxsize = np.sum(automaton.astype(int))

    for i in range(max_iterations):
        (automaton,_,_) = update(automaton)
        asize = np.sum(automaton.astype(int))
        if asize > maxsize:
            maxsize = asize
    return maxsize
