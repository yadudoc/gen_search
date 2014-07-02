#!/usr/bin/env python

'''
Search for patterns using the learn/predict functions provided by scikit-learn library.

There are 3 files involved in every run:
1) A csv input file, which has samples as rows, and variables as columns.
2) A csv labels files, has the same samples as in the input file and,
   the class (0/1) as a row.
3) Params file, which determines the run parameters.
'''

from __future__ import division
import argparse
import ConfigParser
import sys
import csv
import pandas as pd
from pandas import DataFrame, Series
import numpy as np
import itertools as it
import math
from matplotlib import pyplot as plt
import sklearn
from sklearn import cross_validation, metrics
import classifier
import pickle
#Read in feature and label files
def read_csv(csv_file):
    data = pd.read_csv(csv_file, sep=',', header=0, index_col=0)
    print("Read file : %s" % csv_file)
    return data

#Read in parameter file
def read_params(params_file):
    cfg = ConfigParser.ConfigParser()
    cfg.read(params_file)
    try:
        n = cfg.getint("params", "n")
        nsteps = cfg.getint("params", "nsteps")
        k = cfg.getint("params", "k")
        method = cfg.getint("params", "method")
        if method < 1 or method > 2:
            print("ERROR : Method must be between 1 and 2\n\tmethod 1: test and train on same data\n\tmethod 2: k-fold cross validation")
            sys.exit(1)
        print("Read parameters : n = %d, nsteps = %d, k = %d, method = %d" % (n, nsteps, k, method))
    except:
        print("ERROR : Could not read parameter file")
        sys.exit(1)
    return n, nsteps, k, method

#Check that classes on features and labels match
def check_consistency(inputs, labels):
    if (inputs.index.all() == labels.index.all()):
        print("Consistency check : Indices match")
    else:
        print("ERROR : Indices do not match")
        sys.exit(1)

#calculate measures from k-fold cross validation
def kfold(X, y, clf, k):
    nclasses = len(np.unique(y))
    acc = 0
    kf = cross_validation.KFold(len(y), n_folds=k, indices=True, shuffle=True, random_state=np.random.randint(100))
    while (any([len(np.unique(y[test]))<nclasses or len(np.unique(y[train]))<nclasses for test, train in kf])):
        kf = cross_validation.KFold(len(y), n_folds=k, indices=True, shuffle=True, random_state=np.random.randint(100))
    for train, test in kf:
        y_pred = clf.fit(X[train], y[train]).predict(X[test])
        acc += metrics.accuracy_score(y[test], y_pred)
    return acc/k

#Run k-fold cross validation multiple times, return mean accuracy
def kfold_multi_run(X, y, clf, k, nsteps):
    acc = 0
    for i in range(nsteps):
        acc += kfold(X, y, clf, k)
    return acc/nsteps

#Test and train on the same data
def run(X, y, clf):
    y_pred = clf.fit(X, y).predict(X)
    acc = metrics.accuracy_score(y, y_pred)
    return acc


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True,
                        help='Filename of samples file in csv. This argument is required')

    parser.add_argument('-l', '--labels', required=True,
                        help='Filename of the labels file in csv. This argument is required')

    parser.add_argument('-p', '--params', required=False,
                        help='Filename of the sets of combinations')

    parser.add_argument('-o', '--output', required=True,
                        help='Filename of output file to generate. Required')

    parser.add_argument('-v', '--verbose', action="store_true", help='Turn on verbose output')

    parser.add_argument('-n', '--n', required=False,
                        help='The index number of slice ?')

    parser.add_argument('-s', '--nsteps', required=False,
                        help='The number of steps ?')

    parser.add_argument('-k', '--kval', required=False,
                        help='The number of steps ?')

    parser.add_argument('-m', '--method', required=False,
                        help='Choose method 1/2 ?')


    print '\n{s:{c}^{n}}\n'.format(s='Sanity Checks',n=106,c='-')
    args = parser.parse_args()
    inputs = read_csv (args.input)
    labels = read_csv (args.labels)
    param  = args.params
    n      = int(args.n)
    nsteps = int(args.nsteps)
    k      = int(args.kval)
    method = int(args.method)
    outfile= args.output
    print("Arg parameters : n = %d, nsteps = %d, k = %d, method = %d" % (n, nsteps, k, method))

    #Exit immediately if consistency checks do not pass
    check_consistency (inputs, labels)

    #List of possible k-combinations
    #sets = list(it.combinations(range(inputs.shape[1]), n))
    sets = pickle.load(open(param,"rb"))
    numSets = len(sets)
    print '\n{s:{c}^{n}}\n'.format(s='Running for %d Feature Combinations' % numSets,n=106,c='-')

    #Run for all possible n-combinations of feature sets
    y = np.array(labels[labels.columns[0]])
    sys.stdout.write('0%')
    sys.stdout.flush()
    percentDone = 0
    results = []
    for i in range(numSets):
        X = inputs[list(sets[i])].values
        if method == 1:
            acc = run(X, y, classifier.clf)
        elif method == 2:
            acc = kfold_multi_run(X, y, classifier.clf, k, nsteps)
        results.append([round(acc,2)] + [x for x in inputs[list(sets[i])].columns] + [x for x in sets[i]])
        if i/numSets >= percentDone:
            sys.stdout.write('.')
            sys.stdout.flush()
            percentDone += 0.01
    sys.stdout.write('100%\n')
    sys.stdout.flush()

    #Rank results by highest accuracy:
    results.sort(key=lambda x: x[0], reverse=True)
    fp = open(outfile, 'wb')
    w = csv.writer(fp)
    print '\n{s:{c}^{n}}\n'.format(s='Writing Results',n=106,c='-')
    # No need for fancy notices
    #w.writerow(["accuracy"] + ["feature_"+str(i) for i in range(n)] + ["feature_"+str(i)+"_index" for i in range(n)])
    for x in results[:1000]:
        w.writerow(x)
    fp.close()
    print("Done!")



