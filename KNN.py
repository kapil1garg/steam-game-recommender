"""
Implementation of bit-wise hamming distance k-nn classifier
"""

import random
import operator

import sys
import pdb
import traceback

DATA_SET = []
TRAINING_SET = []
TEST_SET = []
HEADER_ROW = []

def load_dataset(filename, split):
    """
    Load dataset

    Inputs:
        filename (string): csv file to be loaded in
        split (int): percentage of data that should be stored in training and test set (between 0-1)

    Output:
        None
    """
    # Open the file
    with open(filename, 'rb') as loaded_file:
        # Read the header line so it is not used in data
        first_row = loaded_file.next()
        first_row = ''.join(first_row.splitlines())
        HEADER_ROW.extend(first_row.split(','))

        for row in loaded_file:
            # Get rid of commas
            row = row.translate(None, ',')

            # Convert bit string into integer
            row = int(row, 2)

            # Add it to the full data set
            if row != 0:
                DATA_SET.append(row)

                # Add it to training or test data according to split
                if random.random() < split:
                    TRAINING_SET.append(row)
                else:
                    TEST_SET.append(row)

def hamming_distance(instance1, instance2):
    """
    Obtains hamming distance between two integers using bit-wise operators
    xor instance1 and instance2, convert to string representation, and count number of 1s

    Inputs:
        instance1 (int)
        instance2 (int)

    Output:
        (int): hamming distance between two integers
    """
    return bin(instance1 ^ instance2).count('1')

def find_closest(target, k):
    """
    Finds closest k matches to target

    Inputs:
        target (int): int representation of row
        k (int): number of closest other people to return

    Outputs:
        (list): list of k closest people to target
        (int): minimum distance to closest person to target
    """
    closest = sorted(TRAINING_SET, key=lambda n: hamming_distance(target, n))[:k]
    min_dist = [hamming_distance(target, x) for x in closest]
    return closest, min_dist

def get_games(target):
    """
    Gets list of games as strings for a bit string input

    Inputs:
        target (int): integer representation of games

    Outputs:
        (list): list of strings containing games to recommend
    """
    header_length = len(HEADER_ROW)
    bit_string = bin(target)[2:].zfill(header_length)
    return [HEADER_ROW[i] for i in range(header_length) if bit_string[i] == '1']

def find_different_games(instance1, instance2):
    """
    Gets games that are different between two instances

    Inputs:
        instance1 (int): integer representation of games owned by person 1
        instance2 (int): integer representation of games owned by person 2

    Outputs:
        (int): integer representing games not owned by instance 1 but owned by 2 (in binary)
    """
    return (instance1 | instance2) ^ instance2

def get_votes(neighbors, instance):
    """
    Counts votes from neighbors for current instance

    Inputs:
        neighbors (list): list of neighbors to vote on games
        insstance (int): current person

    Outputs:
        (dict): dictionary of games and number of votes per games
    """
    # Compress into 1 list
    compressed_games = sum([get_games(find_different_games(x, instance)) for x in neighbors], [])

    # Convert into dictionary and return
    return dict([game, compressed_games.count(game)] for game in compressed_games)

def get_top_games(ranked_games, n_games):
    """
    Gets top n games from ranked_games dictionary

    Inputs:
        ranked_games (dict): games with associated counts
        n (int): number of games to return

    Outputs:
        (list): list of top n games
    """
    sorted_games = sorted(ranked_games.items(), key=operator.itemgetter(1))
    top_n = sorted_games[-n_games:]
    return top_n[::-1]

def main():
    """
    Main Method
    """
    try:
        print "Begin"
        load_dataset('./data/games_by_username_all.csv', 0.99)
        print "Train: " + str(len(TRAINING_SET)) + " instances"
        print "Test: " + str(len(TEST_SET)) + " instances"
        print "# Games: " + str(len(HEADER_ROW))

        n_neighbors = 100
        print "Number of closest neighbors evaluated: " + str(n_neighbors)
        # print int(math.floor(math.log(TRAINING_SET[0])))
        closest, dist = find_closest(TEST_SET[0], n_neighbors)

        # print "Distance: " + str(dist)
        # print "Closest Node: ",
        # print closest

        # print get_games(closest[0])
        # print get_games(closest[1])
        # print get_games(TEST_SET[0])

        # print "\nGetting Game Delta for closest member"
        # print get_games(find_different_games(closest[0], TEST_SET[0]))

        # print "Getting Game Delta for 2nd closest member"
        # print get_games(find_different_games(closest[1], TEST_SET[0]))

        print

        print "All games different"
        print get_votes(closest, TEST_SET[0])
        print

        print "Top 5 games"
        print get_top_games(get_votes(closest, TEST_SET[0]), 5)
        print
    except Exception as e:
        typ, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

if __name__ == '__main__':
    main()
