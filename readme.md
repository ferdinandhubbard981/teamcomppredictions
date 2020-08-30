analyses team composition and gives chances of winning or losing

neural network:

inputs:
  - champion
  - x10 where the first 5 are team blue and last 5 are team red
outputs:
  - lose
  - win

workflow:
  - get all match id from past games of player (within last week due to API)
  - get all 9 summoner names of past games of player (within the last major patch)
  - format champion data from games
  - repeat until enough data
  - train neural network with data and outcomes
  - write script to get champion select picks and calculate odds in real time

training data format:

.txt for each game

champ1 #string with name of champ
champ2 #champ 1-5 is blue 6-10 is red
champ3
champ4
champ5
champ6
champ7
champ8
champ9
champ10
outcome #true for win false for loss
