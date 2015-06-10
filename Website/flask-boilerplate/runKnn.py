import sys
import pdb
import traceback
import json

import KNN

import requests as reqGet

def get_keys(filepath):
    key_list = []
    with open(filepath) as keys:
        for key in keys: 
            key_list.append(key.rstrip())
    return key_list

def getUserGames(nickname, api_key):
    session = reqGet.Session()
    session.mount("http://", reqGet.adapters.HTTPAdapter(max_retries=10))
    print "Retrieving user and game data for " + nickname + "..."
    id_response_json = json.loads(session.get(url='http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=' + api_key + '&vanityurl=' + nickname).text)

    # If user is found
    if id_response_json and id_response_json['response']['success'] == 1:
        steam_id = str(id_response_json['response']['steamid'])

        # Get the list of owned games
        games_response_json = json.loads(session.get(url='http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' + api_key + '&steamid=' + steam_id).text)

        # If the user has games
        if games_response_json['response'] and games_response_json['response']['game_count'] > 0:
            print "Success!"
            return games_response_json['response']['games']
        else:
            print "not enough games. User will be ignored."
    else:
        print "not found. User will be ignored."

def loadGameIDs(filename):
    """Loads game naems from a csv file"""
    # Open the file
    with open(filename, 'rb') as f:
        # Read the header line so it is not used in data
        header = f.next()
        header = ''.join(header.splitlines()).split(",")
        header = [int(x) for x in header]

        return header

def gameRecommendations(u_name):
    # Get API key
    all_api_keys1 = get_keys("./num1.txt")
    all_api_keys2 = get_keys("./num2.txt")
    api_key = str(all_api_keys1[0]) + str(all_api_keys2[0])

    if len(api_key) != 32:
        print("Uh-oh, don't forget to enter your API key!")
        return

    # Set up a requests session to allow retries when a request fails
    session = reqGet.Session()
    session.mount("http://", reqGet.adapters.HTTPAdapter(max_retries=10))

    games_response_json = getUserGames(u_name, api_key)

    all_games = loadGameIDs("./static/data/id_header.csv")

    # Get all of the game names and IDs from steam and save them in a dictionary for easy usage
    game_list = json.loads(session.get(url="http://api.steampowered.com/ISteamApps/GetAppList/v2").text)['applist']['apps']
    game_dict = {}
    for game in game_list:
        game_dict[game['appid']] = game

    user_game_array = ["0"] * len(all_games)

    if not games_response_json:
        return

    for game in games_response_json:
        if game['appid'] in all_games:
            game_index = all_games.index(game['appid'])
            user_game_array[game_index] = "1"

    all_games = [game_dict[x]['name'] for x in all_games]

    game_bit_string = int(''.join(user_game_array), 2)
    dataset = KNN.loadDataset("./static/data/games_by_username_all.csv")
    closest = KNN.findClosest(dataset, game_bit_string, 100)
    return KNN.getTopGames(KNN.getVotes(all_games, closest, game_bit_string), 5)

if __name__ == '__main__':
    # For debugging purposes
    # Tells pdb to break and debug when something bad happens
    # Sort of like a real IDE now!
    try:
        print gameRecommendations("paep3nguin")

    except Exception as e:
        typ, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
