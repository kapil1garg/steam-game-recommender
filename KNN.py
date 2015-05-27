import csv
import random
import math

import sys
import pdb
import traceback

dataset = []
trainingSet = []
testSet = []

def loadDataset(filename, split):
    # Open the file
    with open(filename, 'rb') as f:
        # Read the header line so it is not used in data
        next(f, None)

        for row in f:
            # Get rid of commas
            row = row.translate(None, ",")

            # Convert bit string into integer
            row = int(row, 2)

            # Add it to the full data set
            dataset.append(row)

            # Add it to training or test data according to split
            if random.random() < split:
                trainingSet.append(row)
            else:
                testSet.append(row)

def hammingDistance(instance1, instance2):
    # xor the two numbers, convert it a string representation of the binary number, then count the number of 1s
    return bin(instance1 ^ instance2).count("1")

def findClosest(target, k):
    closest = sorted(trainingSet, key=lambda n: hammingDistance(target, n))[:k]
    minDist = [hammingDistance(target, x) for x in closest]
    return closest, minDist

try:
    print "Begin"
    loadDataset('./data/games_by_username.csv', 0.66)
    print 'Train: ' + str(len(trainingSet))
    print 'Test: ' + str(len(testSet))
    closestOne, dist = findClosest(testSet[0], 2)
    print '# Games: ',
    print int(math.floor(math.log(trainingSet[0])))
    print 'Distance: ' + str(dist)
    print 'Closest Node: ',
    print closestOne
except Exception as e:
    typ, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)
