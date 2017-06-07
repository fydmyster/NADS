import pygame,random,types,textwrap
from pygame.locals import*
from sgf.behaviours.steering_behaviours import*
from sgf.behaviours.easing_behaviours import*
from sgf.utils.g_utils import*
import sgf.utils.Vector2d as Vector2d

from tween_objects import*
from sgf.collision.sat_collision import*
#from sgf.ui.ui_objects import*	# avoid circular import dependencies for now (seems to be spawning bugs im not capable of diagnosing at this stage)
#import sgf.ui.ui_objects as u		

# Not compatible with room editor use
class BackgroundImage(object):
	def __init__(self,filename,x=0,y=0):
		"""Basic wrapper class that encapsulates an image surface used for parallax scrolling
		mainly for partnered use with the CameraHandler intances
		filename -> string that contains the path to the image
		use only with per pixel alpha images"""
		self.image = pygame.image.load(filename).convert_alpha()
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
	
	def centerTo(self,rect):
		"""Adjusts the BackgroundImage objects position to align centers with the passed in rect"""
		# get rect's center
		cx, cy = rect.center
		
		# calculate new position for bg
		new_x = cx - (self.rect.w / 2.0)
		new_y = cy - (self.rect.h / 2.0)
		
		self.x = new_x
		self.y = new_y
		
	def draw(self,Surface):
		Surface.blit(self.image,self.rect)
		
	def update(self,timepassed):
		self.rect.topleft = (self.x,self.y)
		
		
#####
# ImageObject param_list structure is as follows:
# [image_filename,load_style]
# param : image_filename can either be a string of the image filename or a list of one image surface
# param : load_style can be a string containing either 'normal', 'colorkey', or 'alpha'; or the value None
# pass None to load_style if the first index of param_list is a list containing an image
# NOTE: Very compatible with room editor use

class ImageObject(object):
	def __init__(self,param_list,x=0,y=0):
		"""Basic image class with barebones functionality"""
		
		self.x = x
		self.y = y
		
		self.param_list = param_list
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		# do some type checking
		if type(self.param_list[0]) == types.StringType:
			# passed in filename ; use pygame image load function
			if self.param_list[1] == "normal":
				self.image = pygame.image.load(self.param_list[0]).convert()
				
			elif self.param_list[1] == "colorkey":
				self.image = pygame.image.load(self.param_list[0]).convert()
				self.image.set_colorkey((255,0,255))
				
			elif self.param_list[1] == "alpha":
				self.image = pygame.image.load(self.param_list[0]).convert_alpha()
			
		elif type(self.param_list[0]) == types.ListType:
			# passed in list containing single surface
			self.image = self.param_list[0][0]
			
		self.rect = self.image.get_rect()
		
		self.updatePosition(0)
		
	def updatePosition(self,timepassed):
		self.rect.topleft = (self.x,self.y)
		
	def update(self,timepassed):
		"""updates the image position"""
		self.updatePosition(timepassed)
		
	def draw(self,Surface):
		"""Draws the image to specified Surface"""
		Surface.blit(self.image,self.rect)

# NOTE: Very compatible with room editor use		
class SpriteObject(object):
	def __init__(self,imageloader_func,x=0,y=0):
		
		self.x = x
		self.y = y
		
		# param : imageloader_func can be either a list of surfaces or a loader function for the images
		
		# master images should be a list containing lists of surfaces
		# the first item in master_images should contain the starting image(s) of the sprite
		
		self.imageloader_func = imageloader_func
		
		# do some type checking
		if type(self.imageloader_func) == types.FunctionType:
			self.master_images = self.imageloader_func()
			#print "load from function"
			
		elif type(self.imageloader_func) == types.ListType:
			self.master_images = self.imageloader_func
			#print "load from list"
		
		# IMAGE AND BLENDING VARIABLES
		self.image = self.master_images[0][0]
		self.blendimage = self.image.copy()
		self.blendtype = BLEND_MAX			# BLEND_ADD : changes the palette; BLEND_MAX : paints entire image a single color wash
		self.blendcolor = None
		self.color_mode = None				# Dictates whether to use 'colorize' or 'alter' draw modes
		self.colorize_alpha = 255
		
		self.alpha = 255
		
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.x,self.y)
		
		# ANIM VARIABLES
		
		self.current_imagelist = self.master_images[0]
		self.frame = 0
		self.acctime = 0 
		self.fps = 12.0
		self.updatetime = 1000/self.fps
		self.cur_animloops = None
		self.anim_started = False
		
		# STEERING VARIABLES
		self.position = Vector2d.Vector2()
		self.position.x = self.x
		self.position.y = self.y
		self.maxSpeed = 3.0
		self.orientation = 0.0
		self.velocity = Vector2d.Vector2()
		self.rotation = 0.0
		
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
		
		# easing behaviours allowed for object
		self.easing_behaviours_dict = {
		
		"EInQuad" : EaseInQuad(self),
		"EOutQuad" : EaseOutQuad(self),
		"EInOutQuad" : EaseInOutQuad(self),
		"EInSin" : EaseInSin(self),
		"EOutSin" : EaseOutSin(self),
		"EInOutSin" : EaseInOutSin(self),
		"EInExpo" : EaseInExpo(self),
		"EOutExpo" : EaseOutExpo(self),
		"EInOutExpo" : EaseInOutExpo(self),
		"EInCirc" : EaseInCirc(self),
		"EOutCirc" : EaseOutCirc(self),
		"EInOutCirc" : EaseInOutCirc(self),
		"EInElastic" : EaseInElastic(self),
		"EOutElastic" : EaseOutElastic(self)
				}
		
		self.move_to_x = None
		self.move_to_y = None
		self.move_duration = None
		self.new_position = None		# this value is None if moveTo positions are reached
		
		self.current_steering_behaviour = None
		self.current_easing_behaviour = None
		
		# WAVE MOTION VARS
		self.y_motion_enabled = False
		self.x_motion_enabled = False
		self.xy_motion_enabled = False
		
		self.wave_angle = 0
		self.wave_speed = 5
		self.wave_strength = 3
		
		# VISIBILITY AND BLINKING VARS
		self.is_visible = True
		self.blink_acctime = 0
		self.blink_waittime = None		# time between visibilty toggles
		self.is_blinking = False
		
		# COLORIZE FLASHING AND BLINK VARS
		self.flash_color = None
		self.flash_on = False
		self.flash_acctime = 0
		self.flash_waittime = None		# time between flash toggles
		self.is_flashing = False
		
		# COLLISION VARS
		self.rect_SAT = None
		self.assoc_rect = None		# The rect the rect_SAT derives from
		
	def createRectSAT(self,rect):
		"""Creates a SAT collsion rect from an existing pygame rect"""
		param_list = [rect.width,rect.height,(0,0,120)]
		self.rect_SAT = RectSAT(param_list,self.x,self.y)
		self.assoc_rect = rect
		
	def updateRectSAT(self):
		"""Creates a SAT collsion rect from an existing pygame rect"""
		self.rect_SAT.x = self.assoc_rect.x
		self.rect_SAT.y = self.assoc_rect.y
		
		self.rect_SAT.update(0)		# pass in a dummy timepassed value
		
	def setBlendMode(self,blendtype):
		"""Declares the blend mode used on image"""
		self.blendtype = blendtype
	
	def setBlendColor(self,color,mode = "alter"):
		"""Sets the blend color used on image and enable all blending and colorize functionality"""
		# mode can be either 'colorize' or 'alter'  
		
		self.blendcolor = color
		self.color_mode = mode
		
	def clearBlendColor(self):
		"""Removes the blend color used on image"""
		self.blendcolor = None
		self.color_mode = None
		self.colorize_alpha = 255
	
	def toggleVisibility(self):
		"""Toggles the sprites visibilty"""
		self.is_visible = not(self.is_visible)
	
	def toggleFlash(self):
		"""Toggles the sprites flash state"""
		self.flash_on = not(self.flash_on)
		
		if self.flash_on == True:
			# set blendcolor
			self.setBlendColor(self.flash_color,"colorize")
			
		elif self.flash_on == False:
			self.clearBlendColor()
	
	def blink(self,timepassed):
		
		self.blink_acctime += timepassed
			
		if self.blink_acctime > self.blink_waittime:
			# toggle visibilty
			self.toggleVisibility()
			self.blink_acctime = 0
	
	def flash(self,timepassed):
		self.flash_acctime += timepassed
			
		if self.flash_acctime > self.flash_waittime:
			# toggle visibilty
			self.toggleFlash()
			self.flash_acctime = 0
	
	def enableBlinking(self,waittime):
		self.is_blinking = True
		self.blink_waittime = waittime
	
	def enableFlashing(self,waittime,flash_color):
		self.flash_color = flash_color
		self.is_flashing = True
		self.flash_waittime = waittime
	
	def disableBlinking(self):
		self.is_blinking = False
		self.blink_waittime = None
		# set visibilty to On
		self.is_visible = True
	
	def disableFlashing(self):
		self.is_flashing = False
		self.flash_waittime = None
		# set flash state to Off
		self.flash_on = False
		self.flash_color = None
		self.clearBlendColor()
	
	def enableSteeringBehaviour(self,behaviour,target):
		"""Sets a steering mode and a target"""
		# pass a string which will be used as a key to the movement_behaviours_dict
		self.current_steering_behaviour = self.movement_behaviours_dict[behaviour]
		self.current_steering_behaviour.target = target
		
	def disableSteeringBehaviour(self):
		"""Disables behavioural steering"""
		self.current_steering_behaviour = None
	
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
	
	def moveTo(self,behaviour,x_offset,y_offset,duration):
		"""Sets a easing mode and a position to move to"""
		# pass a string which will be used as a key to the easing_behaviours_dict
		self.current_easing_behaviour = self.easing_behaviours_dict[behaviour]
		self.current_easing_behaviour.reInit()
		
		self.move_to_x = x_offset
		self.move_to_y = y_offset
		self.move_duration = duration
		
	def disableEasingBehaviour(self):
		"""Disables behavioural steering"""
		self.current_easing_behaviour = None
	
	def updateEasing(self,timepassed):
		
		self.new_position = self.current_easing_behaviour.getEasing(self.move_to_x,self.move_to_y,self.move_duration,timepassed)
		
		if self.new_position == None:
			# moveTo position has been reached; disable the easing behaviour
			self.disableEasingBehaviour()
			
	def enableOscillate(self,axis="y",strength=5,speed=5):
		"""Enable wavey motion"""
		# axis can be a string ; either "x" , "y" or "xy"
		if axis == "x":
			self.x_motion_enabled = True
			self.y_motion_enabled = False
			self.xy_motion_enabled = False
		
		elif axis == "y":
			self.x_motion_enabled = False
			self.y_motion_enabled = True
			self.xy_motion_enabled = False
		
		elif axis == "xy":
			self.x_motion_enabled = False
			self.y_motion_enabled = False
			self.xy_motion_enabled = True
		
		self.wave_strength = strength
		self.wave_speed = speed
	
	def disableOscillate(self):
		self.x_motion_enabled = False
		self.y_motion_enabled = False
		self.xy_motion_enabled = False
		
		
	def animateSprite(self,imagelist,timepassed):
		
		if self.current_imagelist != imagelist or self.current_imagelist == None:
			# current_imagelist has changed
			# reset self.frame
			self.frame = 0 
			self.acctime = 0
		
		# set current_imagelist to the current animation
		self.current_imagelist = imagelist
		
		self.acctime += timepassed
		
		if self.acctime > self.updatetime:
			self.acctime = 0
			# go to next frame
			self.frame = (self.frame + 1) % len(self.current_imagelist)
	
	def animateSpriteLoop(self,imagelist,timepassed,num_loops=3):
		
		if not self.anim_started:
			self.cur_animloops = num_loops
			self.anim_started = True
			
		if self.current_imagelist != imagelist or self.current_imagelist == None:
			# current_imagelist has changed
			# reset self.frame
			self.frame = 0 
			self.acctime = 0
		
		if self.anim_started:
			# set current_imagelist to the current animation
			self.current_imagelist = imagelist
		
			self.acctime += timepassed
		
			if self.acctime > self.updatetime:
				self.acctime = 0
				# go to next frame
				self.frame += 1
			
			if self.frame > len(self.current_imagelist)-1:
				self.cur_animloops -= 1
				self.frame = 0
				
			if self.cur_animloops == 0:
				self.anim_started=False
	
	def updatePosition(self,timepassed):
		
		if self.x_motion_enabled:
			self.wave_angle += self.wave_speed
			self.x += self.wave_strength * math.cos(self.wave_angle * (math.pi/180))
		
		elif self.y_motion_enabled:
			self.wave_angle += self.wave_speed
			self.y += self.wave_strength * math.sin(self.wave_angle * (math.pi/180))
		
		elif self.xy_motion_enabled:
			self.wave_angle += self.wave_speed
			self.x += self.wave_strength * math.cos(self.wave_angle * (math.pi/180))
			self.y += self.wave_strength * math.sin(self.wave_angle * (math.pi/180))
		
		self.position.x = self.x
		self.position.y = self.y
		
		if self.current_steering_behaviour != None:
			self.updateSteering()
		
		if self.current_easing_behaviour != None:
			self.updateEasing(timepassed)
		
		self.rect.x = self.x
		self.rect.y = self.y
		
		if self.rect_SAT != None:
			self.updateRectSAT()
	
	def update(self,timepassed):
		"""Call this at the end of the child class update method"""
		# set sprite image
		self.image = self.current_imagelist[self.frame]
		#self.blendimage = self.image.copy()
		
		self.image.set_alpha(self.alpha)
		
		if self.is_blinking:
			self.blink(timepassed)
		
		if self.is_flashing:
			self.flash(timepassed)
		
		# update position
		self.updatePosition(timepassed)
		
	def draw(self,Surface):	
		"""Draws sprite to given Surface"""
		
		if self.blendcolor != None:
			# only use this draw mode if blend mode has been set with setBlendColor()
			if self.color_mode == "alter":
	
				# A color is assigned to blendcolor; so use this to alter image color 
				self.blendimage = self.image.copy()
				self.blendimage.fill(self.blendcolor, None, self.blendtype)
				
				if self.is_visible:
					Surface.blit(self.blendimage,self.rect)
			
			elif self.color_mode == "colorize":
				self.blendimage = self.image.copy()
				self.blendimage.fill((0,0,0,self.colorize_alpha), None, BLEND_RGBA_MULT)
				self.blendimage.fill(self.blendcolor[0:3] + (0,), None, BLEND_RGBA_ADD)
				
				if self.is_visible:
					Surface.blit(self.image,self.rect)
					Surface.blit(self.blendimage,self.rect)
			
		else:
			# blit as normal without blend modes
			if self.is_visible:
				Surface.blit(self.image,self.rect)
			else:
				pass
		
		# remove this shit later
		if self.rect_SAT != None:
			self.rect_SAT.draw(Surface)
		
		
#####
# AnimObject param_list structure is as follows:
# [imageloader_func,loops,fps]
# param : imageloader_func can either be a function that returns the imagelist or a list of images
# param : loops can be an int > 0 indicating number of loops ; or -1 indicating an infinite playback
# NOTE: Very compatible with room editor use

class AnimObject(object):
	def __init__(self,param_list,x,y,xvel=0,yvel=0,friction=0.97,collidable=False,collisiontype=None):
		self.x = x
		self.y = y
		self.param_list = param_list
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		# do some type checking
		if type(self.param_list[0]) == types.FunctionType:
			self.frameImages = self.param_list[0]()
			#print "load from function"
			
		elif type(self.param_list[0]) == types.ListType:
			self.frameImages = self.param_list[0]
			#print "load from list"
		
		self.numLoops = self.param_list[1]
		self.fps = self.param_list[2]
		
		self.frame=0
		self.collisiontype=collisiontype
		self.collidable=collidable		
		self.xvel=xvel
		self.yvel=yvel
		self.friction=friction
		
		self.alive=True
		self.image=self.frameImages[self.frame]
		self.rect= self.image.get_rect()
		
		self.numIteration=0
		self.frameCounter=0
		
		self.acctime=0
		self.updateframetime=1000/self.fps
		
	def play(self,timepassed):
		
		if self.alive:
		
			self.acctime+=timepassed
		
			if self.acctime > self.updateframetime:
				if self.numLoops == -1:
					# infinite loop animation
					self.frame = (self.frame + 1) % len(self.frameImages)
					self.acctime=0
			
				elif self.numLoops>0:
					# play for a set number of loop times
					if self.frameCounter >= len(self.frameImages)-1:
						self.numIteration+=1
						self.frameCounter=0
				
					if self.numIteration < self.numLoops:
						self.frame = (self.frame + 1) % len(self.frameImages)
						self.frameCounter+=1
						self.acctime=0
					else:
						#self.frame=len(self.frameImages)-1
						self.alive=False
	
	def updatePosition(self,timepassed):
		self.rect.topleft = (self.x,self.y)
	
	def update(self,timepassed):
		
		# cycle through the frames
		self.play(timepassed)
		
		self.image=self.frameImages[self.frame]
		
		self.x+=self.xvel
		self.y+=self.yvel
		
		self.xvel*=self.friction
		self.yvel*=self.friction
		
		# update position
		self.updatePosition(timepassed)
		
	def draw(self,Surface):
		"""Draws sprite to given Surface"""
		Surface.blit(self.image,self.rect)

# NOTE: Not compatible with room editor use
class AnimEmitter(object):
	def __init__(self,spriteSheet,x=0,y=0,xvel=0,yvel=0,fps=5,numParticles=5,friction=0.94,addParticleTime=100,collidable=False,collisiontype=None):
		self.x = x
		self.y = y
		self.xvel=xvel
		self.yvel=yvel
		self.collidable=collidable
		self.collisiontype=collisiontype
		self.spriteSheet=spriteSheet
		self.fps=fps
		self.acctime=0
		self.numParticles=numParticles
		self.addedParticles=0
		self.alive=True
		self.addParticleTime=addParticleTime
		self.particleList=[]
		self.friction=friction
		
	def update(self,timepassed):
		if self.alive:
			self.acctime+=timepassed
			
			if self.addParticleTime!=0:
			
				if self.acctime>self.addParticleTime:
				
					if self.numParticles>0:
						if self.xvel !=0 and self.yvel==0:
							randyvel=random.choice(range(-3,3))
							newParticle=AnimObject([self.spriteSheet,1,self.fps],self.x,self.y,self.xvel,randyvel,self.friction,collidable=self.collidable,collisiontype=self.collisiontype)
							
						elif self.yvel !=0 and self.xvel==0:
							randxvel=random.choice(range(-3,3))
							newParticle=AnimObject([self.spriteSheet,1,self.fps],self.x,self.y,randxvel,self.yvel,self.friction,collidable=self.collidable,collisiontype=self.collisiontype)
							
						elif self.yvel !=0 and self.xvel!=0:
							randxvel=random.choice(range(-3,3))
							newParticle=AnimObject([self.spriteSheet,1,self.fps],self.x,self.y,self.xvel,self.yvel,self.friction,collidable=self.collidable,collisiontype=self.collisiontype)
						
						else:
							randxvel=random.choice(range(-3,3))
							randyvel=random.choice(range(-3,3))
							newParticle=AnimObject([self.spriteSheet,1,self.fps],self.x,self.y,randxvel,randyvel,friction=self.friction,collidable=self.collidable,collisiontype=self.collisiontype)
						self.particleList.append(newParticle)
						self.numParticles-=1
			
						self.acctime=0
			
			else:
				# add particles in one go
				if self.numParticles>0:
					for i in range(self.numParticles):
						tempAdditive=(random.randint(0,200))/1000
						basefriction=0.96
							
						randfriction=basefriction+tempAdditive
						randfps=random.randint(7,12)			# I might consider dropping randfps; its counter-intuitive
						randxvel=random.choice(range(-3,3))
						randyvel=random.choice(range(-3,3))
						newParticle=AnimObject([self.spriteSheet,1,randfps],self.x,self.y,randxvel,randyvel,friction=randfriction)
						self.particleList.append(newParticle)
			
					self.numParticles=0
					
			for particle in self.particleList:
				if not particle.alive:
					self.particleList.remove(particle)
				
			if self.numParticles <=0 and len(self.particleList)==0:
				self.alive=False
		
		for particle in self.particleList:
			particle.update(timepassed)
		
		
	def draw(self,Surface):
	
		for particle in self.particleList:
			particle.draw(Surface)

			
class MasterSurface(object):
	"""Surface that supports transitions and stuff"""
	def __init__(self,width,height,window,x=0,y=0): 
		"""width and height should only be slightly larger than the progams window"""
		self.x = x 
		self.y = y
		self.width = width
		self.height = height
		self.window = window
		
		self.master_surface = pygame.Surface((self.width,self.height))
		self.surface_overlay = pygame.Surface((self.width,self.height))
		
		# create a master surface and an overlay one we draw transition effects on
		self.master_surface_rect = self.master_surface.get_rect()
		self.master_surface_rect.topleft = (self.x,self.y)
		#self.master_surface.set_colorkey((255,0,255))
		
		self.surface_overlay_rect = self.surface_overlay.get_rect()
		self.surface_overlay.set_colorkey((255,0,255))
		self.surface_overlay.fill((255,0,255))
		
		# helper variable used to check if transition still running
		self.in_transition = False 
		
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
		
	def handleShake(self):
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
		
		if x_params != None and not self.is_shaking_x:
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
			
		if y_params != None and not self.is_shaking_y:
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
			
			
	def clearSurface(self):
		"""Call this before any draw calls to the surface once per game tick"""
		self.master_surface.fill((0,0,0))
		#self.surface_overlay.fill((255,0,255))
	
	def update(self,timepassed):
	
		self.handleShake()
		
		self.master_surface_rect.topleft=(self.x,self.y)
		
	def draw(self):
		"""Surface must be a top level surface(the main window)"""
		self.window.blit(self.master_surface,self.master_surface_rect)
		self.window.blit(self.surface_overlay,self.surface_overlay_rect)
		
	def fadeIn(self,color,duration):
		"""Uses a fade in on the surface_overlay"""
		self.in_transition = True
		alpha = 255
		bg_color = color
		clock = pygame.time.Clock()
		timepassed = 0
		time_since_start = 0.0
		fade_duration = duration
		bg_surface = pygame.Surface((self.width,self.height))
		bg_rect = bg_surface.get_rect()
		bg_surface.fill(bg_color)
		
		while self.in_transition:
			
			time_since_start += timepassed
			
			ratio = time_since_start / duration
			
			if ratio <= 1:
				cur_alpha = alpha * ratio
			else:
				self.in_transition = False
				self.started_fade_in = False
				# return value to show we are done
				return 1
				
			#print cur_alpha
			
			# clear the overlay surface
			self.surface_overlay.fill((255,0,255))
			
			self.surface_overlay.set_alpha(int(cur_alpha))
			
			# draw onto overlay
			self.surface_overlay.blit(bg_surface,bg_rect)
			self.draw()
			
			pygame.display.update()
			timepassed = clock.tick(45)
			
	def fadeOut(self,color,duration):
		"""Uses a fade in on the surface_overlay"""
		self.in_transition = True
		alpha = 255
		bg_color = color
		clock = pygame.time.Clock()
		timepassed = 0
		time_since_start = 0.0
		fade_duration = duration
		bg_surface = pygame.Surface((self.width,self.height))
		bg_rect = bg_surface.get_rect()
		bg_surface.fill(bg_color)
		
		while self.in_transition:
			
			time_since_start += timepassed
			
			ratio = time_since_start / duration
			
			if ratio <= 1:
				neg_alpha = alpha * ratio
				cur_alpha = alpha - neg_alpha
			else:
				self.in_transition = False
		
				# return value to show we are done
				return 1
				
			#print cur_alpha
			
			# clear the overlay surface
			self.surface_overlay.fill((255,0,255))
			
			self.surface_overlay.set_alpha(int(cur_alpha))
			
			# draw onto overlay
			self.surface_overlay.blit(bg_surface,bg_rect)
			self.draw()
			pygame.display.update()
			timepassed = clock.tick(45)
			
	def shutterInX(self,color,duration,easing_function):
		"""Draws a shutter closing in effect on the surface_overlay"""
		self.in_transition = True
		bg_color = color
		clock = pygame.time.Clock()
		timepassed = 0
		time_since_start = 0.0
		fade_duration = duration
		left_shutter = Tweenable((0,0),self.width/2,self.height,bg_color)
		right_shutter = Tweenable((0,0),self.width/2,self.height,bg_color)
		
		left_shutter.rect.topright = (0,0)
		right_shutter.rect.topleft = (self.width,0)
		
		while self.in_transition:
			
			getattr(left_shutter,easing_function)(0,0,fade_duration,timepassed)
			getattr(right_shutter,easing_function)(self.width/2,0,fade_duration,timepassed)
					
			if not left_shutter.startSet and not left_shutter.startSet:
				self.in_transition = False
		
				# return value to show we are done
				return 1
				
			# clear the overlay surface
			self.surface_overlay.fill((255,0,255))
			
			# draw onto overlay
			left_shutter.draw(self.surface_overlay)
			right_shutter.draw(self.surface_overlay)
			
			self.draw()
			pygame.display.update()
			timepassed = clock.tick(45)
			
	def shutterOutX(self,color,duration,easing_function):
		"""Draws a shutter closing in effect on the surface_overlay"""
		self.in_transition = True
		bg_color = color
		clock = pygame.time.Clock()
		timepassed = 0
		time_since_start = 0.0
		fade_duration = duration
		left_shutter = Tweenable((0,0),self.width/2,self.height,bg_color)
		right_shutter = Tweenable((0,0),self.width/2,self.height,bg_color)
		
		left_shutter.rect.topleft = (0,0)
		right_shutter.rect.topleft = (self.width/2,0)
		
		while self.in_transition:
			
			getattr(left_shutter,easing_function)(-left_shutter.rect.width,0,fade_duration,timepassed)
			getattr(right_shutter,easing_function)(self.width,0,fade_duration,timepassed)
					
			if not left_shutter.startSet and not left_shutter.startSet:
				self.in_transition = False
		
				# return value to show we are done
				return 1
				
			# clear the overlay surface
			self.surface_overlay.fill((255,0,255))
			
			# draw onto overlay
			left_shutter.draw(self.surface_overlay)
			right_shutter.draw(self.surface_overlay)
			
			
			self.draw()
			pygame.display.update()
			timepassed = clock.tick(45)
	
	def shutterInY(self,color,duration,easing_function):
		"""Draws a shutter closing in effect on the surface_overlay"""
		self.in_transition = True
		bg_color = color
		clock = pygame.time.Clock()
		timepassed = 0
		time_since_start = 0.0
		fade_duration = duration
		#top_shutter = Tweenable((0,0),self.width,self.height/2,bg_color,["images\\face.png","alpha"])
		top_shutter = Tweenable((0,0),self.width,self.height/2,bg_color)
		bottom_shutter = Tweenable((0,0),self.width,self.height/2,bg_color)
		
		top_shutter.rect.bottomleft = (0,0)
		bottom_shutter.rect.topleft = (0,self.height)
		
		while self.in_transition:
			
			getattr(top_shutter,easing_function)(0,0,fade_duration,timepassed)
			getattr(bottom_shutter,easing_function)(0,self.height/2,fade_duration,timepassed)
					
			if not top_shutter.startSet and not bottom_shutter.startSet:
				self.in_transition = False
		
				# return value to show we are done
				return 1
				
			# clear the overlay surface
			self.surface_overlay.fill((255,0,255))
			
			# draw onto overlay
			top_shutter.draw(self.surface_overlay)
			bottom_shutter.draw(self.surface_overlay)
			
			self.draw()
			pygame.display.update()
			timepassed = clock.tick(45)
	
	def shutterOutY(self,color,duration,easing_function):
		"""Draws a shutter closing in effect on the surface_overlay"""
		self.in_transition = True
		bg_color = color
		clock = pygame.time.Clock()
		timepassed = 0
		time_since_start = 0.0
		fade_duration = duration
		top_shutter = Tweenable((0,0),self.width,self.height/2,bg_color)
		bottom_shutter = Tweenable((0,0),self.width,self.height/2,bg_color)
		
		top_shutter.rect.bottomleft = (0,self.height/2)
		bottom_shutter.rect.topleft = (0,self.height/2)
		
		while self.in_transition:
			
			getattr(top_shutter,easing_function)(0,-top_shutter.rect.height,fade_duration,timepassed)
			getattr(bottom_shutter,easing_function)(0,self.height,fade_duration,timepassed)
					
			if not top_shutter.startSet and not bottom_shutter.startSet:
				self.in_transition = False
		
				# return value to show we are done
				return 1
				
			# clear the overlay surface
			self.surface_overlay.fill((255,0,255))
			
			# draw onto overlay
			top_shutter.draw(self.surface_overlay)
			bottom_shutter.draw(self.surface_overlay)
			
			self.draw()	
			pygame.display.update()
			timepassed = clock.tick(45)
	
class CameraHandler(object):
	"""Handles panning and scrolling of room surfaces larger than the window size
	main_window_size -> size of the top level window surface
	room_to_move -> the room object whose surface position we manipulate
	object_to_track -> the object that will be the target the camera will follow(should have a rect and x,y attributes)"""
	
	# parallax_rects_list should be a list(of arbitrary length) of tuples 
	# each tuple should contain a reference to an images surface rect and index[0]
	# - at index[1] should be a factor which is a point decimal indicating the amount we move the 
	# - surface rect at index [0] e.g a factor of 1.0 moves the rect same as the room surface ; 2.0 twice the amount
		
	def __init__(self,main_window_size,room_to_move,object_to_track,delimit = True,parallax_rects_list = None):
		self.main_window_size = main_window_size
		self.room_to_move = room_to_move
		self.object_to_track = object_to_track
		
		self.slack_minx = None
		self.slack_miny = None
		self.slack_maxx = None
		self.slack_maxy = None
		
		self.lock_position = (self.main_window_size[0]/2,self.main_window_size[1]/2)
		self.current_camx = self.lock_position[0]
		self.current_camy = self.lock_position[1]
		
		self.mode = "lock"		# default mode locks object_to_track position to screen center
		self.delimit = delimit
		
		self.is_moving_to = False
		self.move_end_position = None
		self.dist_to_cover_x = None
		self.dist_to_cover_y = None
		
		# deprecated shit here these velocities
		self.move_speed_x = 0
		self.move_speed_y = 0
		
		self.xvel = 0.0
		self.yvel = 0.0
		self.max_speed = 5.0
		
		self.parallax_rects_list = parallax_rects_list
		
	def setState(self,mode,mode_options):
		"""Defines camera behaviour"""
		# params mode : should be string either 'lock' or 'slack'
		# mode_options : a list containing the selected modes options
		# if mode=='lock' : mode_options should be [(lock_position.x,lock_position.y)]
		# if mode=='slack' : mode_options should be [(slack_minx,slack_maxx),(slack_miny,slack_maxy)]
		# if slack_maxx and slack_minx are equal it locks you to that position
		# same thing goes for slack_miny and slack_maxy
		
		if mode == "lock":
			self.lock_position = mode_options[0] 
			self.mode = "lock"
			
		elif mode == "slack":
			self.slack_minx,self.slack_maxx = mode_options[0]
			self.slack_miny,self.slack_maxy = mode_options[1]
			self.mode = "slack"
	
	def setCamTo(self,object_to_track):
		"""This is currently deprecated; to move the cam(move the object it tracks instead)"""
		self.object_to_track = object_to_track
		ob_truex = self.room_to_move.x + object_to_track.x
		ob_truey = self.room_to_move.y + object_to_track.y 
		
		# center object to window center
		# calculate object_to_track's distance to window center
		xdist = (self.current_camx) - ob_truex
		ydist = (self.current_camy) - ob_truey
		
		self.dist_to_cover_x = abs(xdist)
		self.dist_to_cover_y = abs(ydist)
		
		len = math.sqrt(xdist * xdist + ydist * ydist)
		
		if len > 0:
			xdist /= len
			ydist /= len
		
		self.move_speed_x = xdist
		self.move_speed_y = ydist
		
		self.is_moving_to = True
	
	def move_old(self):
		"""This is currently deprecated; to move the cam(move the object it tracks instead)"""
		self.dist_to_cover_y -= abs(self.move_speed_y)
		self.dist_to_cover_x -= abs(self.move_speed_x)
		
		if self.dist_to_cover_x <=0 and self.dist_to_cover_y <=0:
			self.is_moving_to = False
			return
		else:
			self.room_to_move.x += self.move_speed_x
			self.room_to_move.y += self.move_speed_y
		
		
	def move_new(self):
		"""This is currently deprecated; to move the cam(move the object it tracks instead)"""
		ob_truex = self.room_to_move.x + self.object_to_track.x
		ob_truey = self.room_to_move.y + self.object_to_track.y 
		
		linear_vel_x = self.current_camx - ob_truex 
		linear_vel_y = self.current_camy - ob_truey
		
		# normalize the vectors to get heading
		len = math.sqrt(linear_vel_x * linear_vel_x + linear_vel_y * linear_vel_y)
		
		if len < 3:
			return
		
		if len > 0:
			linear_vel_x /= len
			linear_vel_y /= len
		
		self.xvel = linear_vel_x * self.max_speed
		self.yvel = linear_vel_y * self.max_speed
		
		self.room_to_move.x += self.xvel
		self.room_to_move.y += self.yvel
	
	def track(self):
		"""This is where we update the camera position"""
		if self.mode == "lock":
		
			# calculate object_to_track's screen position on window
			ob_truex = self.room_to_move.x + self.object_to_track.x
			ob_truey = self.room_to_move.y + self.object_to_track.y 
		
			# center object to window center
			# calculate object_to_track's distance to window center
			xdist = (self.lock_position[0]) - ob_truex
			ydist = (self.lock_position[1]) - ob_truey
			
			# set current cam position
			self.current_camx = self.lock_position[0]
			self.current_camy = self.lock_position[1]
			
			#len = math.sqrt(xdist * xdist + ydist * ydist)
			#xdist /= len
			#ydist /= len
			
			if self.delimit:	
				
				if xdist > 0:
					# we are moving the surface right
					if self.room_to_move.surface_rect.left >= 0:
						# check if left side of rect is past screen left
						# do nothing
						pass
					else:
						# allow pan left
						self.room_to_move.x += xdist
						
						# also move parallax_rects_list if provided
						if self.parallax_rects_list != None:
							for rect,factor in self.parallax_rects_list:
								# get how much to move the parallax surface
								p_xdist = xdist * factor
								rect.x += p_xdist
						
				elif xdist < 0:
					# we are moving the surface left
					if self.room_to_move.surface_rect.right <= self.main_window_size[0]:
						# check if right side of rect is past screen right
						# do nothing
						pass
					else:
						# allow pan right
						self.room_to_move.x += xdist
						
						# also move parallax_rects_list if provided
						if self.parallax_rects_list != None:
							for rect,factor in self.parallax_rects_list:
								# get how much to move the parallax surface
								p_xdist = xdist * factor
								rect.x += p_xdist
						
				if ydist > 0:
					# we are moving the surface down
					if self.room_to_move.surface_rect.top >= 0:
						# check if top side of rect is past screen top
						# do nothing
						pass
					else:
						# allow pan up
						self.room_to_move.y += ydist
						
						# also move parallax_rects_list if provided
						if self.parallax_rects_list != None:
							for rect,factor in self.parallax_rects_list:
								# get how much to move the parallax surface
								p_ydist = ydist * factor
								rect.y += p_ydist
						
				elif ydist < 0:
					# we are moving the surface up
					if self.room_to_move.surface_rect.bottom <= self.main_window_size[1]:
						# check if bottom side of rect is past screen bottom
						# do nothing
						pass
					else:
						# allow pan down
						self.room_to_move.y += ydist
						
						# also move parallax_rects_list if provided
						if self.parallax_rects_list != None:
							for rect,factor in self.parallax_rects_list:
								# get how much to move the parallax surface
								p_ydist = ydist * factor
								rect.y += p_ydist
						
			else:
				# no need to delimit
				self.room_to_move.x += xdist
				self.room_to_move.y += ydist
			
				# also move parallax_rects_list if provided
				if self.parallax_rects_list != None:
					for rect,factor in self.parallax_rects_list:
						# get how much to move the parallax surface
						p_xdist = xdist * factor
						p_ydist = ydist * factor
						
						rect.x += p_xdist
						rect.y += p_ydist
						
						
			#print ob_truex,ob_truey
		
			#self.room_to_move.surface_rect.x += int(xdist)
			#self.room_to_move.surface_rect.y += int(ydist)
		
		
			#self.room_to_move.x = int(xdist)
			#self.room_to_move.y = int(ydist)
		
		elif self.mode == "slack":
		
			# calculate object_to_track's screen position on window
			ob_truex = self.room_to_move.x + self.object_to_track.x
			ob_truey = self.room_to_move.y + self.object_to_track.y 
		
			# center object to window center
			# calculate object_to_track's distance to window center
			
			if ob_truex < self.slack_minx:
				xdist = (self.slack_minx) - ob_truex
				self.current_camx = self.slack_minx
				
			elif ob_truex > self.slack_maxx:
				xdist = (self.slack_maxx) - ob_truex
				self.current_camx = self.slack_maxx
			else:
				xdist = 0
			
			if ob_truey < self.slack_miny:
				ydist = (self.slack_miny) - ob_truey
				self.current_camy = self.slack_miny
				
			elif ob_truey > self.slack_maxy:
				ydist = (self.slack_maxy) - ob_truey
				self.current_camy = self.slack_maxy	
			else:
				ydist = 0
			
			#len = math.sqrt(xdist * xdist + ydist * ydist)
			#xdist /= len
			#ydist /= len
			
			if self.delimit:	
				
				if xdist > 0:
					# we are moving the surface right
					if self.room_to_move.surface_rect.left >= 0:
						# check if left side of rect is past screen left
						# do nothing
						pass
					else:
						# allow pan left
						self.room_to_move.x += xdist
						
						# also move parallax_rects_list if provided
						if self.parallax_rects_list != None:
							for rect,factor in self.parallax_rects_list:
								# get how much to move the parallax surface
								p_xdist = xdist * factor
								rect.x += p_xdist
						
				elif xdist < 0:
					# we are moving the surface left
					if self.room_to_move.surface_rect.right <= self.main_window_size[0]:
						# check if right side of rect is past screen right
						# do nothing
						pass
					else:
						# allow pan left
						self.room_to_move.x += xdist
						
						# also move parallax_rects_list if provided
						if self.parallax_rects_list != None:
							for rect,factor in self.parallax_rects_list:
								# get how much to move the parallax surface
								p_xdist = xdist * factor
								rect.x += p_xdist
						
				if ydist > 0:
					# we are moving the surface down
					if self.room_to_move.surface_rect.top >= 0:
						# check if top side of rect is past screen top
						# do nothing
						pass
					else:
						# allow pan left
						self.room_to_move.y += ydist
						
						# also move parallax_rects_list if provided
						if self.parallax_rects_list != None:
							for rect,factor in self.parallax_rects_list:
								# get how much to move the parallax surface
								p_ydist = ydist * factor
								rect.y += p_ydist
						
				elif ydist < 0:
					# we are moving the surface up
					if self.room_to_move.surface_rect.bottom <= self.main_window_size[1]:
						# check if bottom side of rect is past screen bottom
						# do nothing
						pass
					else:
						# allow pan left
						#self.room_to_move.y += ydist
						
						# allow pan left
						self.room_to_move.y += ydist
						
						# also move parallax_rects_list if provided
						if self.parallax_rects_list != None:
							for rect,factor in self.parallax_rects_list:
								# get how much to move the parallax surface
								p_ydist = ydist * factor
								rect.y += p_ydist
						
			else:
				self.room_to_move.x += xdist
				self.room_to_move.y += ydist
				
				# also move parallax_rects_list if provided
				if self.parallax_rects_list != None:
					for rect,factor in self.parallax_rects_list:
						# get how much to move the parallax surface
						p_xdist = xdist * factor
						p_ydist = ydist * factor
						
						rect.x += p_xdist
						rect.y += p_ydist
				
			#print ob_truex,ob_truey
		
		#self.move_new()
		
