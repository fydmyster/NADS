import pygame,sys,math
from pygame.locals import*

class Tweenable(object):
	def __init__(self,pos,w,h,color,optional_draw_surf = None):
		"""A basic class that supports easing movement on its instances"""
		
		# @param : optional_draw_surf: an image_filename[0] and a string[1] in a tuple/list : 'normal','alpha','colorkey'
		# - this image surface will be drawn as an alternate to a filled rect
		# - None means a filled rect will be drawn
		
		# TODO : Have this accept fonts filenames so I can draw text as a tweenable too
		
		self.x,self.y=pos
		self.w = w
		self.h = h
		self.color = color
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = None 	# milliseconds (very pointless since its not utilized)
		self.startSet=False
		self.positionReached=False
		self.optional_draw_surf = optional_draw_surf
		
		if self.optional_draw_surf != None:
		
			if self.optional_draw_surf[1] == "normal":
				self.image = pygame.image.load(self.optional_draw_surf[0]).convert()
		
			elif self.optional_draw_surf[1] == "alpha":
				self.image = pygame.image.load(self.optional_draw_surf[0]).convert_alpha()
		
			elif self.optional_draw_surf[1] == "colorkey":
				self.image = pygame.image.load(self.optional_draw_surf[0]).convert()
				self.image.set_colorkey((255,0,255))
		
			self.rect = self.image.get_rect()
			
		else:
			self.rect=pygame.Rect(self.x,self.y,self.w,self.h)
		
		# these vars are for when you call moveTo(which calls the easing methods indirectly)
		self.current_behaviour = None
		self.xOffset = None
		self.yOffset = None
	
	def __reset(self):
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = None 	# milliseconds (very pointless since its not utilized)
		self.startSet=False
		self.positionReached=False
	
	def moveTo(self,xOffset,yOffset,duration,easing_func):
		"""This is a convenience function that is an alternative to calling the easing functions directly"""
		self.__reset()	# this a reinit so you can change the target at any time with a moveTo call
		
		self.xOffset = xOffset
		self.yOffset = yOffset
		self.duration = duration
		self.current_behaviour = getattr(self,easing_func)
	
	def draw(self,Surface):
		
		if self.optional_draw_surf != None:
			Surface.blit(self.image, self.rect)
		else:
			pygame.draw.rect(Surface,self.color,self.rect)
	
	def update(self,timepassed):
		"""You only need to call this if youre calling easing functions through moveTo()"""
		if self.current_behaviour != None:
			self.current_behaviour(self.xOffset,self.yOffset,self.duration,timepassed)
	
	def easeLinear(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.timeSinceStart = 0.0
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
	
	
		if dt <=1:
			self.rect.x = changeInX *dt + self.startX
			self.rect.y = changeInY *dt + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
	
	
	def easeInQuad(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.timeSinceStart = 0.0
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
	
	
		if dt <=1:
			self.rect.x = changeInX *dt *dt + self.startX
			self.rect.y = changeInY *dt *dt + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
			
	def easeOutQuad(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
		
		if dt <=1:
			self.rect.x = changeInX *dt *(2- dt) + self.startX
			self.rect.y = changeInY *dt *(2- dt) + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeInOutQuad(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.timeSinceStart = 0.0
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
		dt*=2
		
		if dt<=2:
			if dt <1:
				self.rect.x = changeInX /2 *dt *dt + self.startX
				self.rect.y = changeInY /2 *dt *dt + self.startY
		
			else:
				self.rect.x = -changeInX/2 *((dt-1) *((dt -1)-2) -1) + self.startX
				self.rect.y = -changeInY/2 *((dt-1) *((dt -1)-2) -1) + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
	
	def easeInQuart(self,xOffset,yOffset,duration,timepassed):
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
		
		if dt <=1:
			self.rect.x = changeInX *dt*dt*dt*dt + self.startX
			self.rect.y = changeInY *dt*dt*dt*dt + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
			
	def easeOutQuart(self,xOffset,yOffset,duration,timepassed):

		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
		
		if dt <=1:
			dt -= 1
			self.rect.x = (-changeInX) * ((dt)*dt*dt*dt - 1) + self.startX
			self.rect.y = (-changeInY) * ((dt)*dt*dt*dt - 1) + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0

	def easeInOutQuart(self,xOffset,yOffset,duration,timepassed):
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
		dt*=2
		
		if dt<= 2:
			if (dt) < 1: 
				self.rect.x = changeInX/2 *dt*dt*dt*dt + self.startX
				self.rect.y = changeInY/2 *dt*dt*dt*dt + self.startY
			else:
				dt -= 2
				self.rect.x = -changeInX/2 * ((dt)*dt*dt*dt - 2) + self.startX
				self.rect.y = -changeInY/2 * ((dt)*dt*dt*dt - 2) + self.startY
		else:
			self.startSet = False
			self.timeSinceStart = 0.0

	def easeInSin(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.timeSinceStart = 0.0
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
	
		if dt <=1:
			self.rect.x = changeInX *(1 - math.cos((dt) * (math.pi/2))) + self.startX
			self.rect.y = changeInY *(1 - math.cos((dt) * (math.pi/2))) + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeOutSin(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
	
		if dt <=1:
			self.rect.x = changeInX * math.sin(dt * (math.pi/2)) + self.startX
			self.rect.y = changeInY * math.sin(dt * (math.pi/2)) + self.startY

		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeInOutSin(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
				
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
	
		if dt <=1:
			self.rect.x = -changeInX/2 *(math.cos(3.1415 * dt)-1) + self.startX
			self.rect.y = -changeInY/2 *(math.cos(3.1415 * dt)-1) + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeInExpo(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
		n = math.pow(2, 10 * (dt-1))
		
		if dt <=1:
			self.rect.x = changeInX * n + self.startX
			self.rect.y = changeInY * n + self.startY
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeOutExpo(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
		
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		n = - math.pow(2, -10 * (dt)) + 1
		
		if dt <=1:
			self.rect.x = changeInX * n + self.startX
			self.rect.y = changeInY * n + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeInOutExpo(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
				
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		dt *=2
		
		if dt <=2:
			
			if dt < 1:
				n = math.pow(2, 10 * (dt-1)) /2
				self.rect.x = changeInX * n + self.startX
				self.rect.y = changeInY * n + self.startY
	
			else:
				dt-=1
				n = -(math.pow(2,-10 * dt)-2) /2
				self.rect.x = changeInX * n + self.startX
				self.rect.y = changeInY * n + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeInCirc(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
		
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		
		if dt <=1:
			self.rect.x = -changeInX * (math.sqrt(1 - (dt)*dt) -1) + self.startX
			self.rect.y = -changeInY * (math.sqrt(1 - (dt)*dt) -1) + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeOutCirc(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
				
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		
		if dt <=1:
			self.rect.x = changeInX * math.sqrt(1 - (dt-1)*(dt-1)) + self.startX		# without the final set of brackets it gets halfway then heads back to start pos
			self.rect.y = changeInY * math.sqrt(1 - (dt-1)*(dt-1)) + self.startY
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeInOutCirc(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
				
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		dt*=2
		if dt <=2:
			if dt < 1:
			
				self.rect.x = changeInX /2 *(1 - math.sqrt(1 - dt*dt)) + self.startX		
				self.rect.y = changeInY /2 *(1 - math.sqrt(1 - dt*dt)) + self.startY
				
			else:
				self.rect.x = changeInX /2 *(math.sqrt(1 - (dt-2)*(dt-2)) + 1) + self.startX		
				self.rect.y = changeInY /2 *(math.sqrt(1 - (dt-2)*(dt-2)) + 1) + self.startY
				
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeInElastic(self,xOffset,yOffset,duration,timepassed):
		# usable but i think behaviour is not quite 100%
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
				
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		dt*=2
		
		p = duration * 0.3
		ax=changeInX
		ay=changeInY
		s=p/4
		
		
		xpostFix =ax * math.pow(2,10*(dt-1))		# this is a fix, again, with post-increment operators
		ypostFix =ay * math.pow(2,10*(dt-1))		# this is a fix, again, with post-increment operators
		
		xpos = -(xpostFix * math.sin(((dt-1)* duration-s)*(2 * math.pi)/p )) + self.startX
		ypos = -(ypostFix * math.sin(((dt-1)* duration-s)*(2 * math.pi)/p )) + self.startY
		
		if dt <= 2:
			if dt==0:  
				self.rect.x=self.startX
				self.rect.y=self.startY
			
			elif dt==1: 
				self.rect.x=self.startX + changeInX
				self.rect.y=self.startY + changeInY
					
			elif dt <1:
				self.rect.x = xpos
				self.rect.y = ypos
		
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeOutElastic(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.startSet=True
			self.timeSinceStart = 0.0
			
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		dt*=2
		
		p = duration * 0.3
		ax=changeInX
		ay=changeInY
		s=p/4
	
		xpos = (changeInX * math.pow(2,-10 * dt) * math.sin( (dt * duration-s)*(2*math.pi)/p ) + changeInX + self.startX)  
		ypos = (changeInY * math.pow(2,-10 * dt) * math.sin( (dt * duration-s)*(2*math.pi)/p ) + changeInY + self.startY)
		
		if dt <= 2:
			if dt==0:  
				self.x=self.startX
				self.y=self.startY
			
			elif dt==1: 
				self.x=self.startX + changeInX
				self.y=self.startY + changeInY
					
			else:
				self.rect.x = xpos
				self.rect.y = ypos
	
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeInBounce(self,xOffset,yOffset,duration,timepassed):
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			#self.timeSinceStart = 0.0
			#self.startSet=True
			
		#self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
		
		result = self.easeOutBounce(xOffset,yOffset,duration,timepassed)
		if result != None:
			self.rect.x = changeInX - result[0] + self.startX
			self.rect.y = changeInY - result[1] + self.startY
			return (self.rect.x,self.rect.y)
			
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeOutBounce(self,xOffset,yOffset,duration,timepassed):
		"""This one eases in the correct direction. easeInBounce goes the opposite direction"""
		
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			self.timeSinceStart = 0.0
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
		#dt*=2
		#print "yebo yes"
		
		
		if dt <= 1:
		
			if dt < 1 / 2.75:
				
				self.rect.x = changeInX *(7.5625 * dt * dt) + self.startX
				self.rect.y = changeInY *(7.5625 * dt * dt) + self.startY
				
				return (self.rect.x,self.rect.y)
				
			elif dt < 2 / 2.75:
				dt -= (1.5 / 2.75)
				postFix = dt
			
				self.rect.x = changeInX *(7.5625 *(postFix)* dt + 0.75) + self.startX
				self.rect.y = changeInY *(7.5625 *(postFix)* dt + 0.75) + self.startY
				
				return (self.rect.x,self.rect.y)
				
			elif dt < 2.5 / 2.75:
				dt -= (2.25/2.75)
				postFix = dt
				self.rect.x = changeInX *(7.5625 *(postFix)* dt + 0.9375) + self.startX
				self.rect.y = changeInY *(7.5625 *(postFix)* dt + 0.9375) + self.startY
				
				return (self.rect.x,self.rect.y)
				
			else:
				dt -= (2.625/2.75)
				postFix = dt
				self.rect.x = changeInX *(7.5625 *(postFix) *dt + 0.984375) + self.startX
				self.rect.y = changeInY *(7.5625 *(postFix) *dt + 0.984375) + self.startY
				
				return (self.rect.x,self.rect.y)
				
		else:
			self.startSet = False
			self.timeSinceStart = 0.0
		
	def easeInOutBounce(self,xOffset,yOffset,duration,timepassed):
		if not self.startSet:
			self.startX,self.startY = (self.rect.x,self.rect.y)
			#self.timeSinceStart = 0.0
			#self.startSet=True
			
		#self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		if self.timeSinceStart < duration/2: 
			result = self.easeInBounce(xOffset,yOffset,duration/2,timepassed)
			if result != None:
				self.rect.x = result[0] * 0.5 + self.startX
				self.rect.y = result[1] * 0.5 + self.startY
			
		else:  
			result = self.easeOutBounce(xOffset,yOffset,duration/2,timepassed)
			if result != None:
				self.rect.x = result[0] * 0.5 + changeInX * 0.5 + self.startX
				self.rect.y = result[1] * 0.5 + changeInY * 0.5 + self.startY
			