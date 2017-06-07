import math,random
import pygame
from pygame.locals import*
from sgf.utils.g_utils import colorLerp

# todo : and wind and gravity options to particles

class ParticleCircle(object):
	def __init__(self,x,y,**kwargs):
		# @param :kill_condition - is a two item tuple
		# at index 0 - a string (either 'time','alpha')
		# at index 1 - if index 0 == 'time' pass the max particle live time in milliseconds
		#			 - if index 1 == 'alpha' pass in the amount of alpha to subtract each tick
		#			 - will implement collision kill condition soon
		
		self.valid_kwargs = {			
			"xvel" : 0,
			"yvel" : 0,
			"friction" : 0.97,
			"radius" : 4,
			"gravity" : 0.06,
			"wind_direction" : 180,
			"wind_strength" : 0.0,
			"color" : (255,0,0),
			"kill_condition" : ("time",5000),
			"fill" : 0
		}
		
		for key,val in kwargs.items():
			if self.valid_kwargs.has_key(key):
				self.valid_kwargs[key] = val
			else:
				# raise exception
				raise Exception("invalid attribute %s has been referenced" % key)
		# set atrributes
		for key,val in self.valid_kwargs.items():
			setattr(self,key,val)
		
		self.x = x
		self.y = y
		self.alive = True
		self.acctime = 0
		self.alpha = 255
		
		self.image = pygame.Surface((self.radius*2,self.radius*2))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		pygame.draw.circle(self.image,self.color,(self.radius,self.radius),self.radius,self.fill)
		
		self.rect = self.image.get_rect()
		self.rect.center = (self.x,self.y)
		
	def update(self,timepassed):
		
		if self.alive:
		
			if self.kill_condition[0] == "time":
				self.acctime += timepassed
			
				if self.acctime > self.kill_condition[1]:
					self.alive = False
		
			elif self.kill_condition[0] == "alpha":
				self.alpha -= self.kill_condition[1]
				
				if self.alpha < 0:
					self.alpha = 0
					self.alive = False
			
			
			# calculate wind_direction as a vector
			
			angle = self.wind_direction	
			vec_x = math.cos((angle * (math.pi/180)))
			vec_y = math.sin((angle * (math.pi/180)))
						
			vec_x *= self.wind_strength
			vec_y *= self.wind_strength
						
			self.xvel += vec_x
			self.yvel += vec_y
			
			self.yvel += self.gravity
			
			self.x += self.xvel
			self.y += self.yvel
			
			self.xvel *= self.friction
			self.yvel *= self.friction
			
			self.rect.center = (self.x,self.y)
			self.image.set_alpha(self.alpha)
			
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)

class ParticleCircleLerp(object):
	def __init__(self,x,y,**kwargs):
		# @param :kill_condition - is a two item tuple
		# at index 0 - a string (either 'time','alpha')
		# at index 1 - if index 0 == 'time' pass the max particle live time in milliseconds
		#			 - if index 1 == 'alpha' pass in the amount of alpha to subtract each tick
		#			 - will implement collision kill condition soon
		
		self.valid_kwargs = {			
			"xvel" : 0,
			"yvel" : 0,
			"friction" : 0.97,
			"radius" : 4,
			"start_color" : (255,0,0),
			"end_color" : (0,255,0),
			"change" : 0.02,
			"kill_condition" : ("time",5000),
			"gravity" : 0.06,
			"wind_direction" : 180,
			"wind_strength" : 0.0,
			"fill" : 0
		}
		
		for key,val in kwargs.items():
			if self.valid_kwargs.has_key(key):
				self.valid_kwargs[key] = val
			else:
				# raise exception
				raise Exception("invalid attribute %s has been referenced" % key)
		# set atrributes
		for key,val in self.valid_kwargs.items():
			setattr(self,key,val)
		
		self.x = x
		self.y = y
		self.alive = True
		self.factor = 0.0
		self.color = self.start_color
		
		self.acctime = 0
		self.alpha = 255
		
		self.image = pygame.Surface((self.radius*2,self.radius*2))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		pygame.draw.circle(self.image,self.color,(self.radius,self.radius),self.radius,self.fill)
		
		self.rect = self.image.get_rect()
		self.rect.center = (self.x,self.y)
		
	def update(self,timepassed):
		
		if self.alive:
		
			if self.kill_condition[0] == "time":
				self.acctime += timepassed
			
				if self.acctime > self.kill_condition[1]:
					self.alive = False
		
			elif self.kill_condition[0] == "alpha":
				self.alpha -= self.kill_condition[1]
				
				if self.alpha < 0:
					self.alpha = 0
					self.alive = False
			
			self.factor += self.change
			
			if self.factor > 1:
				self.factor = 1
				self.color = self.end_color
			else:	
				self.color = colorLerp(self.start_color,self.end_color,self.factor)
			
			# calculate wind_direction as a vector
			
			angle = self.wind_direction	
			vec_x = math.cos((angle * (math.pi/180)))
			vec_y = math.sin((angle * (math.pi/180)))
						
			vec_x *= self.wind_strength
			vec_y *= self.wind_strength
						
			self.xvel += vec_x
			self.yvel += vec_y
			
			self.yvel += self.gravity
			
			self.x += self.xvel
			self.y += self.yvel
			
			self.xvel *= self.friction
			self.yvel *= self.friction
			
			self.image = pygame.Surface((self.radius*2,self.radius*2))
			self.image.set_colorkey((255,0,255))
			self.image.fill((255,0,255))
		
			pygame.draw.circle(self.image,self.color,(self.radius,self.radius),self.radius,self.fill)
		
			self.rect = self.image.get_rect()
			self.rect.center = (self.x,self.y)
		
			self.image.set_alpha(self.alpha)
			
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)		
		
class ParticleCircleGrow(object):
	def __init__(self,x,y,**kwargs):
		# @param :kill_condition - is a two item tuple
		# at index 0 - a string (either 'time','alpha')
		# at index 1 - if index 0 == 'time' pass the max particle live time in milliseconds
		#			 - if index 1 == 'alpha' pass in the amount of alpha to subtract each tick
		#			 - will implement collision kill condition soon
		
		self.valid_kwargs = {			
			"xvel" : 0,
			"yvel" : 0,
			"friction" : 0.97,
			"radius" : 4,
			"grow_velocity" : 0.5,
			"grow_decay" : 0.98,
			"color" : (255,0,0),
			"gravity" : 0.06,
			"wind_direction" : 270,
			"wind_strength" : 0.2,
			"kill_condition" : ("time",5000),
			"fill" : 0
		}
		
		for key,val in kwargs.items():
			if self.valid_kwargs.has_key(key):
				self.valid_kwargs[key] = val
			else:
				# raise exception
				raise Exception("invalid attribute %s has been referenced" % key)
		# set atrributes
		for key,val in self.valid_kwargs.items():
			setattr(self,key,val)
		
		self.x = x
		self.y = y
		self.alive = True
		
		self.acctime = 0
		self.alpha = 255
		
		self.image = pygame.Surface((self.radius*2,self.radius*2))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		pygame.draw.circle(self.image,self.color,(self.radius,self.radius),self.radius,self.fill)
		
		self.image.set_alpha(self.alpha)
		self.rect = self.image.get_rect()
		self.rect.center = (self.x,self.y)
		
	def update(self,timepassed):
		
		if self.alive:
		
			if self.kill_condition[0] == "time":
				self.acctime += timepassed
			
				if self.acctime > self.kill_condition[1]:
					self.alive = False
		
			elif self.kill_condition[0] == "alpha":
				self.alpha -= self.kill_condition[1]
				
				if self.alpha < 0:
					self.alpha = 0
					self.alive = False
			
			# calculate wind_direction as a vector
			
			angle = self.wind_direction	
			vec_x = math.cos((angle * (math.pi/180)))
			vec_y = math.sin((angle * (math.pi/180)))
						
			vec_x *= self.wind_strength
			vec_y *= self.wind_strength
						
			self.xvel += vec_x
			self.yvel += vec_y
			
			self.yvel += self.gravity
			
			self.x += self.xvel
			self.y += self.yvel
			
			self.radius += self.grow_velocity
			
			self.grow_velocity *= self.grow_decay
			
			self.xvel *= self.friction
			self.yvel *= self.friction
			
			self.image = pygame.Surface((self.radius*2,self.radius*2))
			self.image.set_colorkey((255,0,255))
			self.image.fill((255,0,255))
		
			pygame.draw.circle(self.image,self.color,(self.radius,self.radius),self.radius,self.fill)
		
			self.rect = self.image.get_rect()
			
			self.rect.center = (self.x,self.y)
			self.image.set_alpha(self.alpha)
			
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)

		
class ParticleRect(object):
	def __init__(self,x,y,**kwargs):
		# @param :kill_condition - is a two item tuple
		# at index 0 - a string (either 'time','alpha')
		# at index 1 - if index 0 == 'time' pass the max particle live time in milliseconds
		#			 - if index 1 == 'alpha' pass in the amount of alpha to subtract each tick
		#			 - will implement collision kill condition soon
		
		self.valid_kwargs = {			
			"xvel" : 0,
			"yvel" : 0,
			"friction" : 0.97,
			"gravity" : 0.06,
			"wind_direction" : 180,
			"wind_strength" : 0.0,
			"size" : 4,
			"color" : (255,0,0),
			"kill_condition" : ("time",5000),
			"fill" : 0
		}
		
		for key,val in kwargs.items():
			if self.valid_kwargs.has_key(key):
				self.valid_kwargs[key] = val
			else:
				# raise exception
				raise Exception("invalid attribute %s has been referenced" % key)
		# set atrributes
		for key,val in self.valid_kwargs.items():
			setattr(self,key,val)
			
		self.x = x
		self.y = y
		self.alive = True
		
		self.acctime = 0
		self.alpha = 255
		
		self.image = pygame.Surface((self.size,self.size))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		pygame.draw.rect(self.image,self.color,(0,0,self.size,self.size),self.fill)
		
		self.rect = self.image.get_rect()
		self.rect.center = (self.x,self.y)
		
	def update(self,timepassed):
		
		if self.alive:
		
			if self.kill_condition[0] == "time":
				self.acctime += timepassed
			
				if self.acctime > self.kill_condition[1]:
					self.alive = False
		
			elif self.kill_condition[0] == "alpha":
				self.alpha -= self.kill_condition[1]
				
				if self.alpha < 0:
					self.alpha = 0
					self.alive = False
			
			# calculate wind_direction as a vector
			
			angle = self.wind_direction	
			vec_x = math.cos((angle * (math.pi/180)))
			vec_y = math.sin((angle * (math.pi/180)))
						
			vec_x *= self.wind_strength
			vec_y *= self.wind_strength
						
			self.xvel += vec_x
			self.yvel += vec_y
			
			self.yvel += self.gravity
			
			self.x += self.xvel
			self.y += self.yvel
			
			self.xvel *= self.friction
			self.yvel *= self.friction
			
			self.rect.center = (self.x,self.y)
			self.image.set_alpha(self.alpha)
			
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)

class ParticleRectLerp(object):
	def __init__(self,x,y,**kwargs):
		# @param :kill_condition - is a two item tuple
		# at index 0 - a string (either 'time','alpha')
		# at index 1 - if index 0 == 'time' pass the max particle live time in milliseconds
		#			 - if index 1 == 'alpha' pass in the amount of alpha to subtract each tick
		#			 - will implement collision kill condition soon
		
		self.valid_kwargs = {			
			"xvel" : 0,
			"yvel" : 0,
			"friction" : 0.97,
			"size" : 4,
			"start_color" : (255,0,0),
			"end_color" : (200,255,0),
			"change" : 0.01,
			"gravity" : 0.0,
			"wind_direction" : 180,
			"wind_strength" : 0.0,
			"kill_condition" : ("alpha",2),
			"fill" : 0
		}
		
		for key,val in kwargs.items():
			if self.valid_kwargs.has_key(key):
				self.valid_kwargs[key] = val
			else:
				# raise exception
				raise Exception("invalid attribute %s has been referenced" % key)
		# set atrributes
		for key,val in self.valid_kwargs.items():
			setattr(self,key,val)
		
		self.x = x
		self.y = y
		self.alive = True
		self.factor = 0.0
		self.color = self.start_color
		
		self.acctime = 0
		self.alpha = 255
		
		self.image = pygame.Surface((self.size,self.size))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		pygame.draw.rect(self.image,self.color,(0,0,self.size,self.size),self.fill)
		
		self.rect = self.image.get_rect()
		self.rect.center = (self.x,self.y)
		
	def update(self,timepassed):
		
		if self.alive:
		
			if self.kill_condition[0] == "time":
				self.acctime += timepassed
			
				if self.acctime > self.kill_condition[1]:
					self.alive = False
		
			elif self.kill_condition[0] == "alpha":
				self.alpha -= self.kill_condition[1]
				
				if self.alpha < 0:
					self.alpha = 0
					self.alive = False
			
			self.factor += self.change
			
			if self.factor > 1:
				self.factor = 1
				self.color = self.end_color
			else:	
				self.color = colorLerp(self.start_color,self.end_color,self.factor)
			
			# calculate wind_direction as a vector
			
			angle = self.wind_direction	
			vec_x = math.cos((angle * (math.pi/180)))
			vec_y = math.sin((angle * (math.pi/180)))
						
			vec_x *= self.wind_strength
			vec_y *= self.wind_strength
						
			self.xvel += vec_x
			self.yvel += vec_y
			
			self.yvel += self.gravity
			
			self.x += self.xvel
			self.y += self.yvel
			
			self.xvel *= self.friction
			self.yvel *= self.friction
			
			self.image = pygame.Surface((self.size,self.size))
			self.image.set_colorkey((255,0,255))
			self.image.fill((255,0,255))
		
			pygame.draw.rect(self.image,self.color,(0,0,self.size,self.size),self.fill)
		
			self.rect = self.image.get_rect()
			
			self.rect.center = (self.x,self.y)
			self.image.set_alpha(self.alpha)
			
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)

		
class ParticleEmitter(object):
	def __init__(self,x,y,**kwargs):
		# param direction : 'left','right','top','bottom','random'
		# param emit_mode : a tuple of two items
		#					- index 0 can be a string; either "burst" or "stream"
		# if burst : index 1 is the number of intermidiary milliseconds till next burst or None(trigger no extra burst) 
		# if stream : index 1 is the number of intermidiary milliseconds till next particle emission
		
		self.valid_kwargs = {			
			"mode" : ('burst',3000),
			"direction": 'random',
			"particle_type" : ParticleRectLerp,
			"max_variance" : 20,
			"friction" : 0.93,
			"strength" : 1.4,
			"kill_condition" : ("alpha",3)
		}
		
		for key,val in kwargs.items():
			if self.valid_kwargs.has_key(key):
				self.valid_kwargs[key] = val
			else:
				# raise exception
				raise Exception("invalid attribute %s has been referenced" % key)
		# set atrributes
		for key,val in self.valid_kwargs.items():
			setattr(self,key,val)
		
		self.x = x
		self.y = y
		self.particle_list = []
		self.emit_mode = self.mode[0]
		self.updatetime = self.mode[1]
		self.acctime = self.updatetime 
		self.emit = True
		self.alive = True
		
	def burst(self,num_particles=10):
		"""Releases a set number of particles in an instant"""
		for i in range(num_particles):
			
			if self.direction == "random":
				angle = random.randint(0,360)
				vec_x = math.cos((angle * (math.pi/180)))
				vec_y = math.sin((angle * (math.pi/180)))
						
				vec_x *= self.strength
				vec_y *= self.strength
						
				new_particle = self.particle_type(self.x,self.y,xvel=vec_x,yvel=vec_y,friction=self.friction,kill_condition=self.kill_condition)
				self.particle_list.append(new_particle)
			
			else:
				angle = random.randrange(self.direction-self.max_variance,self.direction+self.max_variance)
				vec_x = math.cos((angle * (math.pi/180)))
				vec_y = math.sin((angle * (math.pi/180)))
						
				vec_x *= self.strength
				vec_y *= self.strength
						
				new_particle = self.particle_type(self.x,self.y,xvel=vec_x,yvel=vec_y,friction=self.friction,kill_condition=self.kill_condition)
				self.particle_list.append(new_particle)
			
			
	def update(self,timepassed):
		
		if self.emit:
			
			self.acctime += timepassed
			
			if self.acctime > self.updatetime:
				self.acctime = 0
				
				# add new particles
				if self.emit_mode == "stream":
					
					if self.direction == "random":
						angle = random.randint(0,360)
						vec_x = math.cos((angle * (math.pi/180)))
						vec_y = math.sin((angle * (math.pi/180)))
						
						vec_x *= self.strength
						vec_y *= self.strength
						
						new_particle = self.particle_type(self.x,self.y,xvel=vec_x,yvel=vec_y,kill_condition=self.kill_condition)
						self.particle_list.append(new_particle)
					
					else:
						angle = random.randrange(self.direction-self.max_variance,self.direction+self.max_variance)
						vec_x = math.cos((angle * (math.pi/180)))
						vec_y = math.sin((angle * (math.pi/180)))
						
						vec_x *= self.strength
						vec_y *= self.strength
						x = random.randrange(self.x-16,self.x+16)
						new_particle = self.particle_type(x,self.y,xvel=vec_x,yvel=vec_y,friction=self.friction,kill_condition=self.kill_condition)
						self.particle_list.append(new_particle)
				
					
			for particle in self.particle_list:
				particle.update(timepassed)
				
			# delete dead particles
			for particle in self.particle_list:
				if not particle.alive:
					self.particle_list.remove(particle)
			
			if len(self.particle_list)<1:
				self.alive = False
			
	def draw(self,Surface):
		
		for particle in self.particle_list:
			particle.draw(Surface)