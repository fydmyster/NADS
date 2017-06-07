import math
from sgf.const import*

def rotate(angle,vertices):
	"""Rotates the square object by given angle around origin(0,0)"""
	new_vertices = []	
	for point in vertices:
		x,y = point
		new_x = (x * math.cos(angle * DEG2RAD) - y * math.sin(angle * DEG2RAD))
		new_y = (x * math.sin(angle * DEG2RAD) + y * math.cos(angle * DEG2RAD))
			
		new_vertices.append((new_x,new_y))
		
	return new_vertices
	
def scale(x_factor,y_factor,vertices):
	"""Scales object by given factor"""
	new_vertices = []	
	for point in vertices:
		x,y = point
		new_x = (x * x_factor)
		new_y = (y * y_factor)
			
		new_vertices.append((new_x,new_y))
		
	return new_vertices
	
def translate(x_t,y_t,vertices):
	"""Scales object by given factor"""
	new_vertices = []	
	for point in vertices:
		x,y = point
		new_x = (x + x_t)
		new_y = (y + y_t)
			
		new_vertices.append((new_x,new_y))
		
	return new_vertices

def shear(a,b,vertices):
	"""Shears object by given factors"""
	new_vertices = []	
	for point in vertices:
		x,y = point
		new_x = (x + (a*y))
		new_y = (y + (b*x))
			
		new_vertices.append((new_x,new_y))
		
	return new_vertices

	