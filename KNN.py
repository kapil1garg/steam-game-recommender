import csv
import random
import math
import operator

import sys
import pdb
import traceback

dataset = []
trainingSet = []
testSet = []
header_row = []

def loadDataset(filename, split):
    # Open the file
    with open(filename, 'rb') as f:
        # Read the header line so it is not used in data
        first_row = f.next()
        first_row = ''.join(first_row.splitlines())
        header_row.extend(first_row.split(","))

        for row in f:
            # Get rid of commas
            row = row.translate(None, ",")

            # Convert bit string into integer
            row = int(row, 2)

            # Add it to the full data set
            if row != 0: 
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

def getGames(target):
    header_length = len(header_row)
    bit_string = bin(target)[2:].zfill(header_length)
    return [header_row[i] for i in range(header_length) if bit_string[i] == "1"]

def findDifferentGames(closest, instance):
    return ((closest | instance) ^ instance)

def getVotes(neighbors, instance):
    # Compress into 1 list
    compressed_games = sum([getGames(findDifferentGames(x, instance)) for x in neighbors], [])

    # Convert into dictionary and return
    return dict([game, compressed_games.count(game)] for game in compressed_games)

def getTopGames(ranked_games, n):
    sorted_games = sorted(ranked_games.items(), key = operator.itemgetter(1))
    top_n = sorted_games[-n:]
    return top_n[::-1]


try:
    print "Begin"
    loadDataset('./data/games_by_username_all.csv', 0.99)
    print 'Train: ' + str(len(trainingSet)) + " instances"
    print 'Test: ' + str(len(testSet)) + " instances"
    print '# Games: ' + str(len(header_row))

    n_neighbors = 100
    print "Number of closest neighbors evaluated: " + str(n_neighbors)
    # print int(math.floor(math.log(trainingSet[0])))
    closest, dist = findClosest(testSet[0], n_neighbors)

    # print 'Distance: ' + str(dist)
    # print 'Closest Node: ',
    # print closest

    # print getGames(closest[0])
    # print getGames(closest[1])
    # print getGames(testSet[0])

    # print "\nGetting Game Delta for closest member"
    # print getGames(findDifferentGames(closest[0], testSet[0]))

    # print "Getting Game Delta for 2nd closest member"
    # print getGames(findDifferentGames(closest[1], testSet[0]))
    
    print

    print "All games different"
    print getVotes(closest, testSet[0])
    print

    print "Top 5 games"
    print getTopGames(getVotes(closest, testSet[0]), 5)
    print
except Exception as e:
    typ, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)
