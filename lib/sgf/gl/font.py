import os.path
import pygame
import pygame.font

from OpenGL.GL import *

import resource

pygame.font.init()

LEFT = 0
RIGHT = 1
TOP = 2
BOTTOM = 3
CENTER = 4
'''
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_TEXTURE_2D)
'''
class Font(object):
	characterSpacing = 2
	maxTextureWidth = 256
	
	def __init__(self, filename, size,
					charset='abcdefghijklmnopqrstuvwxyz' +\
							'ABCDEFGHIJKLMNOPQRSTUVWXYZ' +\
							'1234567890;:,.!?%&"\' '):
		#filename = os.path.join('fonts', filename)
		self.filename = filename
		self.charset = charset
		self.charmap = {}
        
		font = pygame.font.Font(filename, size)
		self.descent = font.get_descent()
		self.w, self.h = font.size(self.charset)
		self.w += len(self.charset) * self.characterSpacing
		self.lineSize = self.h
		if self.w > self.maxTextureWidth:
			self.h = (self.w / self.maxTextureWidth + 1) * self.h
			self.w = self.maxTextureWidth
		self.tw, self.th = resource.pow2(self.w), resource.pow2(self.h)
		data = chr(0) * self.tw * self.th * 4
		surface = pygame.image.fromstring(data, (self.tw, self.th), 'RGBA')
		
		x, y = 0.0, 0.0
		for c in charset:
			render = font.render(c, True, (255, 255, 255))
			render = pygame.transform.flip(render,False,True)		# hack somehow my shit was upside down
		
			cw, ch = font.size(c)
			if x + cw >= self.tw:
				x = 0.0
				y += self.lineSize
			surface.blit(render, (x, y))
			
			self.charmap[c] = (x/self.tw, (self.th-y-self.lineSize)/self.th, 
								(x+cw)/self.tw, (self.th-y)/self.th), cw
			x += cw + self.characterSpacing
			
			
		self.tex = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.tex)
		glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexImage2D(GL_TEXTURE_2D, 0, 4, self.tw, self.th,
					0, GL_RGBA, GL_UNSIGNED_BYTE, 
					pygame.image.tostring(surface, 'RGBA', True))

	def debug(self, outline=None):
		glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
		glColor(0, 0, 0)
		glBindTexture(GL_TEXTURE_2D, self.tex)
		glBegin(GL_QUADS)
		glTexCoord(0, 0)
		glVertex(0, 0)
		glTexCoord(1, 0)
		glVertex(self.tw, 0)
		glTexCoord(1, 1)
		glVertex(self.tw, self.th)
		glTexCoord(0, 1)
		glVertex(0, self.th)
		glEnd()
		glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)

	def textWidth(self, text):
		w = 0
		for c in text:
			w += self.charmap[c][1]
		return w

	def draw(self, text, 
			pos=(0,0), 
			color=(0.0, 0.0, 0.0, 0.0), 
			valign=BOTTOM,
			align=LEFT):
		glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
		glBindTexture(GL_TEXTURE_2D, self.tex)
		glColor4f(*color)

		x, y = pos
		if align == RIGHT:
			x -= self.textWidth(text)
		elif align == CENTER:
			x -= self.textWidth(text)/2

		if valign == CENTER:
			y -= self.lineSize/2
		elif valign == TOP:
			y -= self.lineSize
		y += self.descent

		glBegin(GL_QUADS)
		for c in text:
			box, cw = self.charmap[c]
			glTexCoord(box[0], box[1])
			glVertex(x, y)
			glTexCoord(box[2], box[1])
			glVertex(x + cw, y)
			glTexCoord(box[2], box[3])
			glVertex(x + cw, y + self.lineSize)
			glTexCoord(box[0], box[3])
			glVertex(x, y + self.lineSize)
			x += cw
		glEnd()
		#glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)		# cant use color alpha with this mode
