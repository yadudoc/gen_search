Gen_Search
==========

Gen_Search : Generic search for patterns using Machine learning.


How to run
----------

Use the runner.sh script to run the app. It will go through all stages and ensure that
the right directories are linked along the pipeline.

In the runner.sh there are a few variables set with a banner, such as the SAMPLES and
LABELS variables which should pointat the samples, and labels csv files.

Set the site variable inside the swift.properties file to choose the site to run the
tests on. Osgconnect and local sites are already defined. You can add more sites to
widen the pool of compute resources.

```bash
./runner.sh
```

Stages
------

There are 3 stages to the Gen_search app.
1. Preprocess and generate combination of k items to search for.
2. Find accuracy of each k item pair.
3. Sort the results by accuracy.


Preprocessing
^^^^^^^^^^^^^

Currently this stage is done independent of the next two stages as,
this can be done efficiently on a single machine, and used by subsequent
stages without any need for recomputation. It is trivial to run from a
shell script and requires unnecessary complications with the swift version
used to run the steps further down the pipeline.

To run this stage use the preprocess.py script.

```bash
# For help use the -h option
preprocess.py -h

# To run the basic tests:
python preprocess.py -i <Sample> -l <Labels> -n <N> -s <nsteps> -k <K> -m <method> -x <number of chunks> -f <output_prefix>
# Eg:
# python preprocess.py -i data/miRNA_samples.csv -l data/miRNA_labels.csv -n 2 -s 20 -k 5 -m 2 -x 100 -f output/miRNA
```

Parallel run
^^^^^^^^^^^^

To run the swift script, ensure swift 0.95 or higher is installed and use the following
command:

swift gen_search.swift [-n=<N> -nsteps=<nsteps> -kfold=<k -method=<method> -folder=<folder>] \
    [-prefix=<prefix> -sample=<sample> -labels=<labels>]

Each of these variables can be set to your preference.

The final aggregation is done using a simple sort function.