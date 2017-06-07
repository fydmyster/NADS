import pygame,random
from sgf.collision.gen_collision import Line
import sgf.utils.g_utils as gutils

class WallTile(object):
	def __init__(self,x,y,size=16):
		
		self.image = pygame.image.load("images\\walltile.png").convert()
		self.image.set_colorkey((255,0,255))
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
		self.w = size
		self.h = size
		self.hx = self.w / 2
		self.hy = self.h / 2
		self.collidable = True
		self.color = (0,0,0)
		self.col_rect = pygame.Rect(0,0,14,14)
		
		self.normals = [(0,-1),(1,0),(0,1),(-1,0)]
		
		# decompose sides into linesegs
		self.topline=Line(self.rect.topleft,self.rect.topright,self.color)
		self.bottomline=Line(self.rect.bottomleft,self.rect.bottomright,self.color)
		self.leftline=Line(self.rect.topleft,self.rect.bottomleft,self.color)
		self.rightline=Line(self.rect.topright,self.rect.bottomright,self.color)
		
		self.lines=[self.rightline,self.topline,self.leftline,self.bottomline]
		self.contactedLines=[]
		
		self.rect.topleft = (self.x,self.y)
		self.col_rect.center = self.rect.center
		
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)
		#self.col_rect.draw(Surface)
		
class GroundTile(object):
	def __init__(self,x,y,size=16):
		
		image_choices = ["images\\ground1.png","images\\ground2.png"]
		path = random.choice(image_choices)
		self.image = pygame.image.load(path).convert()
		self.image.set_colorkey((255,0,255))
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
		self.w = size
		self.h = size
		self.hx = self.w / 2
		self.hy = self.h / 2
		self.collidable = False
		
		self.rect.topleft = (self.x,self.y)
		
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)

class DoorTile(object):
	def __init__(self,x,y,size=16):
		
		self.kind = "DoorTile"
		self.master_images = gutils.sliceSheetColKey(16,16,"images\\door.png")
		
		self.image = self.master_images[0]
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
		self.w = size
		self.h = size
		self.hx = self.w / 2
		self.hy = self.h / 2
		self.collidable = False
		self.is_open = False
		self.rect.topleft = (self.x,self.y)
	
	def update(self,timepassed):
		pass
	
	def draw(self,Surface):
		
		if self.is_open:
			self.image = self.master_images[1]
		else:
			self.image = self.master_images[0]
		
		Surface.blit(self.image,self.rect)
		