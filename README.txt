Configuration:
1. Create .config file like ITA.config with all the relevant paths filled in
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
networkx
PyGraphviz?

System libraries:
ffmpeg
libSDL-1.2
graphviz?
