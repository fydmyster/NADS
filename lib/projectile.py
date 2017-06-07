import math,random,pygame
import sgf.gameobjects.g_objects as gobs
import sgf.utils.g_utils as gutils

class BasicBullet(object):
	def __init__(self,x,y,direction,friction=1.0,speed=3.1):
		
		self.trail_list = []
		self.max_traillen = 8
		
		self.kind = "BasicBullet"
		self.x = x
		self.y = y
		self.main_image = pygame.image.load("images\\bullet.png").convert()
		self.main_image.set_colorkey((255,0,255))
		self.rect = self.main_image.get_rect()
		self.rect.center = (self.x,self.y)
		self.col_rect = pygame.Rect(self.x,self.y,4,4)
		self.dir = direction
		self.rot_rect = self.main_image.get_rect()
		self.speed = speed
		self.friction = friction
		self.dx = math.cos(direction * (math.pi/180)) * self.speed
		self.dy = math.sin(direction * (math.pi/180)) * self.speed
		self.alive = True
		
		self.image = pygame.transform.rotate(self.main_image,360-self.dir)
		self.rot_rect = self.image.get_rect(center=self.rect.center)
		
	def update(self,timepassed=0):
		
		self.x += self.dx
		self.y += self.dy
		self.dx *= self.friction
		self.dy *= self.friction
		
		self.trail_list.append(self.rot_rect.topleft)
		
		if len(self.trail_list) > self.max_traillen:
			self.trail_list.pop(0)
		
		self.rect.center = (self.x,self.y)
		self.rot_rect.center = (self.x,self.y)
		self.col_rect.center = self.rot_rect.center
 		
		
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rot_rect)
		
		trail_image = self.image.copy()
		trail_image.set_alpha(70)
		for pos in self.trail_list:
			Surface.blit(trail_image,pos)
 
class AnimatedBullet(object):
	def __init__(self,image_path,x,y,w,h,direction,speed=0.8,fps=12,friction=1.0,rotate=False,trail=False):
		
		self.x = x
		self.y = y
		self.rotate = rotate
		self.kind = "AnimatedBullet"
		self.trail = trail
		
		self.trail_list = []
		self.max_traillen = 6
		
		self.master_images = gutils.sliceSheetColKey(w,h,image_path)
		
		self.main_image = self.master_images[0].copy()
		self.rect = self.main_image.get_rect()
		self.rect.center = (self.x,self.y)
		self.col_rect = pygame.Rect(self.x,self.y,4,4)
		self.dir = direction
		self.rot_rect = self.main_image.get_rect()
		self.speed = speed
		self.friction = friction
		
		self.fps = fps
		self.dx = math.cos(direction * (math.pi/180)) * self.speed
		self.dy = math.sin(direction * (math.pi/180)) * self.speed
		
		self.anim_object = gobs.AnimObject([self.master_images,-1,self.fps],x,y,self.dx,self.dy,self.friction)
		
		self.alive = True
		
		if self.rotate:
			self.image = pygame.transform.rotate(self.main_image,360-self.dir)
			self.rot_rect = self.image.get_rect(center=self.rect.center)
		else:
			self.image = self.main_image
		
	
	def update(self,timepassed):
		
		self.anim_object.update(timepassed)
		
		self.main_image = self.anim_object.image.copy()
		
		if self.rotate:
			self.image = pygame.transform.rotate(self.main_image,360-self.dir)
			self.rot_rect = self.image.get_rect(center=self.rect.center)
		else:
			self.image = self.main_image
		
		if self.trail:
			self.trail_list.append(self.rot_rect.topleft)
		
			if len(self.trail_list) > self.max_traillen:
				self.trail_list.pop(0)
		
		
		self.x,self.y = (self.anim_object.x,self.anim_object.y)
		self.rect.center = (self.x,self.y)
		self.rot_rect.center = (self.x,self.y)
		self.col_rect.center = self.rot_rect.center
 		
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rot_rect)
		#self.anim_object.draw(Surface)
		if self.trail:
			trail_image = self.image.copy()
			trail_image.set_alpha(70)
			for pos in self.trail_list:
				Surface.blit(trail_image,pos)
 
		
class WaveyBullet(AnimatedBullet):
	
	def __init__(self,image_path,x,y,w,h,direction,speed=0.8,fps=12,friction=1.0,rotate=False):
		
		super(WaveyBullet,self).__init__(image_path,x,y,w,h,direction,speed,fps,friction,rotate)
		self.kind = "WaveyBullet"
		self.sin_angle = 0
		self.sin_speed = 18
		self.trail_list = []
		self.max_traillen = 8
		
	def update(self,timepassed):
		
		self.anim_object.update(timepassed)
		self.sin_angle += self.sin_speed
		
		self.main_image = self.anim_object.image.copy()
		
		if self.rotate:
			self.image = pygame.transform.rotate(self.main_image,360-self.dir)
			self.rot_rect = self.image.get_rect(center=self.rect.center)
		else:
			self.image = self.main_image
		
		self.trail_list.append(self.rot_rect.topleft)
		
		if len(self.trail_list) > self.max_traillen:
			self.trail_list.pop(0)
		
		self.x,self.y = (self.anim_object.x,self.anim_object.y)
		self.x += (self.dy*4) * math.cos(self.sin_angle*(math.pi/180))
		self.y += (self.dx*4) * math.cos(self.sin_angle*(math.pi/180))
		
		self.rect.center = (self.x,self.y)
		self.rot_rect.center = (self.x,self.y)
		self.col_rect.center = self.rot_rect.center
	
	def draw(self,Surface):
		super(WaveyBullet,self).draw(Surface)
		
		trail_image = self.image.copy()
		trail_image.set_alpha(70)
		for pos in self.trail_list:
			Surface.blit(trail_image,pos)
 
class PiercerBullet(AnimatedBullet):
	
	def __init__(self,image_path,x,y,w,h,direction,speed=0.8,fps=12,friction=1.0,rotate=False):
		
		super(PiercerBullet,self).__init__(image_path,x,y,w,h,direction,speed,fps,friction,rotate)
		self.kind = "PiercerBullet"
		self.trail_list = []
		self.max_traillen = 6
		
	def update(self,timepassed):
		
		self.anim_object.update(timepassed)
		
		self.main_image = self.anim_object.image.copy()
		
		if self.rotate:
			self.image = pygame.transform.rotate(self.main_image,360-self.dir)
			self.rot_rect = self.image.get_rect(center=self.rect.center)
		else:
			self.image = self.main_image
		
		self.trail_list.append(self.rot_rect.topleft)
		
		if len(self.trail_list) > self.max_traillen:
			self.trail_list.pop(0)
		
		self.x,self.y = (self.anim_object.x,self.anim_object.y)
		
		self.rect.center = (self.x,self.y)
		self.rot_rect.center = (self.x,self.y)
		self.col_rect.center = self.rot_rect.center
	
	def draw(self,Surface):
		super(PiercerBullet,self).draw(Surface)
		
		trail_image = self.image.copy()
		trail_image.set_alpha(70)
		for pos in self.trail_list:
			Surface.blit(trail_image,pos)

 
class BounceBullet(AnimatedBullet):
	
	def __init__(self,image_path,x,y,w,h,direction,speed=0.8,fps=12,friction=1.0,rotate=False):
		
		super(BounceBullet,self).__init__(image_path,x,y,w,h,direction,speed,fps,friction,rotate)
		self.kind = "BounceBullet"
		
		self.trail_list = []
		self.max_traillen = 6
		self.max_rebounds = 2
		self.acc_rebounds = 0
		self.hx = w/2
		self.hy = h/2
		self.w = w
		self.h = h
		self.cool_downtime = 100
		self.cool_acctime = 0
		self.can_collide = True
		
	def update(self,timepassed):
		
		self.anim_object.update(timepassed)
		self.cool_acctime += timepassed
		
		if self.cool_acctime > self.cool_downtime:
			self.can_collide = True
		else:
			self.can_collide = False
		
		self.main_image = self.anim_object.image.copy()
		
		if self.rotate:
			self.image = pygame.transform.rotate(self.main_image,360-self.dir)
			self.rot_rect = self.image.get_rect(center=self.rect.center)
		else:
			self.image = self.main_image
		
		self.trail_list.append(self.rot_rect.topleft)
		
		if len(self.trail_list) > self.max_traillen:
			self.trail_list.pop(0)
		
		self.x,self.y = (self.anim_object.x,self.anim_object.y)
		
		self.rect.center = (self.x,self.y)
		self.rot_rect.center = (self.x,self.y)
		self.col_rect.centerx = self.rot_rect.centerx + self.dx
		self.col_rect.centery = self.rot_rect.centery + self.dy
	
	def draw(self,Surface):
		super(BounceBullet,self).draw(Surface)
		
		trail_image = self.image.copy()
		trail_image.set_alpha(70)
		for pos in self.trail_list:
			Surface.blit(trail_image,pos)
 
	
	def changeDir(self,x,y,dx,dy):
		self.anim_object = gobs.AnimObject([self.master_images,-1,self.fps],x,y,self.dx,self.dy,self.friction)
		self.dir = math.atan2(self.dy,self.dx) * 180/math.pi
		
	def resolveCollisions(self,plat):
		"""Deals with bouncing off walls"""
		
		xdist= plat.rect.centerx - self.rect.centerx
		xpen = (plat.hx + self.hx) - abs(xdist)
					
		ydist= plat.rect.centery - self.rect.centery
		ypen = (plat.hy + self.hy) - abs(ydist)
		
		player_yrange = set(range(self.rect.top+1,self.rect.bottom-1)) 
		player_xrange = set(range(self.rect.left+1,self.rect.right-1)) 
		plat_yrange = set(range(plat.rect.top+1,plat.rect.bottom-1)) 
		plat_xrange = set(range(plat.rect.left+1,plat.rect.right-1)) 
		
		y_intersect = len(plat_yrange.intersection(player_yrange))
		x_intersect = len(plat_xrange.intersection(player_xrange))
		
		#print x_intersect,y_intersect
		
		# find the smallest penetration
		minpen=min(xpen,ypen)
			
		if minpen==xpen and y_intersect > 0:
			# project out along x axis
			if xdist >= 0:
				# push left
				self.dx *= -1
				x = plat.rect.left - (self.w+1)
				self.changeDir(x,self.y,self.dx,self.dy)

				
			else:
			#push right
				x = plat.rect.right+1
				self.dx *= -1
				self.changeDir(x,self.y,self.dx,self.dy)
	
		elif minpen==ypen and x_intersect > 0:
			# project out along y axis
			if ydist > 0:
				# push up
				self.dy *= -1
				y = plat.rect.top-(self.h+1)	# push up but leave 1px in tile
				self.changeDir(self.x,y,self.dx,self.dy)
	
			else:
				#push down
				y = plat.rect.bottom+1
				self.dy *= -1
				self.changeDir(self.x,y,self.dx,self.dy)

class FlameBullet(AnimatedBullet):
	
	def __init__(self,image_path,x,y,w,h,direction,speed=0.8,fps=12,friction=1.0,rotate=False):
		
		super(FlameBullet,self).__init__(image_path,x,y,w,h,direction,speed,fps,friction,rotate)
		self.kind = "FlameBullet"
		
		
	def update(self,timepassed):
		
		self.anim_object.update(timepassed)
		
		self.main_image = self.anim_object.image.copy()
		
		if self.rotate:
			self.image = pygame.transform.rotate(self.main_image,360-self.dir)
			self.rot_rect = self.image.get_rect(center=self.rect.center)
		else:
			self.image = self.main_image
		
		self.x,self.y = (self.anim_object.x,self.anim_object.y)
		
		self.rect.center = (self.x,self.y)
		self.rot_rect.center = (self.x,self.y)
		self.col_rect.center = self.rot_rect.center
		
		if abs(self.anim_object.xvel) < 0.2 and abs(self.anim_object.yvel) < 0.2:
			self.alive = False
		
	def draw(self,Surface):
		super(FlameBullet,self).draw(Surface)
		
		#trail_image = self.image.copy()
		#trail_image.set_alpha(70)
		#for pos in self.trail_list:
		#	Surface.blit(trail_image,pos)

class IceBullet(AnimatedBullet):
	
	def __init__(self,image_path,x,y,w,h,direction,speed=0.8,fps=12,friction=1.0,rotate=True,trail=True):
		
		super(IceBullet,self).__init__(image_path,x,y,w,h,direction,speed,fps,friction,rotate,trail)
		self.kind = "IceBullet"
		
	def update(self,timepassed):
		super(IceBullet,self).update(timepassed)
		
		if abs(self.anim_object.xvel) <0.01 and abs(self.anim_object.yvel) <0.01:
			self.alive = False
			
class RandomBullet(object):
	def __init__(self,image_path,x,y,w,h,target,speed=0.3,fps=15,friction=0.97,trail=True):
		
		self.kind = "RandomBullet"
		
		self.trail_list = []
		self.max_traillen = 6
		
		self.x,self.y = (x,y)
		self.yvel = self.xvel = 0
		
		self.fps = fps
		
		self.master_images = gutils.sliceSheetColKey(w,h,image_path)
		
		self.anim_object = gobs.AnimObject([self.master_images,-1,self.fps],x,y,0,0,1)
		
		self.main_image = self.master_images[0].copy()
		self.image = self.main_image.copy()
		self.rect = self.image.get_rect()
		self.rot_rect = self.image.get_rect()
		self.col_rect = pygame.Rect(self.x,self.y,4,4)
		
		
		self.missileOrientation=0
		self.speed= speed
		self.maxVel = 3.0
		self.vectorToTargetN =(0,0)
		self.angularVelocity = 0
		self.friction = friction
		
		self.alive = True
		self.target = target
	
	def draw(self,Surface):
		Surface.blit(self.image,self.rot_rect)
		
		trail_image = self.image.copy()
		trail_image.set_alpha(70)
		for pos in self.trail_list:
			Surface.blit(trail_image,pos)

	def update(self,timepassed):
		
		self.anim_object.update(timepassed)
		
		# get vector to target
		xVector = self.target.x - self.x
		yVector = self.target.y - self.y
		
		# normalise 
		length = math.sqrt( xVector*xVector + yVector*yVector )
		
		#xVector /= len
		#yVector /= len
		
		self.vectorToTargetN=(xVector,yVector)
		
		# missiles orientation as a vector
		
		mXVector = math.cos((self.missileOrientation * (math.pi/180)))
		mYVector = -math.sin((self.missileOrientation * (math.pi/180)))
	
		# calculate the dotProduct of the 2 vector to determine turning direction
		mDotTargetVector = mXVector * xVector + mYVector * yVector
		
		# if dotProduct is negative ; turn left

		if mDotTargetVector > 0:
			self.angularVelocity-=self.speed
		elif mDotTargetVector < 0:
			self.angularVelocity+=self.speed
 		else:
			# they are aligned ; do nothing
			pass
		
		self.missileOrientation += self.angularVelocity
		
		# resolve vectors to get coordinates
		self.trail_list.append(self.rot_rect.topleft)
		
		if len(self.trail_list) > self.max_traillen:
			self.trail_list.pop(0)
		
		self.x += self.maxVel * math.cos(self.missileOrientation * (math.pi/180))
		self.y += self.maxVel * -math.sin(self.missileOrientation * (math.pi/180))
		
		self.rect.center = (self.x,self.y)
		self.rot_rect.center = self.rect.center
		self.col_rect.center = self.rot_rect.center
		
		self.angularVelocity *= self.friction
		
		self.main_image = self.anim_object.image.copy()
		self.image = pygame.transform.rotate(self.main_image,self.missileOrientation)
		self.rot_rect = self.image.get_rect(center=self.rect.center)

