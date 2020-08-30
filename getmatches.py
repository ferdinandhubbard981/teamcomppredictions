import requests
import time

def sendrequest(url):
    apikeys = ["RGAPI-9fdbc9a6-1a65-4b82-bfe0-fe5bfcc57370", "RGAPI-94872c2a-cb5e-4f46-bec1-74a9da9e45e9"]
    index = 0
    successful = False
    response = []
    while successful == False:
        response = requests.get(url + apikeys[index]).json()
        try:
            if response["status"]["status_code"] == 429:
                print("\nrate limit exceeded\n")
                index += 1
                if index == len(apikeys):
                    index = 0
                time.sleep(0.5)

            else:
                print("\nunknown error, status code: " + str(response["status"]["status_code"]) + "\n")
                time.sleep(10)

        except KeyError as e:
            successful = True
    return response
def getmatchhistoryids(encryptedaccountid):
    url = "https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + encryptedaccountid + "?api_key="
    response = sendrequest(url)
    #print(response["totalGames"])
    gameids = []
    for game in response["matches"]:
        if game["queue"] == 420:
            gameids.append(game["gameId"])
    return gameids

def writeoldgameids(gameids):
    with open("oldgameids.txt", "a") as f:
        for gameid in gameids:
            f.write(str(gameid) + "\n")

def getencryptedaccountid(summonername):
    url = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonername + "?api_key="
    response = sendrequest(url)
    return response["accountId"]

def getchamps(gameid):
        url = "https://euw1.api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key="
        response = sendrequest(url)
        champions = []
        for player in response["participants"]:
            champions.append(player["championId"])
        return champions

def writechampionstofile(champions, gameid):
    with open("games/" + str(gameid) + ".txt", "w") as f:
        for champion in champions:
            f.write(str(champion) + "\n") # NOT TESTED YET


def getplayers(gameid):
    url = "https://euw1.api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key="
    response = sendrequest(url)
    accountids = []
    for participant in response["participantIdentities"]:
        accountids.append(participant["player"]["accountId"])
    return accountids

def writenewaccountids(players):
    with open("newaccountids.txt", "a") as f:
        for player in players:
            f.write(player + "\n")


def writeoldaccountid(id):
    with open("oldaccountids.txt", "a") as f:
        f.write(id + "\n")


def deleterepeatedgameids(gameids):
    repeatedgames = []
    with open("oldgameids.txt", "r") as f:
        previousgameids = f.read().splitlines() #problem maybe
        for oldid in previousgameids:
            for a in gameids:
                if str(gameid) == oldid:
                    gameids.remove(gameid)
    return gameids
def getnewaccountids(amount):
    chosenaccountids = []
    allaccountids = []
    with open("newaccountids.txt", "r") as f:
        allaccountids = f.read().splitlines()
        if amount > len(allaccountids):
            amount = len(allaccountids)
        chosenaccountids = allaccountids[:amount]

        allaccountids = allaccountids[amount:]
    #to remove ids that i have just read and put them in temp file in case of misclicks
    with open("newaccountids.txt", "w") as f:
        for id in allaccountids:
            f.write(id + "\n")
    with open("tempdeletedaccountids.txt", "w") as f:
        for id in chosenaccountids:
            f.write(id + "\n")
    return chosenaccountids

def cycle(accountid):
    gameids = getmatchhistoryids(accountid)
    gameids = deleterepeatedgameids(gameids)
    #gameids = [gameids[0]] #TEMPORARY
    players = []
    for gameid in gameids:
        newplayers = getplayers(gameid)
        newplayers.remove(accountid)
        for player in newplayers: #merging the newplayers list to the full players list
            players.append(player)

        champions = getchamps(gameid)
        writechampionstofile(champions, gameid)
        print("done")

    writeoldgameids(gameids)
    writenewaccountids(players)
    writeoldaccountid(accountid)


def main():
    numofaccountids = 2
    #summonername = "hubbix" #if new accountids is empty
    #accountids = [getencryptedaccountid(summonername)] #if new accountids is empty
    accountids = getnewaccountids(numofaccountids)
    for accountid in accountids:
        cycle(accountid)

if __name__ == "__main__":
    main()
