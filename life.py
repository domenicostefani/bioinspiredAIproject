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
import copy

VERBOSE = False

"""genotype mode"""
# GENOTYPE = "cartesian" # vector of cell coordinates
GENOTYPE = "matrix"   # boolean matrix representing a correct grid

if GENOTYPE == "cartesian":
    GENOTYPE_SIZE = 10
elif GENOTYPE == "matrix":
    GENOTYPExSIZE = 10
    GENOTYPEySIZE = 10
    PLACEMENT = (10,10)

""" Configuration files for c++ core """
CONFIGFILE = "./config/config.txt"
RESULTSFILE = "./result.txt"
BESTRESULTSFILE = "./bestresult.txt"
ANIMATION_FOLDER = "./animation/"

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

## Print nicely the genotype only
#
#  Print in the console the genoptype in a compact way
def display_genotype(genotype):
    genotype = np.reshape(genotype,(GENOTYPEySIZE,GENOTYPExSIZE))
    for i in range(GENOTYPEySIZE):
        for j in range(GENOTYPExSIZE):
            if genotype[i,j] == False:
                print("░░", end = '')
            else:
                print("██", end = '')
        print("")

def savegrid(grid,filename):
    directory,_ = os.path.split(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    f = open(filename,"w")
    for i in range(min_bound,max_bound):
        for j in range(min_bound,max_bound):
            f.write(str(int(grid[i,j])))
        f.write("\n")
    f.close

def get_random_genotype():
    if GENOTYPE == "cartesian":
        print("ERROR: Function not yet implemented!")
        exit(-1)
    elif GENOTYPE == "matrix":
        return (np.random.rand(GENOTYPEySIZE,GENOTYPExSIZE) > 0.5)


## Traduce genotypic description into an initial configuration for the grid
#
def cartesian_genotype_to_grid(genotype):
    grid = np.zeros((N,N),dtype=bool)
    for i in range(int(genotype.size / 2)):
        gen = genotype.reshape((int(genotype.size / 2),2))[i]
        if gen[0] != -1 and gen[1] != -1:
            grid[gen[0]+1,gen[1]+1] = True

    return grid

def matrix_genotype_to_grid(genotype):
    assert(genotype.shape == (GENOTYPEySIZE*GENOTYPExSIZE,))
    assert(PLACEMENT[0] + GENOTYPExSIZE < N-2)
    assert(PLACEMENT[1] + GENOTYPEySIZE < N-2)
    assert(PLACEMENT[0] >= 0)
    assert(PLACEMENT[1] >= 0)
    grid = np.zeros((N,N),dtype=bool)

    genotype = np.reshape(genotype,(GENOTYPEySIZE,GENOTYPExSIZE)) #from flat to matrix
    grid[PLACEMENT[1]:PLACEMENT[1]+GENOTYPEySIZE,PLACEMENT[0]:PLACEMENT[0]+GENOTYPExSIZE] = genotype

    return grid

def genotype_to_grid(genotype):
    # The genotypic desciption is converted into a correct initial configuration
    # for Life.
    # cartesian and matrix-form genotypes are treated differently, depending on
    # the chosen modality
    if GENOTYPE == "cartesian":
        automaton = cartesian_genotype_to_grid(genotype)
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
    final_size = math.inf # inverse of compactness
    max_size = math.inf
    avg_size = math.inf
    iterations = math.inf # inverse of speed
    reached = False

    automaton = genotype_to_grid(genotype)

    savegrid(automaton,CONFIGFILE)
    command = './lifecore ' + CONFIGFILE + ' ' + str(max_it) + ' ' +  str(target[0]) + ' ' + str(target[1]) + ' ' + RESULTSFILE
    output = os.system(command)

    if output is not 0:
        print("ERROR: bad results from c++ core")

    results = readFileAsMatrix(RESULTSFILE)
    ## Content:
    # 0 - Final distance
    # 1 - Final size
    # 2 - iterations
    # 3 - MAXIMUM size (across all iterations)
    # 4 - AVERAGE size (across all iterations)
    # 5 - MINIMUM distance from target (across all iterations)

    final_distance = results[0][0]
    final_size = results[1][0]
    if (final_distance == 0):
        iterations = results[2][0]
    else:
        iterations = max_it
    max_size = results[3][0]
    avg_size = results[4][0]
    min_distance = results[5][0]
    os.remove(RESULTSFILE)

    if VERBOSE:
        print("Final Distance: " + str(final_distance))
        print("Minimum Distance: " + str(min_distance))
        print("Final Size: " + str(final_size))
        print("Max Size: " + str(max_size))
        print("Avg Size: " + str(avg_size))
        print("Iterations: " + str(iterations))
        print("")

    return (final_distance,min_distance),(final_size,max_size,avg_size),iterations

def create_animation(genotype,max_it,target):
    os.system(ANIMATION_FOLDER + "clean.sh")

    automaton = genotype_to_grid(genotype)
    savegrid(automaton,CONFIGFILE)
    command = './displaycore ' + CONFIGFILE + ' ' + str(max_it) + ' ' +  str(target[0]) + ' ' + str(target[1]) + ' ' + BESTRESULTSFILE + ' ' + ANIMATION_FOLDER
    print(command)
    output = os.system(command)

    if output is not 0:
        print("ERROR: bad results from DISPLAY core")

    results = readFileAsMatrix(BESTRESULTSFILE)
    final_distance = results[0][0]
    final_size = results[1][0]
    iterations = results[2][0]
    print("# Best individual Performance #")
    print("final_distance: " + str(final_distance))
    print("final_size: " + str(final_size))
    print("iterations: " + str(iterations))


## Life-iteration for matrix genotype
#
#  Perform one update or iteration of LIFE on the sole genotype matrix
#  This can be used as a custom mutation operator
def lifeiteration(in_genotype):
    in_genotype = np.reshape(in_genotype,(GENOTYPEySIZE,GENOTYPExSIZE))
    genotype = copy.copy(in_genotype)

    # Create 1 cell padding around the genotype
    padded_genotype = np.zeros((GENOTYPEySIZE+2,GENOTYPEySIZE+2),dtype=bool)
    padded_genotype[1:1+GENOTYPEySIZE,1:1+GENOTYPExSIZE] = genotype

    for i in range(1, GENOTYPEySIZE+1):
        for j in range(1, GENOTYPExSIZE+1):
            total = int(padded_genotype[i,j-1]) + int(padded_genotype[i,j+1]) +                    int(padded_genotype[i-1,j]) + int(padded_genotype[i+1,j]) + int(padded_genotype[i-1,j-1]) + int(padded_genotype[i-1,j+1]) + int(padded_genotype[i+1,j-1]) + int(padded_genotype[i+1,j+1])

            if(padded_genotype[i,j] == True):
                if(total >= 2 and total <= 3):
                    genotype[i-1,j-1] = True
                    # using -1 because @genotype is not padded
                else:
                    genotype[i-1,j-1] = False
                    # using -1 because @genotype is not padded
            else:
                if (total == 3):
                    genotype[i-1,j-1] = True
                    # using -1 because @genotype is not padded
                else:
                    genotype[i-1,j-1] = False
                    # using -1 because @genotype is not padded

    return genotype.flatten()
