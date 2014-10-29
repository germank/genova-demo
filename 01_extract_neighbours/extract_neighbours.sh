#!/bin/sh
if [ $# -lt 3 ]
then
    echo "Usage: ./$0 [--global bin-global-file] bin-spaces-directory <pkl-spaces-directory> <target-word>"
    exit -1
fi
if [ "$1" = "--global" ]
then
    shift
    GLOBAL=true
    GLOBAL_SPACE=$1
    shift
else
    GLOBAL=false
fi

BIN_SPACES_DIR=$1
PKL_SPACES_DIR=$2
WORD=$3
OUTPUT_DIR=output/$WORD
NN=$4
PYTHON=$5
MIN_OCCURRENCES=$6


mkdir -p $OUTPUT_DIR
if $GLOBAL
then
    echo $GLOBAL_SPACE
    ./distance $GLOBAL_SPACE $NN $WORD > $OUTPUT_DIR/global_nn.txt
    echo $WORD >>$OUTPUT_DIR/global_nn.txt
fi
PKL_SPACES=""
for SPACE in $BIN_SPACES_DIR/*.bin
do
    SPACE_FILENAME=$(basename $SPACE)
    SPACE_NAME=${SPACE_FILENAME%%.bin}
    echo "$PKL_SPACES_DIR/$SPACE_NAME.pkl" 
    if [ -f "$PKL_SPACES_DIR/$SPACE_NAME.pkl" ]
    then
        PKL_SPACES="$PKL_SPACES_DIR/$SPACE_NAME.pkl $PKL_SPACES" 
        if $GLOBAL
        then
            cp $OUTPUT_DIR/global_nn.txt $OUTPUT_DIR/$SPACE_NAME.txt
        else
            echo  "Extracting neighbours from $PKL_SPACES_DIR/$SPACE_NAME.pkl"
            ./distance $SPACE $NN $WORD > $OUTPUT_DIR/$SPACE_NAME.txt
            echo $WORD >>$OUTPUT_DIR/$SPACE_NAME.txt
        fi
    fi
done

if [ $MIN_OCCURRENCES -gt 1 ]
then
    echo "Filtering words with less than $MIN_OCCURRENCES occurrences"
    $PYTHON filter.py --min-occurrences $MIN_OCCURRENCES --words $OUTPUT_DIR/*.txt \
        --spaces $PKL_SPACES
fi
