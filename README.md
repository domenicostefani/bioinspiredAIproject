# Ec::GoL
___Project for the Bio-Inspired AI 2019 course at UNITN___  
Authors: Domenico Stefani, Daniele Campli  
Presentation slides [here](https://cutt.ly/ecgol)

### Introduction ###
This project consists in applying Evolutionary Computation techniques 
to Conway's Game of Life (or simply LIFE) in order to generate game entities that move across the game board
in a specific way (eg. spaceships).

### Project structure ###
Python is used to perform Evolutionary Computation using the ___inspyred___ framework, while the _simulator_ is written in C++ because the simulation may require thousands of game iterations and speed is required.
Note: Similar Python and C++ implementations of the simulator showed a 100-fold difference in the time requred for the same simulations.  
The _simulator_ is a module that contains the implementation of Conway's game of LIFE, some custom stopping criterions and the computation of several metrics required for fitness evaluation.

### Files and folders: ###
- `LIFEcore/`   Folder containing the source code for the simulator
- `animation/`  Folder containing animation utilities
- `main.py`     Main script that performs evolution
- `life.py`     Module that contains part of LIFE implementation
- `lifecore`    C++ written executable that performs LIFE game execution (__Replace with executable compiled for your architecture__)
- `displaycore` C++ written executable that produces LIFE animation (__Replace with executable compiled for your architecture__)

### External Python3 modules required ###
- `pylab`
- `numpy`
- `inspyred`

### How to run evolution ###
##### Step 1: Compile c++ modules #####

- Compile for your architecture the file`LIFEcore/main.cpp` with the flag __SAVE_VIDEO__ set to `false` and save the executable in the main directory with the name `lifecore`, thereby substituting the already present executable.  
- Compile again`LIFEcore/main.cpp` with the flag __SAVE_VIDEO__ set to `true` and save the executable in the main directory with the name `displaycore`

##### Step 2: Run evolution #####
Make sure to have Python version 3 installed.  
Run:  
`python main.py` 
  
  
_Author note: This was part of a university project and it is not really designed for the public or for wide compatibility. Anyway if you think that this could be useful for you and/or you find a bug that prevents you from using this code, feel free to open a issue and contact me._
