#!python2
import sys
import pdb

import traceback
import requests
import json

def main():
    # Our API key DON'T FORGET TO REMOVE BEFORE COMMITTING
    api_key = 'api_key_here'

    # Minimum number of users a game must have before being used in data
    min_users = 4

    # Require that a user has played a game before using it for data
    require_play = True

    # An array counting the number of users for each game
    # The index is the app_id and the entry is the number of users
    game_users = [0] * 40000

    # List of game app_ids for games with at least min_users
    game_id_list = []

    # List of game names for games with at least min_users
    game_names = []

    # Dictionary of users where the key is their username and the data is a tuple of their steam_id and a dictionary of games
    user_cache = {}

    with open('data/steam_usernames_test.csv', 'r') as f:
        for username in f:
            username = username.rstrip()
            #print("Retrieving user and game data for " + username)
            id_response_json = json.loads(requests.get('http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=' + api_key + '&vanityurl=' + username).text)
            # print json.dumps(id_response_json)

            # If user is found
            if id_response_json and id_response_json['response']['success'] == 1:
                steam_id = str(id_response_json['response']['steamid'])
                # print(steam_id)

                # Get the list of owned games
                games_response_json = json.loads(requests.get('http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' + api_key + '&steamid=' + steam_id).text)
                # print(json.dumps(games_response_json))

                # If the user has games
                if games_response_json['response'] and games_response_json['response']['game_count'] > 0:
                    # Get their steam id and games and save it in our cache
                    user_cache[username] = (steam_id, games_response_json['response']['games'])

                    for game in games_response_json['response']['games']:
                        app_id = game['appid']
                        play_time = int(game['playtime_forever'])

                        # If the game has been played, increment the user count for that game
                        if play_time != 0 or not require_play:
                            game_users[app_id / 10] += 1

    # Look for games with at least min_users, add it to the list of games to consider
    for app_id in range(1, len(game_users)):
        if game_users[app_id] >= min_users:
            game_schema_response_json = json.loads(requests.get("http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key=" + api_key + "&appid=" + str(app_id * 10)).content)
            if game_schema_response_json:
                game_name = game_schema_response_json['game'].get('gameName', str(app_id * 10)).encode('ascii', 'replace')
                game_name = game_name if game_name else str(app_id * 10)

                if "ValveTestApp" not in game_name:
                    # print("Found game name for id " + str(app_id * 10))
                    game_names.append(game_name if game_name else str(app_id * 10))
                    game_id_list.append(app_id * 10)

    # The number of games that we've decided to collect data on
    game_count = len(game_id_list)

    # Lets start writing some data
    # Data is a bit string where 1 means owned 0 means not owned
    with open('data/games_by_username.csv', 'w') as w:
        w.write(",".join(game_names) + "\n")
        #w.write(",".join([str(x) for x in game_id_list]) + "\n")
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
