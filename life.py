#! /usr/bin/python3

## @package life
#  Module that implements Conway's game of life and bridge with a genetic
#  notation
#
#  Author:  Domenico Stefani
#  Created: 04 nov 2019

import numpy as np
import math
import timeit

"""genotype mode"""
# GENOTYPE = "cardinal" # vector of cell coordinates
GENOTYPE = "matrix"   # matrix

if GENOTYPE == "cardinal":
    GENOTYPE_SIZE = 10
elif GENOTYPE == "matrix":
    GENOTYPExSIZE = 10
    GENOTYPEySIZE = 10
    PLACEMENT = (10,0)

"""distance rules"""
# DISTANCE = "euclidean"
DISTANCE = "chebyshev"

"""toroidal rules"""
TOROIDAL = False

""" Life iteration number """
max_iterations = 1000


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
    if TOROIDAL:
        N = n
        min_bound = 0
        max_bound = N-1
    else:
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

## Update the grid by applying life rules
#
#  TODO: change function name?
#  TODO: remove toroidal rules that wrap the grig around and allows cells to go
#        out from a side and come back in on the other side
def update(grid):
    grid = grid.astype(int)
    mask = np.zeros((N,N), dtype=bool)
    for i in range(min_bound,max_bound):
        for j in range(min_bound,max_bound):
            if TOROIDAL:
                # toroidal boundary conditions
                total = int(grid[i, (j-1)%N] + grid[i, (j+1)%N] +
                            grid[(i-1)%N, j] + grid[(i+1)%N, j] +
                            grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+1)%N] +
                            grid[(i+1)%N, (j-1)%N] + grid[(i+1)%N, (j+1)%N])
            else:
                grid[:,0] = 0
                grid[:,max_bound] = 0
                grid[0,:] = 0
                grid[max_bound,:] = 0
                total = int(grid[i, (j-1)] + grid[i, (j+1)] +
                            grid[(i-1), j] + grid[(i+1), j] +
                            grid[(i-1), (j-1)] + grid[(i-1), (j+1)] +
                            grid[(i+1), (j-1)] + grid[(i+1), (j+1)])
            # apply Conway's rules
            if grid[i, j]  == True:
                if (total < 2) or (total > 3):
                    mask[i,j] = True
            else:
                if total == 3:
                    mask[i,j] = True
    return np.logical_xor(grid,mask)

## Traduce genotypic description into an initial configuration for the grid
#
def cardinal_genotype_to_grid(genotype):
    grid = np.zeros((N,N),dtype=bool)
    for i in range(int(genotype.size / 2)):
        gen = genotype.reshape((int(genotype.size / 2),2))[i]
        if gen[0] != -1 and gen[1] != -1:
            if TOROIDAL:
                grid[gen[0],gen[1]] = True
            else:
                grid[gen[0]+1,gen[1]+1] = True

    return grid

def matrix_genotype_to_grid(genotype):
    assert(genotype.shape == (GENOTYPEySIZE,GENOTYPExSIZE))
    assert((not TOROIDAL) or (PLACEMENT[0] + GENOTYPEySIZE < N))
    assert((not TOROIDAL) or (PLACEMENT[1] + GENOTYPExSIZE < N))
    assert((TOROIDAL) or (PLACEMENT[0] + GENOTYPEySIZE < N-2))
    assert((TOROIDAL) or (PLACEMENT[1] + GENOTYPExSIZE < N-2))
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

def bounds(automaton):
    min_max_i = [N,0]
    min_max_j = [N,0]
    for i in range(min_bound,max_bound):
        for j in range(min_bound,max_bound):
            if automaton[i, j] == True:
                if i < min_max_i[0]:
                    min_max_i[0] = i
                elif i > min_max_i[1]:
                    min_max_i[1] = i

                if j < min_max_j[0]:
                    min_max_j[0] = j
                elif j > min_max_j[1]:
                    min_max_j[1] = j
    return (min_max_i, min_max_j)

def center_of_mass(bounds):
    (min_max_i,min_max_j) = bounds
    print("Automaton has bounds (x = " + str(min_max_j[0]) + ", " + str(min_max_j[1]) + ")")
    print("(y) = " + str(min_max_i[0]) + ", " + str(min_max_i[1]) + ")")
    xc = int((min_max_j[1] + min_max_j[0]) / 2)
    yc = int((min_max_i[1] + min_max_i[0]) / 2)

    print("Center is " + str(xc) + ", " + str(yc))

    return xc, yc

def automatonsize(bounds):
    (min_max_i,min_max_j) = bounds

    return (min_max_i[1] - min_max_i[0] + 1) * (min_max_j[1] - min_max_j[0] + 1)

def compute_fitness(genotype,max_it,target):
    start = timeit.default_timer() #REMOVE TODO
    distance = math.inf # inverse of proximity
    size = math.inf # inverse of compactness
    iterations = math.inf # inverse of speed
    reached = False

    automaton = genotype_to_grid(genotype)

    xt = target[0]
    yt = target[1]

    previous_previous_automaton = np.zeros(automaton.shape, dtype=bool)
    previous_automaton = np.zeros(automaton.shape, dtype=bool)
    for i in range(max_it):

        previous_previous_automaton = previous_automaton
        previous_automaton = automaton

        iterations = i
        automaton = update(automaton)

        # ### Stopping
        # # 1. Target reached
        # if automaton[xt,yt] == True:
        #     print("# Stopping: Target reached\n")
        #     reached = True
        #     break
        #
        # # 2. Death
        # if np.sum(automaton.astype(int)) == 0 :
        #     print("# Stopping: Automata died at iteration " + str(i))
        #     break
        # # 3. Static behaviour
        # if(np.array_equal(previous_automaton,automaton)):
        #     print("# Stopping: Automata became static at iteration " + str(i))
        #     break
        # # 4. Repetitive behaviour
        # if(np.array_equal(previous_previous_automaton,automaton)):
        #     print("# Stopping: Automata became repetitive at iteration " + str(i))
        #     break


    stop = timeit.default_timer()
    print('Time: ', stop - start)

    # display(automaton)
    #
    # """ Simulation finished, evaluate results """
    # boundaries = bounds(automaton)
    #
    # # distance
    # if reached:
    #     distance = 0
    # else:
    #     xc,yc = center_of_mass(boundaries)
    #     if DISTANCE == "euclidean":
    #         distance = ((xc - xt)**2) + ((yc - yt)**2)
    #     elif DISTANCE == "chebyshev":
    #         distance = max(abs(xc - xt),abs(yc - yt))
    #
    # # size
    # size = automatonsize(boundaries)
    #
    # # iterations
    # iterations += 1
    #
    # print("Distance: " + str(distance))
    # print("Size: " + str(size))
    # print("Iterations: " + str(iterations))


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
