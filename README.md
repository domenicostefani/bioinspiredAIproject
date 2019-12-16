# Ec::GoL
___Project for the Bio-Inspired AI 2019 course at UNITN___  
Authors: Domenico Stefani, Daniele Campli  
Presentation slides [here](https://cutt.ly/ecgol)

### Introduction ###
This project consists in applying Evolutionary Computation techniques 
to Conway's Game of Life (or simply LIFE) in order to generate game entities that move across the game board
in a specific way (eg. spaceships).

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
  
  
This was part of a university project and it is not really designed for the public or for wide compatibility. Anyway if you think that this could be useful for you and/or you find a bug that prevents you from using this code, feel free to open a issue and contact me.
