#!/bin/bash

if [ -z "$1" ]
then
    echo "Usage: ./$0 <word>"
    exit -1
fi

if [ ! -f ./config ]
then
    echo "Link the right configuration file first with ./use_config.sh <example.config>"
    exit -1
fi
WORD=$1

source ./config

if $USE_GLOBAL 
then
    GLOBAL_SPACE=$BIN_SPACES_DIR/$GLOBAL_VEC
    GLOBAL_CMD="--global $GLOBAL_SPACE"
else
    GLOBAL_CMD=
fi

pushd 01_extract_neighbours
./extract_neighbours.sh $GLOBAL_CMD $BIN_SPACES_DIR $PKL_SPACES_DIR $WORD
popd

pushd 02_extract_vectors
$PYTHON extract_vectors.py $PKL_SPACES_DIR \
    ../01_extract_neighbours/output/$WORD
popd

pushd 03_reduce_and_plot
$PYTHON reduce_and_plot.py ../02_extract_vectors/output/$WORD $SPACES_ORDER $WORD
popd
