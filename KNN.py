import csv
import random
import math

def loadDataset(filename, split, trainingSet=[] , testSet=[]):
	numLine = 0
	with open(filename, 'rb') as csvfile:
	    lines = csv.reader(csvfile)
	    dataset = list(lines)
	    for x in range(len(dataset)-1):
	    	if numLine > 0:
		        for y in range(len(dataset[x])):
		            dataset[x][y] = float(dataset[x][y])
		        if random.random() < split:
		            trainingSet.append(dataset[x])
		        else:
		            testSet.append(dataset[x])
	    	numLine += 1

def hammingDistance(instance1, instance2, length):
	distance = 0
	for x in range(length):
		if instance1[x] != instance2[x]:
			distance += 1
	return distance

def findClosest(test, length):
	closest = None
	minDist = hammingDistance(test, trainingSet[0], len(trainingSet[0]))
	for x in range(len(trainingSet)):
		tempDist = hammingDistance(test, trainingSet[x], len(trainingSet[0]))
		if tempDist < minDist:
			minDist = tempDist
			closest = trainingSet[x]
	return closest, minDist

trainingSet=[]
testSet=[]
print "Begin"
loadDataset('./data/games_by_username_all.csv', 0.66, trainingSet, testSet)
print 'Train: ' + repr(len(trainingSet))
print 'Test: ' + repr(len(testSet))
closestOne, dist = findClosest(testSet[0], len(trainingSet[0]))
print '# Games: ',
print len(trainingSet[0])
print 'Distance: ' + repr(dist)
print 'Closest Node: ',
#print closestOne