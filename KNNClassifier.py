import csv
import random
import math
import operator
import copy

import sys
import pdb
import traceback

class KNNClassifier:
    'k-NN Classifier using Hamming Distanceg'

    def __init__(self, train_data, test_data, test_games):
        train_header_row, self.train_set = self.loadDataset(train_data)
        test_header_row, self.test_set = self.loadDataset(test_data)
        self.game_list = test_games

        # Check if training and test set are from the same dataset
        if set(train_header_row) != set(test_header_row):
            raise ValueError("Header row for test set does not match header for train. Please make sure test and train are from the same dataset.")
        else:
            self.header_row = train_header_row

        # Check if each game in game_list appears in the header row
        for g in self.game_list:
            if not g in self.header_row:
                raise ValueError("Game " + g + " was not found in training/test set. Please remove and try again.")

        # Print some statistics about the test and training data
        print "Total examples: " + str(len(self.train_set) + len(self.test_set))
        print "Number training examples: " + str(len(self.train_set))
        print "Number testing examples: " + str(len(self.test_set))
        print 

    def loadDataset(self, filename):
        """Loads data from a csv file"""
        # Open the file
        with open(filename, 'rb') as f:
            # Read the header line so it is not used in data
            header = f.next()
            header = ''.join(header.splitlines()).split(",")
            data = [row.strip().split(",") for row in f]

            return header, data

    def classifyGames(self, k):
        """Runs kNN classificaion on each game in the inputted gamelist""" 
        for g in self.game_list:
            g_index = self.header_row.index(g)
            true_labels = []
            classification = []

            print "Testing game " + str(g) + " with " + str(k) + " nearest neighbors"

            # for t in range(0, 10): # FOR TESTING ONLY!!!
            for t in range(len(self.test_set)):                
                t = self.test_set[t]
                true_labels.append(t[g_index])
                classification.append(self.getClassification(self.findClosest(t, k, g_index), g_index))

            print "Testing game " + str(g) + " with " + str(k) + " nearest neighbors completed. Accuracy results below."
            confusion_matrix = self.confusion(true_labels, classification)
            self.generateStatistics(confusion_matrix)
    
    def generateStatistics(self, confusion_matrix):
        """Print out accuracy statistics"""
        EPSILON = math.exp(-100) # add to avoid division by 0
        tp_0 = confusion_matrix["0"]["0"] + EPSILON
        tn_0 = confusion_matrix["1"]["1"] + EPSILON
        fp_0 = confusion_matrix["0"]["1"] + EPSILON
        fn_0 = confusion_matrix["1"]["0"] + EPSILON

        tp_1 = confusion_matrix["1"]["1"] + EPSILON
        tn_1 = confusion_matrix["0"]["0"] + EPSILON
        fp_1 = confusion_matrix["1"]["0"] + EPSILON
        fn_1 = confusion_matrix["0"]["1"] + EPSILON

        print "Accuracy: " + str(self.accuracy(tp_0, tn_0, fn_0, fp_0)) + "%"

        print "Precision (0): " + str(self.precision(tp_0, fp_0))
        print "Recall (0): " + str(self.recall(tp_0, fn_0))
        print "F1 (0): " + str(self.f_measure(self.precision(tp_0, fp_0), self.recall(tp_0, fn_0)))

        print "Precision (1): " + str(self.precision(tp_1, fp_1))
        print "Recall (1): " + str(self.recall(tp_1, fn_1))
        print "F1 (1): " + str(self.f_measure(self.precision(tp_1, fp_1), self.recall(tp_1, fn_1)))

        print "a    b"
        print str(confusion_matrix["0"]["0"]) + " | " + str(confusion_matrix["0"]["1"]) + "   a = 0"
        print "-----"
        print str(confusion_matrix["1"]["0"]) + " | " + str(confusion_matrix["1"]["1"])  +  "   b = 1\n"

    def confusion(self, trueLabels, classifications):
        """Generates confusion matrix"""
        labels = list(set(trueLabels))
        confusion_matrix = {"0": {"0": 0, "1": 0}, "1": {"0": 0, "1": 0}}

        true_length = len(trueLabels)
        class_length = len(classifications)
        if true_length == class_length:
            for i in range(true_length):
                confusion_matrix[trueLabels[i]][classifications[i]] += 1
        return confusion_matrix

    def precision(self, tp, fp):
      """Calculates the precision using true positive and false positive metrics"""
      return float(tp)/float(tp + fp)

    def recall(self, tp, fn):
      """Calculates the recall using true positive and false negative metrics"""
      return float(tp)/float(tp + fn)

    def f_measure(self, precision, recall):
      """Calculates the f-measure using precision and recall metrics"""
      return float(2.0 * precision * recall)/float(precision + recall)

    def accuracy(self, tp, tn, fn, fp):
      """Calculates the accuracy using true positive, true negative, false positive, and false negative metrics"""
      return 100.0 * (float(tp + tn)/float(tp + tn + fn + fp))

    def hammingDistance(self, instance1, instance2, ignore_index):
        """Calculates hamming distance between two instances ignoring the classification column"""
        # Do not keep the classification index as part of distance metric
        instance1_woClassify = instance1[:ignore_index] + instance1[ignore_index + 1:]
        instance2_woClassify = instance2[:ignore_index] + instance2[ignore_index + 1:]
        
        # Convert to binary strings
        instance1_woClassify = int(''.join(instance1_woClassify), 2)
        instance2_woClassify = int(''.join(instance2_woClassify), 2)
        
        # xor the two numbers, convert it a string representation of the binary number, then count the number of 1s
        return bin(instance1_woClassify ^ instance2_woClassify).count("1")

    def findClosest(self, target, k, ignore_index):
        """Finds the closest k instances in training data to a target in testing data"""
        closest = sorted(self.train_set, key=lambda n: self.hammingDistance(target, n, ignore_index))[:k]
        return closest

    def getClassification(self, closest, classification_index):
        """Returns classification of a testing instance based on majority vote by k-neighbors"""
        class_one = 0
        class_zero = 0

        for c in closest:
            if c[classification_index] == "1":
                class_one += 1
            else:
                class_zero += 1
        return "1" if class_one > class_zero else "0"

try:
    train_file = "./data/final_train.csv"
    test_file = "./data/final_test.csv"
    games = ["220", "113200", "283040", "1500", "72850", "220200", "55140", "1510", "8980", "4540"]
    # games = ["220"]
    knn = KNNClassifier(train_file, test_file, games)
    knn.classifyGames(5)

except Exception as e:
    typ, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)
