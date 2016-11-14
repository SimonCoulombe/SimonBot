#!/usr/bin/env python

from ants import *
from random import choice

AIVISUALIZE=1 #SET TO 1 TO OUTPUT AI VISULIZATION DATA (STDOUT V LINE ...)
LOG_STDERR=0 #set 1 to output STDERR
LOG_STDERR_END=1 #set 1 to output STDERR
LOG_COMBAT=0
LOG_COMBAT_RESULT=1

# define a class with a do_turn method
# the Ants.run method will parse and update bot input
# it will also run the do_turn method for us
class MyBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        pass

    # do_setup liste_lienis run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.hills = []
        self.explorevalue = {}  #les explorevalues de chacune des tuiles.  Ca monte de 1 ? chaque tour o? elle est non visible, tombe ? 0 quand visible
        for row in range(ants.rows):
            for col in range(ants.cols):
                self.explorevalue[(row, col)]=0
        self.tile_area = {}  #on d?finit un area pour chaque tuile au d?but du tour.   format Tuile:Fourmi
        self.long_missions_explore={}  #mission ? long terme (pour pas que les fourmies changent de cellule de "go to the border tous les tours"
        self.long_missions_food={}  #mission ? long terme (pour pas que les fourmies changent de cellule de "go to the border tous les tours"
        self.this_turn_path={}
        self.broke_last_turn=0
        self.borders_age=0
        self.list_borders=[]

    # do turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use

    def find_key(self,dic, val):
        """return the key of dictionary dic given the value"""
        return [k for k, v in dic.iteritems() if v == val][0]

    def find_value(self,dic, key):
        """return the value of dictionary dic given the key"""
        return dic[key]

    def do_turn(self, ants):

        if LOG_STDERR:
            sys.stderr.write(" *Start of do_turn*** ")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left***** Turn number:")
            b=str(ants.turn_number)
            sys.stderr.write(b)
            sys.stderr.write("\n")


##        def flee(in_myAnt,in_enemyAnts,in_move_esquive,in_enemy_range):
##            move_esquive=defaultdict(list)
##            move_esquive = in_move_esquive.copy()
##
##
##
##
##            myAnts_size= len(in_myAnt)
##            index=0
##            while index < myAnts_size:
##                ant=in_myAnt[index]
##                #if there are esquive moves, find the best one.
##                if move_esquive[ant]:
##                    closest_enemy=99
##                    best_move= ant
##
##                    for move in move_esquive[ant]:
##                        for enemy in in_enemyAnts:
##                             xdist,ydist = ants.xy_distance(enemy,ant)
##                             if xdist+ydist <closest_enemy:
##                                closest_enemy= xdist+ydist
##                                best_move=move
##
##                    if best_move <> ant:
##                        if do_move_location(ant,best_move):
##                            for ant,move
##                pass





        def charge(in_myAnts,in_enemyAnts):
            for ant in in_myAnts:
                tiles_from = {} #dictionnaire
                from_nodes = [] #list des nodes ? ?valuer.  on commence avec seulement food_loc
                from_nodes.append(ant)
                to_nodes = [] # list des nodes ajout?es apr?s ?valuation

                steps = 1
                while (from_nodes and steps < 5 and ant not in orders.values() ):
                    for nodes in from_nodes: #
                        for new_loc in ants.tiles_voisins[(nodes)]:

                            if (new_loc in tiles_from):  #passer si d?ja ?valu?e
                                continue
                            if steps==1 and not can_move_to(new_loc):   #passer si premiere case non atteignable.
                            #if not can_move_to(new_loc):   #passer toutes les cases non atteignables (test).
                                continue

                            #si correcte, continuer le BFS
                            tiles_from[(new_loc)] = nodes
                            to_nodes.append(new_loc)

                            #si on trouve une pas fine, essayer d'y aller..
                            if new_loc in in_enemyAnts and  ant not in orders.values()  : #la case est 1) une bouffe 2 on a pas d?j? trouv? de fourmi pour la bouffe ? cette ?tape-ci 3) la fourmi a pas d'ordre
                                current_tile=new_loc
                                came_from_tile=nodes
                                while came_from_tile <> ant:
                                    current_tile=came_from_tile
                                    came_from_tile=tiles_from[came_from_tile]

                                if do_move_location(ant, current_tile):  #essayer marcher vers la case "nodes" soit celle qui  a ?t? ?valu?e juste apres la fourmi
                                    break

                    from_nodes=to_nodes
                    to_nodes=[]
                    steps=steps+1
        def maximise_combat_frozen_enemy(antIndex,in_bestscore, in_deaths, in_myAnts_best,in_myAnts,in_myAnts_distance,in_enemyAnts,privilegie_survie,in_original_myAnts):
            broken=0

            current_bestscore = -99 # meilleur score actuel
            current_bestscore = in_bestscore

            current_deaths = 0 # de morts dans le meilleur score
            current_deaths = in_deaths

            current_myAnts_best =list(in_myAnts_best)  #ordres, dans le meilleure score

            current_myAnts = list(in_myAnts) #position ? ?valuer

            current_myAnts_distance = in_myAnts_distance # distance total entre mes fourmis et leur enemi le plus proche (a minimiser si possible)

            current_enemyAnts = list(in_enemyAnts)

            if ants.time_remaining()< 500:
                if antIndex==0:
                    sys.stderr.write("Pas assez de temps, on sort de maximise combat! Groupe=")
                    b=str(groupe)
                    sys.stderr.write(b)
                    sys.stderr.write(", antIndex=")
                    b=str(antIndex)
                    sys.stderr.write(b)
                    sys.stderr.write("\n")
                return current_bestscore, current_deaths, current_myAnts_best,current_myAnts_distance,1

            if antIndex < myAnts_size:  #si on est pas a la derniere ?tape...
                ant=myAnts[antIndex]

                for move in move_possible[ant]:
                    current_myAnts[antIndex]=move

                    #before evaluating, check if  this move means sending 2 ants to the same tile, or having 2 ants switch places.
                    double=0
                    switch=0
                    set_unique_mes_fourmis = set()
                    if antIndex>=1:
                        #verifier que je n'ai pas d'ordres en double. Si oui, ne pas ?valuer et retourner un score poche.
                        for ant in current_myAnts[0:antIndex+1]:
                            if ant in set_unique_mes_fourmis:
                                double=1
                            else:
                                set_unique_mes_fourmis.add(ant)

                        #verifier que je n'ai pas de fourmis qui echangent de place.. a date je ne le croise jamais .. weird.
                        i=0
                        while i <antIndex:
                            if current_myAnts[i]== in_original_myAnts[antIndex] and current_myAnts[antIndex]==in_original_myAnts[i]:  #une fourmi a prit ma place et jai prit sa place
                                switch=1
                                break
                            i=i+1

                    if double==1: #if double orders, skip
                        continue

                    if switch==1 : #if exchange spot, skip
                        continue

                    newAntIndex = antIndex+1
                    sub_bestscore, sub_deaths,sub_myAnts_best,sub_myAnts_distance,sub_broken = maximise_combat_frozen_enemy(newAntIndex,current_bestscore, current_deaths, current_myAnts_best,current_myAnts,current_myAnts_distance,current_enemyAnts,privilegie_survie,in_original_myAnts)
                    if sub_broken>broken:
                        broken=sub_broken

                    if sub_bestscore > current_bestscore :
                        current_bestscore   =   sub_bestscore
                        current_deaths      =   sub_deaths
                        current_myAnts_distance = sub_myAnts_distance
                        current_myAnts_best =   list(sub_myAnts_best)


                    elif sub_bestscore == current_bestscore and sub_deaths < current_deaths and privilegie_survie==1:
                        current_bestscore   =   sub_bestscore
                        current_deaths      =   sub_deaths
                        current_myAnts_distance = sub_myAnts_distance
                        current_myAnts_best =   list(sub_myAnts_best)

                    elif sub_bestscore == current_bestscore and sub_deaths > current_deaths and privilegie_survie==0:
                        current_bestscore   =   sub_bestscore
                        current_deaths      =   sub_deaths
                        current_myAnts_distance = sub_myAnts_distance
                        current_myAnts_best =   list(sub_myAnts_best)

                    elif sub_bestscore == current_bestscore and sub_deaths == current_deaths and sub_myAnts_distance<current_myAnts_distance:
                        current_bestscore   =   sub_bestscore
                        current_deaths      =   sub_deaths
                        current_myAnts_distance = sub_myAnts_distance
                        current_myAnts_best =   list(sub_myAnts_best)

                    else: # aucune amelioration a mon positionnement
                        pass

                return current_bestscore, current_deaths, current_myAnts_best,current_myAnts_distance,broken  #apres avoir simul? les 5 moves, on retourne un r?sultat pour pouvoir reculer d'un index

            else:       #si on est a la derni?re ?tape, evaluer directevement avecla fonction eval_survival.
                my_score,my_kills,my_deaths= eval_survival(current_myAnts,in_enemyAnts)
                my_distance = eval_distance(current_myAnts, in_enemyAnts)

                if my_score > current_bestscore : #meilleure score
                    current_bestscore=my_score
                    current_deaths=my_deaths
                    current_myAnts_best=list(current_myAnts)
                    current_myAnts_distance = my_distance

                elif my_score == current_bestscore and my_deaths < current_deaths  and privilegie_survie==1 : #m?me score, moins de morts
                    current_bestscore=my_score
                    current_deaths=my_deaths
                    current_myAnts_best=list(current_myAnts)
                    current_myAnts_distance = my_distance

                elif my_score == current_bestscore and my_deaths > current_deaths  and privilegie_survie==0 : #m?me score, plus de morts et on privilegie les kills
                    current_bestscore=my_score
                    current_deaths=my_deaths
                    current_myAnts_best=list(current_myAnts)
                    current_myAnts_distance = my_distance


                elif my_score == current_bestscore and my_deaths == current_deaths and my_distance<current_myAnts_distance: #m?me score, m?eme mort, moins distance
                    current_bestscore=my_score
                    current_deaths=my_deaths
                    current_myAnts_best=list(current_myAnts)
                    current_myAnts_distance = my_distance

                return current_bestscore, current_deaths, current_myAnts_best,current_myAnts_distance, broken #si je suis le dernier index, calculer un r?sultat et retourner a l'index pr?c?dent.



        def maximise_combat(antIndex,in_bestscore, in_deaths, in_myAnts_best,in_myAnts,in_myAnts_distance,in_enemyAnts,privilegie_survie,in_original_myAnts):
            broken=0

            current_bestscore = -99 # meilleur score actuel
            current_bestscore = in_bestscore

            current_deaths = 0 # de morts dans le meilleur score
            current_deaths = in_deaths

            current_myAnts_best =list(in_myAnts_best)  #ordres, dans le meilleure score

            current_myAnts = list(in_myAnts) #position ? ?valuer

            current_myAnts_distance = in_myAnts_distance # distance total entre mes fourmis et leur enemi le plus proche (a minimiser si possible)

            current_enemyAnts = list(in_enemyAnts)

            if ants.time_remaining()< 500:
                if antIndex==0:
                    sys.stderr.write("Pas assez de temps, on sort de maximise combat! Groupe=")
                    b=str(groupe)
                    sys.stderr.write(b)
                    sys.stderr.write(", antIndex=")
                    b=str(antIndex)
                    sys.stderr.write(b)
                    sys.stderr.write("\n")
                return current_bestscore, current_deaths, current_myAnts_best,current_myAnts_distance,1

            if antIndex < myAnts_size:  #si on est pas a la derniere ?tape...
                ant=myAnts[antIndex]

                for move in move_possible[ant]:
                    current_myAnts[antIndex]=move

                    #before evaluating, check if  this move means sending 2 ants to the same tile, or having 2 ants switch places.
                    double=0
                    switch=0
                    set_unique_mes_fourmis = set()
                    if antIndex>=1:
                        #verifier que je n'ai pas d'ordres en double. Si oui, ne pas ?valuer et retourner un score poche.
                        for ant in current_myAnts[0:antIndex+1]:
                            if ant in set_unique_mes_fourmis:
                                double=1
                            else:
                                set_unique_mes_fourmis.add(ant)

                        #verifier que je n'ai pas de fourmis qui echangent de place.. a date je ne le croise jamais .. weird.
                        i=0
                        while i <antIndex:
                            if current_myAnts[i]== in_original_myAnts[antIndex] and current_myAnts[antIndex]==in_original_myAnts[i]:  #une fourmi a prit ma place et jai prit sa place
                                switch=1
                                break
                            i=i+1

                    if double==1: #if double orders, skip
                        continue

                    if switch==1 : #if exchange spot, skip
                        continue

                    newAntIndex = antIndex+1
                    sub_bestscore, sub_deaths,sub_myAnts_best,sub_myAnts_distance,sub_broken = maximise_combat(newAntIndex,current_bestscore, current_deaths, current_myAnts_best,current_myAnts,current_myAnts_distance,current_enemyAnts,privilegie_survie,in_original_myAnts)
                    if sub_broken>broken:
                        broken=sub_broken

                    if sub_bestscore > current_bestscore :
                        current_bestscore   =   sub_bestscore
                        current_deaths      =   sub_deaths
                        current_myAnts_distance = sub_myAnts_distance
                        current_myAnts_best =   list(sub_myAnts_best)


                    elif sub_bestscore == current_bestscore and sub_deaths < current_deaths and privilegie_survie==1:
                        current_bestscore   =   sub_bestscore
                        current_deaths      =   sub_deaths
                        current_myAnts_distance = sub_myAnts_distance
                        current_myAnts_best =   list(sub_myAnts_best)

                    elif sub_bestscore == current_bestscore and sub_deaths > current_deaths and privilegie_survie==0:
                        current_bestscore   =   sub_bestscore
                        current_deaths      =   sub_deaths
                        current_myAnts_distance = sub_myAnts_distance
                        current_myAnts_best =   list(sub_myAnts_best)

                    elif sub_bestscore == current_bestscore and sub_deaths == current_deaths and sub_myAnts_distance<current_myAnts_distance:
                        current_bestscore   =   sub_bestscore
                        current_deaths      =   sub_deaths
                        current_myAnts_distance = sub_myAnts_distance
                        current_myAnts_best =   list(sub_myAnts_best)

                    else: # aucune amelioration a mon positionnement
                        pass

                return current_bestscore, current_deaths, current_myAnts_best,current_myAnts_distance,broken  #apres avoir simul? les 5 moves, on retourne un r?sultat pour pouvoir reculer d'un index

            else:       #si on est a la derni?re ?tape, ?valuer avec la fonction minimize combat ( si on a pas d'ordre en double)

                #d?terminer les cases qui sont dans ma range.
                my_score,my_deaths,broken = minimize_combat(0,current_bestscore,current_deaths,999, -999, current_myAnts,in_enemyAnts,in_enemyAnts)
                my_distance = eval_distance(current_myAnts, in_enemyAnts)

                if my_score > current_bestscore : #meilleure score
                    current_bestscore=my_score
                    current_deaths=my_deaths
                    current_myAnts_best=list(current_myAnts)
                    current_myAnts_distance = my_distance

                elif my_score == current_bestscore and my_deaths < current_deaths  and privilegie_survie==1 : #m?me score, moins de morts
                    current_bestscore=my_score
                    current_deaths=my_deaths
                    current_myAnts_best=list(current_myAnts)
                    current_myAnts_distance = my_distance

                elif my_score == current_bestscore and my_deaths > current_deaths  and privilegie_survie==0 : #m?me score, plus de morts et on privilegie les kills
                    current_bestscore=my_score
                    current_deaths=my_deaths
                    current_myAnts_best=list(current_myAnts)
                    current_myAnts_distance = my_distance


                elif my_score == current_bestscore and my_deaths == current_deaths and my_distance<current_myAnts_distance: #m?me score, m?eme mort, moins distance
                    current_bestscore=my_score
                    current_deaths=my_deaths
                    current_myAnts_best=list(current_myAnts)
                    current_myAnts_distance = my_distance

                return current_bestscore, current_deaths, current_myAnts_best,current_myAnts_distance, broken #si je suis le dernier index, calculer un r?sultat et retourner a l'index pr?c?dent.

        def minimize_combat(antIndex,in_score_to_beat,in_deaths_to_beat,in_minimum, in_deaths, in_myAnts,in_enemyAnts,in_original_enemyAnts):
            #verifier que je n'ai pas d'ordres en double. Si oui, ne pas ?valuer et retourner un score poche.
            broken=0

            current_myAnts = list(in_myAnts) #position ? ?valuer
            current_enemyAnts = list(in_enemyAnts) #position ? ?valuer

            current_minimum=in_minimum
            current_deaths= in_deaths

            if ants.time_remaining()< 500:
                broken=1
                if antIndex==0:

                    sys.stderr.write("Pas assez de temps, on sort de *minimize* combat! Groupe=")
                    b=str(groupe)
                    sys.stderr.write(b)
                    sys.stderr.write(", antIndex=")
                    b=str(antIndex)
                    sys.stderr.write(b)
                    sys.stderr.write("\n")
                return current_minimum, current_deaths,broken

            if antIndex < enemyAnts_size:  #si on est pas a la derniere ?tape...
                ant=enemyAnts[antIndex]

                for move in move_possible_enemy[ant]:
                    current_enemyAnts[antIndex]=move

                    #before evaluating, check if  this move means sending 2 ants to the same tile, or having 2 ants switch places.
                    double=0
                    switch=0
                    set_unique_mes_fourmis = set()
                    if antIndex>=1:
                        #verifier que je n'ai pas d'ordres en double. Si oui, ne pas ?valuer et retourner un score poche.
                        for ant in current_enemyAnts[0:antIndex+1]:
                            if ant in set_unique_mes_fourmis:
                                double=1
                            else:
                                set_unique_mes_fourmis.add(ant)

                        #verifier que je n'ai pas de fourmis qui echangent de place.. a date je ne le croise jamais .. weird.
                        i=0
                        while i <antIndex:
                            if current_enemyAnts[i]== in_original_enemyAnts[antIndex] and current_enemyAnts[antIndex]==in_original_enemyAnts[i]:  #une fourmi a prit ma place et jai prit sa place
                                switch=1
                                break
                            i=i+1

                    if double==1: #if double orders, skip
                        continue

                    if switch==1 : #if exchange spot, skip
                        continue

                    newAntIndex = antIndex+1
                    sub_minimum, sub_deaths,sub_broken= minimize_combat(newAntIndex,in_score_to_beat,in_deaths_to_beat, current_minimum,current_deaths, in_myAnts,current_enemyAnts,in_original_enemyAnts)
                    if sub_broken> broken:
                        broken=sub_broken
                    if sub_minimum < in_score_to_beat : #le minimum est trop faible, abort la in_myAnts position
                        return sub_minimum, sub_deaths,broken

                    elif sub_minimum == in_score_to_beat and sub_deaths> in_deaths_to_beat : #le minimum est trop faible, abort la in_myAnts position
                        return sub_minimum, sub_deaths,broken

                    elif sub_minimum < current_minimum:  # on a trouv? une branche qui r?duit le minimum ,mais c'est quand m?me plus haut que le score ? battre. utiliser ce minimum.
                        current_minimum= sub_minimum
                        current_deaths = sub_deaths

                    elif sub_minimum == current_minimum and sub_deaths > in_deaths: # on a trouv? une branche qui r?duit le minimum ,mais c'est quand m?me plus haut que le score ? battre. utiliser ce minimum.
                        current_minimum= sub_minimum
                        current_deaths = sub_deaths

                    else:
                        pass

                return current_minimum, current_deaths,broken  #apres avoir simul? les 5 moves, on retourne un r?sultat pour pouvoir reculer d'un index

            else:       #si on est a la derni?re ?tape, ?valuer avec la fonction eval_survival
                my_score,my_kills,my_deaths= eval_survival(in_myAnts,current_enemyAnts)

                if my_score < in_score_to_beat: #dommage, on abaisse trop notre marque
                    return my_score, my_deaths,broken

                elif my_score == in_score_to_beat and my_deaths > in_deaths_to_beat: #dommage, on abaisse trop notre marque
                    return my_score, my_deaths,broken

                elif my_score < current_minimum:  #dommage, on abaisse notre marque.
                    current_minimum= my_score
                    current_deaths = my_deaths

                elif my_score == current_minimum  and my_deaths>current_deaths: #dommage, on abaisse notre marque.
                    current_minimum= my_score
                    current_deaths = my_deaths

                return current_minimum, current_deaths,broken  #si je suis le dernier index, calculer un r?sultat et retourner a l'index pr?c?dent.

        def can_move_to( new_loc ):
			#return (ants.unoccupied( new_loc )  or (not ants.unoccupied( new_loc ) and new_loc in orders.values())) and new_loc not in orders
            return (new_loc not in orders and ants.passable(new_loc) and new_loc not in ants.food_list)

        def eval_survival(set_combat_my_ants, set_combat_enemy_ants):
                #retourne : score,kills,deaths
            score=0
            kills=0
            deaths=0
            #determiner le nombre d enemis en range pour mes fourmis et les enemis
            enemies_in_range={} #dictionnaire, avec la fourmi en K et le nombre d enemis en V
            list_enemies_in_range=defaultdict(list) #dictionnaire, avec la fourmi en K et ses enemis en V.

            for ant in set_combat_my_ants:
                closest_enemy=10

                #determiner le nombre d'enemis a port?e. et la distance de l'enemi le plus proche::
                enemies_in_range[ant]=0
                for enemy in set_combat_enemy_ants:

                    # enemis en port?e:
                    if enemy in ants.tiles_range_attack[ant]:
                        enemies_in_range[ant]=enemies_in_range[ant]+1
                        list_enemies_in_range[ant].append(enemy)

            for ant in set_combat_enemy_ants:
                #determiner le nombre d'enemis a port?e. et la distance de l'enemi le plus proche::
                enemies_in_range[ant]=0
                for enemy in set_combat_my_ants:

                    # enemis en port?e:
                    if enemy in ants.tiles_range_attack[ant]:
                        enemies_in_range[ant]=enemies_in_range[ant]+1
                        list_enemies_in_range[ant].append(enemy)

            #determiner quelles de mes fourmis et des fourmis enemies meurent.

            for ant in set_combat_my_ants:
                for enemy in list_enemies_in_range[ant]:
                    if enemies_in_range[enemy]<= enemies_in_range[ant] :
                        deaths=deaths+1
                        break

            for ant in set_combat_enemy_ants:
                for enemy in list_enemies_in_range[ant]:
                    if enemies_in_range[enemy]<= enemies_in_range[ant] :
                        kills=kills+1
                        break

            score=kills-deaths

            if LOG_COMBAT and len(set_combat_my_ants)>=2 and score>1:
                sys.stderr.write("eval_survival returning a score of ")
                b=str(score)
                sys.stderr.write(b)
                sys.stderr.write(" , with ")
                b=str(kills)
                sys.stderr.write(b)
                sys.stderr.write(" kills and ")
                b=str(deaths)
                sys.stderr.write(b)
                sys.stderr.write(" deaths \n")
                sys.stderr.write(" my ants position:")
                b=str(set_combat_my_ants)
                sys.stderr.write(b)
                sys.stderr.write("   enemy ants position:")
                b=str(set_combat_enemy_ants)
                sys.stderr.write(b)
                sys.stderr.write(" \n")

            return score,kills,deaths

        def eval_distance(set_combat_my_ants, set_combat_enemy_ants):
            distance=0 #distance est la somme des distances manhattan des closest enemies.
            #determiner le nombre d enemis en range pour mes fourmis et les enemis
            enemies_in_range={} #dictionnaire, avec la fourmi en K et le nombre d enemis en V

            for ant in set_combat_my_ants:
                closest_enemy=10
                for enemy in set_combat_enemy_ants:
                    #enemi le plus proche:
                    xdist,ydist = ants.xy_distance(enemy,ant)
                    if xdist+ydist<closest_enemy:
                        closest_enemy =xdist+ydist
                distance=distance+closest_enemy
            return distance

        def astar(self,start,goal):
            if start==goal:
                return start #si le but ?gale le d?part, retourner la cellule de d?part

            if not ants.tiles_voisins[goal]:
                return start #si la cible a aucun voisin (eau) , retourner la cellule de d?part

            closetset= set() #ensemble d?ja ?valu?
            openset = {} #ensemble ? ?valuer, la key = tile, valeur = total_estimated_cost
            openset[start]=ants.distance(start, goal) #il faut entrer le cout total estim? dans openset aussi.
            came_from = {} #map of navigated node
            cost_so_far = {}
            heuristic_cost = {}
            total_estimated_cost = {}
            cost_so_far[start] = 0
            heuristic_cost[start] =ants.distance(start, goal)
            total_estimated_cost[start]=cost_so_far[start]+heuristic_cost[start]

            step=0
            count_cent=0
            while openset and ( (step<(20*heuristic_cost[start]) or step<600) and step< 1000  ):
                count_cent= count_cent+1
                if count_cent == 100:
                    count_cent=0
                    if ants.time_remaining()< 150:
                        return start

                minimum = min(openset,key=openset.get)  #trouver le cout total estim? minimum parmi toutes les cellules  open.   (ex:21)
                dico_mintotal_minheuristic={}
                for legume,prix in openset.iteritems():
                    if prix == openset[minimum]:
                        dico_mintotal_minheuristic[legume]=heuristic_cost[legume]   #pour toutes les cellules ayant le cout minimal (ex:21), ?crire le co?t inconnu de ces cellules dans un nouveau dictionnaire.
                current=min(dico_mintotal_minheuristic,key=dico_mintotal_minheuristic.get) #dans ce nouveau dictionnaire, celui ayant le cout minimal sera la cellule choisie.

                if current==goal: #on a atteint le but, rebrousser chemin pour trouver le premier pas.
                    current_step=goal
                    came_from_step= came_from[goal]

                    while (came_from_step <> start):
                        current_step=came_from_step
                        came_from_step= came_from[current_step]
                    return current_step

                #si on a pas encore atteint le but:
                del openset[current]
                closetset.add(current)

                for neighbor in ants.tiles_voisins[current]:
                    if neighbor in closetset: #ne pas consid?rer les cases d?j? v?rifi?es
                        continue

                    if current==start:  #if first step, go around occupied tiles.. and targeted tiles
                        if not (can_move_to(neighbor)): #enlever les cases o? il y a quelqu'un
                            continue

                    tentative_cost_so_far= cost_so_far[current]+1

                    if neighbor not in openset:
                        tentative_is_better= True

                    elif tentative_cost_so_far+heuristic_cost[neighbor]<total_estimated_cost[neighbor]:
                        tentative_is_better=True
                    else:
                        tentative_is_better=False

                    if tentative_is_better == True:
                        came_from[neighbor]=current
                        heuristic_cost[neighbor]=ants.distance(neighbor,goal)
                        cost_so_far[neighbor]=tentative_cost_so_far
                        total_estimated_cost[neighbor]=tentative_cost_so_far+heuristic_cost[neighbor]
                        openset[neighbor]=total_estimated_cost[neighbor]
                step=step+1
            return start #failed to find a path, return the starting location

        def astar_path(self,start,goal):
            path=str()
            if start==goal:
                return start,path #si le but ?gale le d?part, retourner la cellule de d?part

            if not ants.tiles_voisins[goal]:
                return start,path #si la cible a aucun voisin (eau) , retourner la cellule de d?part

            closetset= set() #ensemble d?ja ?valu?
            openset = {} #ensemble ? ?valuer, la key = tile, valeur = total_estimated_cost
            openset[start]=ants.distance(start, goal) #il faut entrer le cout total estim? dans openset aussi.
            came_from = {} #map of navigated node
            cost_so_far = {}
            heuristic_cost = {}
            total_estimated_cost = {}
            cost_so_far[start] = 0
            heuristic_cost[start] =ants.distance(start, goal)
            total_estimated_cost[start]=cost_so_far[start]+heuristic_cost[start]

            step=0
            count_cent=0
            while openset and ( (step<(20*heuristic_cost[start]) or step<600) and step< 1000  ):
                count_cent= count_cent+1
                if count_cent == 100:
                    count_cent=0
                    if ants.time_remaining()< 150:
                        return start,path

                minimum = min(openset,key=openset.get)  #trouver le cout total estim? minimum parmi toutes les cellules  open.   (ex:21)
                dico_mintotal_minheuristic={}
                for legume,prix in openset.iteritems():
                    if prix == openset[minimum]:
                        dico_mintotal_minheuristic[legume]=heuristic_cost[legume]   #pour toutes les cellules ayant le cout minimal (ex:21), ?crire le co?t inconnu de ces cellules dans un nouveau dictionnaire.
                current=min(dico_mintotal_minheuristic,key=dico_mintotal_minheuristic.get) #dans ce nouveau dictionnaire, celui ayant le cout minimal sera la cellule choisie.

                if current==goal: #on a atteint le but, rebrousser chemin pour trouver le premier pas.
                    current_step=goal
                    came_from_step= came_from[goal]
                    path = str(ants.direction(came_from[goal],goal))[2:3]
                    while (came_from_step <> start):
                        current_step=came_from_step
                        came_from_step= came_from[current_step]
                        path=str(ants.direction(came_from_step,current_step))[2:3]+ path
                    return current_step,path

                #si on a pas encore atteint le but:
                del openset[current]
                closetset.add(current)

                for neighbor in ants.tiles_voisins[current]:
                    if neighbor in closetset: #ne pas consid?rer les cases d?j? v?rifi?es
                        continue

                    if current==start:  #if first step, go around occupied tiles.. and targeted tiles
                        if not (can_move_to(neighbor)): #enlever les cases o? il y a quelqu'un
                            continue

                    tentative_cost_so_far= cost_so_far[current]+1

                    if neighbor not in openset:
                        tentative_is_better= True

                    elif tentative_cost_so_far+heuristic_cost[neighbor]<total_estimated_cost[neighbor]:
                        tentative_is_better=True
                    else:
                        tentative_is_better=False

                    if tentative_is_better == True:
                        came_from[neighbor]=current
                        heuristic_cost[neighbor]=ants.distance(neighbor,goal)
                        cost_so_far[neighbor]=tentative_cost_so_far
                        total_estimated_cost[neighbor]=tentative_cost_so_far+heuristic_cost[neighbor]
                        openset[neighbor]=total_estimated_cost[neighbor]
                step=step+1
            return start,path #failed to find a path, return the starting location

# fin fonctions astar_path_unoccupied

        def astar_path_unoccupied(self,start,goal):
            path=str()
            if start==goal:
                return start,path #si le but ?gale le d?part, retourner la cellule de d?part

            if not ants.tiles_voisins[goal]:
                return start,path #si la cible a aucun voisin (eau) , retourner la cellule de d?part

            closetset= set() #ensemble d?ja ?valu?
            openset = {} #ensemble ? ?valuer, la key = tile, valeur = total_estimated_cost
            openset[start]=ants.distance(start, goal) #il faut entrer le cout total estim? dans openset aussi.
            came_from = {} #map of navigated node
            cost_so_far = {}
            heuristic_cost = {}
            total_estimated_cost = {}
            cost_so_far[start] = 0
            heuristic_cost[start] =ants.distance(start, goal)
            total_estimated_cost[start]=cost_so_far[start]+heuristic_cost[start]

            step=0
            count_cent=0
            while openset and ( (step<(4*heuristic_cost[start]) or step<100) and step< 400  ):
                count_cent= count_cent+1
                if count_cent == 100:
                    count_cent=0
                    if ants.time_remaining()< 150:
                        return start,path
                minimum = min(openset,key=openset.get)  #trouver le cout total estim? minimum parmi toutes les cellules  open.   (ex:21)
                dico_mintotal_minheuristic={}
                for legume,prix in openset.iteritems():
                    if prix == openset[minimum]:
                        dico_mintotal_minheuristic[legume]=heuristic_cost[legume]   #pour toutes les cellules ayant le cout minimal (ex:21), ?crire le co?t inconnu de ces cellules dans un nouveau dictionnaire.
                current=min(dico_mintotal_minheuristic,key=dico_mintotal_minheuristic.get) #dans ce nouveau dictionnaire, celui ayant le cout minimal sera la cellule choisie.

                if current==goal: #on a atteint le but, rebrousser chemin pour trouver le premier pas.
                    current_step=goal
                    came_from_step= came_from[goal]
                    path = str(ants.direction(came_from[goal],goal))[2:3]
                    while (came_from_step <> start):
                        current_step=came_from_step
                        came_from_step= came_from[current_step]
                        path=str(ants.direction(came_from_step,current_step))[2:3]+ path
                    return current_step,path

                #si on a pas encore atteint le but:
                del openset[current]
                closetset.add(current)

                for neighbor in ants.tiles_voisins[current]:
                    if neighbor in closetset: #ne pas consid?rer les cases d?j? v?rifi?es
                        continue

                    if not (can_move_to(neighbor)): #go around targetted tiles AND occupied tiles.
                        continue
                    if not (ants.unoccupied(neighbor)): #go around targetted tiles AND occupied tiles, even after first step.
                        continue


                    tentative_cost_so_far= cost_so_far[current]+1

                    if neighbor not in openset:
                        tentative_is_better= True

                    elif tentative_cost_so_far+heuristic_cost[neighbor]<total_estimated_cost[neighbor]:
                        tentative_is_better=True
                    else:
                        tentative_is_better=False

                    if tentative_is_better == True:
                        came_from[neighbor]=current
                        heuristic_cost[neighbor]=ants.distance(neighbor,goal)
                        cost_so_far[neighbor]=tentative_cost_so_far
                        total_estimated_cost[neighbor]=tentative_cost_so_far+heuristic_cost[neighbor]
                        openset[neighbor]=total_estimated_cost[neighbor]
                step=step+1
            return start,path #failed to find a path, return the starting location

# fin fonctions astar_path_unoccupied


        def do_move_direction(loc, direction):
            new_loc = ants.destination(loc, direction)
            if can_move_to(new_loc):
                ants.issue_order((loc, direction))
                orders[new_loc] = loc
                set_ants_sans_ordre.remove(loc)
                return True
            else:
                return False
        def do_move_location(loc, dest):
            directions = ants.direction(loc, dest)
            for direction in directions:
                if do_move_direction(loc, direction):

                    return True
            return False

# d?but la vrai fonction de tour..
        self.borders_age=self.borders_age+1 #faire vieillir les bordures d'un tour, apres 10 tours elles sont renovuell?es m?me si ?a fait 10 tours que j'ai pas le temps...

        set_my_ants=set()
        set_ants_sans_ordre =set()
        set_enemy_ants=set()

        ant_count=0

        for ant in ants.my_ants():
            ant_count=ant_count+1 #compter les fourmis
            set_my_ants.add(ant)
            set_ants_sans_ordre.add(ant)

        for ant,owner in ants.enemy_ants():
            set_enemy_ants.add(ant)






        # track all moves, prevent collisions
        orders = {} #la liste des ordres donn?s ce tour ci, pour pr?venir les collisions.  la cl? est la destination, la valeur est la fourmi.


 #commencer par faire le m?nage dans les missions...
        for ant,food in self.long_missions_food.items():
            if not ant in set_my_ants or ant in orders.values() or food not in ants.food() : #this mission cannot work (ant got lost/killed,  already has an order or the food is gone..)
                del  self.long_missions_food[ant]



        one_turn_missions = {} #mission, format ant/destination
        new_long_missions_explore={}
        new_long_missions_food={}
        next_turn_path={}   # un dictionnaire format ant/path, o? path est une string.
        broke_this_turn=0

        if self.broke_last_turn==0 or self.borders_age>10: #si on a pas manqu? de temps, ou si les bordures sont vieilles, les calculer.
            self.borders_age=0 #on resette le compteur.
            self.list_borders=[] #reset les cellules frontieres

            #d?terminer les areas et leurs fronti?res.
            if LOG_STDERR:
                sys.stderr.write(" *Start of multi-source BFS (Areas and Borders*")
                b=str(ants.time_remaining())
                sys.stderr.write(b)
                sys.stderr.write(" ms left* \n")


            ants_tiles_scan_distance=15  #distance maximale pour un BFS qui part de chaque fourmi et qui compte le nombre de voisines amies, enemies et la valeur maximum  explorevalue d'une tuile non visible ? 11 pas.
            self.tile_area = {}  #pour chaque tuile, le nom de la fourmi originale
            from_nodes=[]  #liste des from nodes, avec le nom de leur fourmi d origine
            d_ant_zone = defaultdict(list) #pour chaque fourmi originale, une liste des tuiles qui sont dans sa zone.

            #for ant in ants.my_ants():
            for ant in ants.ant_list:
                self.tile_area[ant]=ant
                d_ant_zone[ant].append(ant)
                from_nodes.append(ant)

            #couvrir 15 cases, assigner a chaque tuile couverte un area.  On ne fusionne pas encore
            steps=1

            while (steps<=ants_tiles_scan_distance and from_nodes):  #from_nodes sous-endend "len(from_nodes)>=1
                to_nodes=[] #liste des from nodes, avec le nom de leur fourmi d origine
                for from_node in from_nodes:
                    tile_area_from_node=self.tile_area[from_node]
                    for new_loc in ants.tiles_voisins[(from_node)]:
                        if (new_loc not in self.tile_area):  #if new tile, then assign it to the area of the ant.
                            to_nodes.append(new_loc)    #add to "to do list"
                            self.tile_area[new_loc]=tile_area_from_node # dans le dictionnaire  k=tuile v=fourmi originale
                            d_ant_zone[tile_area_from_node].append(new_loc) # dans le dictionnaire = k=fourmi originale v = tuile
                from_nodes=to_nodes
                to_nodes=[]
                steps=steps+1

            #determiner les cellules frontieres, et les liens entre groupes

            d_ant_zone_frontiere=defaultdict(list)

            if LOG_STDERR:
                sys.stderr.write(" *Start of Areas and Borders -- Liste des liens* ") #c'est ?a qui est long!
                b=str(ants.time_remaining())
                sys.stderr.write(b)
                sys.stderr.write(" ms left** \n")

            #liste_liens=[] #liste des liens entre surfaces
            liste_liens=set()
            for ant in set_my_ants:
                for v in d_ant_zone[(ant)]:
                    for voisin in ants.tiles_voisins[(v)]:
                        if voisin not in d_ant_zone[(ant)]:  #on a trouv? une bordure de la zone.
                            if voisin not in self.tile_area: #la bordure de la zone ne touche pas ? une autre zone : fronti?re.
                                if v not in d_ant_zone_frontiere[ant] : #ajouter ? la liste de cellules bordures si pas d?j? l?.
                                    d_ant_zone_frontiere[ant].append(v)
                            else:    #la bordure de la zone touche ? une autre zone.  joindre si ce sont deux de mes fourmies.  Si seulement une des fourmies nest pas a moi, alors c'est une frontiere..
                                if (ant,self.tile_area[voisin]) in liste_liens or (self.tile_area[voisin],ant) in liste_liens: #voisin ami  ? moi, connu, ignorer.
                                    continue
                                elif  self.tile_area[voisin] in set_my_ants :  #nouveau voisin ami, ajouter aux liens.
                                    liste_liens.add((ant,self.tile_area[voisin]))

                                elif self.tile_area[voisin] in set_enemy_ants : #nouvel enemi, ajouter aux frontieres.
                                    d_ant_zone_frontiere[ant].append(v)


            if LOG_STDERR:
                sys.stderr.write(" *Start of Areas and Borders -- Fusionner les groupes** ")
                b=str(ants.time_remaining())
                sys.stderr.write(b)
                sys.stderr.write(" ms left****** \n")

            # fusionner les groupes (seulement pour mes fourmis)
            groupe_surface_index=1 #le nombre de groupe de surface
            groupe_surface_dictionnaire={} #dans quel groupe a ?t? envoy? chaque fourmi, la cl? est la fourmie centrale qui donne le nom ? la surface, la valeur est le num?ro d,index de groupe ? laquelel sa surface a ?t? fusionn?e
            groupe_surface=defaultdict(list) #la liste des frontieres de chaque groupe, la cl? est le num?ro d'indice de groupe, les valeurs sont les cellules fronti?res.

            for surface1, surface2 in liste_liens:

                if (surface1 not in groupe_surface_dictionnaire.keys() and surface2 not in groupe_surface_dictionnaire.keys()): #none, create new.
                    for i,j in d_ant_zone_frontiere[(surface1)]:
                        groupe_surface[groupe_surface_index].append((i,j))
                    for i,j in d_ant_zone_frontiere[(surface2)]:
                        groupe_surface[groupe_surface_index].append((i,j))
                    groupe_surface_dictionnaire[surface1] =groupe_surface_index
                    groupe_surface_dictionnaire[surface2] =groupe_surface_index
                    groupe_surface_index= groupe_surface_index+1

                if surface1 in groupe_surface_dictionnaire.keys() and surface2 not in groupe_surface_dictionnaire.keys(): #just first one, add.
                    for i,j in d_ant_zone_frontiere[(surface2)]:
                        groupe_surface[groupe_surface_dictionnaire[surface1]].append((i,j)) #append celllules
                    groupe_surface_dictionnaire[surface2] =groupe_surface_dictionnaire[surface1] #assign groupe

                if surface1 not in groupe_surface_dictionnaire.keys() and surface2 in groupe_surface_dictionnaire.keys(): #just second one, add.
                    for i,j in d_ant_zone_frontiere[(surface1)]:
                        groupe_surface[groupe_surface_dictionnaire[surface2]].append((i,j))

                    groupe_surface_dictionnaire[surface1] =groupe_surface_dictionnaire[surface2]

                if surface1 in groupe_surface_dictionnaire.keys() and surface2 in groupe_surface_dictionnaire.keys(): #both
                    if groupe_surface_dictionnaire[surface1] == groupe_surface_dictionnaire[surface2]:  #if same group, do nothing
                        pass
                    else :   #if different, merge in first group number
                        index_groupe_a_joindre=groupe_surface_dictionnaire[surface1]
                        index_groupe_a_effacer=groupe_surface_dictionnaire[surface2]

                        for i,j in groupe_surface[index_groupe_a_effacer]:
                            groupe_surface[groupe_surface_dictionnaire[surface1]].append((i,j))
                        groupe_surface[index_groupe_a_effacer].remove

                        #for k,v in groupe_surface_dictionnaire.items():
                        for k,v in groupe_surface_dictionnaire.items():
                                if v==index_groupe_a_effacer:
                                    groupe_surface_dictionnaire[k]=index_groupe_a_joindre

            for ant in ants.my_ants() :  #on doit donner un groupe aux fourmis isolees
                if ant not in groupe_surface_dictionnaire.keys():
                    groupe_surface_dictionnaire[ant]=groupe_surface_index
                    for i,j in d_ant_zone_frontiere[(ant)]:
                        groupe_surface[groupe_surface_index].append((i,j))
                    groupe_surface_index=groupe_surface_index+1

            set_unique_group_values = [] #list des groupes existants ? la fin
            for k,v in groupe_surface_dictionnaire.iteritems():
                if v not in set_unique_group_values:
                    set_unique_group_values.append(v)


            for groupe in set_unique_group_values: #sauvegarder les cellules frontieres en cas de break..
                for tile in groupe_surface[(groupe)]:
                    self.list_borders.append(tile)

            if AIVISUALIZE: #dessiner les cellules frontieres
                for groupe in set_unique_group_values:
                    rgb=20*groupe
                    if rgb>255:
                        rgb=250
                    sys.stdout.write('v setFillColor %s %s %s 1 \n' % (rgb,rgb,rgb)  )
                    for i,j in groupe_surface[(groupe)]:
                        sys.stdout.write('v tile %s %s \n' % (i,j))
        else: #si on saute les zone de bordures, utiliser les bordures, + le dire.
            groupe_surface=defaultdict(list)
            groupe_surface_dictionnaire = {}
            groupe_surface[1]= list(self.list_borders)
            for ant in set_my_ants:
                groupe_surface_dictionnaire[ant]=1

            if AIVISUALIZE: #dessiner les cellules frontieres, un peu rougeatre pour indiquer qu'elles sont vieilles..
                sys.stdout.write('v setFillColor 255 120 120 1 \n'   )
                for i,j in groupe_surface[1]:
                    sys.stdout.write('v tile %s %s \n' % (i,j))



            if LOG_STDERR:
                sys.stderr.write(" ***** SKIPPED (Areas and Borders) On recycle l'an pass?.")
                b=str(ants.time_remaining())
                sys.stderr.write(b)
                sys.stderr.write(" ms left* \n")
# ****************************************************************************************************
# DEBUT COMBAT ZONE ENEMIES=
# ****************************************************************************************************
        #d?terminer quelles fourmies enemies peuvent entrer en contact avec moi ce tour ci.
        if LOG_STDERR:
            sys.stderr.write(" *Determine which enemy ants can reach my ants*")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left* \n")

        #nouveau liste_close_enemy_ants..
        liste_close_enemy_ants=set() #liste des fourmis enemies qui me menacent.
        d_ant_zone_mes_fourmis=defaultdict(list) #pour chaque fourmi enemies, une liste de mes fourmies pr?sentes.

        for ant in set_enemy_ants:
            for tuile in ants.tiles_range_attack_plus2[ant]:
                if tuile in set_my_ants:
                    d_ant_zone_mes_fourmis[ant].append(tuile) # ajouter ma fourmi a la liste de fourmies que la m?chante pour attaquer..
                    if ant not in liste_close_enemy_ants:
                        liste_close_enemy_ants.add(ant)  #ajouter la fourmi a la liste des fourmies enemies in range

        #d?terminer les areas et leurs fronti?res.
        if LOG_STDERR:
            sys.stderr.write(" *determiner les liens entre les fourmis enemies (combat zones*")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left* \n")
        #determiner lesliens entre les fourmis enemies
        liste_liens=[] #liste des liens entre surfaces

        #for ant,owner in ants.enemy_ants():
        for ant in liste_close_enemy_ants:
            liste_sans_ant = list(liste_close_enemy_ants)
            liste_sans_ant.remove(ant)
            for ant2 in liste_sans_ant: #poru chaque autre fourmi dans la liste d?terminer si elles ont une de mes fourmis comme cible commune:
                for mes_fourmis in d_ant_zone_mes_fourmis[ant]:
                    if mes_fourmis in d_ant_zone_mes_fourmis[ant2]:  #ce sont des voisins!
                        if ([ant,ant2]) and([ant2, ant]) not in liste_liens:  #si ce lien n est pas recens?, l'ajouter ? la liste:
                            liste_liens.append([ant,ant2])

        if LOG_STDERR:
            sys.stderr.write(" *Combatzones-- Fusionner les groupes** ")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left****** \n")


        # fusionner les groupes (seulement pour leurs  fourmis)
        groupe_combat_index=1 #le nombre de groupe de surface
        groupe_combat_dictionnaire={} #dans quel groupe a ?t? envoy? chaque fourmi enemies, la cl? est la fourmie centrale qui donne le nom ? la surface, la valeur est le num?ro d,index de groupe ? laquelel sa surface a ?t? fusionn?e
        groupe_combat=defaultdict(list) #la liste de mes fourmise chaque groupe, la cl? est le num?ro d'indice de groupe, les valeurs sont mes fourmis
        groupe_combat_enemy = defaultdict(list) #la liste des fourmis enemies dans chaque groupe, cl?  = num?ro d'indice de groupe, valeurs = liste des fourmis enemies
        for surface1, surface2 in liste_liens:

            if (surface1 not in groupe_combat_dictionnaire.keys() and surface2 not in groupe_combat_dictionnaire.keys()): #none, create new.
                for i,j in d_ant_zone_mes_fourmis[(surface1)]:
                    if (i,j) not in groupe_combat[groupe_combat_index]:
                        groupe_combat[groupe_combat_index].append((i,j))
                for i,j in d_ant_zone_mes_fourmis[(surface2)]:
                    if (i,j) not in groupe_combat[groupe_combat_index]:
                        groupe_combat[groupe_combat_index].append((i,j))
                groupe_combat_dictionnaire[surface1] =groupe_combat_index
                groupe_combat_dictionnaire[surface2] =groupe_combat_index
                groupe_combat_index= groupe_combat_index+1

            if surface1 in groupe_combat_dictionnaire.keys() and surface2 not in groupe_combat_dictionnaire.keys(): #just first one, add.
                for i,j in d_ant_zone_mes_fourmis[(surface2)]:
                    if (i,j) not in groupe_combat[groupe_combat_dictionnaire[surface1]]:
                        groupe_combat[groupe_combat_dictionnaire[surface1]].append((i,j)) #append celllules
                groupe_combat_dictionnaire[surface2] =groupe_combat_dictionnaire[surface1] #assign groupe

            if surface1 not in groupe_combat_dictionnaire.keys() and surface2 in groupe_combat_dictionnaire.keys(): #just second one, add.
                for i,j in d_ant_zone_mes_fourmis[(surface1)]:
                    if (i,j) not in groupe_combat[groupe_combat_dictionnaire[surface2]]:
                        groupe_combat[groupe_combat_dictionnaire[surface2]].append((i,j))

                groupe_combat_dictionnaire[surface1] =groupe_combat_dictionnaire[surface2]

            if surface1 in groupe_combat_dictionnaire.keys() and surface2 in groupe_combat_dictionnaire.keys(): #both
                if groupe_combat_dictionnaire[surface1] == groupe_combat_dictionnaire[surface2]:  #if same group, do nothing
                    pass
                else :   #if different, merge in first group number
                    index_groupe_a_joindre=groupe_combat_dictionnaire[surface1]
                    index_groupe_a_effacer=groupe_combat_dictionnaire[surface2]

                    for i,j in groupe_combat[index_groupe_a_effacer]:
                        if (i,j) not in groupe_combat[groupe_combat_dictionnaire[surface1]]:
                            groupe_combat[groupe_combat_dictionnaire[surface1]].append((i,j))
                    groupe_combat[index_groupe_a_effacer].remove

                    for k,v in groupe_combat_dictionnaire.items():
                            if v==index_groupe_a_effacer:
                                groupe_combat_dictionnaire[k]=index_groupe_a_joindre

        #for ant,owner in ants.enemy_ants() :  #on doit donner un groupe aux fourmis isolees
        for ant in liste_close_enemy_ants:
            if ant not in groupe_combat_dictionnaire.keys():
                groupe_combat_dictionnaire[ant]=groupe_combat_index
                for i,j in d_ant_zone_mes_fourmis[(ant)]:
                    groupe_combat[groupe_combat_index].append((i,j))
                groupe_combat_index=groupe_combat_index+1

        set_unique_combat_values = []
        for k,v in groupe_combat_dictionnaire.iteritems():
            groupe_combat_enemy[v].append((k))   #liste des enemis dans chaque groupe de combat v

            if v not in set_unique_combat_values:
                set_unique_combat_values.append(v)  #list des groupes uniques existants ? la fin

        set_fourmis_menacees=set()  #creation de mon set de fourmis menacees
        for groupe in set_unique_combat_values:
            for ant in groupe_combat[(groupe)]:
                if ant not in set_fourmis_menacees:
                    set_fourmis_menacees.add(ant)

        if LOG_COMBAT and set_unique_combat_values: #ecrire ceci si il y a au moins un combat...
            sys.stderr.write("Liste des groupes de combat: \n")
            for groupe in set_unique_combat_values:
                b=str(groupe)
                sys.stderr.write("Groupe ")
                sys.stderr.write(b)
                sys.stderr.write(" - Mes fourmis:")
                for ant in groupe_combat[(groupe)]:
                    b=str(ant)
                    sys.stderr.write(b)
                sys.stderr.write(" - Enemy fourmis:")
                for ant in groupe_combat_enemy[(groupe)]:
                    b=str(ant)
                    sys.stderr.write(b)
                sys.stderr.write(" \n")
                sys.stderr.flush

        if AIVISUALIZE: #colorer en rouge les fourmis dans zone de combat
            for groupe in set_unique_combat_values:
                rgb=250
                sys.stdout.write('v setFillColor 250 0 0 1 \n')
                for i,j in groupe_combat[(groupe)]:
                    sys.stdout.write('v tile %s %s \n' % (i,j))



#******************************************************************
#FIN COMBAT ZONE ENEMIES
#******************************************************************
#D?BUT COMBAT!!!
#******************************************************************
        if LOG_STDERR:
            sys.stderr.write(" *Start of COMBAT** ")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left****** \n")

        taille=defaultdict(int)        #dictionnaire groupe et sa taille.

        for groupe in set_unique_combat_values:
            taille[groupe]= len(groupe_combat[groupe])

    #ccode pour ?valuer les groupes en ordre de taille. Comme ?a le fait qu'un gros groupe prenne du temps ne p?nalise pas les petits...
        for groupe in sorted(taille,key=taille.get):
            myAnts=[]
            myAnts=groupe_combat[groupe]
            enemyAnts=[]
            enemyAnts=groupe_combat_enemy[groupe]
            myAnts_size=len(myAnts)
            enemyAnts_size=len(enemyAnts)
            enemyAnts_temp=list(enemyAnts)

            if LOG_COMBAT_RESULT:
                a=ants.time_remaining()

            #verifier quelles tuiles ne sont pas atteignables par l'enemi en 1 tour
            set_inside_of_enemy_range_plus1=set()
            for enemy in enemyAnts:
                for tuile in ants.tiles_range_attack_plus1[enemy]:
                    if tuile not in set_inside_of_enemy_range_plus1:
                        set_inside_of_enemy_range_plus1.add(tuile)



            #verifier quelles tuiles ne sont pas atteignables par moi en **2** tours.
            set_inside_of_my_range_plus2=set()
            for ant in myAnts:
                for tuile in ants.tiles_range_attack_plus2[ant]:
                    if tuile not in set_inside_of_my_range_plus2:
                        set_inside_of_my_range_plus2.add(tuile)

            # ************* Move possibles mon ?quipe (on ne consid?re qu'un move d'esquive)
            move_possible=defaultdict(list) #liste des moves possibles pour chacunes des fourmis dans le combat. (garder seulement 1 move d'esquive pour mes fourmis)
            move_esquive = defaultdict(list) #liste des moves d'esquives pour chacune de mes fourmis.
            for ant in groupe_combat[groupe]:
                if ant in set_inside_of_enemy_range_plus1: #je suis en port?e enemie, donc ajouter aux moves possibles
                    move_possible[ant].append(ant)
                elif not move_esquive[ant]: #je suis pas en port?e enemie, mais premiere case hors de porter: ajouter aux moves possibles
                    move_possible[ant].append(ant)
                    move_esquive[ant].append(ant)
                else: #2e ou plus move hors de port?e, ne pas ajouter aux moves possibles.
                    move_esquive[ant].append(ant)

                for voisin in ants.tiles_voisins[ant]:
                    if voisin in set_inside_of_enemy_range_plus1: #je suis en port?e enemie, donc ajouter aux moves possibles
                        move_possible[ant].append(voisin)
                    elif not move_esquive[ant]: #je suis pas en port?e enemie, mais premiere case hors de porter: ajouter aux moves possibles
                        move_possible[ant].append(voisin)
                        move_esquive[ant].append(voisin)
                    else: #2e ou plus move hors de port?e, ne pas ajouter aux moves possibles.
                        move_esquive[ant].append(voisin)

            #test..

            # ************* Move possibles m?chants (on ne consid?re qu'un move d'esquive)
            move_possible_enemy=defaultdict(list) #liste des moves possibles pour chacunes des fourmis dans le combat. (garder seulement 1 move d'esquive pour mes fourmis)
            move_esquive_enemy = defaultdict(list) #liste des moves d'esquives pour chacune de mes fourmis.
            for ant in groupe_combat_enemy[groupe]:
                if ant in set_inside_of_my_range_plus2: #je suis en port?e enemie, donc ajouter aux moves possibles
                    move_possible_enemy[ant].append(ant)
                elif not move_esquive_enemy[ant]: #je suis pas en port?e enemie, mais premiere case hors de porter: ajouter aux moves possibles
                    move_possible_enemy[ant].append(ant)
                    move_esquive_enemy[ant].append(ant)
                else: #2e ou plus move hors de port?e, ne pas ajouter aux moves possibles.
                    move_esquive_enemy[ant].append(ant)

                for voisin in ants.tiles_voisins[ant]:
                    if voisin in set_inside_of_my_range_plus2: #je suis en port?e enemie, donc ajouter aux moves possibles
                        move_possible_enemy[ant].append(voisin)
                    elif not move_esquive_enemy[ant]: #je suis pas en port?e enemie, mais premiere case hors de porter: ajouter aux moves possibles
                        move_possible_enemy[ant].append(voisin)
                        move_esquive_enemy[ant].append(voisin)
                    else: #2e ou plus move hors de port?e, ne pas ajouter aux moves possibles.
                        move_esquive_enemy[ant].append(voisin)

            # verifier si on se met en mode agressif.
            privilegie_survie=1

            for ant in groupe_combat_enemy[groupe]:
                if ant in ants.set_tiles_close_to_my_hills:  #proche de mes hills, ?tre agressif.
                    privilegie_survie=0


            if len(myAnts)>=14:  # ** mettre agressif si j'ai N fourmis ou plus
                privilegie_survie=0
            #if len(myAnts)>=5 and self.broke_last_turn==1:  # ** mettre agressif si j'ai N fourmis ou plus et que j'ai break? au dernier tour (faire du m?nage..)
            #    privilegie_survie=0



            if privilegie_survie==0 and AIVISUALIZE==1:  #dessiner mes fourmis en jaune (plutot que rouge) si elles sont agressives.
                sys.stdout.write('v setFillColor 250 250 0 1 \n' )
                for ant in groupe_combat[groupe]:
                        i,j=ant
                        sys.stdout.write('v tile %s %s \n' % (i,j))

            # ************* ?valuer le combat
            if len(myAnts)==1  and privilegie_survie==1: #si seulement une fourmi, privil?gier la recherche de bouffe.. (sauf si agressif, donc proche de ma maison..)
                ant=myAnts[0]
                enemy=enemyAnts[0]
                if ant in self.long_missions_food: # if ant already has a food mission,get rid of it.
                    del self.long_missions_food[ant] #


                if ant not in orders.values():
                    tiles_from = {} #dictionnaire
                    from_nodes = [] #list des nodes ? ?valuer.  on commence avec seulement food_loc
                    from_nodes.append(ant)
                    to_nodes = [] # list des nodes ajout?es apr?s ?valuation

                    steps = 1
                    while (from_nodes and steps < 13 and ant not in orders.values() ):
                        for nodes in from_nodes: #
                            for new_loc in ants.tiles_voisins[(nodes)]:

                                if (new_loc in tiles_from):  #passer si d?ja ?valu?e
                                    continue
                                if steps==1 and not can_move_to(new_loc):   #passer si premiere case non atteignable.
                                    continue

                                if new_loc in set_inside_of_enemy_range_plus1:   #passer si dans range de l'enemi
                                    continue

                                #si correcte, continuer le BFS
                                tiles_from[(new_loc)] = nodes
                                to_nodes.append(new_loc)

                                #si on trouve qqch, essayer d'y aller..
                                if (new_loc in ants.food() and  new_loc not in new_long_missions_food.values() and new_loc not in self.long_missions_food.values() and ant not in orders.values()  ): #la case est 1) une bouffe 2 on a pas d?j? trouv? de fourmi pour la bouffe ? cette ?tape-ci 3) la fourmi a pas d'ordre
                                    current_tile=new_loc
                                    came_from_tile=nodes
                                    while came_from_tile <> ant:
                                        current_tile=came_from_tile
                                        came_from_tile=tiles_from[came_from_tile]

                                    if do_move_location(ant, current_tile):  #essayer marcher vers la case "nodes" soit celle qui  a ?t? ?valu?e juste apres la fourmi
                                        new_long_missions_food[(current_tile)]=new_loc #on veut pas changer d'id?e ? tous les tours...
                                        if AIVISUALIZE:
                                            row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                                            row2, col2 = new_loc #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.write('v setLineColor 120 120 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.flush()
                        from_nodes=to_nodes
                        to_nodes=[]
                        steps=steps+1
                if ant not in orders.values(): #if we didnt give an order to the ant, let's resolve this combast normally.
                    bestscore, deaths, myAnts_best,distance,broken = maximise_combat(0,-99, 0,myAnts,myAnts,99,enemyAnts,privilegie_survie,myAnts)
                    if broken==1:
                        sys.stderr.write("*********broken!!!*****")

                    # ************* Donner les ordres de combat, si c'est un move d'esquive l'?valuer..
                    else:

                        index=0
                        while index < myAnts_size:
                            ant= myAnts[index]
                            if ant <> myAnts_best[index]:  #move
                                if myAnts_best[index] not in move_esquive[ant]: #si le move n'est pas un move d'esquive:
                                    do_move_location(myAnts[index], myAnts_best[index])

                                elif len(ants.tiles_voisins[myAnts_best[index]]) ==1 : #move d esquive dans un trou. . agressif!!
                                        privilegie_survie=0
                                        bestscore, deaths, myAnts_best,distance,broken = maximise_combat(0,-99, 0,myAnts,myAnts,99,enemyAnts,privilegie_survie,myAnts)
                                        do_move_location(myAnts[index], myAnts_best[index])

                                elif len(move_esquive[ant])==1  :  #juste un move d'esquive, le faire.
                                        do_move_location(myAnts[index], myAnts_best[index])

                                else:  #plusieurs move d'Esquive possible. trouver le meilleur.
                                    tiles_from = {} #dictionnaire
                                    score = {} # dictionnaire avec la tuile et son score (distance - 5*enemie + 5* friendly
                                    from_nodes = [] #list des nodes ? ?valuer.  on commence avec seulement food_loc

                                    for move in myAnts_best: #enlever de mes choix les moves d'esquives utilis?s par les autres.
                                        if move in move_esquive[ant] and move <> myAnts_best[index]:
                                            move_esquive[ant].remove(move)

                                    for move in move_esquive[ant]:
                                        from_nodes.append(move)
                                        score[move]=0
                                    to_nodes = [] # list des nodes ajout?es apr?s ?valuation

                                    steps = 1
                                    while (from_nodes and steps < 7):
                                        for nodes in from_nodes: #
                                            for voisin in ants.tiles_voisins[(nodes)]:

                                                if (voisin in tiles_from):  #passer si d?ja ?valu?e
                                                    continue


                                                if steps==1 and not can_move_to(voisin):   #passer si premiere case non atteignable.
                                                #if not can_move_to(new_loc):   #passer toutes les cases non atteignables (test).
                                                    continue

                                                #si correcte, continuer le BFS
                                                tiles_from[(voisin)] = nodes
                                                to_nodes.append(voisin)
                                                score[voisin]=score[nodes]+1
                                                if voisin in set_inside_of_enemy_range_plus1:
                                                    score[voisin]= score[voisin]-2
                                                if voisin in set_enemy_ants:
                                                    score[voisin]= score[voisin]-5
                                                if voisin in set_my_ants:
                                                    score[voisin]=score[voisin]+2


                                        from_nodes=to_nodes
                                        to_nodes=[]
                                        steps=steps+1
                                    target = max(score,key=score.get)
                                    current_tile=target
                                    came_from_tile=tiles_from[target]
                                    while came_from_tile not in move_esquive[ant]:
                                        current_tile=came_from_tile
                                        came_from_tile=tiles_from[came_from_tile]
                                    do_move_location(ant,came_from_tile) #On choisi ce move d'esquive.
                                    myAnts_best[index]=came_from_tile

                            else: #si le move est "bouge pas", ajouter ce move a la liste d'ordres.
                                orders[myAnts[index]]= myAnts[index]
                                set_ants_sans_ordre.remove(myAnts[index])
                            row1,col1 =myAnts[index]
                            row2,col2 =myAnts_best[index]
                            sys.stdout.write('v setLineColor 0 0 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                            sys.stdout.write('v line %s %s %s %s \n' % (row1,col1,row2,col2))
                            index=index+1

            elif len(myAnts)<=6 and len(myAnts)+len(enemyAnts)<=8: #si petit groupe, utiliser maximiser, puis donner ordres.
                bestscore, deaths, myAnts_best,distance,broken = maximise_combat(0,-99, 0,myAnts,myAnts,99,enemyAnts,privilegie_survie,myAnts)
                #si on est pacifique, verifier si qqun recule dans un trou.  si oui, recommencer en agressif.
                if privilegie_survie==1:
                    index=0
                    while index <myAnts_size:
                        if len(ants.tiles_voisins[myAnts_best[index]]) ==1 : #move d esquive dans un trou. . agressif!!
                            sys.stderr.write("qqun recule dans le trou, recommencer en agressif! \n")
                            privilegie_survie=0
                            bestscore, deaths, myAnts_best,distance,broken = maximise_combat(0,-99, 0,myAnts,myAnts,99,enemyAnts,privilegie_survie,myAnts)
                            break
                        index=index+1


                #if broken==1:
                    #sys.stderr.write("*********broken!!! flee!*****")
                    #flee(myAnts,enemyAnts,move_esquive,set_inside_of_enemy_range_plus1)

                #else:

                # ************* Donner les ordres de combat, si c'est un move d'esquive l'?valuer..
                index=0
                while index < myAnts_size:
                    ant= myAnts[index]
                    if ant <> myAnts_best[index]:  #move
                        if myAnts_best[index] not in move_esquive[ant]: #si le move n'est pas un move d'esquive:
                            do_move_location(myAnts[index], myAnts_best[index])

                        elif len(move_esquive[ant]) ==1 : # il y a juste un move d'esquive, pas d'alternative.
                            do_move_location(myAnts[index], myAnts_best[index])

                        else:  #si on fait un move d'esquive, trouver le meilleur (loin des enemis)
                            tiles_from = {} #dictionnaire
                            score = {} # dictionnaire avec la tuile et son score (distance - 5*enemie + 5* friendly
                            from_nodes = [] #list des nodes ? ?valuer.  on commence avec seulement food_loc

                            for move in myAnts_best: #enlever de mes choix les moves d'esquives utilis?s par les autres.
                                if move in move_esquive[ant] and move <> myAnts_best[index]:
                                    move_esquive[ant].remove(move)

                            for move in move_esquive[ant]:
                                from_nodes.append(move)
                                score[move]=0
                            to_nodes = [] # list des nodes ajout?es apr?s ?valuation

                            steps = 1
                            while (from_nodes and steps < 7):
                                for nodes in from_nodes: #
                                    for voisin in ants.tiles_voisins[(nodes)]:

                                        if (voisin in tiles_from):  #passer si d?ja ?valu?e
                                            continue

                                        if steps==1 and not can_move_to(voisin):   #passer si premiere case non atteignable.
                                        #if not can_move_to(new_loc):   #passer toutes les cases non atteignables (test).
                                            continue

                                        #si correcte, continuer le BFS
                                        tiles_from[(voisin)] = nodes
                                        to_nodes.append(voisin)
                                        score[voisin]=score[nodes]+1
                                        if voisin in set_inside_of_enemy_range_plus1:
                                            score[voisin]= score[voisin]-2
                                        if voisin in set_enemy_ants:
                                            score[voisin]= score[voisin]-5
                                        if voisin in set_my_ants:
                                            score[voisin]=score[voisin]+2

                                from_nodes=to_nodes
                                to_nodes=[]
                                steps=steps+1
                            target = max(score,key=score.get)
                            current_tile=target
                            came_from_tile=tiles_from[target]
                            while came_from_tile not in move_esquive[ant]:
                                current_tile=came_from_tile
                                came_from_tile=tiles_from[came_from_tile]
                            do_move_location(ant,came_from_tile) #On choisi ce move d'esquive.
                            myAnts_best[index]=came_from_tile

                    else: #si le move est "bouge pas", ajouter ce move a la liste d'ordres.
                        orders[myAnts[index]]= myAnts[index]
                        set_ants_sans_ordre.remove(myAnts[index])
                    row1,col1 =myAnts[index]
                    row2,col2 =myAnts_best[index]
                    sys.stdout.write('v setLineColor 0 0 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                    sys.stdout.write('v line %s %s %s %s \n' % (row1,col1,row2,col2))
                    index=index+1


            elif len(myAnts)<=8 : #si petit groupe,mais trop d'enemis, assumer enemies immobiles.
                sys.stderr.write("gros combat, on fait comme si les enemis ?taient frozen \n")
                bestscore, deaths, myAnts_best,distance,broken = maximise_combat_frozen_enemy(0,-99, 0,myAnts,myAnts,99,enemyAnts,privilegie_survie,myAnts)
                #if broken==1:
                    #sys.stderr.write("*********broken!!! flee!*****")
                    #flee(myAnts,enemyAnts,move_esquive,set_inside_of_enemy_range_plus1)

                #else:

                # ************* Donner les ordres de combat, si c'est un move d'esquive l'?valuer..
                index=0
                while index < myAnts_size:
                    ant= myAnts[index]
                    if ant <> myAnts_best[index]:  #move
                        if myAnts_best[index] not in move_esquive[ant]: #si le move n'est pas un move d'esquive:
                            do_move_location(myAnts[index], myAnts_best[index])

                        elif len(move_esquive[ant]) ==1 : # il y a juste un move d'esquive, pas d'alternative.
                            do_move_location(myAnts[index], myAnts_best[index])

                        else:  #si on fait un move d'esquive, trouver le meilleur (loin des enemis)
                            tiles_from = {} #dictionnaire
                            score = {} # dictionnaire avec la tuile et son score (distance - 5*enemie + 5* friendly
                            from_nodes = [] #list des nodes ? ?valuer.  on commence avec seulement food_loc

                            for move in myAnts_best: #enlever de mes choix les moves d'esquives utilis?s par les autres.
                                if move in move_esquive[ant] and move <> myAnts_best[index]:
                                    move_esquive[ant].remove(move)

                            for move in move_esquive[ant]:
                                from_nodes.append(move)
                                score[move]=0
                            to_nodes = [] # list des nodes ajout?es apr?s ?valuation

                            steps = 1
                            while (from_nodes and steps < 7):
                                for nodes in from_nodes: #
                                    for voisin in ants.tiles_voisins[(nodes)]:

                                        if (voisin in tiles_from):  #passer si d?ja ?valu?e
                                            continue

                                        if steps==1 and not can_move_to(voisin):   #passer si premiere case non atteignable.
                                        #if not can_move_to(new_loc):   #passer toutes les cases non atteignables (test).
                                            continue

                                        #si correcte, continuer le BFS
                                        tiles_from[(voisin)] = nodes
                                        to_nodes.append(voisin)
                                        score[voisin]=score[nodes]+1
                                        if voisin in set_inside_of_enemy_range_plus1:
                                            score[voisin]= score[voisin]-2
                                        if voisin in set_enemy_ants:
                                            score[voisin]= score[voisin]-5
                                        if voisin in set_my_ants:
                                            score[voisin]=score[voisin]+2

                                from_nodes=to_nodes
                                to_nodes=[]
                                steps=steps+1
                            target = max(score,key=score.get)
                            current_tile=target
                            came_from_tile=tiles_from[target]
                            while came_from_tile not in move_esquive[ant]:
                                current_tile=came_from_tile
                                came_from_tile=tiles_from[came_from_tile]
                            do_move_location(ant,came_from_tile) #On choisi ce move d'esquive.
                            myAnts_best[index]=came_from_tile

                    else: #si le move est "bouge pas", ajouter ce move a la liste d'ordres.
                        orders[myAnts[index]]= myAnts[index]
                        set_ants_sans_ordre.remove(myAnts[index])
                    row1,col1 =myAnts[index]
                    row2,col2 =myAnts_best[index]
                    sys.stdout.write('v setLineColor 0 0 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                    sys.stdout.write('v line %s %s %s %s \n' % (row1,col1,row2,col2))
                    index=index+1




            else: #si gros groupe, utiliser fonction charge..
                charge(myAnts,enemyAnts)

            if LOG_COMBAT_RESULT:
                b=str(groupe)
                sys.stderr.write("eval groupe ")
                sys.stderr.write(b)
                sys.stderr.write(" termin?e-  ")
                sys.stderr.write(" Temps ")
                b=str(a-ants.time_remaining())
                sys.stderr.write(b)
                sys.stderr.write(" ms.")
                sys.stderr.write("Moi=  ")
                b=str(len(myAnts))
                sys.stderr.write(b)
                sys.stderr.write(" Eux=  ")
                b=str(len(enemyAnts))
                sys.stderr.write(b)
                sys.stderr.write(" Total:=  ")
                b=str(len(enemyAnts)+len(myAnts))
                sys.stderr.write(b)
                sys.stderr.write(" \n  ")

#******************************************************************
#FIN COMBAT
#******************************************************************
#D?BUT VISIBLIT?
#******************************************************************
        #d?terminer les tuiles visibles, le nombre d'amis en dedans de N tuiles, les ennemis dans N tuiles
        if LOG_STDERR:
            sys.stderr.write(" *Start of BFS (visibility)*multi source**** ")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left*** \n")

        #maintenant on va chercher de mes fourmi ET de mes hills (pour ne pas que les gens retournent sur leurs pas pour explorer les collines..

        ants_tiles_scan_distance=10  #distance maximale pour un BFS qui part de chaque fourmi et qui compte le nombre de voisines amies, enemies et la valeur maximum  explorevalue d'une tuile non visible ? 11 pas.

        set_my_ants_and_hills=set(set_my_ants)
        for hill in ants.my_hills():
            if hill not in set_my_ants_and_hills:
                set_my_ants_and_hills.add(hill)


        tiles_from = {} #dictionnaire tuiles visit?es (tuile pr?c?dente)
        from_nodes=[]
        for ant in set_my_ants_and_hills: #start bfs of length ants_tiles_can_distance
            from_nodes.append(ant)
        to_nodes=[]
        steps=1
        while (steps<=ants_tiles_scan_distance and from_nodes):
            for from_node in from_nodes:
                for new_loc in ants.tiles_voisins[(from_node)]:

                    if (new_loc not in tiles_from):
                        tiles_from[new_loc]=from_node
                        to_nodes.append(new_loc)
                        self.explorevalue[new_loc]=-1

            from_nodes=to_nodes
            to_nodes=[]
            steps=steps+1

        #mettre ? jour les explore values (on monte tout de 1)

        if LOG_STDERR:
            sys.stderr.write(" *Start ofUpdate ExploreValues*")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left* \n")

        # (on monte tout de 1 apr?s avoir baiss? les visible ? -1)
        for tile in self.explorevalue.keys() :
            self.explorevalue[tile]=self.explorevalue[tile]+1
#******************************************************************
#FIN VISIBILIT?
#******************************************************************
#D?BUT BOUFFE
#******************************************************************
        #*************************************** ********BFS FOOD
        if LOG_STDERR:
            sys.stderr.write(" *Start of BFS (food) single source* ")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left* \n")

        if ant_count<=5:
     #commencer par faire le m?nage dans les missions...
            for ant,food in self.long_missions_food.items():
                if not ant in set_my_ants or ant in orders.values() or food not in ants.food() : #this mission cannot work (ant got lost/killed,  already has an order or the food is gone..)
                    del  self.long_missions_food[ant]



            for ant in self.long_missions_food: # if ant already has a food mission, try to continue it

                    to_loc,path=astar_path(self,ant,self.long_missions_food[ant])
                    if to_loc<> ant:
                        if do_move_location(ant, to_loc):
                            next_turn_path[to_loc]=str(path[1:])
                            new_long_missions_food[(to_loc)]=self.long_missions_food[ant]
                            if AIVISUALIZE:
                                row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                                row2, col2 = self.long_missions_food[ant] #test AI visualisation % (food_loc, new_loc)
                                sys.stdout.write('v setLineColor 250 250 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                                sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                                sys.stdout.flush()

                    else:
                        del self.long_missions_food[ant] #couldnt find path between ant and food, delete mission.


            for ant in ants.my_ants():  # if doesnt already has a mission, search from ants.
                if ant not in orders.values():
                    tiles_from = {} #dictionnaire
                    from_nodes = [] #list des nodes ? ?valuer.  on commence avec seulement food_loc
                    from_nodes.append(ant)
                    to_nodes = [] # list des nodes ajout?es apr?s ?valuation

                    steps = 1
                    while (from_nodes and steps < 13 and ant not in orders.values() ):
                        for nodes in from_nodes: #
                            for new_loc in ants.tiles_voisins[(nodes)]:

                                if (new_loc in tiles_from):  #passer si d?ja ?valu?e
                                    continue
                                if steps==1 and not can_move_to(new_loc):   #passer si premiere case non atteignable.
                                #if not can_move_to(new_loc):   #passer toutes les cases non atteignables (test).
                                    continue
                                #si correcte, continuer le BFS
                                tiles_from[(new_loc)] = nodes
                                to_nodes.append(new_loc)

                                #si on trouve qqch, essayer d'y aller..
                                if (new_loc in ants.food() and  new_loc not in new_long_missions_food.values() and ant not in orders.values()  ): #la case est 1) une bouffe 2 on a pas d?j? trouv? de fourmi pour la bouffe ? cette ?tape-ci 3) la fourmi a pas d'ordre
                                    current_tile=new_loc
                                    came_from_tile=nodes
                                    while came_from_tile <> ant:
                                        current_tile=came_from_tile
                                        came_from_tile=tiles_from[came_from_tile]

                                    if do_move_location(ant, current_tile):  #essayer marcher vers la case "nodes" soit celle qui  a ?t? ?valu?e juste apres la fourmi
                                        new_long_missions_food[(current_tile)]=new_loc #on veut pas changer d'id?e ? tous les tours...
                                        if AIVISUALIZE:
                                            row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                                            row2, col2 = new_loc #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.write('v setLineColor 120 120 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.flush()
                        from_nodes=to_nodes
                        to_nodes=[]
                        steps=steps+1

                        #fin de BFS Ants to Food (if less than X ants)
            self.long_missions_food={}
            self.long_missions_food= new_long_missions_food.copy()

        else: #if ant_count >5
     #commencer par faire le m?nage dans les missions...
            for ant,food in self.long_missions_food.items():
                if not ant in set_my_ants or ant in orders.values() or food not in ants.food() : #this mission cannot work (ant got lost/killed,  already has an order or the food is gone..)
                    del  self.long_missions_food[ant]


            for food_loc in self.long_missions_food.values(): #START breadth first search for each food_loc
#                ant= find_key(self.long_missions_food,food_loc)
                ant= self.find_key(self.long_missions_food,food_loc)
                to_loc=astar(self,ant,food_loc)
                if to_loc<> ant:
                    if do_move_location(ant, to_loc):
                        new_long_missions_food[(to_loc)]=food_loc
                        if AIVISUALIZE:
                            row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                            row2, col2 = food_loc #test AI visualisation % (food_loc, new_loc)
                            sys.stdout.write('v setLineColor 250 250 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                            sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                            sys.stdout.flush()
                else:
                    del self.long_missions_food[ant] #couldnt find path between ant and food, delete mission.

            for food_loc in ants.food():
                if food_loc not in self.long_missions_food.values():#2- food that are not in the list or were deleted because no path was found..

                    tiles_dist = {} #dictionnaire
                    tiles_from = {} #dictionnaire
                    from_nodes = [] #list des nodes ? ?valuer.  on commence avec seulement food_loc
                    from_nodes.append(food_loc)
                    to_nodes = [] # list des nodes ajout?es apr?s ?valuation
                    steps = 1
                    while (from_nodes and steps < 13 and food_loc not in new_long_missions_food.values()):
                        for nodes in from_nodes:
                            for new_loc in ants.tiles_voisins[(nodes)]:
                                if (new_loc in ants.my_ants() and new_loc not in orders.values() and food_loc not in new_long_missions_food.values()): #la case est 1) une fourmi et 2) une forum pas occup?e et 3) on a pas d?j? trouv? de fourmi pour la bouffe ? cette ?tape-ci
                                    if  do_move_location(new_loc, nodes):  #marcher vers la case "nodes" soit celle qui  a ?t? ?valu?e juste avant la fourmi.

                                        new_long_missions_food[(nodes)] =food_loc
                                        if AIVISUALIZE:
                                            row1, col1 = new_loc #test AI visualisation % (food_loc, new_loc)
                                            row2, col2 = food_loc #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.write('v setLineColor 120 120 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.flush()
                                    else:               #cant move to last BFS square, let's a-star this
                                            to_loc=astar(self,new_loc,food_loc)
                                            if to_loc<> new_loc:
                                                do_move_location(new_loc, to_loc)
                                                new_long_missions_food[(to_loc)]=food_loc
                                                if AIVISUALIZE:
                                                    row1, col1 = new_loc #test AI visualisation % (food_loc, new_loc)
                                                    row2, col2 = food_loc #test AI visualisation % (food_loc, new_loc)
                                                    sys.stdout.write('v setLineColor 120 120 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                                                    sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                                                    sys.stdout.flush()

                                if (new_loc not in tiles_dist):  #si la tile nouvellement ?valu?e est  pas d?ja ?valu?e, alors ajouter ? la liste "to_nodes" qui sera ?valu?e au prochain tour
                                    tiles_dist[(new_loc)] = steps
                                    tiles_from[(new_loc)] = nodes
                                    to_nodes.append(new_loc)

                        from_nodes=to_nodes
                        to_nodes=[]
                        steps=steps+1
            #fin breadth first search FOOD
            self.long_missions_food={}
            self.long_missions_food= new_long_missions_food.copy()
		# prevent stepping on own hill
##    	for hill_loc in ants.my_hills():
##    		orders[hill_loc] = None

        # attack hills####################
        if LOG_STDERR:
            sys.stderr.write(" *Start of attack hills*")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left\n")

        #ajouter les nouvelles collines visibles a ma listee de collines ennemies connues "self.hills):
        current_hills=[]

        for hill_loc, hill_owner in ants.enemy_hills():
            current_hills.append(hill_loc)
            if hill_loc not in self.hills:
                self.hills.append(hill_loc)
        #enlever les collines enemies que j'ai ajout? a la liste mais qui ont ?t? ras?es depuis:
        for hill_loc in self.hills:
                if hill_loc not in current_hills and self.explorevalue[hill_loc]==0 :
                    self.hills.remove(hill_loc)

        for hill_loc in self.hills:  #BFS 30 steps jusqua 6 attaquantes.
                tiles_dist = {} #dictionnaire
                tiles_from = {} #dictionnaire
                from_nodes = [] #list des nodes ? ?valuer.  on commence avec seulement food_loc
                from_nodes.append(hill_loc)
                counter=0
                to_nodes = [] # list des nodes ajout?es apr?s ?valuation
                steps = 1
                while (from_nodes and steps < 30 and counter <=4 ):  #on va chercher max 4 fourmis
                        for nodes in from_nodes: #
                            for new_loc in ants.tiles_voisins[(nodes)]:
                                if (new_loc in ants.my_ants() and new_loc not in orders.values() ): #la case est 1) une fourmi et 2) une forum pas occup?e et 3) on a pas d?j? trouv? de fourmi pour la bouffe ? cette ?tape-ci
                                    if do_move_location(new_loc, nodes):  #marcher vers la case "nodes" soit celle qui  a ?t? ?valu?e juste avant la fourmi.
                                        counter=counter+1
                                        if AIVISUALIZE:
                                            row1, col1 = new_loc #test AI visualisation % (food_loc, new_loc)
                                            row2, col2 = hill_loc #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.write('v setLineColor 0 250 250 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                                            sys.stdout.flush()
                                    else:
                                            to_loc=astar(self,new_loc,hill_loc)
                                            if to_loc<> new_loc:
                                                do_move_location(new_loc, to_loc)
                                                counter=counter+1
                                                if AIVISUALIZE:
                                                    row1, col1 = new_loc #test AI visualisation % (food_loc, new_loc)
                                                    row2, col2 = hill_loc #test AI visualisation % (food_loc, new_loc)
                                                    sys.stdout.write('v setLineColor 200 200 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                                                    sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                                                    sys.stdout.flush()

                                if (new_loc not in tiles_dist):  #si la tile nouvellement ?valu?e est passable et pas d?ja ?valu?e, alors ajouter ? la liste "to_nodes" qui sera ?valu?e au prochain tour
                                    tiles_dist[(new_loc)] = steps
                                    tiles_from[(new_loc)] = nodes
                                    to_nodes.append(new_loc)

                        from_nodes=to_nodes
                        to_nodes=[]
                        steps=steps+1

        #send newly spawned ants to random border tile.
        if LOG_STDERR:
            sys.stderr.write(" *Send ants away from hills*")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left* \n")

        for ant in ants.my_hills():   #2 if on one of my hills, then go to a random border tile;
            if ant in ants.my_ants() and ant not in orders.values():
                groupe_de_la_fourmi = groupe_surface_dictionnaire[ant]
                liste=[]
                for i,j in groupe_surface[groupe_de_la_fourmi]:
                    liste.append((i,j))
                dest = choice(liste)
                to_loc,path=astar_path(self,ant,dest) #simon


                if to_loc<> ant:
                    new_long_missions_explore[to_loc]=dest
                    next_turn_path[to_loc]=str(path[1:])
                    do_move_location(ant, to_loc) #simon
                    if AIVISUALIZE:
                        row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                        row2, col2 = dest #test AI visualisation % (food_loc, new_loc)
                        sys.stdout.write('v setLineColor 0 250 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                        sys.stdout.write('v routePlan %s %s %s \n' % (row1,col1,path)) #test AI visualisation % (food_loc, new_loc)
                        #sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                        sys.stdout.flush() #test AI visualisation  v line row1 col1 row2 col2



                else:  #to_loc= ant .. why?
                    if AIVISUALIZE:
                        i,j=ant
                        sys.stdout.write('v setFillColor 250 0 0 1 \n' )
                        sys.stdout.write('v tile %s %s \n' % (i,j))



        # si on a break? le dernier tour, on essaye de continuer nos vieux paths pour sauver du temps..
        if self.broke_last_turn==1:
            if LOG_STDERR:
                sys.stderr.write(" *On a break? au dernier tour, continuer les vieux paths avant de calculer des nouveaux) ")
                b=str(ants.time_remaining())
                sys.stderr.write(b)
                sys.stderr.write(" ms left \n")

            for ant in list(set_ants_sans_ordre):

                if ant in self.long_missions_explore.keys() :
                        if ant in self.this_turn_path and len(self.this_turn_path[ant])>0:
                            direction=str(self.this_turn_path[ant])[0:1]
                            nextpath=str(self.this_turn_path[ant])[1:]
                            if do_move_direction(ant,direction):
                                new_loc = ants.destination(ant, direction)
                                next_turn_path[new_loc]=nextpath
                                new_long_missions_explore[new_loc]=self.long_missions_explore[ant]
                                if AIVISUALIZE:
                                    row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                                    sys.stdout.write('v setLineColor 250 0 0 1 \n' )
                                    sys.stdout.write('v routePlan %s %s %s \n' % (row1,col1,self.this_turn_path[ant])) #test AI visualisation % (food_loc, new_loc)
                                    sys.stdout.flush()



        # explore unseen areas / continue border move / go to nearby border
        if LOG_STDERR:
            intAntsLeft = len(set_ants_sans_ordre)
            sys.stderr.write(" *Start BFS (explore 11 steps/borders 16 steps) -  ")
            b=str(intAntsLeft)
            sys.stderr.write(b)
            sys.stderr.write(" ants left - ")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left \n")

        intAntsLeft = len(set_ants_sans_ordre)
        intAntCount = 0
        for ant in list(set_ants_sans_ordre):
            intAntCount= intAntCount+1
            if ants.time_remaining()< 150:
                sys.stderr.write(" Not enough time left, breaking at ant ")
                b=str(intAntCount)
                sys.stderr.write(b)
                sys.stderr.write(" of ")
                b=str(intAntsLeft)
                sys.stderr.write(b)
                sys.stderr.write(" \n")
                broke_this_turn=1
                break
            tiles_explorevalue = {} #dictionnaire explore values
            tiles_from = {} #dictionnaire contenant la cellule menant a chaque tuile.
            from_nodes=[]
            from_nodes.append(ant)
            to_nodes=[]
                    #parametres pour try to find a nearby border:
            groupe_de_la_fourmi=groupe_surface_dictionnaire[ant] #dans quel groupe a ?t? envoy? chaque fourmi, la cl? est la fourmie centrale qui donne le nom ? la surface, la valeur est le num?ro d,index de groupe ? laquelel sa surface a ?t? fusionn?e
            bordures=[]
            for i,j in groupe_surface[groupe_de_la_fourmi]: #ajouter chaque cellules dans la liste des frontieres a la liste bordures
                bordures.append((i,j))

            closest_border_tile_move=(0,0)
            closest_enemy_ant=(0,0)

            steps=1
            while (steps<=25 and from_nodes and ant not in orders.values()):
                for from_node in from_nodes: #BFS part
                    for new_loc in ants.tiles_voisins[(from_node)]:
                        if (new_loc in tiles_from ): #deja visite, ignorer.
                            continue
                        if steps==1 and not can_move_to(new_loc):   #premiere case depuis le d?part, ignorer si on ne peut pas marcher dessus.
                        #if not can_move_to(new_loc):  #TEST passer toutes les cases non atteignables
                            continue

                        #si pas d?j? visit?e

                        #continuer le BFS
                        tiles_from[new_loc]=from_node
                        to_nodes.append(new_loc)

                        #verifier si c'est une tuile de bordure a chaque tour
                        if closest_border_tile_move==(0,0) and new_loc in bordures: #sauvegarder le move vers la cellule de border la plus proche , mais ne pas utiliser tout de suite
                                current_tile=new_loc
                                came_from_tile=from_node
                                path=str()
                                path = str(ants.direction(from_node,new_loc))[2:3]
                                while came_from_tile <> ant:
                                    current_tile=came_from_tile
                                    came_from_tile=tiles_from[came_from_tile]
                                    path=str(ants.direction(came_from_tile,current_tile))[2:3]+ path
                                closest_border_tile_move=current_tile

                        #verifier si c'est une fourmie enemie
                        if closest_enemy_ant==(0,0) and new_loc in set_enemy_ants and ant not in orders.values(): #sauvegarder le move vers la cellule de border la plus proche , mais ne pas utiliser tout de suite
                                closest_enemy_ant=new_loc
                                to_loc,path = astar_path_unoccupied(self,ant,new_loc)
                                if to_loc <> ant:
                                    do_move_location(ant, to_loc)

                                else: #astar unoccupied a pas marcher, essayer avec astar_path normal...
                                    if ants.time_remaining()< 150:
                                        to_loc,path = astar_path(self,ant,new_loc)
                                        if to_loc<> ant:
                                            do_move_location(ant, to_loc)


                                if to_loc<> ant and AIVISUALIZE:
                                    row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                                    row2, col2 = new_loc #test AI visualisation % (food_loc, new_loc)
                                    sys.stdout.write('v setLineColor 0 0 120 .4 \n' ) #test AI visualisation % (food_loc, new_loc)
                                    sys.stdout.write('v routePlan %s %s %s \n' % (row1,col1,path)) #test AI visualisation % (food_loc, new_loc)
                                    sys.stdout.flush()

                                #sinon , tant pis..


                        if steps>11 and closest_border_tile_move<>(0,0)  and ant not in orders.values(): #commencer a essayer de se d?placer vers la bordure la plus proche seulement apres avoir trouv? une closest border move
                                if do_move_location(ant, closest_border_tile_move):
                                    new_long_missions_explore[closest_border_tile_move]=new_loc
                                    next_turn_path[closest_border_tile_move]=str(path[1:])
                                    if AIVISUALIZE:
                                        row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                                        row2, col2 = new_loc #test AI visualisation % (food_loc, new_loc)
                                        sys.stdout.write('v setLineColor 0 0 250 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                                        sys.stdout.write('v routePlan %s %s %s \n' % (row1,col1,path)) #test AI visualisation % (food_loc, new_loc)
                                        sys.stdout.flush()
                                else:
                                    closest_border_tile_move= (0,0) #ca a pas march?, effacer.



                        #si c'est le tour 11, verifier si c'est une tuile invisible.  Si oui, ajouter au dictionnaire des tuiles invisibles.
                        if steps==11:
                            tiles_explorevalue[new_loc] = self.explorevalue[new_loc] #la meilleure tuile juste a la limite de la vision



                if steps==11 and ant not in orders.values():
                    #after 11 full steps, check explore values and send the ant to a invisible square.
                    max_explore_value=max(tiles_explorevalue,key=tiles_explorevalue.get)  #m va ?tre "un des items au prix minimal"
                    if tiles_explorevalue[max_explore_value]>2:
                        to_loc,path=astar_path(self,ant,max_explore_value) #simon
                        if to_loc<> ant:
                            if AIVISUALIZE:
                                row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                                #row2, col2 = max_explore_value #test AI visualisation % (food_loc, new_loc)
                                sys.stdout.write('v setLineColor 250 250 250 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                                sys.stdout.write('v routePlan %s %s %s \n' % (row1,col1,path)) #test AI visualisation % (food_loc, new_loc)
                                #sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                                #sys.stdout.write('i %s %s explore value %s \n'% (row2,col2,tiles_explorevalue[max_explore_value]) ) #test AI visualisation % (food_loc, new_loc)
                                sys.stdout.flush() #test AI visualisation  v line row1 col1 row2 col2
                            do_move_location(ant, to_loc) #simon
                    #if no square with explore value, try to continue explore mission:
                    if ant in self.long_missions_explore.keys() and ant not in orders.values():

                            if ant in self.this_turn_path and len(self.this_turn_path[ant])>0:
                                direction=str(self.this_turn_path[ant])[0:1]
                                nextpath=str(self.this_turn_path[ant])[1:]
                                if do_move_direction(ant,direction):
                                    new_loc = ants.destination(ant, direction)
                                    next_turn_path[new_loc]=nextpath
                                    new_long_missions_explore[new_loc]=self.long_missions_explore[ant]

                                    if AIVISUALIZE:
                                        row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                                        sys.stdout.write('v setLineColor 250 0 0 1 \n' )
                                        sys.stdout.write('v routePlan %s %s %s \n' % (row1,col1,self.this_turn_path[ant])) #test AI visualisation % (food_loc, new_loc)
                                        sys.stdout.flush()



                            if ant not in orders.values() :  #les fourmies qui n avaient pas de PATH ou qui n ont pas pu le continuer se retrouvent ici:
                                to_loc,path=astar_path(self,ant,self.long_missions_explore[ant])
                                if to_loc==ant: #failed to find a path,stay put one turn
                                    new_long_missions_explore[ant]=self.long_missions_explore[ant]
                                    if AIVISUALIZE:
                                        row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                                        row2, col2 = self.long_missions_explore[ant] #test AI visualisation % (food_loc, new_loc)
                                        sys.stdout.write('v setLineColor 250 0 0 0.5 \n' ) #test AI visualisation % (food_loc, new_loc)
                                        sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                                        sys.stdout.flush() #test AI visualisation  v line row1 col1 row2 col2

                                else :
                                    do_move_location(ant, to_loc) #simon
                                    new_long_missions_explore[to_loc]=self.long_missions_explore[ant]
                                    next_turn_path[to_loc]=str(path[1:])
                                    if AIVISUALIZE:
                                        row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                                        row2, col2 = self.long_missions_explore[ant] #test AI visualisation % (food_loc, new_loc)
                                        sys.stdout.write('v setLineColor 250 0 0 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                                        sys.stdout.write('v routePlan %s %s %s \n' % (row1,col1,path)) #test AI visualisation % (food_loc, new_loc)
                                        #sys.stdout.write('v line %s %s %s %s \n'% (row1,col1,row2,col2) ) #test AI visualisation % (food_loc, new_loc)
                                        sys.stdout.flush() #test AI visualisation  v line row1 col1 row2 col2
                        #if no unexplored square and no mission to continue, will move to the closest border tile.

                from_nodes=to_nodes
                to_nodes=[]
                steps=steps+1



            if ant not in orders.values(): #4: on a pas trouv? de tile frontiere proche, on y va au random.

                groupe_de_la_fourmi = groupe_surface_dictionnaire[ant]
                liste=[]
                for i,j in groupe_surface[groupe_de_la_fourmi]:
                    liste.append((i,j))
                dest = choice(liste)

                to_loc,path=astar_path(self,ant,dest)
                if to_loc<>ant:
                    new_long_missions_explore[to_loc]=dest
                    do_move_location(ant, to_loc) #simon
                    next_turn_path[to_loc]=str(path[1:])
                    if AIVISUALIZE:
                        row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                        sys.stdout.write('v setLineColor 120 0 120 1 \n' ) #test AI visualisation % (food_loc, new_loc)
                        sys.stdout.write('v routePlan %s %s %s \n' % (row1,col1,path)) #test AI visualisation % (food_loc, new_loc)
                        sys.stdout.flush() #test AI visualisation  v line row1 col1 row2 col2




        #fin breadth first search ant to  border tile
        self.long_missions_explore={}
        self.long_missions_explore= new_long_missions_explore.copy()

        if LOG_STDERR:
            sys.stderr.write(" *Start - Unblock own hill* ")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left \n")


		# unblock own hill
        for hill_loc in ants.my_hills():
            if hill_loc in set_ants_sans_ordre:
                for voisin in ants.tiles_voisins[hill_loc]:
                    if do_move_location(hill_loc,voisin):
                        break

        if broke_this_turn==1:
            if LOG_STDERR:
                sys.stderr.write(" *Start - moves rapides apres break.* ")
                b=str(ants.time_remaining())
                sys.stderr.write(b)
                sys.stderr.write("ms left - ")


            # si on a break?, essayer quand m?me de continuer les paths d?j? calcul?s..
            count=0
            for ant in list(set_ants_sans_ordre):

                if ant in self.long_missions_explore.keys() :
                        if ant in self.this_turn_path and len(self.this_turn_path[ant])>0:
                            direction=str(self.this_turn_path[ant])[0:1]
                            nextpath=str(self.this_turn_path[ant])[1:]
                            if do_move_direction(ant,direction):
                                new_loc = ants.destination(ant, direction)
                                next_turn_path[new_loc]=nextpath
                                new_long_missions_explore[new_loc]=self.long_missions_explore[ant]
                                count=count+1
                                if AIVISUALIZE:
                                    row1, col1 = ant #test AI visualisation % (food_loc, new_loc)
                                    sys.stdout.write('v setLineColor 250 0 0 1 \n' )
                                    sys.stdout.write('v routePlan %s %s %s \n' % (row1,col1,self.this_turn_path[ant])) #test AI visualisation % (food_loc, new_loc)
                                    sys.stdout.flush()
            if LOG_STDERR:
                b=str(count)
                sys.stderr.write(b)
                sys.stderr.write("  moves continu?s ")
            #prevent self kills apres un break par manque de temps..
            count=0
            for ant in list(set_ants_sans_ordre):
                if ants.time_remaining()< 50:
                    break
                if ant in orders.keys(): #qqun s'en vient sur ta case, decrisse!
                    for voisin in ants.tiles_voisins[ant]:
                        if voisin not in orders.keys() and  ants.unoccupied(voisin): #voisin libre..
                            do_move_location(ant,voisin) #d?crisse!
                            count=count+1
                            break #apres 1 d?crissage, on a assez d?criss?..
            if LOG_STDERR:
                b=str(count)
                sys.stderr.write(b)
                sys.stderr.write(" crashs ?vit?s\n")


        self.broke_last_turn=broke_this_turn

        if LOG_STDERR_END:
            sys.stderr.write(" *END OF TURN - ")
            b=str(ants.turn_number)
            sys.stderr.write(b)
            sys.stderr.write(" * - ")
            b=str(ants.time_remaining())
            sys.stderr.write(b)
            sys.stderr.write(" ms left. Ants counts= ")
            b=str(ant_count)
            sys.stderr.write(b)
            if set_ants_sans_ordre:
                sys.stderr.write(" Ants sans ordres:")
                b=str(len(set_ants_sans_ordre))
                sys.stderr.write(b)
            sys.stderr.write("\n")
            sys.stderr.flush


        self.this_turn_path= next_turn_path.copy()
        next_turn_path={}


        sys.stderr.flush
if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass

    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
