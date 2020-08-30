#resets all files for debugging
def reset(filename):
    with open(filename, "w"):
        print("wiped")

if __name__ == "__main__":
    reset("newaccountids.txt")
    reset("oldaccountids.txt")
    reset("oldgameids.txt")
