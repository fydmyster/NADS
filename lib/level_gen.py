import pygame,random
import tiles
import generic
import enemy
from cnst import*


class LevelGenerator(object):
	def __init__(self,w,h):
		self.w = w
		self.h = h
		self.startpos = (10,10)
		self.start_color = (0,0,0)
		self.rects_list = []
	
	def drawRandShape(self,pixelarray):
		
		for i in range(len(self.rects_list)):
			
			rect_to_draw_in = self.rects_list[i]
			
			# pick a random config and draw it into room
			r_int = random.randint(0,4)
			
			if r_int == 0:
				# draw vertical tiles
				sx = random.randrange(rect_to_draw_in.left+2,rect_to_draw_in.right-2)
				sy = random.randrange(rect_to_draw_in.top+2,rect_to_draw_in.bottom-2)
				
				try:
					pixelarray[sx][sy] = FIRECRATE
					pixelarray[sx][sy+1] = FIRECRATE
					pixelarray[sx][sy+2] = FIRECRATE
					#pixelarray[sx][sy+3] = (255,0,0)
				except IndexError:
					pass
			
			elif r_int == 1:
				# draw vertical tiles
				sx = random.randrange(rect_to_draw_in.left+2,rect_to_draw_in.right-2)
				sy = random.randrange(rect_to_draw_in.top+2,rect_to_draw_in.bottom-2)
				
				try:
					pixelarray[sx][sy] = FIRECRATE
					pixelarray[sx+1][sy] = FIRECRATE
					pixelarray[sx+2][sy] = FIRECRATE
					#pixelarray[sx+3][sy] = (255,0,0)
				except IndexError:
					#print "Out of range buddy ouch"
					pass
					
			elif r_int == 2:
				# draw t tiles
				sx = random.randrange(rect_to_draw_in.left+2,rect_to_draw_in.right-2)
				sy = random.randrange(rect_to_draw_in.top+2,rect_to_draw_in.bottom-2)
		
				try:
					pixelarray[sx][sy] = FIRECRATE
					pixelarray[sx+1][sy] = FIRECRATE
					pixelarray[sx+2][sy] = FIRECRATE
				#pixelarray[sx+3][sy] = (255,0,0)
					pixelarray[sx+1][sy+1] = FIRECRATE
					pixelarray[sx+1][sy+2] = FIRECRATE
				except IndexError:
					#print "Out of range buddy ouch"
					pass
					
			elif r_int == 3:
				# draw l tiles
				sx = random.randrange(rect_to_draw_in.left+2,rect_to_draw_in.right-2)
				sy = random.randrange(rect_to_draw_in.top+2,rect_to_draw_in.bottom-2)
				
				try:
					pixelarray[sx+1][sy] = FIRECRATE
					pixelarray[sx+1][sy+1] = FIRECRATE
					pixelarray[sx+1][sy+2] = FIRECRATE
					pixelarray[sx][sy+2] = FIRECRATE
				except IndexError:
					#print "Out of range buddy ouch"
					pass
				
			elif r_int == 4:
				# draw dash tiles
				sx = random.randrange(rect_to_draw_in.left+2,rect_to_draw_in.right-2)
				sy = random.randrange(rect_to_draw_in.top+2,rect_to_draw_in.bottom-2)
				
				try:
					pixelarray[sx][sy] = FIRECRATE
					pixelarray[sx+1][sy+1] = FIRECRATE
					pixelarray[sx+1][sy+2] = FIRECRATE
					pixelarray[sx+2][sy+2] = FIRECRATE
				except IndexError:
					#print "Out of range buddy ouch"
					pass
					
	def generateLevel(self):
	
		w,h = (self.w,self.h)
		
		# create dummy surface we do operations on
		dummy_surf = pygame.Surface((w,h))
		dummy_surf.fill((0,255,0))
	
		fill_surf = pygame.Surface((w,h))
		fill_surf.fill((0,255,0))
	
		temp_dsurf = pygame.Surface((w,h))
		temp_dsurf.fill((0,255,0))
	
		# each floor will contain 6 adjoined rooms
		max_room_size = 10
		min_room_size = 8
	
		placement_points_x = (1,(w/3),(w/3)*2)
		placement_points_y = (1,(h/2))
	
		rects_list = self.rects_list
	
		for row in range(2):
			for col in range(3):
				width = random.randrange(min_room_size,max_room_size)
				height = random.randrange(min_room_size,max_room_size)
				xpoint = random.randrange(placement_points_x[col]-1,placement_points_x[col]+1)
				ypoint = random.randrange(placement_points_y[row]-1,placement_points_y[row]+1)
			
				new_rect = pygame.Rect(xpoint,ypoint,width,height)
				rects_list.append(new_rect)
				pygame.draw.rect(dummy_surf,(255,0,0),(xpoint,ypoint,width,height),1)
				pygame.draw.rect(fill_surf,(255,0,0),(xpoint+1,ypoint+1,width-2,height-2))
	
		# top adjoinment
		top_join_rect_w = (rects_list[2].right - rects_list[0].left)-2
	
		r1 = set(range(rects_list[0].top,rects_list[0].bottom))	
		r2 = set(range(rects_list[1].top,rects_list[1].bottom))
		r3 = set(range(rects_list[2].top,rects_list[2].bottom))
	
		tem_r = r1.intersection(r2)
		delt_r = tem_r.intersection(r3)
	
		temp_list = list(delt_r)
	
		av = 0
		for i in temp_list:
			av += i
		
		average = av/float(len(temp_list))
		top_rect = pygame.Rect(rects_list[0].left+1,average,top_join_rect_w,3)
		#rects_list.append(top_rect)
		pygame.draw.rect(dummy_surf,(255,0,0),(rects_list[0].left+1,average,top_join_rect_w,3),1)
		pygame.draw.rect(temp_dsurf,(255,0,0),(rects_list[0].left+1,average,top_join_rect_w,3))
		#pygame.draw.rect(fill_surf,(255,0,0),(rects_list[0].left+2,average+1,top_join_rect_w-2,1))
	
	
		# bottom adjoinment
		bottom_join_rect_w = (rects_list[5].right - rects_list[3].left)-2
	
		r1 = set(range(rects_list[3].top,rects_list[3].bottom))	
		r2 = set(range(rects_list[4].top,rects_list[4].bottom))
		r3 = set(range(rects_list[5].top,rects_list[5].bottom))
	
		tem_r = r1.intersection(r2)
		delt_r = tem_r.intersection(r3)
	
		temp_list = list(delt_r)
	
		av = 0
		for i in temp_list:
			av += i
		
		average = av/float(len(temp_list))
		bottom_rect = pygame.Rect(rects_list[3].left+1,average,bottom_join_rect_w,3)
		#rects_list.append(bottom_rect)
		pygame.draw.rect(dummy_surf,(255,0,0),(rects_list[3].left+1,average,bottom_join_rect_w,3),1)
		pygame.draw.rect(temp_dsurf,(255,0,0),(rects_list[3].left+1,average,bottom_join_rect_w,3))

		# create pixel array
		pxarray = pygame.PixelArray(dummy_surf)
		dpxarray = pygame.PixelArray(temp_dsurf)
		fpxarray = pygame.PixelArray(fill_surf)
	
		# center to top adjoinment
		mid_join_rect_h = (rects_list[4].bottom - rects_list[1].top)-2
	
		r1 = set(range(rects_list[1].left,rects_list[1].right))	
		r2 = set(range(rects_list[4].left,rects_list[4].right))
	
		delt_r = r1.intersection(r2)
	
		temp_list = list(delt_r)
	
		av = 0
		for i in temp_list:
			av += i
		
		average = av/float(len(temp_list))
		mid_rect = pygame.Rect(average,rects_list[1].top+1,3,mid_join_rect_h)
		#rects_list.append(bottom_rect)
		pygame.draw.rect(dummy_surf,(255,0,0),(average,rects_list[1].top+1,3,mid_join_rect_h),1)
		pygame.draw.rect(temp_dsurf,(255,0,0),(average,rects_list[1].top+1,3,mid_join_rect_h))

		# create pixel array
		pxarray = pygame.PixelArray(dummy_surf)
		dpxarray = pygame.PixelArray(temp_dsurf)
		fpxarray = pygame.PixelArray(fill_surf)
	
	
		# test rooms
		for row in range(h):
			for col in range(w):
			
				num_collisions = 0
				for rect in rects_list:
					if fpxarray[col][row] == dummy_surf.map_rgb((255,0,0)):
						test_rect = pygame.Rect(rect.x,rect.y,rect.w,rect.h)
						if test_rect.collidepoint(col,row):
							num_collisions += 1
			
				if num_collisions == 2:
					pxarray[col][row] = (0,255,0)
			
				elif num_collisions > 3:
					pxarray[col][row] = (0,0,0)
				
				else:
					pass
	
		# test adjoinments
		for row in range(h):
			for col in range(w):
			
				num_collisions = 0
				for rect in rects_list:
					if dpxarray[col][row] == dummy_surf.map_rgb((255,0,0)):
						test_rect = pygame.Rect(rect.x,rect.y,rect.w,rect.h)
						if test_rect.collidepoint(col,row):
							pxarray[col][row] = (0,255,0)
	

		new_surf = pxarray.make_surface()
		# draw border to quell anomalies and to sanity check the level and prevent invalid configurations
		pygame.draw.rect(new_surf,(255,0,0),(0,0,w,h),1)
	
		level_pxarray = pygame.PixelArray(new_surf)
		
		# flood fill
		xpos = random.randrange(3,rects_list[0].right-1)
		ypos = random.randrange(3,rects_list[0].bottom-1)
		self.startpos = (xpos,ypos)
		
		self.start_color = new_surf.unmap_rgb(level_pxarray[self.startpos[0]][self.startpos[1]])
		self.floodFill(self.startpos,(0,0,0),w,h,new_surf,level_pxarray)
		
		# add decorator elements
		self.drawRandShape(level_pxarray)
		
		# place entities
		
		# get free positions and store them
		free_positions = []
		for row in range(h):
			for col in range(w):
				
				if level_pxarray[col][row] == new_surf.map_rgb(GROUND):
					free_positions.append((col,row))
		
		T_ENTITIES = ENTITIES[:]
		T_ENTITIES.remove(FIRECRATE)
		
		#t_enemy = free_positions.pop()
		#level_pxarray[t_enemy[0]][t_enemy[1]] = DASHER
		
		for i in range(4):
			r_int = random.randint(0,len(free_positions)-1)
			entity_pos = free_positions.pop(r_int)
			entity = random.choice(T_ENTITIES)
			level_pxarray[entity_pos[0]][entity_pos[1]] = entity
		
		# place door
		r_int = random.randint(0,len(free_positions)-1)
		door_pos = free_positions.pop(r_int)
		level_pxarray[door_pos[0]][door_pos[1]] = DOOR
		
		#level_pxarray[xpos][ypos] = (0,0,255)
	
		new_surf = level_pxarray.make_surface()
		#pygame.image.save(new_surf,"test_image.png")
			
		return (w,h,new_surf,level_pxarray)

	
	def floodFill(self,pos,color,w,h,surf,array): #worst algorithm
		
		c = surf.unmap_rgb(array[pos[0]][pos[1]])
		if c == color: 
			return
		if array[pos[0]][pos[1]] == surf.map_rgb(self.start_color):
			array[pos[0]][pos[1]] = color
			x,y = pos
			if x > 0: self.floodFill((x-1,y),color,w,h,surf,array)
			if x < w-1: self.floodFill((x+1,y),color,w,h,surf,array)
			if y > 0: self.floodFill((x,y-1),color,w,h,surf,array)
			if y < h-1: self.floodFill((x,y+1),color,w,h,surf,array)
    
def createLevelFrom(w,h,surf,array,enemy_list,tile_list,item_list,draw_list,fx,pcs,images,grid,tilesize=16):	
	
	mapped_entity_colors = []
	for color in ENTITIES:
		mapped_color = surf.map_rgb(color)
		mapped_entity_colors.append(mapped_color)
		
	for row in range(h):
		for col in range(w):
			
			# create tiles 
			if array[col][row] == surf.map_rgb((255,0,0)):
				
				tile = tiles.WallTile(col*tilesize,row*tilesize,tilesize)
				tile_list.append(tile)
			
			if array[col][row] == surf.map_rgb((0,0,0)) or array[col][row] in mapped_entity_colors:
				
				tile = tiles.GroundTile(col*tilesize,row*tilesize,tilesize)
				draw_list.append(tile)
			
			if array[col][row] == surf.map_rgb(DOOR):
				door = tiles.DoorTile(col*tilesize,row*tilesize,tilesize)
				item_list.append(door)
			
			# create items and enemies
			if array[col][row] == surf.map_rgb(FIRECRATE):
				crate = generic.FireCrate(col*tilesize,row*tilesize,tilesize,tilesize)
				item_list.append(crate)
			
			if array[col][row] == surf.map_rgb(BONEMAN):
				advesary = enemy.Boneman(col*tilesize,row*tilesize,tilesize,tilesize,
										grid,tile_list,item_list,pcs,fx,images)
				enemy_list.append(advesary)
			
			if array[col][row] == surf.map_rgb(SPROUT):
				advesary = enemy.Sprout(col*tilesize,row*tilesize,tilesize,tilesize,
										grid,tile_list,item_list,pcs,fx,images)
				enemy_list.append(advesary)
			
			if array[col][row] == surf.map_rgb(FLOORMAN):
				advesary = enemy.Floorman(col*tilesize,row*tilesize,tilesize,tilesize,
										grid,tile_list,item_list,pcs,fx,images)
				enemy_list.append(advesary)
			
			if array[col][row] == surf.map_rgb(MAGUS):
				advesary = enemy.Magus(col*tilesize,row*tilesize,tilesize,tilesize,
										grid,tile_list,item_list,pcs,fx,images)
				enemy_list.append(advesary)
			
			if array[col][row] == surf.map_rgb(REDMAGUS):
				advesary = enemy.RedMagus(col*tilesize,row*tilesize,tilesize,tilesize,
										grid,tile_list,item_list,pcs,fx,images)
				enemy_list.append(advesary)
			
			if array[col][row] == surf.map_rgb(BENTMAGUS):
				advesary = enemy.BentMagus(col*tilesize,row*tilesize,tilesize,tilesize,
										grid,tile_list,item_list,pcs,fx,images)
				enemy_list.append(advesary)
			
			if array[col][row] == surf.map_rgb(ICEWITCH):
				advesary = enemy.IceWitch(col*tilesize,row*tilesize,tilesize,tilesize,
										grid,tile_list,item_list,pcs,fx,images)
				enemy_list.append(advesary)
			
			if array[col][row] == surf.map_rgb(DASHER):
				advesary = enemy.Dasher(col*tilesize,row*tilesize,tilesize,tilesize,
										grid,tile_list,item_list,pcs,fx,images)
				enemy_list.append(advesary)
			
			if array[col][row] == surf.map_rgb(BUZZER):
				advesary = enemy.Buzzer(col*tilesize,row*tilesize,tilesize,tilesize,
										grid,tile_list,item_list,pcs,fx,images)
				enemy_list.append(advesary)
			
			if array[col][row] == surf.map_rgb(GHOST):
				advesary = enemy.Ghost(col*tilesize,row*tilesize,tilesize,tilesize,
										grid,tile_list,item_list,pcs,fx,images)
				enemy_list.append(advesary)
			
generator = LevelGenerator(40,30)				
generator.generateLevel()
	
	