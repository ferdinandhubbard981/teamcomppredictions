import json
import os
def main():
    folder = "..\games\\"
    maxcount = 10000000000000000000
    tensorflowdata = []
    tensorflowlabels = []
    dict = {}
    numofchampions = 0
    with open("champion.json", encoding="utf-8") as f:
        data = json.load(f)
        numofchampions = len(data["data"])
        x = 0
        for i in data["data"]:
            dict.update({i.lower() : x})
            x += 1
    datafilenames = os.listdir(folder)
    count = 0
    for i in datafilenames:
        print(i)
        with open(folder + i, "r") as f:
            content = f.read().split()
            if content[10] == "Win":
                tensorflowlabels.append([1]) #change to ([1]) for array of arrays
            if content[10] == "Fail":
                tensorflowlabels.append([0]) #change to ([0]) for array of arrays
            binarystring = []
            for x in range(10):
                for y in range(numofchampions):
                    if dict[content[x]] == y:
                        binarystring.append(1)
                    else:
                        binarystring.append(0)
            tensorflowdata.append(binarystring)
        count += 1
        if count == maxcount:
            break
    with open("data.json", "w") as f:
        json.dump(tensorflowdata, f)

    with open("labels.json", "w") as f:
        json.dump(tensorflowlabels, f)


if __name__ == "__main__":
    main()
