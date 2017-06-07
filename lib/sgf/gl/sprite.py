import pygame
from pygame.locals import*

from OpenGL.GL import*
from OpenGL.GLU import*
import sgf.utils.g_utils as utils
import sgf.gl.resource as res
from sgf.utils.helpers import*
#print "Hi5"

class Sprite(object):
	"""GL Sprite object"""
	def __init__(self,x,y,w,h,imagepath_list,colorkey=None):
		"""Sets up the sprite"""
		# imagepath_list is a list of pathnames leading to the images to load
		# can just be one path or multiple of them, if multiple the sprite will support animation
		
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.hx, self.hy = self.w/2, self.h/2
		
		self.alpha = 1.0
		self.rotation = 0
		self.color = (1.0,1.0,1.0)
		self.scale = 1.0
		
		self.texture_list = []
		self.image_index = 0
		self.frame = 0
		
		for path in imagepath_list:
			texture = res.getTexture(path,w,h,colorkey)
			self.texture_list.append(texture)
		
		self.cur_texture = self.texture_list[self.image_index] 
		self.v = self.cur_texture.v
		self.min_u,self.max_u = self.cur_texture.u_coords[self.frame]
		
		# create display list
		#self.draw_list = glGenLists(1)
		#glNewList(self.draw_list, GL_COMPILE)	# once compiled I cant seem to modify a display list
		
		#glEndList()
	
	def draw(self,x=None,y=None):
		glBindTexture(GL_TEXTURE_2D, self.cur_texture.tex_id)
		#glDisable(GL_TEXTURE_2D)
		self.drawQuad(x,y)
		#print self.alpha
	
	def update(self,timepassed):
		"""updates the sprite"""
		
		self.cur_texture = self.texture_list[self.image_index] 
		self.v = self.cur_texture.v
		self.min_u,self.max_u = self.cur_texture.u_coords[self.frame]
		
	def drawQuad(self,x=None,y=None):
		
		glPushMatrix()
		if x is not None and y is None:
			glTranslate(x + self.hx,self.y + self.hy,0)	# position relative to quad center
		elif y is not None and x is None:
			glTranslate(self.x + self.hx,y + self.hy,0)	# position relative to quad center
		elif y is not None and x is not None:
			glTranslate(x + self.hx,y + self.hy,0)	# position relative to quad center
		else:
			glTranslate(self.x + self.hx,self.y + self.hy,0)	# position relative to quad center
		
		glRotate(self.rotation,0,0,1)
		glScalef(self.scale,self.scale,1.0)
		glColor4f(self.color[0],self.color[1],self.color[2],self.alpha)
		glBegin(GL_QUADS)
		
		glTexCoord2f(self.min_u, 1)
		glVertex(-self.hx, -self.hy)
		glTexCoord2f(self.max_u, 1)
		glVertex(self.hx, -self.hy)
		glTexCoord2f(self.max_u, 1-self.v)
		glVertex(self.hx, self.hy)
		glTexCoord2f(self.min_u, 1-self.v)
		glVertex(-self.hx, self.hy)
		glEnd()
		#glCallList(self.draw_list)
		glPopMatrix()
		
		