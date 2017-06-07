import pygame
from pygame.locals import *
import os.path

from OpenGL.GL import *

def pow2(x):
	y = 1
	while y < x:
		y <<= 1
	return y

class Texture:
	def __init__(self, tex_id, width, height, u, v, num_sprites_x=1,num_sprites_y=1):
		self.tex_id = tex_id
		self.width = width
		self.height = height
		self.u = u
		self.v = v
		self.v_coords = []
		
		self.num_sprites_x = num_sprites_x
		self.num_sprites_y = num_sprites_y
		
		# create u texcoords for the sheet
		if num_sprites_x > 1:
			self.u_coords = []
			# find the width of each sprite in coord space
			w = self.u / float(num_sprites_x)
			for i in range(num_sprites_x):
				u_coord = w * (i+1)
				self.u_coords.append((u_coord-w, u_coord))
		else:
			# this is a single image not a sheet
			self.u_coords = [(0,self.u)] 

		# create v texcoords for the sheet
		if num_sprites_y > 1:
			self.v_coords = []
			# find the height of each sprite in coord space
			h = self.v / float(num_sprites_y)
			for i in range(num_sprites_y):
				v_coord = h * (i+1)
				self.u_coords.append((v_coord-h, v_coord))
		else:
			# this is a single image not a sheet
			self.v_coords = [(0,self.v)] 
	
			
class Resources:
	def __init__(self):
		self.textures = {}      # filename -> (id, width, height, u, v)
		# u, v are the max texture coords for the image

	def getTexture(self,filename,sprite_w = None,sprite_h=None,colorkey = None):
		"""retrieves textures from images"""
		
		# sprite_w : used to indicate the size of a single sprite if the filename points to a sprite sheet
		# colorkey : the color used as transparent on the loaded image, usually (255,0,0)- MAGENTA
		
		if filename in self.textures:
			return self.textures[filename]
		else:
			img = pygame.image.load(filename)
			
			if colorkey is not None:
				img.set_colorkey(colorkey)
			
			width = img.get_width()
			height = img.get_height()
			texwidth = pow2(width)
			texheight = pow2(height)
			if texwidth != width or texheight != height:
				data = chr(0) * texwidth* texheight*4
				surf = pygame.image.fromstring(data, 
                                               (texwidth, texheight), 'RGBA')
				surf.blit(img, (0,0))
				img = surf
				
			#img = pygame.transform.flip(img,False,True)
			u, v = width / float(texwidth), height/float(texheight)
			tex_id = glGenTextures(1)
			glBindTexture(GL_TEXTURE_2D, tex_id)
			glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
			glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			glPixelStorei(GL_UNPACK_ALIGNMENT,1)
			glTexImage2D(GL_TEXTURE_2D, 0, 4, texwidth, texheight,
					0, GL_RGBA, GL_UNSIGNED_BYTE, 
					pygame.image.tostring(img, 'RGBA', True))
						
			if sprite_w is not None:
				cx_num_sprites = width/sprite_w
			else: 
				cx_num_sprites = 1
			
			if sprite_h is not None:
				cy_num_sprites = height/sprite_h
			else: 
				cy_num_sprites = 1
			
			
			texture = Texture(tex_id, width, height, u, v, cx_num_sprites, cy_num_sprites)
				
			self.textures[filename] = texture
			return texture

res = Resources()

# here we specify the size of one item on the sprite sheet as sprite_w/sprite_h
def getTexture(filename, sprite_w=None,sprite_h=None, colorkey=None):
	"""Returns a texture object. Specify sprite_w so as to find out the number of texture frames"""
	return res.getTexture(filename, sprite_w,sprite_h,colorkey)
