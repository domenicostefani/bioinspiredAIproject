import numpy as np

N = -1;

def set_grid_size(n):
    global N
    N = n

def display(mgrid):
    for i in range(N):
        for j in range(N):
            if mgrid[i,j] == False:
                print("  ", end = '')
            else:
                print("█ ", end = '')
        print("");

def evolve(grid):
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


def genotype_to_grid(genotype):
    grid = np.zeros((N,N),dtype=bool);
    for i in range(int(genotype.size / 2)):
        gen = genotype.reshape((int(genotype.size / 2),2))[i]
        if gen[0] != -1 and gen[1] != -1:
            grid[gen[0],gen[1]] = True
    return grid


def automata_maxsize(genotype):
    automata = genotype_to_grid(genotype)
    maxsize = np.sum(automata.astype(int))

    for i in range(1000):
        (automata,_,_) = evolve(automata)
        asize = np.sum(automata.astype(int))
        if asize > maxsize:
            maxsize = asize
    return maxsize

def automata_cellscount(genotype):
    automata = genotype_to_grid(genotype)
    cellsborn = 0
    cellsdead= 0
    previous_previous_automata = np.zeros(automata.shape, dtype=bool)
    previous_automata = np.zeros(automata.shape, dtype=bool)
    for i in range(8):
        previous_previous_automata = previous_automata
        previous_automata = automata
        [automata,b,d] = evolve(automata)
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
