#resets all files for debugging
def reset(filename):
    with open(filename, "w"):
        print("wiped")

if __name__ == "__main__":
    reset("newsummonernames.bin")
    reset("oldsummonernames.txt") #useless
    reset("oldgameids.txt")
