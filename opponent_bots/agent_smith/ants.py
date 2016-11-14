#!/usr/bin/env python
import sys
import traceback
import random
import time
from collections import defaultdict
from math import sqrt, log
import copy

import offsets

# scent sets for different situations
from scents import *
from scents_no_hill import *
from scents_few_ants import *

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
		  
####################		  
		  
DEBUG_FILE_PATH = 'game_logs/debug.txt'
BOT_INPUT_FILE_PATH = "game_logs/0.bot0.input"
THERAPIST_FILE_PATH = 'game_logs/0.bot0.log'

class Ants():

	def __init__(self, map_passes = 1):
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

		###################################################
		
		self.scents = Scents()
		
		self.map_passes = map_passes
		self.ants_close_to_enemy = []
		
		# offsets
		self.offsets_attack = offsets.calculate( 5 )
		self.offsets_r1 = offsets.calculate( 1 )
		self.offsets_r2 = offsets.calculate( 2 ** 2 )
		self.offsets_r3 = offsets.calculate( 3 ** 2 )
		self.offsets_influence = offsets.calculate( 10 )
		self.offsets_r4 = offsets.calculate( 4 ** 2 )
		self.offsets_r7 = offsets.calculate( 7 ** 2 )
		self.offsets_r10 = offsets.calculate( 10 ** 2 )
		
		# ring r3
		self.offsets_influence_ring = list( set( self.offsets_influence ).difference( set( self.offsets_attack )))
		
		self.previous_turn_enemy_ants = {}
		self.bot_running_time = 100
		
		self.all_hills = {}
	
	
	# only scent is actually used (not own_scent or enemy_scent)
	def reset_map( self, kind = 'enemy_scent' ):
		new_map = [[0.0 for col in range( self.cols )]
					for row in range( self.rows )]
					
		if kind == 'enemy_scent':
			self.enemy_scent_map = new_map
		elif kind == 'own_scent':
			self.own_scent_map = new_map
		elif kind == 'scent':
			self.scent_map = new_map


	def setup(self, data):
		'parse initial input and setup starting game state'
		
		self.debug( data, BOT_INPUT_FILE_PATH, "w", add_newline = False )
		
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
					
		self.calculate_vision_offsets2()
					
		# mapy zapachu
		self.reset_map( 'scent' )
		self.reset_map( 'own_scent' )		
		self.reset_map( 'enemy_scent' )
					
		self.seen_map = [[False for col in range(self.cols)]
					for row in range(self.rows)]
					
		self.hill_zones = []
		self.hill_zone_offsets = offsets.calculate( self.viewradius2 )
			
	def update(self, data):
		'parse engine input and update the game state'
		# start timer
		self.turn_start_time = time.time()
		
		self.debug( data, BOT_INPUT_FILE_PATH, 'a', add_newline = False )		
		
		# reset vision
		self.vision = None
		
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
				
				if len( tokens ) == 2:
					if tokens[0] == 'turn':
						self.turn = tokens[1]
				
				if len(tokens) >= 3:
					row = int(tokens[1])
					col = int(tokens[2])
					if tokens[0] == 'w':
						self.map[row][col] = WATER
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
							
		self.my_update()

	def my_update( self ):
	
		if len( self.my_ants()) < 10:
			self.scents = Scents_few_ants()
		else:
			self.scents = Scents()
	
		if not self.my_hills():
			self.scents = Scents_no_hill()
	
		
		self.update_all_hills()
		
		self.update_unmoved_enemy_ants()
		
		self.update_neis()
		self.update_food_neis()
		
		self.update_hill_zones()
		self.update_enemy_hill_zones()
		
		self.update_own_zones()		
		self.update_enemy_zones()	
		
		self.update_ants_close_to_enemy()		# in enemy zones (r4)
		#self.update_ants_in_sight_of_enemy()	# in enemy zones_bigger (r7)
		
	
		self.update_scent_map( self.map_passes )
		
		#self.update_stats()
		self.save_enemy_ants()
		
		
		
	def update_all_hills( self ):	
		self.all_hills.update( self.hill_list )
		new_all_hills = {}

		for hill in self.all_hills:
			if self.visible( hill ) and hill not in self.hill_list:
				continue
			new_all_hills[hill] = self.all_hills[hill]
			
		self.all_hills = new_all_hills		
		
		
	# dict { ant : owner } unmoved ants
	def update_unmoved_enemy_ants( self ):
		self.unmoved_enemy_ants = {}
		for ant, owner in self.enemy_ants():
			if ( ant, owner ) in self.previous_turn_enemy_ants:
				self.unmoved_enemy_ants[ant] = owner
				
		if self.unmoved_enemy_ants:
			self.debug( 'unmoved enemy ants:' )
			self.debug( self.unmoved_enemy_ants )
		
	def save_enemy_ants( self ):
		self.previous_turn_enemy_ants = self.enemy_ants()
		
	# stats are unused
	def update_stats( self ):
		self.update_visibility_stats()
		self.update_density_stats()
		self.debug( "visibility: %d percent, density: %f" % ( self.visibility * 100, self.density ))
		
	def update_visibility_stats( self ):
		self.visibility = 1.0 * self.visible_count / ( self.rows * self.cols )
		
	def update_density_stats( self ):
		try:
			self.density = 1.0 * len( self.my_ants()) / self.visible_count
		except ZeroDivisionError:
			self.density = 0
						
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

	def enemy_hills(self):
		return [(loc, owner) for loc, owner in self.hill_list.items()
					if owner != MY_ANT]
					
	def enemy_hill_locations(self):
		return [loc for loc, owner in self.all_hills.items()
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
			
		random.shuffle( d )
		return d

	def seen( self, loc ):
		row, col = loc
		return self.seen_map[row][col]

	def visible(self, loc):
		' determine which squares are visible to the given player '
		self.init_vision()

		row, col = loc
		return self.vision[row][col]
		
	def calculate_vision_offsets2( self ):
	
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
	
	def init_vision( self ):
		if self.vision == None:

			# set all spaces as not visible
			# loop through ants and set all squares around ant as visible
			self.vision = [[False]*self.cols for row in range(self.rows)]
			for ant in self.my_ants():
				a_row, a_col = ant
				for v_row, v_col in self.vision_offsets_2:
					self.vision[a_row + v_row][a_col + v_col] = True
					self.mark_seen( a_row + v_row, a_col + v_col )
		
		
	
	def render_text_map(self):
		'return a pretty string representing the map'
		tmp = ''
		for row in self.map:
			tmp += '# %s\n' % ''.join([MAP_RENDER[col] for col in row])
		return tmp

	# static methods are not tied to a class and don't have self passed in
	# this is a python decorator
	@staticmethod
	def run( bot, passes = 1, debugging = True ):
		'parse input, update game state and call the bot classes do_turn method'

		ants = Ants( passes )

		ants.bot = bot
		ants.set_debugging( debugging )

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

###########################################################

	def in_sight( self, loc1, loc2, max_rec = sys.getrecursionlimit() - 100 ):
		if self.distance( loc1, loc2 ) == 1:
			return True
			
		if max_rec <= 0:
			return False
			
		directions = self.direction( loc1, loc2 )
		for direction in directions:
			new_loc = self.destination( loc1, direction )
			if ( self.passable( new_loc )):
				return self.in_sight( new_loc, loc2, max_rec - 1 )

		return False
		
	def get_random_direction( self ):
		directions = ['n', 's', 'e', 'w']
		random.shuffle( directions )
		return directions[0]
		

		
		
	### logging and debugging #######################################
	
	def set_debugging( self, debugging ):
		self.debugging = debugging
		
	def debug( self, something, path = DEBUG_FILE_PATH, mode = 'a', add_newline = True ):
			
		if not self.debugging:
			return False			
			
		f = open( path, mode )
		
		something = something.__str__()
		if add_newline:
			something += "\n"
		
		f.writelines( something )
		f.close()		
		
		
	
	
	###
		
	def get_neighbours( self, loc ):
		row, col = loc
		neighbours = []
		for offsets in AIM.values():
			d_row, d_col = offsets
			new_row = ( row + d_row ) % self.rows
			new_col = ( col + d_col ) % self.cols
			neighbours.append(( new_row, new_col ))
			
		#self.debug( neighbours )
		return neighbours
		
	def update_neis( self ):
		self.neis = []
		
		for ant_loc in self.my_ants():
			nei_locs = self.get_neighbours( ant_loc )
			self.neis.extend( nei_locs )
				
	def update_food_neis( self ):
		self.food_neis = []
		
		for food_loc in self.food_list:
			food_neis = self.get_neighbours( food_loc )
			self.food_neis.extend( food_neis )	
			
		if self.bot.visai:
			for loc in self.food_neis:
				self.bot.visai.vis_food( loc )
				
	def update_ants_close_to_enemy( self ):
		self.ants_close_to_enemy = []
		for loc in self.my_ants():
			if loc in self.enemy_zones:
				self.ants_close_to_enemy.append( loc )
				
	def update_ants_in_sight_of_enemy( self ):
		self.ants_in_sight_of_enemy = []
		for loc in self.my_ants():
			if loc in self.enemy_zones_bigger:
				self.ants_in_sight_of_enemy.append( loc )	
				

	# dict { loc -> how many ants }
	def update_own_attack_areas( self ):
		self.own_attack_areas = {}
		for row, col in self.my_ants():
			for d_row, d_col in self.offsets_attack:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols
				new_loc = ( new_row, new_col )
				if new_loc not in self.own_attack_areas:
					self.own_attack_areas[new_loc] = 1
				else:
					self.own_attack_areas[new_loc] += 1
		
	def update_enemy_attack_areas( self ):
		self.enemy_attack_areas = {}
		for row, col in [loc for loc, owner in self.enemy_ants()]:
			for d_row, d_col in self.offsets_attack:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols
				new_loc = ( new_row, new_col )
				if new_loc not in self.enemy_attack_areas:
					self.enemy_attack_areas[new_loc] = 1
				else:
					self.enemy_attack_areas[new_loc] += 1					
		
		
	def update_hill_zones( self ):
			
		self.hill_zones = []
		for loc in self.my_hills():
			row, col = loc
			for d_row, d_col in self.hill_zone_offsets:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols			
				self.hill_zones.append(( new_row, new_col ))
				
		self.hill_zones_bigger = []
		for loc in self.my_hills():
			row, col = loc
			for d_row, d_col in self.offsets_r10:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols			
				self.hill_zones_bigger.append(( new_row, new_col ))				
		
	def update_enemy_hill_zones( self ):
			
		self.enemy_hill_zones = []
		self.enemy_hill_zones_r2 = []
		self.enemy_hill_zones_r1 = []
		
		for loc in self.enemy_hill_locations():
			row, col = loc
			for d_row, d_col in self.offsets_r10:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols			
				self.enemy_hill_zones.append(( new_row, new_col ))

			for d_row, d_col in self.offsets_attack:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols			
				self.enemy_hill_zones_r2.append(( new_row, new_col ))
				
			for d_row, d_col in self.offsets_r1:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols			
				self.enemy_hill_zones_r1.append(( new_row, new_col ))				
				
	
	def update_own_zone( self, loc, new_loc ):	
		self.clear_own_zone( loc )
		self.create_own_zone( new_loc )
	
	def clear_own_zone( self, loc ):
		row, col = loc
		for d_row, d_col in self.offsets_influence:
			new_row = ( row + d_row ) % self.rows
			new_col = ( col + d_col ) % self.cols
			new_loc = ( new_row, new_col )
			self.own_zones[new_loc] -= 1		
	
	def create_own_zone( self, loc ):	
		row, col = loc
		for d_row, d_col in self.offsets_attack:
			new_row = ( row + d_row ) % self.rows
			new_col = ( col + d_col ) % self.cols
			new_loc = ( new_row, new_col )
			self.own_zones[new_loc] += 1		
		
	def update_own_zones( self ):
		
		self.own_zones = {}
		
		for row, col in self.my_ants():
			for d_row, d_col in self.offsets_influence:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols
				new_loc = ( new_row, new_col )
				if new_loc not in self.own_zones:
					self.own_zones[new_loc] = 1
				else:
					self.own_zones[new_loc] += 1	

		
	def update_enemy_zones( self ):
		
		self.enemy_zones_attack = {}
		self.enemy_zones = {}
		self.enemy_zones_bigger = {}
		self.enemy_zones_influence = {}
		
		
		enemy_ants = [loc for loc, owner in self.enemy_ants()]	
		for row, col in enemy_ants:
		
			# attack
			for d_row, d_col in self.offsets_attack:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols
				new_loc = ( new_row, new_col )
				if new_loc not in self.enemy_zones_attack:
					self.enemy_zones_attack[new_loc] = 1
				else:
					self.enemy_zones_attack[new_loc] += 1	
					
			# influence (r3)
			if ( row, col ) in self.unmoved_enemy_ants:
				influence_offsets = self.offsets_attack
			else:
				influence_offsets = self.offsets_influence
				
			for d_row, d_col in influence_offsets:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols
				new_loc = ( new_row, new_col )
				if new_loc not in self.enemy_zones_influence:
					self.enemy_zones_influence[new_loc] = 1
				else:
					self.enemy_zones_influence[new_loc] += 1						
		
			# r4
			for d_row, d_col in self.offsets_r4:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols
				new_loc = ( new_row, new_col )
				if new_loc not in self.enemy_zones:
					self.enemy_zones[new_loc] = 1
				else:
					self.enemy_zones[new_loc] += 1	
					
			# r7
			for d_row, d_col in self.offsets_r7:
				new_row = ( row + d_row ) % self.rows
				new_col = ( col + d_col ) % self.cols
				new_loc = ( new_row, new_col )
				if new_loc not in self.enemy_zones_bigger:
					self.enemy_zones_bigger[new_loc] = 1
				else:
					self.enemy_zones_bigger[new_loc] += 1	
				
				
		

		
		
	################## scent	
		
	def update_scent_map( self, passes = 1, write_log = False ):
		self.init_vision()
		self.scent_log = ''
		
		my_ants = self.my_ants()	# no owner here
		enemy_ants = [loc for loc, owner in self.enemy_ants()]
		enemy_hill_locations = self.enemy_hill_locations()
		food_locations = self.food()
		
		scent_sum = 0
		scent_max = 0
		
		self.visible_count = 0
		pass_time = 0
		
		for i in range( passes ):
		
			if self.time_remaining() < ( self.bot_running_time * 1.1 + pass_time ):
				return
		
			start_pass_time = self.time_remaining()
		
			for row_i, row in enumerate( self.vision ):
				for col_i, col in enumerate( row ):

					if i == 0 and self.vision[row_i][col_i]:
						self.visible_count += 1

					if self.time_remaining() < 250:
						return

					loc = ( row_i, col_i )
					scent_value = 0

					if not self.passable( loc ):
						scent_value = 0		
						
					elif loc in food_locations:
						scent_value = max( self.scents.FOOD_SCENT_VALUE, self.scent_map[row_i][col_i] )
						
					elif not self.seen_map[row_i][col_i]:
						scent_value = max( self.scents.UNSEEN_SCENT_VALUE, self.scent_map[row_i][col_i]	)

					elif not self.vision[row_i][col_i]:
						scent_value = max( self.scents.INVISIBLE_SCENT_VALUE, self.scent_map[row_i][col_i] )
						
					elif loc in enemy_hill_locations:
						scent_value = self.scents.ENEMY_HILL_SCENT_VALUE
						
					elif loc in self.enemy_hill_zones_r1:
						scent_value = max( self.scents.ENEMY_HILL_R1_SCENT_VALUE, self.scent_map[row_i][col_i] )	
						
					# this gives buggy behaviour
					elif loc in self.enemy_hill_zones_r2:
						scent_value = max( self.scents.ENEMY_HILL_R2_SCENT_VALUE, self.scent_map[row_i][col_i] )
						
					
					elif loc in enemy_ants and loc in self.hill_zones_bigger and loc not in self.hill_zones:
						scent_value = self.scents.ENEMY_NEAR_OWN_HILL_SCENT_VALUE	
						
					elif loc in enemy_ants and loc in self.hill_zones:
						scent_value = self.scents.ENEMY_AT_OWN_HILL_SCENT_VALUE							
					
					elif loc in enemy_ants:
						scent_value = self.scents.ENEMY_SCENT_VALUE
						
					else:
						scent_value = self.calculate_scent( loc )
						
					
					if scent_value > 0 and loc in my_ants:
						
						if loc in self.enemy_zones or loc in self.enemy_hill_zones:
							scent_value *= 0.99
						else:
							scent_value = 0		
					
					self.set_scent( loc, scent_value )
					


					if write_log:
						self.log_scent( scent_value, row_i, col_i )
						
			pass_time = start_pass_time - self.time_remaining()
		
		if write_log:
			self.write_scent_log()
			
					
	def calculate_scent( self, loc, kind = '' ):
		directions = ['s', 'w', 'n', 'e']
		suma = 0.0
		for direction in directions:
			destination = self.destination( loc, direction )
			suma += self.get_scent( destination, kind )
		return suma / 4					
					
	def set_scent( self, loc, val, kind = '' ):
		row, col = loc
		if kind == 'own':
			self.own_scent_map[row][col] = val
		elif kind == 'enemy':
			self.enemy_scent_map[row][col] = val
		else:
			self.scent_map[row][col] = val
		
	def get_scent( self, loc, kind = '' ):
		row, col = loc
		
		if kind == 'own':
			return self.own_scent_map[row][col]
		elif kind == 'enemy':
			return self.enemy_scent_map[row][col]
		else:
			return self.scent_map[row][col]		
		
	def get_enemy_scent( self, loc ):
		row, col = loc
		return self.enemy_scent_map[row][col]		
		
	def get_scents( self, loc ):
		scents = []
		for n in self.get_neighbours( loc ):
			scent = self.get_scent( n )
			if scent > 0:
				scents.append(( n, scent ))
				
		if scents:
			# order by scent DESC
			#self.debug( scents )
			scents = sorted( scents, key = lambda x: x[1], reverse = True )
			#self.debug( scents )
			return scents
	
		
			
	def mark_seen( self, row, col ):
		'oznacza lokacje jako odkryta'
		self.seen_map[row][col] = True		
		
		
		
	def get_enemy_ants_controlling( self, loc ):
		
		enemy_ants = []		
		zone = []
		row, col = loc
		
		for d_row, d_col in self.offsets_attack:
			new_row = ( row + d_row ) % self.rows
			new_col = ( col + d_col ) % self.cols
			new_loc = ( new_row, new_col )
			zone.append( new_loc )
			
		all_enemy_ants = [loc for loc, owner in self.enemy_ants()]	
		for ant_loc in all_enemy_ants:
			if ant_loc in zone:
				enemy_ants.append( ant_loc )
				
		return enemy_ants
		
	def get_enemy_ants_possibly_controlling( self, loc ):
	
		enemy_ants = []		# in zone
		zone = []
		row, col = loc
		
		for d_row, d_col in self.offsets_influence_ring:
			new_row = ( row + d_row ) % self.rows
			new_col = ( col + d_col ) % self.cols
			new_loc = ( new_row, new_col )
			zone.append( new_loc )
			
		all_enemy_ants = [loc for loc, owner in self.enemy_ants()]	
		for ant_loc in all_enemy_ants:
			if ant_loc in zone:
				enemy_ants.append( ant_loc )
				
		return enemy_ants	
		
		
	def get_min_enemy_weakness( self, enemy_ants ):
		weaknesses = []
		for loc in enemy_ants:
			try:
				weaknesses.append( self.own_zones[loc] )	
			except KeyError:
				continue
			
		try:
			return min( weaknesses )
		except ValueError:
			return 0
				

	def get_possible_min_enemy_weakness( self, loc, enemy_ants ):
		weaknesses = []
		for ant in enemy_ants:
			directions = self.direction( ant, loc )
			new_loc = self.destination( ant, directions[0] )
			try:
				weaknesses.append( self.own_zones[new_loc] )	
			except KeyError:
				continue	
				
		try:
			return min( weaknesses )
		except ValueError:
			return 0				


	def bot_start( self ):
		self.bot_start_time = self.time_remaining()
		
	def bot_finish( self ):
		self.bot_finish_time = self.time_remaining()
		
		self.bot_running_time = self.bot_start_time - self.bot_finish_time

