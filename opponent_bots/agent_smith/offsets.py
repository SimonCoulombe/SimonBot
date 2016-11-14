import math

def calculate( radius2 ):
	
	offsets = []
	mx = int( math.sqrt( radius2 ))
	for d_row in range( -mx, mx + 1 ):
		for d_col in range( -mx, mx + 1 ):
			d2 = d_row ** 2 + d_col ** 2
			#print d_row, d_col
			if d2 <= radius2:
				offsets.append((
					# Create all negative offsets so vision will
					# wrap around the edges properly
					#( d_row % map_rows ) - map_rows,
					#( d_col % map_cols ) - map_cols
					d_row, d_col
				))		
	return offsets
	

def calculate_d( radius2 ):
	'j.w., tyle ze dict (offset) => distance'
	
	offsets = {}
	mx = int( math.sqrt( radius2 ))
	for d_row in range( -mx, mx + 1 ):
		for d_col in range( -mx, mx + 1 ):
			d2 = d_row ** 2 + d_col ** 2
			#print d_row, d_col
			if d2 <= radius2:
				offsets[( d_row, d_col )] = round( math.sqrt( d2 ))
	return offsets	
	
def calculate_gradient( radius2 ):
	offsets = {}
	mx = int( math.ceil( math.sqrt( radius2 )))
	for i in range( mx, -1, -1 ):
		tmp_offsets = calculate( i ** 2 )
		for r,c in tmp_offsets:
			if r ** 2 + c ** 2 <= radius2:
				offsets[(r,c)] = i
	return offsets
		
				
