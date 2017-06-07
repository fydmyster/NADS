import math,random
from OpenGL.GL import*

import sgf.gl.resource as res
import sgf.utils.g_utils as utils

class Sector(object):
	def __init__(self,x,y,w,h,max_rows,max_cols):
		"""Represents a quad"""
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.hx = self.w/2
		self.hy = self.h/2
		
		self.center = (self.x+self.hx, self.y+self.hy) 
		
		self.start_x = self.x
		self.start_y = self.y
		
		max_w = w * max_cols
		max_h = h * max_rows
		
		
		self.topleft = (self.x, self.y)
		self.topright = (self.x+self.w, self.y)
		self.bottomright = (self.x+self.w, self.y+self.h)
		self.bottomleft = (self.x, self.y+self.h)
		
		self.points = [self.topleft,self.topright,self.bottomright,self.bottomleft]
		self.spoints = [self.topleft,self.topright,self.bottomright,self.bottomleft]
		
		
		x = self.x/float(self.w) 
		y = self.y/float(self.h)
		
		self.tlx = (x) /float(max_cols)
		self.tly = 1 - (y/float(max_rows))
		
		self.trx = (x + 1) /float(max_cols)
		self.trry = 1 - (y/float(max_rows))
		
		self.brx = (x + 1) /float(max_cols)
		self.bry = 1 - (y + 1/float(max_rows))
		
		self.blx = self.tlx
		self.bly = self.bry
		
	def __str__(self):
		return "x is %s y is %s" % (self.x,self.y)
	
	def update(self):
		pass

class VertexGrid(object,):
	def __init__(self,rows=20,cols=10,width=50,height=50,image_path=None,image_w=None,image_h=None,colorkey=None):
		
		
		self.image_path = image_path
		
		if self.image_path is not None:
			self.texture = res.getTexture(self.image_path,image_w,image_h,colorkey)
		
		else:
			self.texture = None
			
		self.grid = []
		self.change = 0.0
		self.factor = 0.0
		self.rows = rows
		self.cols = cols
		self.width = width
		self.height = height
		
		self.h_col = self.cols/2
		self.h_row = self.rows/2
		
		for row in range(self.rows):
			row_list =[]
			self.grid.append(row_list)
			for col in range(self.cols):
				# create sector
				new_sector = Sector(col*self.width,row*self.height,self.width,self.height,self.rows,self.cols)
				row_list.append(new_sector)
		
		self.tx = 1.0/cols
		self.ty = 1.0/rows
		
		
	def drawQuadImage(self):
		
		glBindTexture(GL_TEXTURE_2D,self.texture.tex_id)
		#glDisable(GL_TEXTURE_2D)
		glBegin(GL_QUADS)
		glColor4f(1.0,1.0,1.0,1.0)
		
		# calculate xf
		xf = 1.0/self.cols
		yf = 1.0/self.rows
		x_b = 0.0
		y_b = 1.0-(yf)
		
		for row in range(len(self.grid)):
			for col in range(len(self.grid[row])):
				sector = self.grid[row][col]
				

				rgb=utils.getRandColor()
				
				color_1 = (rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
				#glColor4f(color_1[0],color_1[1],color_1[2],1.0)
				
				y = self.rows - row
				x = self.cols - col
				s = sector
				
				#glTexCoord(s.tlx,s.tly)
				glTexCoord(x_b, y_b+yf)
				glVertex2f(*sector.points[0])
				#glTexCoord(1,1)
				glTexCoord(x_b+xf, y_b+yf)
				glVertex2f(*sector.points[1])
				#glTexCoord(1,0)
				glTexCoord(x_b+xf, y_b)
				glVertex2f(*sector.points[2])
				#glTexCoord(0,0)
				glTexCoord(x_b, y_b)
				glVertex2f(*sector.points[3])
				
				x_b += xf
				
			y_b -= yf
			x_b = 0.0
			
		glEnd()
	
	def snakeEffectDraw(self):
		glBindTexture(GL_TEXTURE_2D,self.texture.tex_id)
		glBegin(GL_QUADS)
		glColor4f(1.0,1.0,1.0,1.0)
		
		for row in range(len(self.grid)):
			for col in range(len(self.grid[row])):
				sector = self.grid[row][col]
					
				y = self.rows - row
				x = self.cols - col
				'''
				glTexCoord(self.tx*x,((self.ty*y)+self.ty))
				glVertex2f(*sector.topleft)
				glTexCoord((self.tx*x)+self.tx,((self.ty*y)+self.ty))
				glVertex2f(*sector.topright)
				glTexCoord((self.tx*x)+self.tx,((self.ty*y)))
				glVertex2f(*sector.bottomright)
				glTexCoord(self.tx*x,self.ty*y)
				glVertex2f(*sector.bottomleft)
				'''
				
				glTexCoord(0,1)
				glVertex2f(*sector.topleft)
				glTexCoord(1,1)
				glVertex2f(*sector.topright)
				glTexCoord(1,0)
				glVertex2f(*sector.bottomright)
				glTexCoord(0,0)
				glVertex2f(*sector.bottomleft)
				
				
		glEnd()
	
	def drawQuadBasic(self):
		
		glDisable(GL_TEXTURE_2D)
		glBegin(GL_POINTS)
		for row in range(len(self.grid)):
			for col in range(len(self.grid[row])):
				sector = self.grid[row][col]
					
					
				glVertex2f(*sector.topleft)
				#glVertex2f(*sector.topright)
				#glVertex2f(*sector.bottomright)
				#glVertex2f(*sector.bottomleft)
		
		glEnd()			
		glEnable(GL_TEXTURE_2D)
		
	def liquid(self):
		
		for row in range(len(self.grid)):
			
			for col in range(len(self.grid[row])):
				sector = self.grid[row][col]
				x = sector.x
				y = sector.y
				
				points = sector.points[:]
				spoints = sector.spoints[:]
				
				for i in range(len(sector.points)):
					x,y = points[i]
					sx,sy = spoints[i]
				
					new_x = (sx + (math.sin(self.change + (sx) * .04) * 6)) + self.cols		# this is a wave behaviour
					new_y = (sy + (math.sin(self.change + (sy) * .04) * 6)) + self.rows		
					sector.points[i] = (new_x,new_y)
				
				
				#xpos = ((col*4) + (math.sin(self.change + (col*50) * .01) * 2)) + self.cols		# this is a wave behaviour
				#ypos = ((row*4) + (math.sin(self.change + (row*50) * .01) * 2)) + self.rows		# this works better
				
				#xpos = ((sector.start_x) + (math.sin(self.change + (sector.x*50) * .01) * 2)) + self.cols		# this is a weird one behaviour
				#ypos = ((sector.start_y) + (math.sin(self.change + (sector.y*50) * .01) * 2)) + self.rows		
				#self.factor = (self.factor + 0.35) % 1
				#self.factor = random.random()
				
				#xpos = ((col*10) + (math.sin((self.change+(col/(self.cols*self.factor))) + (col * sector.w) * .01) * 2)) + self.cols		# this is a weird one behaviour
				#ypos = ((row*10) + (math.sin((self.change +(row/(self.cols*self.factor))) + (row * sector.h) * .01) * 2)) + self.rows		
				
		self.change += 0.2
	
	def twirl(self):
		
		for row in range(len(self.grid)):
				
			for col in range(len(self.grid[row])):
				sector = self.grid[row][col]
				px = sector.w
				py = sector.h
				
				points = sector.points[:]
				spoints = sector.spoints[:]
				
				for i in range(len(sector.points)):
					x,y = points[i]
					sx,sy = spoints[i]
					
					cx,cy = sector.hx,sector.hy
					r = math.sqrt((sector.x-px/2.0) ** 2 + (sector.y-py/2.0) ** 2 )

					amplitude = 0.1 * 1 * 1
					
					a = r * math.sin( math.pi/2.0  * math.pi * 4 * 2 ) * amplitude

					#dx = math.sin(a) + self.change * (y-cy) + math.cos(a) + self.change * (x-cx)
					#dy = math.cos(a) + self.change * (y-cy) - math.sin(a) + self.change * (x-cx)
					
					dx = math.sin(a) * (y-cy) + math.cos(a) * (x-cx)
					dy = math.cos(a) * (y-cy) - math.sin(a) * (x-cx)

					
					new_x = cx + dx
					new_y = cy + dy
					
					sector.points[i] = (new_x,new_y)
		self.change -= 0.06 
		
	def wave(self,hsin=False,vsin=True):
		
		for row in range(len(self.grid)):
				
			for col in range(len(self.grid[row])):
				sector = self.grid[row][col]
				px = sector.x
				py = sector.y
				
				points = sector.points[:]
				spoints = sector.spoints[:]
				
				for i in range(len(sector.points)):
					x,y = points[i]
					sx,sy = spoints[i]
					
					if hsin:
						xpos = (sx + (math.sin(math.pi* 2 *2 + (y+self.change) * .01) * 20 * 1))
					else:
						xpos = sx
					
					if vsin:
						ypos = (sy + (math.sin(math.pi* 2 *2 + (x+self.change) * .01) * 20 * 1))
					else:
						ypos = sy
						
					sector.points[i] = (xpos,ypos)
		
		self.change += 4.2	
	
	def ripple(self,hsin=False,vsin=True):
		
		for row in range(len(self.grid)):
				
			for col in range(len(self.grid[row])):
				sector = self.grid[row][col]
				px = sector.x
				py = sector.y
				
				points = sector.points[:]
				spoints = sector.spoints[:]
				
				for i in range(len(sector.points)):
					x,y = points[i]
					sx,sy = spoints[i]
					
					if hsin:
						xpos = (sx + (math.sin(math.pi* 2 *2 + (x+self.change) * .01) * 20 * 1))
					else:
						xpos = sx
					
					if vsin:
						ypos = (sy + (math.sin(math.pi* 2 *2 + (y+self.change) * .01) * 20 * 1))
					else:
						ypos = sy
						
					sector.points[i] = (xpos,ypos)
		
		self.change += 4.2	
	
	def update(self):
		
		
		for row in range(len(self.grid)):
			for col in range(len(self.grid[row])):
				self.grid[row][col].update()
		
		self.liquid()
		
	
	def draw(self):
	
		glPushMatrix()
		glTranslate(40,100,0)
		glScalef(1.0,1.0,0.0)
		
		if self.texture is not None:
			self.drawQuadImage()
		else:
			self.drawQuadBasic()
		glPopMatrix()
		