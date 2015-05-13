#!python2
import requests
import json

def main():
    username = 'paep3nguin'
    api_key = 'INSERT_KEY_HERE'
    id_response_json = json.loads(requests.get('http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=' + api_key + '&vanityurl=' + username).text)
    # print json.dumps(id_response_json)

    if id_response_json['response']['success'] == 1:
        steam_id = str(id_response_json['response']['steamid'])
        print steam_id

        games_response_json = json.loads(requests.get('http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' + api_key + '&steamid=' + steam_id + '&format=json').text)
        print json.dumps(games_response_json)

if __name__ == '__main__':
    main()
