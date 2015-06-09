import heapq
import csv
import random
import itertools
from multiprocessing import Process, Queue

import sys
import pdb
import traceback

class KNNClassifier:
    'k-NN Classifier using Hamming Distance'

    def __init__(self, train_data, test_data):
        train_header_row, self.train_set = self.loadDataset(train_data)
        test_header_row, self.test_set = self.loadDataset(test_data)

        # Check if training and test set are from the same dataset
        if set(train_header_row) != set(test_header_row):
            raise ValueError("Header row for test set does not match header for train. Please make sure test and train are from the same dataset.")
        else:
            self.header_row = train_header_row

        self.total_players = len(self.test_set)
        self.players_per_game_test = self.countPlayers()
        self.classify_output = []

        # Print some statistics about the test and training data
        print "Total examples: " + str(len(self.train_set) + len(self.test_set))
        print "Number training players: " + str(len(self.train_set))
        print "Number testing players: " + str(len(self.test_set))
        print "Number of games: " + str(len(self.header_row))
        print 

    def nthBit(self, i, n):
        """Get the nth bit of the integer i"""
        return "0" if not i & (1 << n) else "1"

    def countPlayers(self):
        """Count number of players for each game"""
        header_length = len(self.header_row)
        player_game_count = [0 for x in range(header_length)]
        for i in range(len(self.test_set)):
            for j in range(header_length):
                player_game_count[j] += int(self.nthBit(self.test_set[i], header_length - j - 1))
        return player_game_count

    def loadDataset(self, filename):
        """Loads data from a csv file"""
        # Open the file
        with open(filename, 'rb') as f:
            # Read the header line so it is not used in data
            header = f.next()
            header = ''.join(header.splitlines()).split(",")
            data = [int(row.translate(None, ","), 2) for row in f]

            return header, data

    def classifyGame(self, k, game_index, game_name, out_queue):
        """Runs kNN classificaion on each game in the inputted gamelist"""
        game_id = self.header_row[game_index]
        algorithm_name = "kNN (k = " + str(k) + ")"
        g_index = len(self.header_row) - self.header_row.index(game_id) - 1
        true_labels = []
        classification = []

        print "Testing game " + str(game_name) + " with " + str(k) + " nearest neighbors"

        for i in range(len(self.test_set)):
            t = self.test_set[i]
            true_labels.append(self.nthBit(t, g_index))
            classification.append(self.getClassification(self.findClosest(t, k, g_index), g_index))

        print "Testing game " + str(game_name) + " with " + str(k) + " nearest neighbors completed. Accuracy results below."
        confusion_matrix = self.confusion(true_labels, classification)
        result = [
            game_name,
            game_id,
            algorithm_name,
            self.players_per_game_test[game_index],
            self.players_per_game_test[game_index]/float(self.total_players)
        ]
        result += self.generateStatistics(confusion_matrix)
        out_queue.put(result) # for multithreading
    
    def generateStatistics(self, confusion_matrix):
        """Print out accuracy statistics"""
        EPSILON = sys.float_info.epsilon # add to avoid division by 0
        tp_0 = confusion_matrix["0"]["0"] + EPSILON
        tn_0 = confusion_matrix["1"]["1"] + EPSILON
        fp_0 = confusion_matrix["0"]["1"] + EPSILON
        fn_0 = confusion_matrix["1"]["0"] + EPSILON

        tp_1 = confusion_matrix["1"]["1"] + EPSILON
        tn_1 = confusion_matrix["0"]["0"] + EPSILON
        fp_1 = confusion_matrix["1"]["0"] + EPSILON
        fn_1 = confusion_matrix["0"]["1"] + EPSILON

        accuracy = self.accuracy(tp_0, tn_0, fn_0, fp_0)
        precision_0 = self.precision(tp_0, fp_0)
        recall_0 = self.recall(tp_0, fn_0)
        f_measure_0 = self.f_measure(precision_0, recall_0)
        precision_1 = self.precision(tp_1, fp_1)
        recall_1 = self.recall(tp_1, fn_1)
        f_measure_1 = self.f_measure(precision_1, recall_1)

        output = [
            accuracy,
            precision_0,
            recall_0,
            f_measure_0,
            precision_1,
            recall_1,
            f_measure_1
        ]

        print "Accuracy: " + str(100.0 * accuracy) + "%"
        print "Precision (0): " + str(precision_0)
        print "Recall (0): " + str(recall_0)
        print "F1 (0): " + str(f_measure_0)
        print "Precision (1): " + str(precision_1)
        print "Recall (1): " + str(recall_1)
        print "F1 (1): " + str(f_measure_1)

        print "a    b"
        print str(confusion_matrix["0"]["0"]) + " | " + str(confusion_matrix["0"]["1"]) + "   a = 0"
        print "-----"
        print str(confusion_matrix["1"]["0"]) + " | " + str(confusion_matrix["1"]["1"])  +  "   b = 1\n"

        return output 

    def confusion(self, trueLabels, classifications):
        """Generates confusion matrix"""
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
      return (float(tp + tn)/float(tp + tn + fn + fp))

    def hammingDistance(self, instance1, instance2, ignore_index):
        """Calculates hamming distance between two instances ignoring the classification column"""

        # xor the two numbers, convert it a string representation of the binary number, then count the number of 1s
        # If the classification index of the two instances will cause a difference in distance, subtract 1
        return bin(instance1 ^ instance2).count("1") - (self.nthBit(instance1, ignore_index) != self.nthBit(instance2, ignore_index))

    def findClosest(self, target, k, ignore_index):
        """Finds the closest k instances in training data to a target in testing data"""

        return heapq.nsmallest(k, self.train_set, key=lambda n: self.hammingDistance(target, n, ignore_index))

    def getClassification(self, closest, classification_index):
        """Returns classification of a testing instance based on majority vote by k-neighbors"""
        class_one = len([c for c in closest if self.nthBit(c, classification_index) == "1"])
        class_zero = len(closest) - class_one

        return "1" if class_one > class_zero else "0"

try:
    # Setup output
    random.seed("ML349")
    csv_header = [
                    "Game Name",
                    "SteamID",
                    "Algorithm",
                    "Number Players",
                    "% Players of Training Set",
                    "Accuracy",
                    "Precision (0)",
                    "Recall (0)",
                    "F1 (0)",
                    "Precision (1)",
                    "Recall (1)",
                    "F1 (1)"
    ]
    game_results = []
    with open("data/games_by_username_all.csv", "r") as f:
        game_list = f.next().rstrip().split(",")

    # Build kNN
    train_file = "./data/final_train.csv"
    test_file = "./data/final_test.csv"
    knn = KNNClassifier(train_file, test_file)

    # Classify test data for each game and get accuracy statistics
    q = Queue() # create queue to hold output as it finishes
    jobs = [] # list of jobs run
    
    for i in itertools.chain(xrange(0, 50), random.sample(xrange(50, len(game_list)), 450)):
        # start a process for each iteration and store its output in the queue
        p = Process(target = knn.classifyGame, args = (5, i, game_list[i], q))
        jobs.append(p)
        p.start()
    
    # combine output into one list
    for i in range(len(jobs)):
        game_results.append(q.get())

    # wait until each job is finished
    for p in jobs:
        p.join()

    # export
    with open("./data/knn_5_results.csv", "wb") as f:
        csv_writer = csv.writer(f, delimiter=",")
        csv_writer.writerow(csv_header)
        for r in game_results:
            csv_writer.writerow(r)

except Exception as e:
    typ, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)

