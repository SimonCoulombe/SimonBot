#!/usr/bin/env python
import sys
import traceback
import random
import time
from collections import defaultdict
from math import sqrt




MY_ANT = 0
ANTS = 0
DEAD = -1
LAND = -2
FOOD = -3
WATER = -4

PLAYER_ANT = 'abcdefghij'
HILL_ANT = string = 'ABCDEFGHIJ'
PLAYER_HILL = string = '0123456789'
MAP_OBJECT = '?%*.!'
MAP_RENDER = PLAYER_ANT + HILL_ANT + PLAYER_HILL + MAP_OBJECT

AIM = {'n': (-1, 0),
       'e': (0, 1),
       's': (1, 0),
       'w': (0, -1)}
RIGHT = {'n': 'e',
         'e': 's',
         's': 'w',
         'w': 'n'}
LEFT = {'n': 'w',
        'e': 'n',
        's': 'e',
        'w': 's'}
BEHIND = {'n': 's',
          's': 'n',
          'e': 'w',
          'w': 'e'}

directions = ('n','e','s','w')

class Ants():
    def __init__(self):
        self.cols = None
        self.rows = None
        self.map = None
        self.hill_list = {}
        self.ant_list = {}
        self.dead_list = defaultdict(list)
        self.food_list = []
        self.turntime = 0
        self.loadtime = 0
        self.turn_start_time = None
        self.vision = None
        self.viewradius2 = 0
        self.attackradius2 = 0
        self.spawnradius2 = 0
        self.turns = 0

        self.turn_number=0
        self.last_turn_hill_list= {}

    def setup(self, data):
        'parse initial input and setup starting game state'
        for line in data.split('\n'):
            line = line.strip().lower()
            if len(line) > 0:
                tokens = line.split()
                key = tokens[0]
                if key == 'cols':
                    self.cols = int(tokens[1])
                elif key == 'rows':
                    self.rows = int(tokens[1])
                elif key == 'player_seed':
                    random.seed(int(tokens[1]))
                elif key == 'turntime':
                    self.turntime = int(tokens[1])
                elif key == 'loadtime':
                    self.loadtime = int(tokens[1])
                elif key == 'viewradius2':
                    self.viewradius2 = int(tokens[1])
                elif key == 'attackradius2':
                    self.attackradius2 = int(tokens[1])
                elif key == 'spawnradius2':
                    self.spawnradius2 = int(tokens[1])
                elif key == 'turns':
                    self.turns = int(tokens[1])
        self.map = [[LAND for col in range(self.cols)]
                    for row in range(self.rows)]

        self.tiles_voisins = defaultdict(list) #on cree un dictionnaire de liste, contenant chaque cellule et les coordonn?es de ses voisins (plus rapide on esp?re)
        for row in range(self.rows):
			for col in range(self.cols):
					dest=self.destination([row,col], 'n')
					self.tiles_voisins[(row,col)].append(dest)
					dest=self.destination([row,col], 's')
					self.tiles_voisins[(row,col)].append(dest)
					dest=self.destination([row,col], 'w')
					self.tiles_voisins[(row,col)].append(dest)
					dest=self.destination([row,col], 'e')
					self.tiles_voisins[(row,col)].append(dest)


        self.tiles_range_attack = defaultdict(list) #on cree un dictionnaire de liste, contenant chaque cellule et les coordonn?es de ses voisins qui sont "in range" d attaque.
        self.tiles_range_attack_plus1 = defaultdict(list) #on cree un dictionnaire de liste, contenant chaque cellule et les coordonn?es de ses voisins qui sont "in range" d attaque.
        self.tiles_range_attack_plus2 = defaultdict(list) #on cree un dictionnaire de liste, contenant chaque cellule et les coordonn?es de ses voisins qui sont "in range" d attaque.
        for row in range(self.rows):
            for col in range(self.cols):
                ant=(row,col)
                tiles_from ={}
                from_nodes = []
                from_nodes.append(ant)
                to_nodes =[]
                step=1
                while step<=5: #la distance n?cessaire pour attack radius square =5.
                    for node in from_nodes:
                        for voisin in self.tiles_voisins[(node)]:
                                #si d?j? visit?, on saute
                                if voisin in tiles_from:
                                    continue
                                #sinon, on verifie si c est une cellule in range.. si oui, on l'ajoute ? la liste
                                xdist,ydist = self.xy_distance(voisin,ant)

                                if xdist*xdist + ydist*ydist <= 5:  #17  =a max 2 pas de   attack radius squared 5
                                        self.tiles_range_attack[(row,col)].append(voisin)

                                if xdist*xdist + ydist*ydist <= 10:  #17  =a max 2 pas de   attack radius squared 5
                                        self.tiles_range_attack_plus1[(row,col)].append(voisin)

                                if xdist*xdist + ydist*ydist <= 17:  #17  =a max 2 pas de   attack radius squared 5
                                        self.tiles_range_attack_plus2[(row,col)].append(voisin)

                                tiles_from[voisin]=node
                                to_nodes.append(voisin)

                    from_nodes=to_nodes
                    to_nodes=[]
                    step=step+1




    def update(self, data):
        'parse engine input and update the game state'
        # start timer
        self.turn_start_time = time.time()

        self.turn_number=self.turn_number+1
        # reset vision
        self.vision = None

        self.last_turn_hill_list =dict(self.hill_list)

        # clear hill, ant and food data
        self.hill_list = {}

        for row, col in self.ant_list.keys():
            self.map[row][col] = LAND
        self.ant_list = {}

        for row, col in self.dead_list.keys():
            self.map[row][col] = LAND
        self.dead_list = defaultdict(list)

        for row, col in self.food_list:
            self.map[row][col] = LAND
        self.food_list = []

        # update map and create new ant and food lists
        for line in data.split('\n'):
            line = line.strip().lower()
            if len(line) > 0:
                tokens = line.split()
                if len(tokens) >= 3:
                    row = int(tokens[1])
                    col = int(tokens[2])
                    if tokens[0] == 'w':
                        self.map[row][col] = WATER

                        #enlever les liens vers cette cellule
                        temp_list=[] #j'ai pas trouv? de meilleure fa?on de pr?parer l'it?ration pour enlever tous les voisins d'une personne... sinon on brisait..
                        for voisin in self.tiles_voisins[(row,col)]:
                            temp_list.append(voisin)
                        for voisin in temp_list:
                            self.tiles_voisins[(row,col)].remove((voisin)) #enlever les voisins de la cellule d 'eau
                            self.tiles_voisins[voisin].remove((row,col)) # enlever le lien du voisin vers la cellule d'eau ##parenth?se double = funky.

                        #enlever cette cellule du in-range
                        cell=(row,col)
                        liste_attack_range= list(self.tiles_range_attack[cell])
                        for tuile in liste_attack_range:
                            self.tiles_range_attack[cell].remove(tuile)
                            if cell in self.tiles_range_attack[tuile]:
                                self.tiles_range_attack[tuile].remove(cell)


                        #enlever cette cellule du in-range_plus2
                        cell=(row,col)
                        liste_attack_range= list(self.tiles_range_attack_plus1[cell])
                        for tuile in liste_attack_range:
                            self.tiles_range_attack_plus1[cell].remove(tuile)
                            if cell in self.tiles_range_attack_plus1[tuile]:
                                self.tiles_range_attack_plus1[tuile].remove(cell)



                        #enlever cette cellule du in-range_plus2
                        cell=(row,col)
                        liste_attack_range= list(self.tiles_range_attack_plus2[cell])
                        for tuile in liste_attack_range:
                            self.tiles_range_attack_plus2[cell].remove(tuile)
                            if cell in self.tiles_range_attack_plus2[tuile]:
                                self.tiles_range_attack_plus2[tuile].remove(cell)





                    elif tokens[0] == 'f':
                        self.map[row][col] = FOOD
                        self.food_list.append((row, col))
                    else:
                        owner = int(tokens[3])
                        if tokens[0] == 'a':
                            self.map[row][col] = owner
                            self.ant_list[(row, col)] = owner
                        elif tokens[0] == 'd':
                            # food could spawn on a spot where an ant just died
                            # don't overwrite the space unless it is land
                            if self.map[row][col] == LAND:
                                self.map[row][col] = DEAD
                            # but always add to the dead list
                            self.dead_list[(row, col)].append(owner)
                        elif tokens[0] == 'h':
                            owner = int(tokens[3])
                            self.hill_list[(row, col)] = owner


        if self.my_hills() <> self.my_old_hills():
            sys.stderr.write("updating self.set_tiles_close_to_my_hills ")
            self.set_tiles_close_to_my_hills = set() #on cree un dictionnaire de liste, contenant chaque cellule et les coordonn?es de ses voisins qui sont "in range" d attaque.
            tiles_from ={}
            from_nodes = []
            for hill in self.my_hills():
                from_nodes.append(hill)
            to_nodes =[]
            step=1
            while step<=10: #la distance n?cessaire pour attack radius square =5.
                for node in from_nodes:
                    for voisin in self.tiles_voisins[(node)]:
                            #si d?j? visit?, on saute
                            if voisin in tiles_from:
                                continue
                            #sinon, on ajoute a la liste des tuiles a moins de 10 cases de mes hills.
                            self.set_tiles_close_to_my_hills.add(voisin)
                            tiles_from[voisin]=node
                            to_nodes.append(voisin)

                from_nodes=to_nodes
                to_nodes=[]
                step=step+1


    def time_remaining(self):
        return self.turntime - int(1000 * (time.time() - self.turn_start_time))

    def issue_order(self, order):
        'issue an order by writing the proper ant location and direction'
        (row, col), direction = order
        sys.stdout.write('o %s %s %s\n' % (row, col, direction))
        sys.stdout.flush()

    def finish_turn(self):
        'finish the turn by writing the go line'
        sys.stdout.write('go\n')
        sys.stdout.flush()

    def my_hills(self):
        return [loc for loc, owner in self.hill_list.items()
                    if owner == MY_ANT]

    def my_old_hills(self):
        return [loc for loc, owner in self.last_turn_hill_list.items()
                    if owner == MY_ANT]


    def enemy_hills(self):
        return [(loc, owner) for loc, owner in self.hill_list.items()
                    if owner != MY_ANT]

    def my_ants(self):
        'return a list of all my ants'
        return [(row, col) for (row, col), owner in self.ant_list.items()
                    if owner == MY_ANT]

    def enemy_ants(self):
        'return a list of all visible enemy ants'
        return [((row, col), owner)
                    for (row, col), owner in self.ant_list.items()
                    if owner != MY_ANT]

    def food(self):
        'return a list of all food locations'
        return self.food_list[:]

    def passable(self, loc):
        'true if not water'
        row, col = loc
        return self.map[row][col] != WATER

    def unoccupied(self, loc):
        'true if no ants are at the location'
        row, col = loc
        return self.map[row][col] in (LAND, DEAD)

    def destination(self, loc, direction):
        'calculate a new location given the direction and wrap correctly'
        row, col = loc
        d_row, d_col = AIM[direction]
        return ((row + d_row) % self.rows, (col + d_col) % self.cols)

    def distance(self, loc1, loc2):
        'calculate the closest distance between to locations'
        row1, col1 = loc1
        row2, col2 = loc2
        d_col = min(abs(col1 - col2), self.cols - abs(col1 - col2))
        d_row = min(abs(row1 - row2), self.rows - abs(row1 - row2))
        return d_row + d_col

    def xy_distance(self, loc1, loc2):
        'calculate the closest distance between to locations - donne 2 donn?es'
        row1, col1 = loc1
        row2, col2 = loc2
        d_col = min(abs(col1 - col2), self.cols - abs(col1 - col2))
        d_row = min(abs(row1 - row2), self.rows - abs(row1 - row2))
        return d_row , d_col

    def direction(self, loc1, loc2):
        'determine the 1 or 2 fastest (closest) directions to reach a location'
        row1, col1 = loc1
        row2, col2 = loc2
        height2 = self.rows//2
        width2 = self.cols//2
        d = []
        if row1 < row2:
            if row2 - row1 >= height2:
                d.append('n')
            if row2 - row1 <= height2:
                d.append('s')
        if row2 < row1:
            if row1 - row2 >= height2:
                d.append('s')
            if row1 - row2 <= height2:
                d.append('n')
        if col1 < col2:
            if col2 - col1 >= width2:
                d.append('w')
            if col2 - col1 <= width2:
                d.append('e')
        if col2 < col1:
            if col1 - col2 >= width2:
                d.append('e')
            if col1 - col2 <= width2:
                d.append('w')
        return d



    def astar_orders(self,start,goal,orders):
        closetset= [] #ensemble d?ja ?valu?
        openset = {} #ensemble ? ?valuer, la key = tile, valeur = total_estimated_cost
        openset[start]=self.distance(start, goal) #il faut entrer le cout total estim? dans openset aussi.
        came_from = {} #map of navigated node
        cost_so_far = {}
        heuristic_cost = {}
        total_estimated_cost = {}
        cost_so_far[start] = 0
        heuristic_cost[start] =self.distance(start, goal)
        total_estimated_cost[start]=cost_so_far[start]+heuristic_cost[start]

        step=0
        while (openset and (step<10*total_estimated_cost[start] or step<700  )):
            minimum = min(openset,key=openset.get)
            dico_mintotal_minheuristic={}
            for legume,prix in openset.iteritems():
                if prix == openset[minimum]:
                    dico_mintotal_minheuristic[legume]=heuristic_cost[legume]
            current=min(dico_mintotal_minheuristic,key=dico_mintotal_minheuristic.get) #le fruit le moins cher avec le moins de dico_CO2 : la fraise!

            if current==goal: #on a atteint le but, rebrousser chemin pour trouver le premier pas.
                if step==0 :
                    return start #si le but ?gale le d?part, retourner la cellule de d?part
                else:
                    current_step=goal
                    came_from_step= came_from[goal]

                    while (came_from_step <> start):
                        current_step=came_from_step
                        came_from_step= came_from[current_step]

                    return current_step
            del openset[current]
            closetset.append(current)

            for neighbor in self.tiles_voisins[current]:
                if neighbor in closetset: #ne pas consid?rer les cases d?j? v?rifi?es
                    continue

                if step==0:  #if first step, go around occupied tiles.. and targeted tiles  (c'est r?gl? par le call "orders".
                    if neighbor in orders:
                        closedset.append(neighbor)
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
                    heuristic_cost[neighbor]=self.distance(neighbor,goal)
                    cost_so_far[neighbor]=tentative_cost_so_far
                    total_estimated_cost[neighbor]=tentative_cost_so_far+heuristic_cost[neighbor]
                    openset[neighbor]=total_estimated_cost[neighbor]
            step=step+1

        return start #failed to find a path, return the starting location







    def visible(self, loc):
        ' determine which squares are visible to the given player '

        if self.vision == None:
            if not hasattr(self, 'vision_offsets_2'):
                # precalculate squares around an ant to set as visible
                self.vision_offsets_2 = []
                mx = int(sqrt(self.viewradius2))
                for d_row in range(-mx,mx+1):
                    for d_col in range(-mx,mx+1):
                        d = d_row**2 + d_col**2
                        if d <= self.viewradius2:
                            self.vision_offsets_2.append((
                                # Create all negative offsets so vision will
                                # wrap around the edges properly
                                (d_row % self.rows) - self.rows,
                                (d_col % self.cols) - self.cols
                            ))
            # set all spaces as not visible
            # loop through ants and set all squares around ant as visible
            self.vision = [[False]*self.cols for row in range(self.rows)]
            for ant in self.my_ants():
                a_row, a_col = ant
                for v_row, v_col in self.vision_offsets_2:
                    self.vision[a_row + v_row][a_col + v_col] = True
        row, col = loc
        return self.vision[row][col]

    def render_text_map(self):
        'return a pretty string representing the map'
        tmp = ''
        for row in self.map:
            tmp += '# %s\n' % ''.join([MAP_RENDER[col] for col in row])
        return tmp

    # static methods are not tied to a class and don't have self passed in
    # this is a python decorator
    @staticmethod
    def run(bot):
        'parse input, update game state and call the bot classes do_turn method'
        ants = Ants()
        map_data = ''
        while(True):
            try:
                current_line = sys.stdin.readline().rstrip('\r\n') # string new line char
                if current_line.lower() == 'ready':
                    ants.setup(map_data)
                    bot.do_setup(ants)
                    ants.finish_turn()
                    map_data = ''
                elif current_line.lower() == 'go':
                    ants.update(map_data)
                    # call the do_turn method of the class passed in
                    bot.do_turn(ants)
                    ants.finish_turn()
                    map_data = ''
                else:
                    map_data += current_line + '\n'
            except EOFError:
                break
            except KeyboardInterrupt:
                raise
            except:
                # don't raise error or return so that bot attempts to stay alive
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()
