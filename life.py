#! /usr/bin/python3

## @package life
#  Module that implements Conway's game of life and bridge with a genetic
#  notation
#
#  Author:  Domenico Stefani
#  Created: 04 nov 2019

import numpy as np

# grid size #TODO: change name
N = -1;

## Set grid size
#
def set_grid_size(n):
    global N
    N = n

## Print nicely the grid
#
#  Print in the console the whole grid in a compact way
def display(mgrid):
    for i in range(N):
        for j in range(N):
            if mgrid[i,j] == False:
                print("  ", end = '')
            else:
                print("█ ", end = '')
        print("");

## Update the grid by applying life rules
#
#  TODO: change function name?
#  TODO: remove toroidal rules that wrap the grig around and allows cells to go
#        out from a side and come back in on the other side
def update(grid):
    cellsborn = 0
    cellsdead = 0
    grid = grid.astype(int)
    mask = np.zeros((N,N), dtype=bool)
    for i in range(N):
        for j in range(N):
            # toroidal boundary conditions
            total = int(grid[i, (j-1)%N] + grid[i, (j+1)%N] +
                        grid[(i-1)%N, j] + grid[(i+1)%N, j] +
                        grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+1)%N] +
                        grid[(i+1)%N, (j-1)%N] + grid[(i+1)%N, (j+1)%N])
            # apply Conway's rules
            if grid[i, j]  == True:
                if (total < 2) or (total > 3):
                    mask[i,j] = True
                    cellsdead += 1
            else:
                if total == 3:
                    mask[i,j] = True
                    cellsborn += 1
    return (np.logical_xor(grid,mask),cellsborn,cellsdead)

## Traduce genotypic description into an initial configuration for the grid
#
def genotype_to_grid(genotype):
    grid = np.zeros((N,N),dtype=bool);
    for i in range(int(genotype.size / 2)):
        gen = genotype.reshape((int(genotype.size / 2),2))[i]
        if gen[0] != -1 and gen[1] != -1:
            grid[gen[0],gen[1]] = True
    return grid

####### This is testing #######################################################
## try to run life for 1000 epochs and return the maximum number of
#  cells obtained in one epoch
def automata_maxsize(genotype):
    automata = genotype_to_grid(genotype)
    maxsize = np.sum(automata.astype(int))

    for i in range(1000):
        (automata,_,_) = update(automata)
        asize = np.sum(automata.astype(int))
        if asize > maxsize:
            maxsize = asize
    return maxsize


####### This is testing #######################################################
## try to run life for a number of epochs and return the number of
#  cells that are born and the ones that die
#
#   This includes a few stopping criteria
def automata_cellscount(genotype):
    automata = genotype_to_grid(genotype)
    cellsborn = 0
    cellsdead= 0
    previous_previous_automata = np.zeros(automata.shape, dtype=bool)
    previous_automata = np.zeros(automata.shape, dtype=bool)
    for i in range(8):
        previous_previous_automata = previous_automata
        previous_automata = automata
        [automata,b,d] = update(automata)
        cellsborn += b
        cellsdead += d
        """ Stopping criterion: automata death """
        if np.sum(automata.astype(int)) == 0 :
            print("# WARNING: Automata died at generation " + str(i))
            break
        """ Stopping criterion: static behaviour """
        if(np.array_equal(previous_automata,automata)):
            print("# WARNING: Automata became static at generation " + str(i))
            break
        """ Stopping criterion: repetitive behaviour """
        if(np.array_equal(previous_previous_automata,automata)):
            print("# WARNING: Automata became repetitive at generation " + str(i))
            break


    return [cellsborn,cellsdead]
