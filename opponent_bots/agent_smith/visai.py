#!/usr/bin/env python
import sys
import math

VISAI_DEBUG_FILE_PATH = 'game_logs/visai_debug.txt'
green = ( 0, 255, 0 )
red = ( 255, 0, 0 )
black = ( 0, 0, 0 )
white = ( 255, 255, 255 )
default_alpha = 0.5

DEFAULT_MAX_SCENT_VALUE = 1000


class visAI():

	def __init__( self, debugging = False ):
		self.debugging = debugging
		self.colors = False
		self.update_max_scent_value( DEFAULT_MAX_SCENT_VALUE )
		self.avg_scent = ''

	def update_max_scent_value( self, max_scent_value ):
		self.max_scent_value = max_scent_value
		self.normalizing_factor = 1.0 / math.log( max_scent_value ) / 3
		
	def update_max_scent_value2( self, max_scent_value, avg_scent ):
		self.max_scent_value = max_scent_value
		self.avg_scent = avg_scent
		self.scent_range = max_scent_value - avg_scent
		self.debug( "scent: max: %s, avg: %s, range: %s\n" \
			% ( max_scent_value, avg_scent, self.scent_range ))
		self.normalizing_factor2 = 1.0 / math.log( self.scent_range, 2 ) / 2			
		
	def init_colors( self ):
		if self.colors:
			return
			
		self.set_fill_color( green, default_alpha )	
		self.colors = True
		
	def write( self, command ):
		sys.stdout.write( command )
		sys.stdout.flush()
		#self.debug( command )
		
	def debug( self, something, path = VISAI_DEBUG_FILE_PATH, mode = 'a', add_newline = False ):
			
		if not self.debugging:
			return False			
			
		f = open( path, mode )
		
		something.__str__()
		if add_newline:
			something += "\n"
		
		f.writelines( something )
		f.close()
		
	#######################################################

	def set_fill_color( self, color, alpha, return_value = False ):
		r, g, b = color
		command = "v sfc %s %s %s %s\n" % ( r, g, b, alpha )

		if return_value:
			return command
			
		self.write( command )
		
	def rect( self, row, col, width, height, fill = 'false' ):
		command = "v rect %s %s %s %s %s\n" % ( row, col, width, height, fill )
		self.write( command )
		
	def tile( self, row, col, return_value = False ):
		command = "v t %s %s\n" % ( row, col )
		
		if return_value:
			return command		
		
		self.write( command )	
		
	#######################################################	
		
	def	vis_ant_close_to_enemy( self, loc ):
		
		row, col = loc
		self.set_fill_color( red, default_alpha )
		self.tile( row, col )	
		
	def	vis_ant_in_sight_of_enemy( self, loc ):
		
		row, col = loc
		self.set_fill_color( red, 0.2 )
		self.tile( row, col )			

	def	vis_ant_charging( self, loc ):
		
		row, col = loc
		self.set_fill_color( black, 0.5 )
		self.tile( row, col )
		
	def vis_food( self, loc ):
	
		self.set_fill_color( green, default_alpha )	
	
		row, col = loc
		self.tile( row, col )
		
	def vis_strongest_scent( self, loc ):
		self.set_fill_color( white, default_alpha )	
	
		row, col = loc
		self.tile( row, col )		
		
		
	#######################################################
	
	def log_zones( self, zones, color, alpha ):
		self.set_fill_color( color, alpha )

		output_lines = []

		for row, col in zones:
			tile_line = self.tile( row, col, True )
			output_lines.append( tile_line )
				
		sys.stdout.writelines( output_lines )
		sys.stdout.flush()		
		
	def log_enemy_zones( self, zones ):
		self.log_zones( zones, red, 0.1 )
		
	def log_hill_zones( self, zones ):
		self.log_zones( zones, green, 0.1 )
		
		
	def log_seen_map( self, seen_map ):
		self.set_fill_color(( 0, 0, 0 ), 0.5 )	

		output_lines = []

		for row in range( len( seen_map )):
			for col in range( len( seen_map[row] )):		
				if not seen_map[row][col]:
					tile_line = self.tile( row, col, True )
					output_lines.append( tile_line )
				
		sys.stdout.writelines( output_lines )
		sys.stdout.flush()				
		
	def log_scent_map( self, scent_map, max_scent_value = '' ):

		if max_scent_value:
			self.update_max_scent_value( max_scent_value )

		output_lines = []
		values_locs = {}
		
		for row_i, row in enumerate( scent_map ):
			for col_i, value in enumerate( row ):
				value = self.get_normalized( value )
				if value in values_locs:
					values_locs[value].append(( row_i, col_i ))
				else:
					values_locs[value] = [( row_i, col_i )]
				
		for value in values_locs.iterkeys():
			color_line = self.set_fill_color(( 255, 255, 255 ), value, True )
			output_lines.append( color_line )
			
			for loc in values_locs[value]:
				row, col = loc
				tile_line = self.tile( row, col, True )
				output_lines.append( tile_line )
				
		sys.stdout.writelines( output_lines )
		sys.stdout.flush()
				
	def get_normalized( self, value ):
		if not value:
			return 0
		return math.log( value ) * self.normalizing_factor




		
	def log_scent_map2( self, scent_map, max_scent_value, scent_sum ):

		rows = len( scent_map )
		cols = len( scent_map[0] )
		fields = rows * cols
		avg_scent = scent_sum / fields
		self.update_max_scent_value2( max_scent_value, avg_scent )
		

		output_lines = []
		values_locs = {}
		
		for row_i, row in enumerate( scent_map ):
			for col_i, value in enumerate( row ):
			
				if value < avg_scent:
					continue
			
				value = self.get_normalized2( value )
				if value in values_locs:
					values_locs[value].append(( row_i, col_i ))
				else:
					values_locs[value] = [( row_i, col_i )]
					#self.debug( 'new value: %s\n' % ( value ))
				
		for value in values_locs.iterkeys():
			#self.debug( 'value: %s\n' % ( value ))
			color_line = self.set_fill_color(( 255, 255, 255 ), value, True )
			output_lines.append( color_line )
			
			for loc in values_locs[value]:
				row, col = loc
				tile_line = self.tile( row, col, True )
				output_lines.append( tile_line )
			
		#self.debug( output_lines )
		sys.stdout.writelines( output_lines )
		sys.stdout.flush()		
		
		
	def get_normalized2( self, value ):
		if not value:
			return 0
		
		return math.log( value - self.avg_scent, 2 ) * self.normalizing_factor
