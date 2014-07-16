#!/bin/bash

############# START OF CONFIGURABLES######################
#SAMPLES=data/miRNA_samples.csv
#LABELS=data/miRNA_labels.csv
#OUTPUT_PREFIX=splits/miRNA

#SAMPLES=data/golub_samples.csv
#LABELS=data/golub_labels.csv
#OUTPUT_PREFIX=output/golub

SAMPLES=data/iris_samples.csv
LABELS=data/iris_labels.csv
OUTPUT_PREFIX=output/iris

N=2
STEPS=20
K=5
METHOD=2
SPLITNUM=1000
# This must be set as a directory/prefix
############ END OF CONFIGURABLES ########################


source python_wrapper.sh "-c exit(0)"

swift -version | grep "Swift 0.95 RC6"
if [[ "$?" != "0" ]]
then
    echo "ERROR: Must run script with Swift 0.95 RC6 or higher"
fi

echo "Cleaning previous results"

rm -rf results
rm -rf test


if [[ "$1" == "skip" ]]
then
    echo "Skipping preprocessing stage"
else
    rm -rf $OUTPUT_PREFIX* &> /dev/null
    python preprocess.py -i $SAMPLES -l $LABELS -n $N -s $STEPS -k $K -m $METHOD -x $SPLITNUM -f $OUTPUT_PREFIX
    if [[ "$?" != "0" ]]
    then
        echo "ERROR: Preprocessing failed. Stopping"
    fi
fi

swift gen_search.swift \
    -n=$N \
    -nsteps=$STEPS \
    -kfold=$K \
    -method=$METHOD \
    -folder=$(dirname $OUTPUT_PREFIX) \
    -prefix=$(basename $OUTPUT_PREFIX) \
    -sample=$SAMPLES \
    -labels=$LABELS
