#!python2
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

def main():
    # Get API key
    all_api_keys = get_keys("./APIs/steam.txt")
    api_key = str(all_api_keys[0])

    if len(api_key) != 32:
        print("Uh-oh, don't forget to enter your API key!")
        return

    # Minimum number of users a game must have before being used in data
    # Can be adjusted after user data is pulled
    min_users = 5

    # Require that a user has played a game before using it for data
    require_play = True

    # An array counting the number of users for each game
    # The index is the app_id and the entry is the number of users
    game_users = [0] * 400000

    # List of game app_ids for games with at least min_users
    game_id_list = []

    # List of game names for games with at least min_users
    game_names = []

    # Dictionary of users where the key is their username and the data is a tuple of their steam_id and a dictionary of games
    user_cache = {}

    with open('data/steam_id.csv', 'rU') as f:
        for username in f:
            username = username.rstrip()
            print "Retrieving user and game data for " + username + "...",
            id_response_json = json.loads(requests.get('http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=' + api_key + '&vanityurl=' + username).text)
            # print json.dumps(id_response_json)

            # If user is found
            if id_response_json and id_response_json['response']['success'] == 1:
                steam_id = str(id_response_json['response']['steamid'])

                # Get the list of owned games
                games_response_json = json.loads(requests.get('http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' + api_key + '&steamid=' + steam_id).text)

                # If the user has games
                if games_response_json['response'] and games_response_json['response']['game_count'] > 0:
                    print "success"

                    # Get their steam id and games and save it in our cache
                    user_cache[username] = (steam_id, games_response_json['response']['games'])

                    for game in games_response_json['response']['games']:
                        app_id = game['appid']
                        play_time = int(game['playtime_forever'])

                        # If the game has been played, increment the user count for that game
                        if play_time != 0 or not require_play:
                            game_users[app_id] += 1
                else:
                    print "not enough games. User will be ignored."
            else:
                print "not found. User will be ignored."

    # Get all of the game names and IDs from steam and save them in a dictionary for easy usage
    game_list = json.loads(requests.get("http://api.steampowered.com/ISteamApps/GetAppList/v2").text)['applist']['apps']
    game_dict = {}
    for game in game_list:
        game_dict[game['appid']] = game

    # Display results and give a chance to adjust min_users
    print("A total of " + str(len(user_cache)) + " users were successfully found")

    desired_min_users = min_users

    while desired_min_users != "okay":
        min_users = int(desired_min_users)
        game_count = sum(i >= min_users for i in game_users)
        print("\nThe current minimum number of users a game must have to be considered is: " + str(min_users))
        print(str(game_count) + " games satisfy this criteria")
        desired_min_users = raw_input("Type a new minimum number of users to try it out, else type okay to continue: ")

    # Look for games with at least min_users, add it to the list of games to consider
    for app_id in range(1, len(game_users)):
        if game_users[app_id] >= min_users:
            game_name = game_dict[app_id]['name'].encode('ascii', 'ignore').translate(None, string.punctuation).replace(" ", "_")

            game_names.append(game_name)
            game_id_list.append(app_id)

    # The number of games that we've decided to collect data on
    game_count = len(game_id_list)

    # Lets start writing some data
    # Data is a bit string where 1 means owned 0 means not owned
    with open('data/games_by_username_all_ids.arff', 'w') as w:
        w.write("@RELATION steam_users\n\n")
        for id in game_id_list:
            w.write("@ATTRIBUTE " + name + " {0,1}\n")
        w.write("\n@DATA\n")
        # w.write(",".join([str(x) for x in game_id_list]) + "\n")
        for username in user_cache:
            #print("Processing user data for " + username)
            steam_id = user_cache[username][0]
            data = [0] * game_count

            # Go through their games
            for game in user_cache[username][1]:
                app_id = game['appid']
                play_time = game['playtime_forever']

                # If the game has been played, save that in the data bit string
                if (play_time or not require_play) and app_id in game_id_list:
                    data[game_id_list.index(app_id)] = 1

            # Write the data
            w.write(",".join([str(x) for x in data]) + "\n")

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