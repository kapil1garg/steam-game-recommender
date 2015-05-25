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
		        for y in range(4):
		            dataset[x][y] = float(dataset[x][y])
		        if random.random() < split:
		            trainingSet.append(dataset[x])
		        else:
		            testSet.append(dataset[x])
	    	numLine += 1

def hammingDistance(instance1, instance2, length):
	



trainingSet=[]
testSet=[]
loadDataset('./data/games_by_username.csv', 0.66, trainingSet, testSet)
print 'Train: ' + repr(len(trainingSet))
print 'Test: ' + repr(len(testSet))