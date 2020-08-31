import requests
import time
from shutil import copyfile
import sys
import json

index = 1
failed = 0
success = 0
def sendrequest(url, randomapikey): #apikeys index 0 will always be my main account due to riot games attempt at preventing the use of multiple developer api keys
    apikeys = []
    global index
    #index = 1 #primary api key is only used for the operations that require a constant api key (explained above) others can be used interchangeably for when rate limit is reached
    successful = False
    response = []
    while successful == False:
        actualindex = index
        if randomapikey == False:
            actualindex = 0
        try:
            response = requests.get(url + apikeys[actualindex]).json()
        except OSError:
            print("disconnected")
            time.sleep(1)
        #print(url + apikeys[actualindex])
        try:
            if response["status"]["status_code"] == 429:
                print("\nrate limit exceeded\n")
                if randomapikey == True:
                    index += 1
                    if index == len(apikeys):
                        index = 1
                time.sleep(0.5)

            elif response["status"]["status_code"] == 403:
                print("\n wrong api key or it had expired\n")
                if randomapikey == True:
                    index += 1
                    if index == len(apikeys):
                        index = 1

            else:
                print("\nunknown error, status code: " + str(response["status"]["status_code"]) + "\n")
                time.sleep(10)

        except KeyError:
            successful = True
        except TimeoutError:
            print("timeout")
        except TypeError:
            pass
    return response


def getmatchhistoryids(encryptedaccountid):
    url = "https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + encryptedaccountid + "?api_key="
    response = sendrequest(url, False) #use primary api key
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
    response = sendrequest(url, False) #use primary api key
    return response["accountId"]

def addchampstoorderedlist(response):
    champions = [None] * 10
    for player in response["participants"]:
        if player["timeline"]["lane"] == "TOP":
            if player["teamId"] == 100:
                champions[0] = player["championId"]
            elif player["teamId"] == 200:
                champions[5] = player["championId"]

        elif player["timeline"]["lane"] == "JUNGLE":
            if player["teamId"] == 100:
                champions[1] = player["championId"]
            elif player["teamId"] == 200:
                champions[6] = player["championId"]

        elif player["timeline"]["lane"] == "MIDDLE":
            if player["teamId"] == 100:
                champions[2] = player["championId"]
            elif player["teamId"] == 200:
                champions[7] = player["championId"]

        elif player["timeline"]["lane"] == "BOTTOM" and player["timeline"]["role"] == "DUO_CARRY":
            if player["teamId"] == 100:
                champions[3] = player["championId"]
            elif player["teamId"] == 200:
                champions[8] = player["championId"]

        elif player["timeline"]["lane"] == "BOTTOM" and player["timeline"]["role"] == "DUO_SUPPORT":
            if player["teamId"] == 100:
                champions[4] = player["championId"]
            elif player["teamId"] == 200:
                champions[9] = player["championId"]

    return champions

def convertchampsfromidtoname(championids):
    champions = []
    with open("champion.json", encoding="utf-8") as f:
        data = json.load(f)
        for championid in championids:
            foundchamp = False
            for champion in data["data"]:
                if str(championid) == data["data"][champion]["key"]:
                    champions.append(data["data"][champion]["id"].lower())
                    foundchamp = True
            if foundchamp == False:
                champions.append(championid)
    return champions

def getteamblueresult(response):
    for team in response["teams"]:
        if team["teamId"] == 100:
            return team["win"] #Win or Fail

def getgamedata(gameid):
        url = "https://euw1.api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key="
        response = sendrequest(url, True) #use random api key
        champions = addchampstoorderedlist(response)
        champions = convertchampsfromidtoname(champions)
        teamblueresult = getteamblueresult(response)
        gamedata = champions
        gamedata.append(teamblueresult)
        return gamedata

def writegamedatatofile(gamedata, gameid):
    with open("games/" + str(gameid) + ".txt", "w") as f:
        for entry in gamedata:
            f.write(str(entry) + "\n")


def getplayers(gameid):
    url = "https://euw1.api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key="
    response = sendrequest(url, True) #random api key works if getting summonerName, not accountid
    playernames = []
    for participant in response["participantIdentities"]:
        playernames.append(participant["player"]["summonerName"].replace(" ", ""))
    return playernames

def writenewsummonernames(summonernames):
    with open("newsummonernames.bin", "ab") as f:
        for summonername in summonernames:
            f.write((summonername + " ").encode("utf-8"))


def writeoldsummonername(summonername):
    with open("oldsummonernames.txt", "a") as f:
        f.write(str(summonername.encode("utf-8")))
        f.write("\n")

def deleterepeatedgameids(gameids):
    repeatedgames = []
    with open("oldgameids.txt", "r") as f:
        previousgameids = f.read().splitlines() #problem maybe
        for oldid in previousgameids:
            for gameid in gameids:
                if str(gameid) == oldid:
                    gameids.remove(gameid)
    return gameids
def getnewsummonernames(amount):
    chosensummonernames = []
    allsummonernames = []

    copyfile("newsummonernames.bin", "backup/newsummonernames.bin")
    copyfile("oldgameids.txt", "backup/oldgameids.txt")     #backup
    copyfile("oldsummonernames.txt", "backup/oldsummonernames.txt")

    with open("newsummonernames.bin", "rb") as f:
        allsummonernames = bytes(list(f.read())).decode("utf-8").split()
        if amount > len(allsummonernames):
            amount = len(allsummonernames)
        chosensummonernames = allsummonernames[:amount]

        allsummonernames = allsummonernames[amount:] #removes current summonernames(that are in use) so they can be put back file
    with open("newsummonernames.bin", "wb") as f:
        for summonername in allsummonernames:
            f.write((summonername + " ").encode("utf-8"))

    return chosensummonernames

def cycle(summonername):
    global failed, success
    accountid = getencryptedaccountid(summonername)
    gameids = getmatchhistoryids(accountid) #used less often
    gameids = deleterepeatedgameids(gameids) #used less often
    players = []
    for gameid in gameids:
        newplayers = getplayers(gameid) #used frequently
        try:
            newplayers.remove(summonername)
        except ValueError:
            print("didnt find " + summonername + " because he changed his name recently")
            continue

        for player in newplayers: #repeatedly merging the newplayers list to the full players list
            players.append(player)

        gamedata = getgamedata(gameid) #used frequently
        if None in gamedata:
            print("line 68 function, addchampstoorderedlist 'role' might be None")
            failed += 1
            #sys.exit()
        else:
            success += 1
            writegamedatatofile(gamedata, gameid)
            print("done")


    writeoldgameids(gameids)
    writenewsummonernames(players)
    writeoldsummonername(summonername) #not necessary, just for seeing how many iterations have been made


def main():
    numofplayeriterations = 10
    #summonernames = ["hubbix"] #if newsummonernames.txt is empty
    #for i in range(numofplayeriterations)
    #    summonernames = getnewsummonernames(1)
    #    cycle(summonername) #for a fixed number of iterations
    while True:
        try:
            summonernames = getnewsummonernames(1)
            if (len(summonernames) == 0):
                print("no summoner names")
                sys.exit()
            cycle(summonernames[0])
        except KeyboardInterrupt:
            print("copy all files from backup into main folder and overwrite")
            continue
        try:
            for i in range(100):
                print("you can quit safely now")
            time.sleep(5)
        except KeyboardInterrupt:
            print("all files ok")
            continue

    print ("success: " + str(success) + " failed: " + str(failed))

if __name__ == "__main__":
    main()
