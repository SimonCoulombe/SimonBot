# SimonBot
My bot for the ants AI challenge at aichallenge.org

######################################################
## FIRST, INSTALL THE VIZ_OVERLAY BY j-h-a into C:\Projets
######################################################
##
##* Clone the repository to your machine: `git clone git://github.com/j-h-a/aichallenge.git ./aichallenge`
##* Change directory to the newly cloned repository: `cd aichallenge`
##* Switch to the `vis_overlay` branch: `git checkout vis_overlay`
##* Initialize the submodules: `git submodule init; git submodule update`
##
######################################################


## create python27 environment in anacadon3
conda create -n py27 python=2.7 anaconda

## activate python27 environment in anaconda3
activate py27

## call the SimonBot, playing against itself
python "c:/projets/aichallenge/ants/playgame.py" "python c:/projets/SimonBot/SimonBot.py" "python c:/projets/SimonBot/SimonBot.py" --log_stderr --map_file  "c:/projets/aichallenge/ants/maps/random_walk/random_walk_02p_02.map" --log_dir game_logs --turns 600  --player_seed 7 --verbose -e

## OR call the bot playing against agent_smith ,and memetix (top 10) and qbot
python "c:/projets/aichallenge/ants/playgame.py" "python c:/projets/SimonBot/SimonBot.py" "python C:\Projets\SimonBot\opponent_bots\agent_smith\MyBot.pypy" "java -jar C:\Projets\SimonBot\opponent_bots\memetix\MyBot.jar" "java -jar C:\Projets\SimonBot\opponent_bots\qbot\MyBot.jar"  --log_stderr --map_file  "c:/projets/aichallenge/ants/maps/maze/maze_04p_01.map" --log_dir game_logs --turns 2000  --player_seed 7 --verbose -e

#########################
## OPEN THE HTML FILE IN FIREFOX (google chrome and internet explorer dont work)
#########################

## View the wiki for screenshots of the log and visualisation.

