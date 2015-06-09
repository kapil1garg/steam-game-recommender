import sys
import pdb

import traceback
import requests
import string
import json

def get_keys(filepath):
    key_list = []
    with open(filepath) as keys:
        for key in keys: 
            key_list.append(key.rstrip())
    return key_list

u_name = "paep3nguin"

def getUsername(nickname, api_key):
    username = nickname
    session = requests.Session()
    session.mount("http://", requests.adapters.HTTPAdapter(max_retries=10))
    print "Retrieving user and game data for " + username + "...",
    id_response_json = json.loads(session.get(url='http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=' + api_key + '&vanityurl=' + username).text)
    # print json.dumps(id_response_json)
   
    # List of game app_ids for games with at least min_users
    game_id_list = []

    # List of game names for games with at least min_users
    game_names = []

    # Dictionary of users where the key is their username and the data is a tuple of their steam_id and a dictionary of games
    user_cache = {}

    # If user is found
    if id_response_json and id_response_json['response']['success'] == 1:
        steam_id = str(id_response_json['response']['steamid'])

        # Get the list of owned games
        games_response_json = json.loads(session.get(url='http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' + api_key + '&steamid=' + steam_id).text)

        # If the user has games
        if games_response_json['response'] and games_response_json['response']['game_count'] > 0:
            return games_response_json['response']['games']
        else:
            print "not enough games. User will be ignored."
            return
    else:
        print "not found. User will be ignored."

def loadDataset(filename):
        """Loads data from a csv file"""
        # Open the file
        with open(filename, 'rb') as f:
            # Read the header line so it is not used in data
            header = f.next()
            header = ''.join(header.splitlines()).split(",")

            return header

def main():
    # Get API key
    all_api_keys1 = get_keys("./num1.txt")
    all_api_keys2 = get_keys("./num2.txt")
    api_key = str(all_api_keys1[0]) + str(all_api_keys2[0])

    if len(api_key) != 32:
        print("Uh-oh, don't forget to enter your API key!")
        return

    # Set up a requests session to allow retries when a request fails
    session = requests.Session()
    session.mount("http://", requests.adapters.HTTPAdapter(max_retries=10))

    games_response_json = getUsername(u_name, api_key)

    all_games = loadDataset("./data/games_by_username_all.csv")


    # Get all of the game names and IDs from steam and save them in a dictionary for easy usage
    game_list = json.loads(session.get(url="http://api.steampowered.com/ISteamApps/GetAppList/v2").text)['applist']['apps']
    game_dict = {}
    for game in game_list:
        game_dict[game['appid']] = game

    user_game_array = [0]*len(all_games)

    for game in games_response_json:
        game = game_dict[game['appid']]['name'].encode('ascii', 'ignore').translate(None, string.punctuation).replace(" ", "_")
        game_index = all_games.index(game)
        user_game_array[game_index] = 1

    print len(games_response_json)

if __name__ == '__main__':
    # For debugging purposes
    # Tells pdb to break and debug when something bad happens
    # Sort of like a real IDE now!
    try:
        main()
    except Exception as e:
        typ, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)