import time
import requests
import time
from shutil import copyfile
import sys
import json
from os import remove
from multiprocessing import Process
from multiprocessing.dummy import Pool as ThreadPool


failed = 0
success = 0
def sendrequest(url, index, indexoverride=None): #apikeys index 0 will always be my main account due to riot games attempt at preventing the use of multiple developer api keys
    apikeys = []
    #index = 1 #primary api key is only used for the operations that require a constant api key (explained above) others can be used interchangeably for when rate limit is reached
    successful = False
    response = []
    while successful == False:
        actualindex = index
        if indexoverride != None:
            actualindex = indexoverride
        try:
            response = requests.get(url + apikeys[actualindex]).json()
        except OSError:
            print("disconnected")
            time.sleep(1)
        #print(url + apikeys[actualindex])
        try:
            if response["status"]["status_code"] == 429:
                print("\nrate limit exceeded on index " + str(actualindex) + "\n")
                if indexoverride == None:
                    index += 1
                    if index == len(apikeys):
                        index = 0
                time.sleep(0.5)

            elif response["status"]["status_code"] == 403:
                print("\n wrong api key or it has expired with index " + str(actualindex) + "\n")
                if indexoverride == None:
                    index += 1
                    if index == len(apikeys):
                        index = 0

            elif response["status"]["status_code"] == 404:
                print("\n 404 error message: " + response["status"]["message"] + "\n")
                if "summoner not found" in response["status"]["message"]:
                    print("summoner account doesn't exist anymore")
                return "error", index

            else:
                print("\nunknown error, status code: " + str(response["status"]["status_code"]) + "\n")
                time.sleep(10)

        except KeyError:
            successful = True
        except TimeoutError:
            print("timeout")
        except TypeError:
            pass
    return response, index


def getmatchhistoryids(encryptedaccountid, index):
    url = "https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + encryptedaccountid + "?api_key="
    response, index = sendrequest(url, index, indexoverride=index) #use primary api key
    if response == "error":
        return ["error"], index
    gameids = []
    for game in response["matches"]:
        if game["queue"] == 420:
            gameids.append(game["gameId"])
    return gameids, index

def writeoldgameids(gameids):
    with open("oldgameids.txt", "a") as f:
        for gameid in gameids:
            f.write(str(gameid) + "\n")

def getencryptedaccountid(summonername, index):
    url = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonername + "?api_key="
    response, index = sendrequest(url, index) #use primary api key
    if response == "error":
        return response, index
    return response["accountId"], index

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

def getmatchdata(gameid, index):
    url = "https://euw1.api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key="
    response, index = sendrequest(url, index) #use random api key
    if response == "error":
        return ["error"], index

    return response, index

def getgamedata(matchdata):
        champions = addchampstoorderedlist(matchdata)
        champions = convertchampsfromidtoname(champions)
        teamblueresult = getteamblueresult(matchdata)
        gamedata = champions
        gamedata.append(teamblueresult)
        return gamedata

def writegamedatatofile(gamedata, gameid):
    with open("games/" + str(gameid) + ".txt", "w") as f:
        for entry in gamedata:
            f.write(str(entry) + "\n")


def getplayers(matchdata):
    playernames = []
    try:
        for participant in matchdata["participantIdentities"]:
            playernames.append(participant["player"]["summonerName"].replace(" ", ""))
    except:
        return ["key error"]
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

    remove("backup/newsummonernames.bin")
    remove("backup/oldgameids.txt")
    remove("backup/oldsummonernames.txt")
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
def checkerror(data):

    try:
        if data[0] == "error":
            return True
        else:
            return False
    except IndexError:
        return True
    except KeyError:
        return False

def cycle(summonername):
    global failed, success
    index = 0
    accountid, index = getencryptedaccountid(summonername, index) #used less often
    if checkerror([accountid]):
            return

    gameids, index = getmatchhistoryids(accountid, index) #used less often
    if checkerror(gameids):
        return
    gameids = deleterepeatedgameids(gameids)
    players = []
    for gameid in gameids:
        matchdata, index = getmatchdata(gameid, index)
        if checkerror(matchdata):
            continue
        newplayers = getplayers(matchdata) #used frequently
        if newplayers[0] == "key error":
            continue

        try:
            newplayers.remove(summonername)
        except ValueError:
            print("didnt find " + summonername + " because he changed his name recently")
            continue

        for player in newplayers: #repeatedly merging the newplayers list to the full players list
            players.append(player)

        gamedata = getgamedata(matchdata) #used frequently
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
    start_time = time.time()
    threadcount = 100
    loop = True
    #summonernames = ["hubbix"] #if newsummonernames.txt is empty
    #for i in range(numofplayeriterations)
    #    summonernames = getnewsummonernames(1)
    #    cycle(summonername) #for a fixed number of iterations
    while loop:
        try:
            summonernames = getnewsummonernames(threadcount)
            if (len(summonernames) == 0):
                print("no summoner names, files are ok")
                sys.exit()
            pool = ThreadPool(threadcount)
            results = pool.map(cycle, summonernames)
            #cycle(summonernames[0]) #for no multi threading
            #break #for only one iteration
        except KeyboardInterrupt:
            pool.terminate()
            remove("newsummonernames.bin")
            remove("oldgameids.txt")
            remove("oldsummonernames.txt")
            copyfile("backup/newsummonernames.bin", "newsummonernames.bin")
            copyfile("backup/oldgameids.txt", "oldgameids.txt")     #backup
            copyfile("backup/oldsummonernames.txt", "oldsummonernames.txt")
            #print("copy all files from backup into main folder and overwrite")
            loop = False
            continue

        pool.terminate()
        try:
            for i in range(100):
                print("finished " + str(len(summonernames))  + " cycles")

            time.sleep(10)
            start_time + 10
        except KeyboardInterrupt:
            break

    print ("success: " + str(success) + " failed: " + str(failed))
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()
