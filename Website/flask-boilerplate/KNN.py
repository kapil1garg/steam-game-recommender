import heapq

def loadDataset(filename):
    dataset = []

    # Open the file
    with open(filename, 'rb') as f:
        # Read the header line so it is not used in data
        f.next()

        for row in f:
            # Get rid of commas
            row = row.translate(None, ",")

            # Convert bit string into integer
            row = int(row, 2)

            # Add it to the full data set
            if row != 0: 
                dataset.append(row)

    return dataset

def hammingDistance(instance1, instance2):
    # xor the two numbers, convert it a string representation of the binary number, then count the number of 1s
    return bin(instance1 ^ instance2).count("1")

def findClosest(dataset, target, k):
    closest = heapq.nsmallest(k, dataset, key=lambda n: hammingDistance(target, n))
    return closest

def getGames(header_row, target):
    header_length = len(header_row)
    bit_string = bin(target)[2:].zfill(header_length)
    return [header_row[i] for i in range(header_length) if bit_string[i] == "1"]

def findDifferentGames(closest, instance):
    return (closest | instance) ^ instance

def getVotes(header_row, neighbors, instance):
    # Compress into 1 list
    compressed_games = sum([getGames(header_row, findDifferentGames(x, instance)) for x in neighbors], [])

    # Convert into dictionary and return
    return dict([game, compressed_games.count(game)] for game in compressed_games)

def getTopGames(ranked_games, n):
    sorted_games = sorted(ranked_games.items(), key=lambda x: x[1])
    top_n = sorted_games[-n:]
    return top_n[::-1]
