import pygame,math
from pygame.locals import*
from sgf.behaviours.steering_behaviours import*	
import sgf.utils.Vector2d as Vector2d

class Steerable(object):
	"""Basic object that supports easing behaviours"""
	def __init__(self,steer_type,pos,w,h,color=None):
		self.x,self.y = pos
		self.w = w
		self.h = h
		self.color = color
		
		self.rect = pygame.Rect(self.x,self.y,self.w,self.h)
		
		# STEERING VARIABLES(Eventually need to define getters, setters for these)
		self.position = Vector2d.Vector2()
		self.position.x = self.x
		self.position.y = self.y
		self.maxSpeed = 3.0
		self.orientation = 0.0
		self.velocity = Vector2d.Vector2()
		self.rotation = 0.0
		
		self.steer_type = steer_type
		
		# movement behaviours allowed for object
		self.movement_behaviours_dict = {
		
		"KSeekMovement" : KinematicSeek(self,None),
		"KFleeMovement" : KinematicFlee(self,None),
		"KArriveMovement" : KinematicArrive(self,None),
		"KWanderMovement" : KinematicWander(self),
		"DSeekMovement" : DynamicSeek(self,None),
		"DFleeMovement" : DynamicFlee(self,None),
		"DArriveMovement" : DynamicArrive(self,None),
		"DAlignMovement" : DynamicAlign(self,None),
		"DVelocityMatch" : DynamicVelocityMatch(self,None),
		"DPursueMovement" : Pursue(self,None),
		"DFaceMovement" : Face(self,None)
				}
		
		self.current_steering_behaviour = self.movement_behaviours_dict[self.steer_type]
		self.target = None
		
		# camera shake vars
		# x
		self.default_intensity_x = 4.0
		self.angle_x = 0
		self.shake_intensity_x = 4.0
		self.shake_speed_x = 80
		self.is_shaking_x = False
		self.shake_length_x = 0.3
		
		# y
		self.default_intensity_y = 4.0
		self.angle_y = 0
		self.shake_intensity_y = 4.0
		self.shake_speed_y = 80
		self.is_shaking_y = False
		self.shake_length_y = 0.3
	
	def __handleShake(self):
		"""Is called internally in the update method to handle camera shaking"""
		if not self.is_shaking_x:
			pass
			
		else:
			self.angle_x += self.shake_speed_x
			self.shake_intensity_x -= self.shake_length_x
			
			if self.shake_intensity_x >= -self.shake_length_x:
				self.x += self.shake_intensity_x * math.sin(self.angle_x *(math.pi/180))
			
			else:
				self.is_shaking_x = False
				self.shake_intensity_x = self.default_intensity_x
				#self.x = 0
				
		if not self.is_shaking_y:
			pass
			
		else:
			self.angle_y += self.shake_speed_y
			self.shake_intensity_y -= self.shake_length_y
			
			if self.shake_intensity_y >= -self.shake_length_y:
				self.y += self.shake_intensity_y * math.cos(self.angle_y *(math.pi/180))
			
			else:
				self.is_shaking_y = False
				self.shake_intensity_y = self.default_intensity_y
				#self.y = 0
				
	###
	# x_params : list containing [shake_intensity_x ,shake_speed_x,shake_length_x ] or None if no x axis shake required
	# y_params : list containing [shake_intensity_y ,shake_speed_y,shake_length_y ] or None if no x axis shake required
	# shake_intensity should be a float usually between 1.0 - 10.0 is good
	# shake_speed an int or float (is practically an angle - 80 is good figure for it)
	# shake_length : is a float describing how much we reduce the intensity by(therefore it affect how long the effect spans in time)
	
	def shake(self,x_params,y_params):
		
		if x_params != None: # and not self.is_shaking_x:
			self.angle_x = 0
			self.shake_intensity_x = x_params[0]
			self.shake_speed_x = x_params[1]
			self.shake_length_x = x_params[2]
			self.is_shaking_x = True
			#self.x -= (((self.shake_intensity_x - self.shake_length_x) * math.sin(self.angle_x + self.shake_speed_x *(math.pi/180)))/self.shake_length_x)
			
			# calculate the offset shaking creates and subtract so we dont offset the surface
	
			start_pos = 0
			for i in range(100):
				self.angle_x += self.shake_speed_x
				self.shake_intensity_x -= self.shake_length_x
			
				if self.shake_intensity_x >= -self.shake_length_x:
					shake_val = self.shake_intensity_x * math.sin(self.angle_x *(math.pi/180))
					
					start_pos += shake_val
				else:
					break
					
			# reset
			self.angle_x = 0
			self.shake_intensity_x = x_params[0]
			self.shake_speed_x = x_params[1]
			self.shake_length_x = x_params[2]
			self.is_shaking_x = True
			
			self.x -= start_pos
			
		if y_params != None: # and not self.is_shaking_y:
			self.angle_y = 0
			self.shake_intensity_y = y_params[0]
			self.shake_speed_y = y_params[1]
			self.shake_length_y = y_params[2]
			self.is_shaking_y = True
			#self.y -= (((self.shake_intensity_y - self.shake_length_y) * math.cos(self.angle_y + self.shake_speed_y *(math.pi/180)))/2)
			
			# calculate the offset shaking creates and subtract so we dont offset the surface
	
			start_pos = 0
			for i in range(100):
				self.angle_y += self.shake_speed_y
				self.shake_intensity_y -= self.shake_length_y
			
				if self.shake_intensity_y >= -self.shake_length_y:
					shake_val = self.shake_intensity_y * math.cos(self.angle_y *(math.pi/180))
					
					start_pos += shake_val
				else:
					break
			
			# reset
			self.angle_y = 0
			self.shake_intensity_y = y_params[0]
			self.shake_speed_y = y_params[1]
			self.shake_length_y = y_params[2]
			self.is_shaking_y = True
			self.y -= start_pos
	
	def setTarget(self,target):
		self.current_steering_behaviour.target = target
	
	def updateSteering(self):
	
		self.steering=self.current_steering_behaviour.getSteering()
		
		if self.steering != None:
			# this is for kinematic movement only
			self.position += self.steering.velocity
			self.orientation += self.steering.rotation
		
		self.position += self.velocity
		self.orientation += self.rotation
		
		if self.steering != None:
			self.velocity += self.steering.linear
			self.orientation += self.steering.angular
		
		if self.velocity.get_magnitude() > self.maxSpeed:
			self.velocity.normalize()
			self.velocity *= self.maxSpeed
	
		self.x = self.position.x
		self.y = self.position.y
	
	def draw(self,Surface):
		if self.color != None:
			# draw a filled rect
			pygame.draw.rect(Surface,self.color,self.rect)
			
	def update(self,timepassed):
		
		self.position.x = self.x
		self.position.y = self.y
		
		self.updateSteering()
		
		self.__handleShake()
		
		self.rect.topleft = (self.x,self.y)