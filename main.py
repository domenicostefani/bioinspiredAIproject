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

"""--Parameters for LIFE..---------------------------------------------------"""

""" Life iteration number """
MAX_ITERATIONS = 1000
""" Life grid size        """
N = 40
""" Life target cell      """
TARGET = (N-4,N-4)

"""--Parameters for the EC---------------------------------------------------"""

populationSize = 30
numberOfGenerations = 100
numberOfEvaluations = 2500                    # used with evaluation_termination
tournamentSize = 3
mutationRate = 0.8
gaussianMean = 0
gaussianStdev = 10.0
crossoverRate = 0.95
numCrossoverPoints =  5
selectionSize = populationSize
numElites = 2

"""--Visualization-----------------------------------------------------------"""
display = True
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
            distances,sizes,iterations = life.compute_fitness(candidate,
                                                              MAX_ITERATIONS,
                                                              TARGET)

            (final_distance,min_distance) = distances
            (final_size,max_size,avg_size) = sizes

            """-----------Fitness formulation--------------------------------"""
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
    ea.variator = [inspyred.ec.variators.gaussian_mutation,
                   # inspyred.ec.variators.n_point_crossover,
                    inspyred.ec.variators.random_reset_mutation,
                    # inspyred.ec.variators.inversion_mutation,
                    inspyred.ec.variators.uniform_crossover
                    # inspyred.ec.variators.partially_matched_crossover
                    ]

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
                          num_elites=numElites)

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
