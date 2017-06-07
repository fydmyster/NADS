from OpenGL.GL import*
from OpenGL.GLU import*

import math,random
from sprite import Sprite
import sgf.utils.helpers as helpers
import sgf.utils.g_utils as g_utils

class QuadParticle(object):
	"""Particle that renders on the screen as a quad"""
	def __init__(self,x,y,w,h,**kwargs):
		
		self.valid_kwargs = {
							"lifetime" : 3000,			# how long the particle lives in milliseconds
							"xvel" : 0,
							"yvel" : 0,
							"color_1" : (1.0,1.0,1.0),
							"color_2" : (0.0,0.0,0.0),
							"alive": True,
							"lerp_vel" : 0.008,
							"friction" : 0.97,
							"rotate_friction":0.97,
							"rotate_vel" : 0,				# can be negative/positive 0 if no rotation
							"scale_velocity" : 0.00,	# how much particle grows/shrinks by depending on -/+
							"gravity" : 0.0,
							"scale_x_only":False,
							"scale_y_only":False,
							"trail_length" : 7,
							"wind_direction" : 45,
							"wind_strength" : 0.0,
							"alpha" : 1.0,
							"alpha_decay" : 0.009,		# if alpha < 0 or acc_livetime>lifetime : kill particle
								}
		
		self.acc_livetime = 0
		
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
		self.w = w
		self.h = h
		self.hx = self.w/2.0
		self.hy = self.h/2.0
		self.scale = 1.0
		self.rotation = 0

		self.color = self.color_1
		self.factor = 0.0
		self.trail_list = []
		
		if self.color_1 != self.color_2:
			self.can_lerp = True
		else:
			self.can_lerp = False
		
		angle = self.wind_direction	
		self.vec_x = math.cos((angle * (math.pi/180)))
		self.vec_y = math.sin((angle * (math.pi/180)))
						
		self.vec_x *= self.wind_strength
		self.vec_y *= self.wind_strength
		
	def updateParticle(self,timepassed):
		"""Sorts out the particle state specifically"""
		
		self.acc_livetime += timepassed
		
		if self.acc_livetime > self.lifetime:
			self.alive = False
		
		self.alpha -= self.alpha_decay
		
		if self.alpha < 0.0:
			self.alpha = 0.0
			self.alive = False
		
		self.scale += self.scale_velocity
		if self.scale < 0:
			self.scale = 0
			self.alive = False
		
		self.rotate_vel *= self.rotate_friction
		self.rotation += self.rotate_vel
		
		self.xvel += self.vec_x
		self.yvel += self.vec_y
			
		self.yvel += self.gravity
		
		self.xvel *= self.friction
		self.yvel *= self.friction
		
		self.x += self.xvel
		self.y += self.yvel
		
		if self.trail_length > 0 :
			self.trail_list.append((self.x,self.y))
		
			if len(self.trail_list) > self.trail_length:
				self.trail_list = self.trail_list[-self.trail_length:]
		
		
	def update(self,timepassed):
		"""Manages the particles state"""
		
		if self.can_lerp:
			self.factor += self.lerp_vel
			if self.factor > 1:
				self.can_lerp = False
		
		if self.can_lerp:
			self.color = g_utils.colorLerp(self.color_1,self.color_2,self.factor)
		
		self.updateParticle(timepassed)
	
	def drawTrail(self):
		"""Renders the particles trail"""
		
		for i in range(len(self.trail_list)):
			glPushMatrix()
			particle = self.trail_list[i]
			
			glTranslatef(particle[0],particle[1],0.0)
		
			if self.scale_x_only:
				glScalef(self.scale,1.0,1.0)
			elif self.scale_y_only:
				glScalef(1.0,self.scale,1.0)
			else:
				glScalef(self.scale,self.scale,1.0)
		
			glRotate(self.rotation,0,0,1)
		
			self.drawQuad()
			glPopMatrix()
	
	def drawQuad(self):
		"""Draws a quad"""
		
		glDisable(GL_TEXTURE_2D)
		glBegin(GL_QUADS)
		glColor4f(self.color[0],self.color[1],self.color[2],self.alpha)
		glVertex2f(-self.hx,-self.hy)
		glVertex2f(self.hx,-self.hy)
		glVertex2f(self.hx,self.hy)
		glVertex2f(-self.hx,self.hy)
		glEnd()
		glEnable(GL_TEXTURE_2D)
	
	def draw(self):
		"""Renders the particle"""
		glPushMatrix()
		
		glTranslatef(self.x,self.y,0.0)
		
		if self.scale_x_only:
			glScalef(self.scale,1.0,1.0)
		elif self.scale_y_only:
			glScalef(1.0,self.scale,1.0)
		else:
			glScalef(self.scale,self.scale,1.0)
		
		glRotate(self.rotation,0,0,1)
		
		self.drawQuad()
		
		glPopMatrix()
		
		if self.trail_length > 0:
			self.drawTrail()			
		
class SpriteParticle(Sprite):
	"""Particle that renders on the screen as a basic sprite"""
	def __init__(self,x,y,w,h,imagepath_list,colorkey=None,**kwargs):
		super(SpriteParticle,self).__init__(x,y,w,h,imagepath_list,colorkey)
		
		self.valid_kwargs = {
							"lifetime" : 3000,			# how long the particle lives in milliseconds
							"xvel" : 6,
							"yvel" : 0,
							"alive": True,
							"friction" : 0.97,
							"rotate_friction":0.97,
							"rotate_vel" : -20,				# can be negative/positive 0 if no rotation
							"scale_velocity" : -0.007,	# how much particle grows/shrinks by depending on -/+
							"gravity" : 0.0,
							"wind_direction" : 45,
							"wind_strength" : 0.0,
							"alpha_decay" : 0.005,		# if alpha < 0 or acc_livetime>lifetime : kill particle
							"trail_length" : 8,
							"alpha_var" : 1.0
								}
		
		self.acc_livetime = 0
		
		for key,val in kwargs.items():
			if self.valid_kwargs.has_key(key):
				self.valid_kwargs[key] = val
			else:
				# raise exception
				raise Exception("invalid attribute %s has been referenced" % key)
		# set atrributes
		for key,val in self.valid_kwargs.items():
			setattr(self,key,val)
		
		angle = self.wind_direction	
		self.vec_x = math.cos((angle * (math.pi/180)))
		self.vec_y = math.sin((angle * (math.pi/180)))
						
		self.vec_x *= self.wind_strength
		self.vec_y *= self.wind_strength
		
		self.trail_list = []
		
		# create animation manager
		self.frame_manager = helpers.AnimManager([self.cur_texture.num_sprites_x])
		self.frame_manager.playRepeat(0,-1)
		
		self.alpha = self.alpha_var
		
	def updateParticle(self,timepassed):
		"""Sorts out the particle state specifically"""
		
		self.acc_livetime += timepassed
		
		if self.acc_livetime > self.lifetime:
			self.alive = False
		
		self.alpha -= self.alpha_decay
		
		if self.alpha < 0.0:
			self.alpha = 0.0
			self.alive = False
		
		self.scale += self.scale_velocity
		if self.scale < 0:
			self.scale = 0
			self.alive = False
		
		self.rotate_vel *= self.rotate_friction
		self.rotation += self.rotate_vel
		
		self.xvel += self.vec_x
		self.yvel += self.vec_y
			
		self.yvel += self.gravity
		
		self.xvel *= self.friction
		self.yvel *= self.friction
		
		self.x += self.xvel
		self.y += self.yvel
		
		if self.trail_length > 0 :
			self.trail_list.append((self.x,self.y))
		
			if len(self.trail_list) > self.trail_length:
				self.trail_list = self.trail_list[-self.trail_length:]
		
		
	def update(self,timepassed):
		"""Manages the particles state"""
		
		self.updateParticle(timepassed)
		
		self.frame_manager.update(timepassed)
		self.frame = self.frame_manager.getFrame()[1]
		
		super(SpriteParticle,self).update(timepassed)
	
	def drawTrail(self):
		"""Renders the particles trail"""
		
		for i in range(len(self.trail_list)):
			
			particle = self.trail_list[i]
			
			glPushMatrix()
			glTranslate(particle[0] + self.hx,particle[1] + self.hy,0)	# position relative to quad center
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

			glPopMatrix()
	
	def draw(self):
		
		super(SpriteParticle,self).draw()
		
		if self.trail_length > 0:
			self.drawTrail()
	
class SpriteParticleEmitter(object):
	def __init__(self,x,y,w,h,imagepath_list,colorkey=None,**kwargs):
		# param direction : 'left','right','top','bottom','random'
		# param emit_mode : a tuple of two items
		#					- index 0 can be a string; either "burst" or "stream"
		# if burst : index 1 is the number of intermidiary milliseconds till next burst or None(trigger no extra burst) 
		# if stream : index 1 is the number of intermidiary milliseconds till next particle emission
		
		self.valid_kwargs = {			
			"mode" : ('stream',3000),
			"direction": 'random',
			"lifetime" : 5000,
			"particle_type" : SpriteParticle,
			"dir_variance" : 5,
			"fric_variance" : 0,
			"x_pos_variance" : 0,
			"y_pos_variance" : 0,
			"str_variance" : 0,
			"friction" : 0.97,
			"strength" : 2,
			"blend" : 0,
			# particle specific shit we can pass
			"rotate_friction":0.97,
			"rotate_vel" : -20,				# can be negative/positive 0 if no rotation
			"scale_velocity" : -0.007,	# how much particle grows/shrinks by depending on -/+
			"gravity" : 0.0,
			"wind_direction" : 45,
			"wind_strength" : 0.0,
			"alpha_decay" : 0.005,		# if alpha < 0 or acc_livetime>lifetime : kill particle
			"trail_length" : 4,
			"alpha_var" : 1.0
											
		}
		
		self.imagepath_list = imagepath_list
		self.colorkey = colorkey
		
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
		self.w = w
		self.h = h
		self.particle_list = []
		self.emit_mode = self.mode[0]
		self.updatetime = self.mode[1]
		self.acctime = self.updatetime 
		self.emit = True
		
		self.blend_modes =[(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA),
					(GL_ONE_MINUS_DST_ALPHA,GL_ONE_MINUS_DST_ALPHA),	
					(GL_ONE_MINUS_DST_ALPHA,GL_ONE),		
					(GL_ONE_MINUS_DST_ALPHA,GL_ONE_MINUS_SRC_ALPHA),
					(GL_ONE_MINUS_SRC_ALPHA,GL_ONE_MINUS_DST_ALPHA),	
					(GL_ONE_MINUS_SRC_ALPHA,GL_ONE),		
					(GL_ONE_MINUS_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA),
					(GL_ONE,GL_ONE_MINUS_SRC_ALPHA),
					(GL_ONE,GL_ONE_MINUS_DST_ALPHA),
					(GL_ONE,GL_DST_COLOR),
					(GL_SRC_COLOR,GL_ONE)]
						
		max_modes = len(self.blend_modes)
		
		if self.blend > max_modes - 1:
			self.blend = 0
		
	def burst(self,num_particles=15):
		"""Releases a set number of particles in an instant"""
		for i in range(num_particles):
			
			if self.direction == "random":
				angle = random.randint(0,360)
				vec_x = math.cos((angle * (math.pi/180)))
				vec_y = math.sin((angle * (math.pi/180)))
				
			else:
				# an angle was provided
				if self.dir_variance != 0:
					angle = random.randrange(self.direction-self.dir_variance,self.direction + self.dir_variance)
				else:
					angle = self.direction
						
				vec_x = math.cos((angle * (math.pi/180)))
				vec_y = math.sin((angle * (math.pi/180)))
						
			calc_strength = random.uniform(max(self.strength-self.str_variance,0),self.strength+self.str_variance)
			vec_x *= calc_strength
			vec_y *= calc_strength
				
			#fric = random.uniform(self.friction-self.fric_variance,min(self.friction+self.fric_variance,1.0))
			fric = random.uniform(self.friction-self.fric_variance,(self.friction+self.fric_variance))
			
			xpos = random.uniform(self.x - self.x_pos_variance,self.x + self.x_pos_variance)
			ypos = random.uniform(self.y - self.y_pos_variance,self.y + self.y_pos_variance)
				
			new_particle = self.particle_type(
										xpos,
										ypos,
										self.w,
										self.h,
										self.imagepath_list,
										self.colorkey,
										friction = fric,
										lifetime = self.lifetime,
										xvel = vec_x,
										yvel = vec_y,
										rotate_friction = self.rotate_friction,
										rotate_vel = self.rotate_vel,				
										scale_velocity = self.scale_velocity,
										gravity = self.gravity,
										wind_direction = self.wind_direction,
										wind_strength = self.wind_strength,
										alpha_decay = self.alpha_decay,
										trail_length = self.trail_length,
										alpha_var = self.alpha_var
										)
										
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
						
					else:
						# an angle was provided
						if self.dir_variance != 0:
							angle = random.randrange(self.direction-self.dir_variance,self.direction + self.dir_variance)
						else:
							angle = self.direction
						
						vec_x = math.cos((angle * (math.pi/180)))
						vec_y = math.sin((angle * (math.pi/180)))
						
					calc_strength = random.uniform(max(self.strength-self.str_variance,0),self.strength+self.str_variance)
					vec_x *= calc_strength
					vec_y *= calc_strength
				
					#fric = random.uniform(self.friction-self.fric_variance,min(self.friction+self.fric_variance,1.0))
					fric = random.uniform(self.friction-self.fric_variance,(self.friction+self.fric_variance))
			
					xpos = random.uniform(self.x - self.x_pos_variance,self.x + self.x_pos_variance)
					ypos = random.uniform(self.y - self.y_pos_variance,self.y + self.y_pos_variance)
			
					new_particle = self.particle_type(
										xpos,
										ypos,
										self.w,
										self.h,
										self.imagepath_list,
										self.colorkey,
										friction = fric,
										lifetime = self.lifetime,
										xvel = vec_x,
										yvel = vec_y,
										rotate_friction = self.rotate_friction,
										rotate_vel = self.rotate_vel,				
										scale_velocity = self.scale_velocity,
										gravity = self.gravity,
										wind_direction = self.wind_direction,
										wind_strength = self.wind_strength,
										alpha_decay = self.alpha_decay,
										trail_length = self.trail_length,
										alpha_var = self.alpha_var
										)
					
					self.particle_list.append(new_particle)
					
			for particle in self.particle_list:
				particle.update(timepassed)
				
			# delete dead particles
			for particle in self.particle_list:
				if not particle.alive:
					self.particle_list.remove(particle)
					
	def draw(self):
		
		# set the specified blending function
		glBlendFunc(*self.blend_modes[self.blend])
		
		for particle in self.particle_list:
			particle.draw()	
		
		# set the specified blending function to default
		glBlendFunc(*self.blend_modes[0])
	
class QuadParticleEmitter(object):
	def __init__(self,x,y,**kwargs):
		# param direction : 'left','right','top','bottom','random'
		# param emit_mode : a tuple of two items
		#					- index 0 can be a string; either "burst" or "stream"
		# if burst : index 1 is the number of intermidiary milliseconds till next burst or None(trigger no extra burst) 
		# if stream : index 1 is the number of intermidiary milliseconds till next particle emission
		
		self.valid_kwargs = {			
			"mode" : ('stream',3000),
			"direction": 'random',
			"particle_type" : QuadParticle,
			"dir_variance" : 0,
			"size_variance" : 0,		# still to be implemented
			"fric_variance" : 0.0,
			"str_variance" : 0,
			"x_pos_variance":0,
			"y_pos_variance":0,
			"friction" : 0.97,
			"strength" : 2,
			"particle_w" : 20,
			"particle_h" : 20,
			"rand_color" : False,
			"blend" : 6,
			# particle specific parameters next
			"color_1" : (1.0,0.0,0.0),
			"color_2" : (0.1,0.3,0.9),
			"lerp_vel" : 0.008,				
			"rotate_friction":0.97,
			"rotate_vel" : 0,
			"alpha" : 1.0,
			"scale_velocity" : 0.0,	
			"gravity" : 0.0,
			"trail_length" : 8,
			"scale_x_only":False,
			"scale_y_only":False,			
			"wind_direction" : 45,
			"wind_strength" : 0.0,
			"alpha_decay" : 0.009	
							
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
		
		self.blend_modes =[(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA),
					(GL_ONE_MINUS_DST_ALPHA,GL_ONE_MINUS_DST_ALPHA),	
					(GL_ONE_MINUS_DST_ALPHA,GL_ONE),		
					(GL_ONE_MINUS_DST_ALPHA,GL_ONE_MINUS_SRC_ALPHA),
					(GL_ONE,GL_ONE_MINUS_SRC_ALPHA),
					(GL_ONE,GL_ONE_MINUS_DST_ALPHA),
					(GL_ONE,GL_DST_COLOR),
					(GL_SRC_COLOR,GL_ONE)]
						
		max_modes = len(self.blend_modes)
		
		if self.blend > max_modes - 1:
			self.blend = 0
	
		
	def burst(self,num_particles=15):
		"""Releases a set number of particles in an instant"""
		for i in range(num_particles):
			
			if self.direction == "random":
				angle = random.randint(0,360)
				vec_x = math.cos((angle * (math.pi/180)))
				vec_y = math.sin((angle * (math.pi/180)))
				
			else:
				
				# an angle was provided
				if self.dir_variance != 0:
					angle = random.randrange(self.direction-self.dir_variance,self.direction + self.dir_variance)
				else:
					angle = self.direction
						
				vec_x = math.cos((angle * (math.pi/180)))
				vec_y = math.sin((angle * (math.pi/180)))
						
			
			calc_strength = random.uniform(max(self.strength-self.str_variance,0),self.strength+self.str_variance)
			vec_x *= calc_strength
			vec_y *= calc_strength
				
			#fric = random.uniform(self.friction-self.fric_variance,min(self.friction+self.fric_variance,1.0))
			fric = random.uniform(self.friction-self.fric_variance,(self.friction+self.fric_variance))
			
			xpos = random.uniform(self.x - self.x_pos_variance,self.x + self.x_pos_variance)
			ypos = random.uniform(self.y - self.y_pos_variance,self.y + self.y_pos_variance)
			
			if self.rand_color:
				rgb = g_utils.getRandColor()
				self.color_1 = (rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
				rgb = g_utils.getRandColor()
				self.color_2 = (rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
				
			new_particle = self.particle_type(xpos,
												ypos,
												self.particle_w,
												self.particle_h,
												xvel = vec_x,
												yvel = vec_y,
												friction = fric,
												color_1 = self.color_1,
												color_2 = self.color_2,
												lerp_vel = self.lerp_vel,				
												rotate_friction = self.rotate_friction,
												rotate_vel = self.rotate_vel,		
												scale_velocity = self.scale_velocity,												
												gravity = self.gravity,
												scale_x_only = self.scale_x_only,
												scale_y_only = self.scale_y_only,
												trail_length = self.trail_length,
												wind_direction = self.wind_direction,
												wind_strength = self.wind_strength,
												alpha_decay = self.alpha_decay,
												alpha = self.alpha
												)
												
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
				
					else:
						# an angle was provided
						if self.dir_variance != 0:
							angle = random.randrange(self.direction-self.dir_variance,self.direction + self.dir_variance)
						else:
							angle = self.direction
						
						vec_x = math.cos((angle * (math.pi/180)))
						vec_y = math.sin((angle * (math.pi/180)))
						
						
					calc_strength = random.uniform(max(self.strength-self.str_variance,0),self.strength+self.str_variance)
					vec_x *= calc_strength
					vec_y *= calc_strength
				
					#fric = random.uniform(self.friction-self.fric_variance,min(self.friction+self.fric_variance,1.0))
					fric = random.uniform(self.friction-self.fric_variance,(self.friction+self.fric_variance))
			
					xpos = random.uniform(self.x - self.x_pos_variance,self.x + self.x_pos_variance)
					ypos = random.uniform(self.y - self.y_pos_variance,self.y + self.y_pos_variance)
					
					if self.rand_color:
						rgb = g_utils.getRandColor()
						self.color_1 = (rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
						rgb = g_utils.getRandColor()
						self.color_2 = (rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
				
					new_particle = self.particle_type(xpos,
												ypos,
												self.particle_w,
												self.particle_h,
												xvel = vec_x,
												yvel = vec_y,
												friction = fric,
												color_1 = self.color_1,
												color_2 = self.color_2,
												lerp_vel = self.lerp_vel,				
												rotate_friction = self.rotate_friction,
												rotate_vel = self.rotate_vel,		
												scale_velocity = self.scale_velocity,												
												gravity = self.gravity,
												scale_x_only = self.scale_x_only,
												scale_y_only = self.scale_y_only,
												trail_length = self.trail_length,
												wind_direction = self.wind_direction,
												wind_strength = self.wind_strength,
												alpha_decay = self.alpha_decay,
												alpha = self.alpha
												)
												
					self.particle_list.append(new_particle)
					
			for particle in self.particle_list:
				particle.update(timepassed)
				
			# delete dead particles
			for particle in self.particle_list:
				if not particle.alive:
					self.particle_list.remove(particle)
					
	def draw(self):
		
			
		# set the specified blending function
		glBlendFunc(*self.blend_modes[self.blend])
	
		for particle in self.particle_list:
			particle.draw()	
				
		# set the specified blending function to default
		glBlendFunc(*self.blend_modes[0])
	