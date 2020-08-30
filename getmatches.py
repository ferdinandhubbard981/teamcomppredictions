import requests
import time

def sendrequest(url):
    successful = False
    response = []
    while successful == False:
        response = requests.get(url).json()
        try:
            if response["status"]["status_code"] == 429:
                print("\nrate limit exceeded\n")
                time.sleep(10)

            else:
                print("\nunknown error, status code: " + str(response["status"]["status_code"]) + "\n")
                time.sleep(10)

        except KeyError as e:
            successful = True
    return response
def getmatchhistoryids(apikey, encryptedaccountid):
    url = "https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + encryptedaccountid + "?api_key=" + apikey
    response = sendrequest(url)
    #print(response["totalGames"])
    gameids = []
    for game in response["matches"]:
        if game["queue"] == 420:
            gameids.append(game["gameId"])
    return gameids

def getencryptedaccountid(summonername, apikey):
    url = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonername + "?api_key=" + apikey
    response = sendrequest(url)
    return response["accountId"]

def getchamps(gameid, apikey):
        url = "https://euw1.api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key=" + apikey
        response = sendrequest(url)
        champions = []
        for player in response["participants"]:
            champions.append(player["championId"])
        return champions

def writecompositiontofile(champions, gameid):
    with open(str(gameid) + ".txt", "w") as f:
        for champion in champions:
            f.writeline(champion) # NOT TESTED YET


def getplayers(apikey, gameid):
    url = "https://euw1.api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key=" + apikey
    response = sendrequest(url)
    accountids = []
    for participant in response["participantIdentities"]:
        accountids.append(participant["player"]["accountId"])
    return accountids
def deleterepeatedgameids(gameids):
    repeatedgames = []
    with open("previousgameids.txt", "r") as f:
        previousgameids = f.read()
        previousgameids = previousgameids.splitlines()
        for oldid in previousgameids:
            for gameid in gameids:
                if str(gameid) == oldid:
                    gameids.remove(gameid)
    return gameids

def main():
    apikey = "RGAPI-d9ce9e7f-87cb-49b4-8684-9017e6c7b831"
    summonername = "hubbix"
    accountid = getencryptedaccountid(summonername, apikey)
    gameids = getmatchhistoryids(apikey, accountid)
    print(len(gameids))
    gameids = deleterepeatedgameids(gameids)
    print(len(gameids))
    #players = getplayers(apikey, gameids[0])
    #champions = getchamps(gameids[0], apikey)
if __name__ == "__main__":
    main()
