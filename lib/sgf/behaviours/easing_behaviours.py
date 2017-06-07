import pygame,sys,math
from pygame.locals import*

class EaseInQuad(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
	
		if dt <= 1:
			self.character.x = changeInX *dt *dt + self.startX
			self.character.y = changeInY *dt *dt + self.startY
			
			return (self.character.x, self.character.y)
			
		else:
			return None
		

class EaseOutQuad(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
		
		if dt <=1:
			self.character.x = changeInX *dt *(2- dt) + self.startX
			self.character.y = changeInY *dt *(2- dt) + self.startY
			
			return (self.character.x, self.character.y)
		
		else:
			return None

class EaseInOutQuad(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
		
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
		dt*=2
		
		if dt<=2:
			if dt <1:
				self.character.x = changeInX /2 *dt *dt + self.startX
				self.character.y = changeInY /2 *dt *dt + self.startY
				return (self.character.x, self.character.y)
		
				
			else:
				self.character.x= -changeInX/2 *((dt-1) *((dt -1)-2) -1) + self.startX
				self.character.y= -changeInY/2 *((dt-1) *((dt -1)-2) -1) + self.startY
				return (self.character.x, self.character.y)
		else:
			return None

class EaseInSin(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
	
		if dt <=1:
			self.character.x = changeInX *(1 - math.cos((dt) * (math.pi/2))) + self.startX
			self.character.y = changeInY *(1 - math.cos((dt) * (math.pi/2))) + self.startY
			return (self.character.x, self.character.y)
		
		else:
			return None
		
class EaseOutSin(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
		
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
	
		if dt <=1:
			self.character.x = changeInX * math.sin(dt * (math.pi/2)) + self.startX
			self.character.y = changeInY * math.sin(dt * (math.pi/2)) + self.startY
			return (self.character.x, self.character.y)
		
		
		else:
			return None
			
class EaseInOutSin(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
	
		if dt <=1:
			self.character.x = -changeInX/2 *(math.cos(3.1415 * dt)-1) + self.startX
			self.character.y = -changeInY/2 *(math.cos(3.1415 * dt)-1) + self.startY
			return (self.character.x,self.character.y)
			
		else:
			return None

class EaseInExpo(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX = xOffset - self.startX
		changeInY = yOffset - self.startY
	
		dt = self.timeSinceStart / duration
		n = math.pow(2, 10 * (dt-1))
		
		if dt <=1:
			self.character.x = changeInX * n + self.startX
			self.character.y = changeInY * n + self.startY
			return (self.character.x,self.character.y)
			
		else:
			return None

class EaseOutExpo(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		n = - math.pow(2, -10 * (dt)) + 1
		
		if dt <=1:
			self,character.x = changeInX * n + self.startX
			self.character.y = changeInY * n + self.startY
			return (self.character.x,self.character.y)
			
		else:
			return None
	
class EaseInOutExpo(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		dt *=2
		
		if dt <=2:
			
			if dt < 1:
				n = math.pow(2, 10 * (dt-1)) /2
				self.character.x = changeInX * n + self.startX
				self.character.y = changeInY * n + self.startY
				return (self.character.x,self.character.y)
				
			else:
				dt-=1
				n = -(math.pow(2,-10 * dt)-2) /2
				self.character.x = changeInX * n + self.startX
				self.character.y = changeInY * n + self.startY
				return (self.character.x,self.character.y)
		else:
			return None
	
class EaseInCirc(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False	
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		
		if dt <=1:
			self.character.x = -changeInX * (math.sqrt(1 - (dt)*dt) -1) + self.startX
			self.character.y = -changeInY * (math.sqrt(1 - (dt)*dt) -1) + self.startY
			return (self.character.x,self.character.y)
		else:
			return None

class EaseOutCirc(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		
		if dt <=1:
			self.character.x = changeInX * math.sqrt(1 - (dt-1)*(dt-1)) + self.startX		# without the final set of brackets it gets halfway then heads back to start pos
			self.character.y = changeInY * math.sqrt(1 - (dt-1)*(dt-1)) + self.startY
			return (self.character.x,self.character.y)
		else:
			return None
		
class EaseInOutCirc(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False	
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
		self.timeSinceStart += float(timepassed)
		changeInX =  xOffset - self.startX
		changeInY =  yOffset - self.startY  
	
		dt = self.timeSinceStart / duration
		dt*=2
		if dt <=2:
			if dt < 1:
			
				self.character.x = changeInX /2 *(1 - math.sqrt(1 - dt*dt)) + self.startX		
				self.character.y = changeInY /2 *(1 - math.sqrt(1 - dt*dt)) + self.startY
				return (self.character.x,self.character.y)
				
			else:
				self.character.x = changeInX /2 *(math.sqrt(1 - (dt-2)*(dt-2)) + 1) + self.startX		
				self.character.y = changeInY /2 *(math.sqrt(1 - (dt-2)*(dt-2)) + 1) + self.startY
				return (self.character.x,self.character.y)
		else:
			return None
		
class EaseInElastic(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		# usable but i think behaviour is not quite 100%
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
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
				self.character.x=self.startX
				self.character.y=self.startY
				return (self.character.x,self.character.y)
				
			elif dt==1: 
				self.character.x=self.startX + changeInX
				self.character.y=self.startY + changeInY
				return (self.character.x,self.character.y)
				
			elif dt <1:
				self.character.x = xpos
				self.character.y = ypos
				return (self.character.x,self.character.y)
		
		else:
			return None

class EaseOutElastic(object):
	def __init__(self,char):
		self.character = char
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0
		self.duration = 5000 	# milliseconds 
		self.startSet=False
	
	def reInit(self):
		"""Re initializes the object to default"""
		self.startX = self.startY = None
		self.endX = self.endY = None
		self.timeSinceStart=0.0 
		self.startSet=False
	
	def getEasing(self,xOffset,yOffset,duration,timepassed):
		
		if not self.startSet:
			self.startX,self.startY = (self.character.x,self.character.y)
			self.startSet=True
			
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
				self.character.x=self.startX
				self.character.y=self.startY
				return (self.character.x,self.character.y)
				
			elif dt==1: 
				self.character.x=self.startX + changeInX
				self.character.y=self.startY + changeInY
				return (self.character.x,self.character.y)
					
			else:
				self.character.x = xpos
				self.character.y = ypos
				return (self.character.x,self.character.y)
		else:
			return None