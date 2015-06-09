#!python2

import csv
import random
import itertools
import weka.core.jvm as jvm
from weka.core.converters import Loader
from weka.classifiers import Classifier, Evaluation
from weka.core.classes import Random

import sys
import pdb
import traceback

def classify_and_save(classifier, name, outfile):
    random.seed("ML349")

    csv_header = [
                    "Game Name",
                    "SteamID",
                    "Algorithm",
                    "Number Players",
                    "%Players of Training Set",
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

    loader = Loader(classname="weka.core.converters.ArffLoader")
    train = loader.load_file("data/final_train.arff")
    test = loader.load_file("data/final_test.arff")

    count = 0
    for i in itertools.chain(xrange(0, 50), random.sample(xrange(50, len(game_list)), 450)):
        train.class_index = i
        test.class_index = i
        count += 1

        classifier.build_classifier(train)

        evaluation = Evaluation(train)
        evaluation.test_model(classifier, test)

        confusion = evaluation.confusion_matrix
        num_players = sum(confusion[1])
        steam_id = repr(train.class_attribute).split(" ")[1]
        result = [
                    game_list[i],
                    steam_id,
                    name,
                    int(num_players),
                    num_players/1955,
                    evaluation.percent_correct,
                    evaluation.precision(0),
                    evaluation.recall(0),
                    evaluation.f_measure(0),
                    evaluation.precision(1),
                    evaluation.recall(1),
                    evaluation.f_measure(1)
        ]

        game_results.append(result)
        print "\nResult #{2}/500 for {0} (SteamID {1}):".format(game_list[i], steam_id, count),
        print evaluation.summary()

    with open(outfile, "wb") as f:
        csv_writer = csv.writer(f, delimiter=",")
        csv_writer.writerow(csv_header)
        for r in game_results:
            csv_writer.writerow(r)


if __name__ == "__main__":
    try:
        jvm.start(max_heap_size="512m")

        # d_tree = Classifier(classname="weka.classifiers.trees.J48", options=["-C", "0.25", "-M", "2"])
        # classify_and_save(d_tree, "Decision Tree", "data/d_tree_results.csv")

        naive_bayes = Classifier(classname="weka.classifiers.bayes.NaiveBayes")
        classify_and_save(naive_bayes, "Naive Bayes", "data/naive_bayes_results.csv")
    except Exception as e:
        typ, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
    finally:
        jvm.stop()
