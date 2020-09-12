analyses team composition and gives chances of winning or losing

neural network:

inputs:
  - champion
  - x10 where the first 5 champions are team blue and last 5 are team red

outputs:
  - Win
  - Lose

scheme of work:
  - get all match id from past games of player (within last week due to API)
  - get all 9 summoner names(excluding you) of past games of player (within the last major patch)
  - format champion data from games
  - repeat until enough data
  - find good hyperparameters for neural network (bayesian optimization)
  - train neural network with data and outcomes
  - write script to get champion select picks (from memory) and calculate odds in real time

training data format:

.txt for each game

champ1 teamblue top
champ2 teamblue jgl
champ3 teamblue mid
champ4 teamblue adc
champ5 teamblue sup
champ6 teamred top
champ7 teamred jgl
champ8 teamred mid
champ9 teamred adc
champ10 teamred sup
outcome #true for win false for loss relative to blue team

team100 is blue team
team200 is red team



Files:

getmatches.py 
              - gets game data and saves each game individually as a txt file
              - gets all summonernames from past games and adds them to newsummonernames.txt (deleting the old ones)
              - adds old games to the old gameids list and oldsummonernames to oldsummonernames.txt
              
converdata.py
              - converts txt game data to two json files: data.json, labels.json (which are compressed to .rar and used to train the neural network)
