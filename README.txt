Configuration:
1. Create .config file like ITA.config with all the relevant paths filled in
Variables:
PYTHON: path to the python interpreter
BIN_SPACES_DIR: path to the spaces in bin format
PKL_SPACES_DIR: path to the spaces in pkl format
SPACES_ORDER: a file containing the names of the pkl spaces in the right order
GLOBAL_VEC: the bin space with global data
USE_GLOBAL: true if want to use GLOBAL_VEC to extract nearest neighbours.
false otherwise
EXPORT_ONLY: true if one wants only to obtain a csv file with the words
coordinates
NUM_NEIGHBOURS: the number of neighbours to extract per space (or in total for
the global)
MIN_OCCURRENCES:  number of times a word must occur in any space to be
considered in the plot

2. Run ./use_config.sh passing as the argument the desired configuration file.
    e.g. 
        ./use_config.sh ITA.config
3. Execute the visualization with the desired target word
    e.g.
        ./run_visualization.sh cane


Requirements:

Python libraries:
numpy
scipy
composes toolkit
networkx (soon to be removed)

System libraries:
ffmpeg
libSDL-1.2
