import pygame,math
import sgf.utils.Vector2d as Vector2d

def posToCoord(pos,gridsize):
	x,y = (int(pos[0]), int(pos[1]))
	grid_size_x,grid_size_y = gridsize
	coord_x = x / grid_size_x
	coord_y = y / grid_size_y
	
	return (coord_x,coord_y)
	
def coordToPos(coord,gridsize):
	coord_x,coord_y = coord
	grid_size_x,grid_size_y = gridsize
	pos_x = coord_x * grid_size_x
	pos_y = coord_y * grid_size_y
	
	return (pos_x,pos_y)
	
class Square(object):
	def __init__(self,coord):
		self.coord = coord
		self.blocked = False
		self.parent = None
	
	def reset(self):
		self.parent = None
		
class Grid(object):
	def __init__(self,width,height):
		self.width = width
		self.height = height
		
		self.rows = []
		for row in xrange(height):
			row_squares = []
			for col in xrange(width):
				row_squares.append(Square((col,row)))
			self.rows.append(row_squares)
	
	def get(self,coord):
		
		if not self.isValidCoord(coord):
			return None
		x,y = coord
		return self.rows[y][x]
		
	def set(self,coord,blocked):
		
		if self.isValidCoord(coord):
			x,y = coord
			self.rows[y][x].blocked = blocked
	
	def draw(self,Surface):
		
		for row in self.rows:
			for col in row:
				if col.blocked:
					pygame.draw.rect(Surface,(255,255,255),(col.coord[0]*16,col.coord[1]*16,16,16))
				#	pass
				
	def isValidCoord(self,coord):
		x,y = coord
		if x < 0 or y < 0 or x >= self.width or y >= self.height:
			return False
		return True
		
	def reset(self):
		
		for row in self.rows:
			for square in row:
				square.reset()
	
	def raycast(self,p0,p1,TILESIZE):
	
		# X and Y are cell/grid (not world) coords of the top left position of a tile
		X=(math.floor(p0[0]/TILESIZE))
		Y=(math.floor(p0[1]/TILESIZE))
	
		rayDir=Vector2d.Vector2.from_points(p0,p1)
		rayDir.normalize()

	
		x = (X*TILESIZE) + (TILESIZE/2)		# TILESIZE/2 is added here because metanet uses tile center as registration coord
		y = (Y*TILESIZE) + (TILESIZE/2)		# Somehow innacuracies are produced if starting point Y is not a multiple of TILESIZE
	
	
		if rayDir.x < 0:
			stepX = -1
			tMaxX = ((x -(TILESIZE/2)) - p0[0])/rayDir.x
			tDeltaX = TILESIZE / -rayDir.x
		
		elif 0 < rayDir.x:
			stepX = 1
			tMaxX = ((x +(TILESIZE/2)) - p0[0])/rayDir.x
			tDeltaX = TILESIZE / rayDir.x
		
		else:
			stepX = 0
			tMaxX = 100000000
			tDeltaX =0

		if rayDir.y < 0:
			stepY = -1
			tMaxY = ((y -(TILESIZE/2)) - p0[1])/rayDir.y
			tDeltaY = TILESIZE / -rayDir.y
		
		elif 0 < rayDir.y:
			stepY = 1
			tMaxY = ((y +(TILESIZE/2)) - p0[1])/rayDir.y
			tDeltaY = TILESIZE / rayDir.y
			
		else:
			stepY = 0
			tMaxY = 100000000
			tDeltaY = 0
		
		for i in range(200):				# the loop number of 13 is arbitrary
			if tMaxX < tMaxY:			# the loop breaks before we reach 13 anyway when we exceed the grid
				tMaxX+=tDeltaX			# or the ray hits an occupied cell
				X+=stepX
			
			else:
				tMaxY+=tDeltaY
				Y+=stepY
			
		
			if X>(self.width-1) or X<0 or Y>(self.height-1) or Y<0:
				return False

		
			if self.rows[int(Y)][int(X)].blocked:
				return (int(Y),int(X))
				
	def findPath(self,start_coord,dest_coord):
		
		self.reset()
		
		visited = set()
		open_squares = []
		
		open_squares.append(start_coord)
		
		steps = ( (0, +1), (+1, 0), (0, -1), (-1, 0),
				  (+1, -1), (+1, +1), (-1, +1), (-1, -1))
				  
		while open_squares:
			
			coord = open_squares.pop(0)
			
			if coord == dest_coord:
				path = []
				while coord != start_coord:
					path.append(coord)
					square = self.get(coord)
					parent_square = self.get(square.parent)
					coord = square.parent
				return path[::-1]
				
			for step in steps:
				
				new_coord = (coord[0]+step[0], coord[1]+step[1])
				
				if new_coord in visited:
					continue
					
				visited.add(new_coord)
				square = self.get(new_coord)
				
				if square is None or square.blocked:
					continue
					
				self.get(new_coord).parent = coord
				open_squares.append(new_coord)
				
		return None