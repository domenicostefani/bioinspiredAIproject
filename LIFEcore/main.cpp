/*
 *                     Conway's game of LIFE simulator
 *                (custom implementation and metric computation) 
 * 
 * Conway's game of LIFE implementation along with fitness evaluation metrics 
 * computation for an evolutionary computation algorithm.
 * EC is configured to generate a LIFE configuration in an area of the grid and
 * to evolve it in order to make it reach a specific TARGET point 
 * ([target_X,target_Y]).
 * 
 * Command:
 * life <in_filename> <max_it_s> <target_X> <target_Y> <out_filename> 
 * 
 * With SAVEVIDEO flag set to TRUE:
 * life <in_filename> <max_it_s> <target_X> <target_Y> <out_filename> <folder>
 * 
 * Input:
 *  - <in_filename>   File with a @N_VALUE x @N_VALUE square matrics of 0/1 
 *                    values representing LIFE's grid.
 *  - <max_it>        Maximum number of LIFE iterations to execute
 *  - <target_X>      X coordinate of the Target
 *  - <target_Y>      Y coordinate of the Target
 *  - <out_filename>  Output file with computed metrics
 * 
 *  * <folder> ****** Path of the folder where to store the  image sequence
 * 
 * Computed Metrics:
 *  - <distance>      Final Chebychev distance between the center of the 
 *                    automaton(group of alive cells) and the target
 *  - <size>          Final Size of the bounding box containing the alive cells
 *  - <iterations>    Number of iterations required to reach the end of the sim.
 * 
 *
 * File:   main.cpp
 * Author: Domenico Stefani
 *
 * Created on November 19, 2019, 9:42 PM
 */

#include <cstdlib>  
#include <cstdio>
#include <chrono>
#include <unistd.h>
#include <stdio.h> 
#include <iostream>
#include <fstream>
#include <string>
#include <string.h> //memset

/*----------------------------------------------------------------------------*/
/* PRECOMPILER FLAGS                                                          */
/*----------------------------------------------------------------------------*/

//#define VERBOSE   // Compile this for verbose output and display (debug only)
#define SAVEVIDEO   // Compile with this flag to produce the image animation

/*----------------------------------------------------------------------------*/
/* CONSTANTS                                                                  */
/*----------------------------------------------------------------------------*/

#define N_VALUE 40  // Effective grid size (Check coherency with EC script
unsigned const short R_SIZE = N_VALUE + 2;  //RealGridSize, accounts for borders
unsigned const short min_bound = 1;         //First effective row/column
unsigned const short max_bound = R_SIZE-1;  //Last effective row/column

using namespace std;

/*----------------------------------------------------------------------------*/
/* FUNCTION DECLARATIONS                                                      */
/*----------------------------------------------------------------------------*/

#ifdef VERBOSE
void display(bool grid[][R_SIZE])  
void display2(bool grid[][R_SIZE],int it, int jt);
#endif

#ifdef SAVEVIDEO
void save_img(bool grid[][R_SIZE], string filename, int magnification, 
              short targetX, short targetY);
#endif

/**
 * Copy @gridOne into @gridTwo
 * @param gridOne structure to copy
 * @param gridTwo scructure where to copy
 */
void copygrid(bool gridOne[R_SIZE][R_SIZE], bool gridTwo[R_SIZE][R_SIZE]);

/**
 * Check if two grids are equal
 * @param gridOne
 * @param gridTwo
 * @return True if the two grids are equal, False otherwise
 */
bool boolgridequal(bool gridOne[R_SIZE][R_SIZE], bool gridTwo[R_SIZE][R_SIZE]);

/**
 * Compute the boundaries (indexes) of the set of alive cells (automaton)
 * @param grid  game board
 * @param min_i minimum i value (return)
 * @param max_i maximum i value (return)
 * @param min_j minimum j value (return)
 * @param max_j maximum j value (return)
 */
void bounds(bool grid[R_SIZE][R_SIZE],short &min_i,short &max_i,short &min_j,
            short &max_j);

/**
 * Compute the center of the bounding box of the automaton
 * @param min_i   minimum i value
 * @param max_i   maximum i value
 * @param min_j   minimum j value
 * @param max_j   maximum j value
 * @param xc      x coordinate of the center
 * @param yc      y coordinate of the center
 */
void center_of_mass(short min_i,short max_i,short min_j,short max_j, short &xc, 
                    short &yc);

/**
 * Compute the surface of the bounding box of the automaton
 * @param min_i   minimum i value
 * @param max_i   maximum i value
 * @param min_j   minimum j value
 * @param max_j   maximum j value
 * @return        surface of the bounding box of the automaton
 */
int automatonsize(short min_i,short max_i,short min_j,short max_j);

/**
 * Simulate one iteration of LIFE
 * @param grid  game board
 * @return      number of alive cells
 */
int update(bool grid[][R_SIZE]);

/**
 * Main routine
 * @param argc
 * @param argv
 * @return      program state
 */
int main(int argc, char** argv)
{
  // READ CLI PARAMETERS
  
#ifdef SAVEVIDEO
  if(argc != 7){
    fprintf( stderr, "Error: wrong argument number\n");
    return -1;
  }
#else
  if(argc != 6){
    fprintf( stderr, "Error: wrong argument number\n");
    return -1;
  }
#endif
  
  string  in_filename = argv[1];
  string  max_it_s = argv[2];
  string  targetX_s = argv[3];
  string  targetY_s = argv[4];
  string  out_filename = argv[5];
#ifdef SAVEVIDEO
  string  folder = argv[6];  
#endif
  
  #ifdef VERBOSE
    printf("file: %s\n",in_filename.c_str());
  #endif
  
  int max_it = std::stoi(max_it_s);
  int targetX = std::stoi(targetX_s);
  int targetY = std::stoi(targetY_s);
  
  #ifdef VERBOSE
    printf("max_it: %d\n",max_it);
    printf("targetX: %d\n",targetX);
    printf("targetY: %d\n",targetY);
  #endif
    
  bool grid[R_SIZE][R_SIZE] = {false};
  int linenumber = 0;
  string line;
  ifstream myfile(in_filename);
  if (myfile.is_open())
  {
    while ( getline (myfile,line) )
    {
      const char* cline;
      cline = line.c_str();
      for(int j=0; j<R_SIZE; ++j){
        grid[linenumber+min_bound][j+min_bound] = (*(cline+j) == '1'?true:false);
      } 
      linenumber++;
    }
    myfile.close();
  }else{
    fprintf(stderr,"ERROR: unable to open file!\n"); 
    return -1;
  }
  
  bool reached = false;
  int iterations;
  int countTrue = 0;
  bool previous_grid[R_SIZE][R_SIZE] = {false};
  bool previous_previous_grid[R_SIZE][R_SIZE] = {false};
  
#ifdef VERBOSE
    display2(grid,targetY,targetX);
    std::cin.ignore();
    std::cin.ignore();
#endif
#ifdef SAVEVIDEO
    save_img(grid,folder + "0000.bmp",10,targetX,targetY);
#endif
  
  for(int i = 0; i < max_it; i++){
    iterations = i+1;
    copygrid(previous_grid,previous_previous_grid);
    copygrid(grid,previous_grid);
    countTrue = update(grid);
#ifdef VERBOSE
      display2(grid,targetY,targetX);
      std::cin.ignore();
#endif
#ifdef SAVEVIDEO
      string zero_pad = (iterations < 10)?"000":(iterations<100?"00":(iterations<1000?"0":""));
      save_img(grid,folder + zero_pad + to_string(iterations) + ".bmp",10,targetX,targetY);
#endif
    /* Stopping*/
    // 1. Target reached
    if (grid[targetY][targetX] == true){
      #ifdef VERBOSE
        printf("// Stopping: Target reached\n");
      #endif
      reached = true;
      break;
    }
    // 2. Death
    if (countTrue== 0){
      #ifdef VERBOSE
        printf("// Stopping: Automata died at iteration %d\n", i);
      #endif
      break;
    }
    // 3. Static behaviour
    if (boolgridequal(previous_grid,grid)){
      #ifdef VERBOSE
        printf("// Stopping: Automata became static at iteration %d\n", i);
      #endif
      break;
    }
    // 4. Repetitive behaviour
    if (boolgridequal(previous_previous_grid,grid)){
      #ifdef VERBOSE
        printf("// Stopping: Automata became repetitive at iteration %d\n", i);
      #endif
      break;
    }
  }
  
  
  
  short min_i = max_bound, max_i= min_bound;
  short min_j = max_bound, max_j = min_bound;
  bounds(grid,min_i,max_i,min_j,max_j);
  
  
  int distance = 0;
  int size = 0;
  
  /// distance
  if (reached)
      distance = 0;
  else{
      short xc,yc;
      center_of_mass(min_i,max_i,min_j,max_j,xc,yc);
      // chebyshev distance
      distance = max(abs(xc - targetX),abs(yc - targetY));
  }
  /// size
  size = automatonsize(min_i,max_i,min_j,max_j);

  /// iterations
  //  iterations is already correct
  
  FILE * fp;
  fp = fopen (out_filename.c_str(),"w");
  fprintf(fp,"%d\n%d\n%d\n", distance,size,iterations); 
  fclose (fp);
  
  return 0;
}


void copygrid(bool gridOne[R_SIZE][R_SIZE], bool gridTwo[R_SIZE][R_SIZE]){
  for (int i = min_bound; i < max_bound; i++) 
    for (int j = min_bound; j < max_bound; j++) 
      gridTwo[i][j] = gridOne[i][j];
}

bool boolgridequal(bool gridOne[R_SIZE][R_SIZE], bool gridTwo[R_SIZE][R_SIZE]){
  for (int i = min_bound; i < max_bound; i++) 
    for (int j = min_bound; j < max_bound; j++) 
      if(gridTwo[i][j] != gridOne[i][j])
        return false;
  return true;
}

void bounds(bool grid[R_SIZE][R_SIZE],short &min_i,short &max_i,short &min_j,short &max_j){
  for(short i=min_bound; i < max_bound; ++i){
    for(short j=min_bound; j < max_bound; ++j){
      if(grid[i][j] == true){
          if(i < min_i)
               min_i = i;
          else if( i > max_i)
              max_i = i;

          if(j < min_j)
              min_j= j;
          else if(j > max_j)
              max_j = j;
      }
    }
  }
}

void center_of_mass(short min_i,short max_i,short min_j,short max_j, short &xc, short &yc){
    xc = int((max_j + min_j) / 2);
    yc = int((max_i + min_i) / 2);
}

int automatonsize(short min_i,short max_i,short min_j,short max_j){
    return (max_i - min_i + 1) * (max_j - min_j + 1);
}


int update(bool grid[][R_SIZE]){
  for (int idx = min_bound; idx < max_bound; idx++) {
    grid[idx][min_bound] = false;
    grid[idx][max_bound-1] = false;
    grid[min_bound][idx] = false;
    grid[max_bound-1][idx] = false;
  }
  
  bool new_grid[R_SIZE][R_SIZE] = {};
  copygrid(grid,new_grid);
  
  int countTrue = 0;
  
  for (int i = min_bound; i < max_bound; i++) {
    for (int j = min_bound; j < max_bound; j++) {
      
      int total = int(new_grid[i][j-1]) + int(new_grid[i][j+1]) +
                            int(new_grid[i-1][j]) + int(new_grid[i+1][j]) +
                            int(new_grid[i-1][j-1]) + int(new_grid[i-1][j+1]) +
                            int(new_grid[i+1][j-1]) + int(new_grid[i+1][j+1]);
      if(new_grid[i][j] == true){
        if(total >= 2 and total <= 3){
          grid[i][j] = true;
          countTrue++;
        }else{
          grid[i][j] = false;
        }
      }else{
        if (total == 3){
          grid[i][j] = true;
          countTrue++;
        }else{
          grid[i][j] = false;
        }
      }
      
    }
  }
  return countTrue;
}

  
#ifdef VERBOSE
  void display(bool grid[][R_SIZE]){
    for (int i = min_bound; i < max_bound; i++) {
      for (int j = min_bound; j < max_bound; j++) {
        if(grid[i][j] == true)
          printf("██");
        else
          printf("░░");
        fflush(stdout);
      }
      printf("\n");
      fflush(stdout);
    }
  }
  
  void display2(bool grid[][R_SIZE],int it, int jt){
    for (int i = min_bound; i < max_bound; i++) {
      for (int j = min_bound; j < max_bound; j++) {
        if(grid[i][j] == true)
          printf("██");
        else{
          if(i == it && j == jt)
            printf("TT");
          else
            printf("░░");
        }
        fflush(stdout);
      }
      printf("\n");
      fflush(stdout);
    }
  }
#endif

#ifdef SAVEVIDEO

//Color for alive cells
#define color1r 190
#define color1g 190
#define color1b 190
//Color for target cell
#define colorTr 0
#define colorTg 0
#define colorTb 0
//Color for reached target cell
#define colorRr 255
#define colorRg 255
#define colorRb 255
//Color for dead cells
#define color2r 43
#define color2g 43
#define color2b 43
  
void save_img(bool grid[][R_SIZE], string filename, int magnification, short targetX, short targetY){
  FILE *fileimg;
  short w = N_VALUE*magnification, h = N_VALUE*magnification;
  unsigned char * img = NULL;
  int filesize = 54 + 3*w*h;  //w is your image width, h is image height, both int

  img = (unsigned char *)malloc(3*w*h);
  memset(img,0,3*w*h);

  for(int i=0; i<N_VALUE*magnification; i++){
    for(int j=0; j<N_VALUE*magnification; j++){ 
          short x=i, y=(j);
          bool c = grid[(i/magnification)+min_bound][(j/magnification)+min_bound];
          if(((i/magnification)+min_bound == targetY)&&((j/magnification)+min_bound == targetX)){
            img[(y+x*h)*3+2] = (unsigned char)(c?colorRr:colorTr);
            img[(y+x*h)*3+1] = (unsigned char)(c?colorRg:colorTg);
            img[(y+x*h)*3+0] = (unsigned char)(c?colorRb:colorTb);
          }else{
            img[(y+x*h)*3+2] = (unsigned char)(c?color1r:color2r);
            img[(y+x*h)*3+1] = (unsigned char)(c?color1g:color2g);
            img[(y+x*h)*3+0] = (unsigned char)(c?color1b:color2b);
          }
      }
  }

  unsigned char bmpfileheader[14] = {'B','M', 0,0,0,0, 0,0, 0,0, 54,0,0,0};
  unsigned char bmpinfoheader[40] = {40,0,0,0, 0,0,0,0, 0,0,0,0, 1,0, 24,0};
  unsigned char bmppad[3] = {0,0,0};

  bmpfileheader[ 2] = (unsigned char)(filesize    );
  bmpfileheader[ 3] = (unsigned char)(filesize>> 8);
  bmpfileheader[ 4] = (unsigned char)(filesize>>16);
  bmpfileheader[ 5] = (unsigned char)(filesize>>24);

  bmpinfoheader[ 4] = (unsigned char)(       w    );
  bmpinfoheader[ 5] = (unsigned char)(       w>> 8);
  bmpinfoheader[ 6] = (unsigned char)(       w>>16);
  bmpinfoheader[ 7] = (unsigned char)(       w>>24);
  bmpinfoheader[ 8] = (unsigned char)(       h    );
  bmpinfoheader[ 9] = (unsigned char)(       h>> 8);
  bmpinfoheader[10] = (unsigned char)(       h>>16);
  bmpinfoheader[11] = (unsigned char)(       h>>24);

  fileimg = fopen(filename.c_str(),"wb");
  fwrite(bmpfileheader,1,14,fileimg);
  fwrite(bmpinfoheader,1,40,fileimg);
  for(int i=0; i<h; i++)
  {
      fwrite(img+(w*(h-i-1)*3),3,w,fileimg);
      fwrite(bmppad,1,(4-(w*3)%4)%4,fileimg);
  }
  free(img);
  fclose(fileimg);
}
#endif