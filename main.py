#! /usr/bin/python3

#  Main test module to verify feasibility of the application of genetic
#  computation and evolutionary algorithms to Conway's game of life
#
#  Author:  Domenico Stefani
#  Created: 04 nov 2019

from pylab import *
from random import Random
import inspyred
import sys
import numpy as np
import os
import life
from inspyred import ec
import copy

"""--Parameters for LIFE..---------------------------------------------------"""

""" Life iteration number """
MAX_ITERATIONS = 1000
""" Life grid size        """
N = 40
""" Life target cell      """
TARGET = (N-4,N-4)

"""--Parameters for the EC---------------------------------------------------"""

populationSize = 50
numberOfGenerations = 500
numberOfEvaluations = 2500                    # used with evaluation_termination
tournamentSize = 3
mutationRate = 0.2
gaussianMean = 0
gaussianStdev = 10.0
crossoverRate = 0.95
numCrossoverPoints =  5
selectionSize = populationSize
numElites = 2

"""--Visualization-----------------------------------------------------------"""
display = True
SHOW_BEFOREAFTER_LIFEFLIP = False
SHOW_BEFOREAFTER_RESETRANDOM = False
"""--------------------------------------------------------------------------"""

# this object is used for single-thread evaluations (only pickleable objects can be used in multi-thread)
class AutomatonEvaluator():
    def __init__(self,seed):
        self.seed = seed                # seed for random generator
        # self.bounder = ec.Bounder(0, 1) # Discrete bounder to boolean values
        self.bounder = ec.DiscreteBounder([0,1]) # Discrete bounder to boolean values
        self.maximize = False           # Flag to define the problem nature
        self.genCount = 0               # generation count

    ## Generator method
    #  This generates new individuals
    def generator(self, random, args):
        newgen = life.get_random_genotype()
        return np.reshape(newgen,-1)

    ## Evaluator method
    #  This evaluates the fitness of the given individual/s (@candidates)
    def evaluator(self, candidates, args):
        fitness = []
        for candidate in candidates:
            """
            # TODO: Here we can computate also the INITIAL size and use it
              in the fitness formulation.
              Also the number of alive cells, maybe it's better cause on a
              small matrix size does not vary much
            """
            distances,sizes,iterations = life.compute_fitness(candidate,
                                                              MAX_ITERATIONS,
                                                              TARGET)

            (final_distance,min_distance) = distances
            (final_size,max_size,avg_size) = sizes



            """-----------Fitness formulation--------------------------------"""
            """
               Metrics that can be used
                - final_distance
                - min_distance
                - final_size
                - max_size
                - avg_size
                - iterations
            """
            if(final_distance != 0):
                iterations = 1000
                max_size = 1600
            # else:
            #     print("iterations: " + str(iterations))
            #     print("max_size  : " + str(max_size))

            fitness_c  = (1 * min_distance) + (1 * iterations) + (10 * max_size)
            """--------------------------------------------------------------"""

            fitness.append(fitness_c)
        self.genCount += 1
        return fitness


'''
            custom CROSSOVER operators
    Following functions implements custom crossover operators based on logic
    operations.
    In this application of EC, the setting is known and injecting information
    through custom operators should be beneficial for the search.

    The included set operators between automata are:
     - union         (logical disjunction, OR)
     - intersection  (logical conjunction, AND)
     - subtraction   (relative complement, Both A\B and B\A)
     - xor
'''
def UNIONcrossover(random, mom, dad, args):
    """Return the union (logical disjunction) of the candidates.

    ░░░░░░░░░░     ░░░░░░░░░░     ░░░░░░░░░░
    ░░██████░░     ░░██░░░░░░     ░░██████░░
    ░░░░░░██░░ OR  ░░██░░░░░░  =  ░░██░░██░░
    ░░░░██░░░░     ░░██░░██░░     ░░██████░░
    ░░░░░░░░░░     ░░░░░░░░░░     ░░░░░░░░░░

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)

    """
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    children = []
    if random.random() < crossover_rate:
        son = np.logical_or(dad,mom)
        children.append(son)
    else:
        children.append(mom)
        children.append(dad)
    return children

def INTERcrossover(random, mom, dad, args):
    """Return the intersection (logical conjunction) of the candidates.

    ░░░░░░░░░░     ░░░░░░░░░░     ░░░░░░░░░░
    ░░██████░░     ░░██░░░░░░     ░░██░░░░░░
    ░░░░░░██░░ AND ░░██░░░░░░  =  ░░░░░░░░░░
    ░░░░██░░░░     ░░██░░██░░     ░░░░░░░░░░
    ░░░░░░░░░░     ░░░░░░░░░░     ░░░░░░░░░░

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)

    """
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    children = []
    if random.random() < crossover_rate:
        son = np.logical_and(dad,mom)
        children.append(son)
    else:
        children.append(mom)
        children.append(dad)
    return children

def XORcrossover(random, mom, dad, args):
    """Return the boolean XOR of the candidates.

    ░░░░░░░░░░     ░░░░░░░░░░     ░░░░░░░░░░
    ░░██████░░     ░░██░░░░░░     ░░░░████░░
    ░░░░░░██░░ XOR ░░██░░░░░░  =  ░░██░░██░░
    ░░░░██░░░░     ░░██░░██░░     ░░██████░░
    ░░░░░░░░░░     ░░░░░░░░░░     ░░░░░░░░░░

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)

    """
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    children = []
    if random.random() < crossover_rate:
        son = np.logical_xor(dad,mom)
        children.append(son)
    else:
        children.append(mom)
        children.append(dad)
    return children

def SUBcrossover(random, mom, dad, args):
    """Return the two set subtractions of the candidates.

    ░░░░░░░░░░     ░░░░░░░░░░     ░░░░░░░░░░
    ░░██████░░     ░░██░░░░░░     ░░░░████░░
    ░░░░░░██░░  \  ░░██░░░░░░  =  ░░░░░░██░░
    ░░░░██░░░░     ░░██░░██░░     ░░░░██░░░░
    ░░░░░░░░░░     ░░░░░░░░░░     ░░░░░░░░░░

    ░░░░░░░░░░     ░░░░░░░░░░     ░░░░░░░░░░
    ░░██░░░░░░     ░░██████░░     ░░░░░░░░░░
    ░░██░░░░░░  \  ░░░░░░██░░  =  ░░██░░░░░░
    ░░██░░██░░     ░░░░██░░░░     ░░██░░██░░
    ░░░░░░░░░░     ░░░░░░░░░░     ░░░░░░░░░░

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)

    """
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    children = []
    if random.random() < crossover_rate:
        bro = np.logical_and(dad,np.logical_not(mom))
        sis = np.logical_and(mom,np.logical_not(dad))
        children.append(bro)
        children.append(sis)
    else:
        children.append(mom)
        children.append(dad)
    return children

'''
            custom MUTATION operators
    Following functions implements custom mutation operators.

    The included set operators between automata are:
     - random bitflip
     - biased reset and random flip
'''

def life_flip_mutation(random, candidate, args):
    """Return the mutants produced by bit-flip mutation on the candidates.

    .. Arguments:
       random -- the random number generator object
       candidate -- the candidate solution
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
                         The mutation rate is applied on a bit by bit basis.
    """
    if(SHOW_BEFOREAFTER_LIFEFLIP):
        print("\nBefore")
        life.display_genotype(candidate)

    rate = args.setdefault('mutation_rate', 0.1)
    mutant = copy.copy(candidate)
    for i, m in enumerate(mutant):
        if random.random() < rate:
            mutant[i] = not mutant[i]

    if(SHOW_BEFOREAFTER_LIFEFLIP):
        print("\nAfter")
        life.display_genotype(mutant)
    return mutant

def resetrandom_mutation(random, candidate, args):
    """Reset cells and randomly flip them on, with certain bias

    .. Arguments:
       random -- the random number generator object
       candidate -- the candidate solution
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
                         The mutation rate is applied on a bit by bit basis.
    - *flip_bias*     -- The bias towards the TRUE value
    """
    rate = args.setdefault('mutation_rate', 0.1)
    bias = args.setdefault('flip_bias', 0.5)

    if(SHOW_BEFOREAFTER_RESETRANDOM):
        print("\nBefore")
        life.display_genotype(candidate)

    mutant = copy.copy(candidate)
    for i, m in enumerate(mutant):
        if random.random() < rate:
            if random.random() < bias:
                mutant[i] = True
            else:
                mutant[i] = False

    if(SHOW_BEFOREAFTER_RESETRANDOM):
        print("\nAfter")
        life.display_genotype(mutant)

    return mutant


def main(rng, seed, display=False):
    problem = AutomatonEvaluator(seed)

    # --------------------------------------------------------------------------- #
    # EA configuration

    # the evolutionary algorithm (EvolutionaryComputation is a fully configurable evolutionary algorithm)
    # standard GA, ES, SA, DE, EDA, PAES, NSGA2, PSO and ACO are also available
    ea = inspyred.ec.EvolutionaryComputation(rng)

    # observers: provide various logging features
    if display:
        ea.observer = [inspyred.ec.observers.stats_observer,
                       inspyred.ec.observers.file_observer,
                       inspyred.ec.observers.plot_observer] #,
                       #inspyred.ec.observers.best_observer,
                       #inspyred.ec.observers.population_observer,

    # selection operator
    #ea.selector = inspyred.ec.selectors.truncation_selection
    #ea.selector = inspyred.ec.selectors.uniform_selection
    #ea.selector = inspyred.ec.selectors.fitness_proportionate_selection
    #ea.selector = inspyred.ec.selectors.rank_selection
    ea.selector = inspyred.ec.selectors.tournament_selection

    # variation operators (mutation/crossover)
    ea.variator = [
                    inspyred.ec.variators.gaussian_mutation,
                    # inspyred.ec.variators.n_point_crossover,
                    inspyred.ec.variators.random_reset_mutation,
                    # # inspyred.ec.variators.inversion_mutation,
                    # inspyred.ec.variators.uniform_crossover,
                    # inspyred.ec.variators.partially_matched_crossover,
                    inspyred.ec.variators.crossover(UNIONcrossover),
                    inspyred.ec.variators.crossover(INTERcrossover),
                    inspyred.ec.variators.crossover(XORcrossover),
                    inspyred.ec.variators.crossover(SUBcrossover),
                    inspyred.ec.variators.mutator(life_flip_mutation),
                    inspyred.ec.variators.mutator(resetrandom_mutation)]

    # replacement operator
    #ea.replacer = inspyred.ec.replacers.truncation_replacement
    #ea.replacer = inspyred.ec.replacers.steady_state_replacement
    #ea.replacer = inspyred.ec.replacers.random_replacement
    # ea.replacer = inspyred.ec.replacers.plus_replacement
    # ea.replacer = inspyred.ec.replacers.comma_replacement
    #ea.replacer = inspyred.ec.replacers.crowding_replacement
    #ea.replacer = inspyred.ec.replacers.simulated_annealing_replacement
    #ea.replacer = inspyred.ec.replacers.nsga_replacement
    #ea.replacer = inspyred.ec.replacers.paes_replacement
    ea.replacer = inspyred.ec.replacers.generational_replacement

    # termination condition
    #ea.terminator = inspyred.ec.terminators.evaluation_termination
    #ea.terminator = inspyred.ec.terminators.no_improvement_termination
    #ea.terminator = inspyred.ec.terminators.diversity_termination
    #ea.terminator = inspyred.ec.terminators.time_termination
    ea.terminator = inspyred.ec.terminators.generation_termination

    # --------------------------------------------------------------------------- #

    # run the EA
    final_pop = ea.evolve(evaluator=problem.evaluator,
                          generator=problem.generator,
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          pop_size=populationSize,
                          max_generations=numberOfGenerations,
                          max_evaluations=numberOfEvaluations,
                          tournament_size=tournamentSize,
                          mutation_rate=mutationRate,
                          gaussian_mean=gaussianMean,
                          gaussian_stdev=gaussianStdev,
                          crossover_rate=crossoverRate,
                          num_crossover_points=numCrossoverPoints,
                          num_selected=selectionSize,
                          num_elites=numElites,
                          flip_bias = 0.2)

    if display:
        final_pop.sort(reverse=True)
        print(final_pop[0])
        candidate = final_pop[0].candidate
        grid = life.genotype_to_grid(candidate)
        life.display(grid)
        life.savegrid(grid,"./bestindividual.txt")
        life.create_animation(candidate,MAX_ITERATIONS,TARGET)


if __name__ == "__main__":
    # Initialize LIFE grid
    life.set_grid_size(N)
    # Initialize the random generator
    if len(sys.argv) > 1 :
        seed = int(sys.argv[1])
    else:
        seed = int(time.time())

    rng = Random(int(seed))

    main(rng,seed,display)

    if display:
        ioff()
        show()
