import pygame,math,random
import sgf.gameobjects.steer_objects as steer
import sgf.utils.g_utils as gutils
import projectile

class BasicGun(object):
	def __init__(self,player):
		
		self.kind = "BasicGun"
		self.player = player
		self.fireacctime = 0  
		self.bullet_speed = 2.0
		self.friction = 1.0
		self.base_damage = 2.0
		self.base_fire_rate = 180
		self.fire_rate = 180
		self.damage = 3.0
		
		# load image 
		self.path = "images\\bullet.png"
		
	def fire(self):
		if self.fireacctime > self.fire_rate:
			self.fireacctime = 0
			
			# launch bullet
			new_bullet = projectile.AnimatedBullet(self.path,self.player.magic_orb.rect.centerx,
										self.player.magic_orb.rect.centery,
										6,6,
										self.player.firing_angle,speed = self.bullet_speed,
										friction = self.friction,
										fps=18,
										rotate=False,trail=True)
			self.player.bullets_list.append(new_bullet)
			self.player.sound_manager.play("basic.ogg")
			
	def update(self,timepassed):
		self.fireacctime += timepassed
	
	def draw(self,Surface):
		pass

class WaveyGun(object):
	def __init__(self,player):
		
		self.kind = "WaveyGun"
		self.player = player
		self.fireacctime = 0  
		self.bullet_speed = 2.0
		self.friction = 1.0
		
		self.base_damage = 2.0
		self.base_fire_rate = 180
		self.fire_rate = 180
		self.damage = 8.0
		self.mana_req = 6
		
		# load image 
		self.path = "images\\dual_proj.png"
		
		
	def fire(self):
		
		if self.player.mana_amount >= self.mana_req:
			if self.fireacctime > self.fire_rate:
				self.fireacctime = 0
			
			
				new_bullet = projectile.WaveyBullet(self.path,self.player.magic_orb.rect.centerx,self.player.magic_orb.rect.centery,
										8,8,
										self.player.firing_angle,speed = self.bullet_speed,
										friction = self.friction,
										fps=12,
										rotate=True)
				self.player.bullets_list.append(new_bullet)
				self.player.mana_amount -= self.mana_req
				self.player.sound_manager.play("wavey.ogg")
			
				
	def update(self,timepassed):
		self.fireacctime += timepassed
	
	def draw(self,Surface):
		pass

class PiercerGun(object):
	def __init__(self,player):
		
		self.kind = "PiercerGun"
		self.player = player
		self.fireacctime = 0  
		self.bullet_speed = 3.7
		self.friction = 1.0
		
		self.base_damage = 2.0
		self.base_fire_rate = 180
		self.fire_rate = 180
		self.damage = 4.0
		self.mana_req = 12
		
		# load image 
		self.path = "images\\piercer_proj.png"
		
		
	def fire(self):
		
		if self.player.mana_amount >= self.mana_req:
			if self.fireacctime > self.fire_rate:
				self.fireacctime = 0
			
			
				new_bullet = projectile.PiercerBullet(self.path,self.player.magic_orb.rect.centerx,self.player.magic_orb.rect.centery,
										8,8,
										self.player.firing_angle,speed = self.bullet_speed,
										friction = self.friction,
										fps=12,
										rotate=True)
				self.player.bullets_list.append(new_bullet)
				self.player.mana_amount -= self.mana_req
				self.player.sound_manager.play("piercer.ogg")
			
				
	def update(self,timepassed):
		self.fireacctime += timepassed
	
	def draw(self,Surface):
		pass
		
class RandomGun(object):
	def __init__(self,player):
		
		self.kind = "RandomGun"
		self.player = player
		self.fireacctime = 0  
		self.bullet_speed = 2.0
		self.friction = 0.97
		
		self.base_damage = 2.0
		self.base_fire_rate = 180
		self.fire_rate = 180
		self.damage = 1.0
		self.mana_req = 3
		
		# load image 
		self.path = "images\\rand_proj.png"
		
		
	def fire(self):
		
		if self.player.mana_amount >= self.mana_req:
			if self.fireacctime > self.fire_rate:
				self.fireacctime = 0
			
				#if len(self.player.enemyList) > 0:
				#	target = random.choice(self.player.enemyList)
				#else:
				target = self.player
				
				new_bullet = projectile.RandomBullet(self.path,self.player.magic_orb.rect.centerx,self.player.magic_orb.rect.centery,
										8,8,
										target=target,speed = self.bullet_speed,
										friction = self.friction,
										fps=12)
				self.player.bullets_list.append(new_bullet)
				self.player.mana_amount -= self.mana_req
				self.player.sound_manager.play("dual.ogg")
			
	def update(self,timepassed):
		self.fireacctime += timepassed
	
	def draw(self,Surface):
		pass

		
class BounceGun(object):
	def __init__(self,player):
		
		self.kind = "BounceGun"
		self.player = player
		self.fireacctime = 0  
		self.bullet_speed = 2.0
		self.friction = 1.0
		
		self.base_damage = 2.0
		self.base_fire_rate = 180
		self.fire_rate = 180
		self.damage = 4.0
		self.mana_req = 8
		
		# load image 
		self.path = "images\\bounce_proj.png"
		
		
	def fire(self):
		if self.player.mana_amount >= self.mana_req:
			if self.fireacctime > self.fire_rate:
				self.fireacctime = 0
			
			
				new_bullet = projectile.BounceBullet(self.path,self.player.magic_orb.rect.centerx,self.player.magic_orb.rect.centery,
											8,8,
											self.player.firing_angle,speed = self.bullet_speed,
											friction = self.friction,
											fps=12,
											rotate=True)
				self.player.bullets_list.append(new_bullet)
				self.player.mana_amount -= self.mana_req
				self.player.sound_manager.play("bounce_w.ogg")
			
	def update(self,timepassed):
		self.fireacctime += timepassed
	
	def draw(self,Surface):
		pass
		
		
class DualGun(object):
	def __init__(self,player):
		
		self.kind = "DualGun"
		self.player = player
		self.fireacctime = 0  
		self.bullet_speed = 2.0
		self.friction = 1.0
		
		self.base_damage = 2.0
		self.base_fire_rate = 180
		self.fire_rate = 180
		self.damage = 2.0
		self.mana_req = 7
		
		
		# load image 
		self.path = "images\\dual_proj.png"
		
		
	def fire(self):
		if self.player.mana_amount >= self.mana_req:
			if self.fireacctime > self.fire_rate:
				self.fireacctime = 0
			
				dirs = [self.player.firing_angle-5,self.player.firing_angle+5]
			
				for i in range(2):
					# launch bullet
					new_bullet = projectile.AnimatedBullet(self.path,self.player.magic_orb.rect.centerx,self.player.magic_orb.rect.centery,
												8,8,
												dirs[i],speed = self.bullet_speed,
												friction = self.friction,
												fps=12,
												rotate=True,trail=True)
					self.player.bullets_list.append(new_bullet)
					self.player.mana_amount -= self.mana_req
					self.player.sound_manager.play("softgun.ogg")
			
				
	def update(self,timepassed):
		self.fireacctime += timepassed
	
	def draw(self,Surface):
		pass

class FlameGun(object):
	def __init__(self,player):
		
		self.kind = "FlameGun"
		self.player = player
		self.fireacctime = 0  
		self.bullet_speed = 3.0
		self.friction = 0.97
		
		self.base_damage = 0.5
		self.base_fire_rate = 100
		self.fire_rate = 100
		self.damage = 0.5
		self.mana_req = 7
		
		# load image 
		self.path = "images\\flame_proj.png"
		
		
	def fire(self):
	
		if self.player.mana_amount >= self.mana_req:
			if self.fireacctime > self.fire_rate:
				self.fireacctime = 0
			
				dir = random.randrange(int(self.player.firing_angle)-5,int(self.player.firing_angle)+5)
			
				new_bullet = projectile.FlameBullet(self.path,self.player.magic_orb.rect.centerx,self.player.magic_orb.rect.centery,
											12,12,
											dir,speed = self.bullet_speed,
											friction = self.friction,
											fps=10,
											rotate=True)
				self.player.bullets_list.append(new_bullet)
				self.player.mana_amount -= self.mana_req
				self.player.sound_manager.play("flame.ogg")
			
				
	def update(self,timepassed):
		self.fireacctime += timepassed
	
	def draw(self,Surface):
		pass

		
class LightningGun(object):
	def __init__(self,player):
	
		self.kind = "LightningGun"
		self.player = player
		self.is_firing = False
		self.t_object = None
		self.fire_range = 100
		self.fire_waittime = 0
		self.nodes_lists = []
		self.fireacctime = 0
		self.fire_duration = 800
		
		self.base_damage = 2.0
		self.base_fire_rate = 1000
		self.fire_rate = 1000
		self.damage = 0.18 #0.18
		self.mana_req = 12
			
	def fire(self):
		
		if self.player.mana_amount >= self.mana_req:
			if not self.is_firing:
				if self.fire_waittime > self.fire_rate:
			
					if self.t_object is not None:
						self.is_firing = True
						self.fire_waittime = 0
						self.fireacctime = 0
						
						self.player.mana_amount -= self.mana_req
						self.player.cam_tracker.shake([abs(self.player.firing_vector[0])*2.8,80,0.08],
											[abs(self.player.firing_vector[1])*2.8,80,0.08])
						
						self.player.sound_manager.play("lightning_s.ogg")
			
	def isEnemyInRange(self):
		
		for enemy in self.player.enemyList:
			# calculate distance to enemy
			xvec = enemy.rect.centerx - self.player.magic_orb.rect.centerx
			yvec = enemy.rect.centery - self.player.magic_orb.rect.centery
			delta_dist = math.sqrt(xvec*xvec + yvec*yvec)
			
			if delta_dist < self.fire_range:
				self.t_object = enemy
				return
		
		self.t_object = None
	
	def calculateRandomNodes(self,num_nodes=5):
		
		self.nodes_lists = []
		# get vector to t_object
		xvec = self.t_object.rect.centerx - self.player.magic_orb.rect.centerx
		yvec = self.t_object.rect.centery - self.player.magic_orb.rect.centery
		
		# calculate angle
		radangle = math.atan2(yvec,xvec)
		angle = int(radangle * (180/math.pi))
		
		magnitude = math.sqrt(xvec*xvec + yvec*yvec)
		
		xvec_n = xvec / magnitude
		yvec_n = yvec / magnitude
		
		self.nodes_lists.append((self.player.magic_orb.rect.centerx,self.player.magic_orb.rect.centery))
		
		for i in range(num_nodes,1,-1):
			angle_rand = random.randrange(angle-20,angle+20)
			angle_xvec = math.cos(angle_rand*(math.pi/180))
			angle_yvec = math.sin(angle_rand*(math.pi/180))
			
			dist = magnitude/float(i)
			#print dist
			angle_xvec *= dist
			angle_yvec *= dist
			
			x_point = self.player.magic_orb.rect.centerx + angle_xvec
			y_point = self.player.magic_orb.rect.centery + angle_yvec
			self.nodes_lists.append((x_point,y_point))
			
		self.nodes_lists.append((self.t_object.rect.centerx,self.t_object.rect.centery))
			
	def update(self,timepassed):
		
		self.fire_waittime += timepassed
		
		self.isEnemyInRange()
				
		#print len(self.nodes_lists)
		if self.is_firing:
			
			self.fireacctime += timepassed
			
			if self.fireacctime > self.fire_duration:
				self.is_firing = False
			
			if self.t_object is not None:
				self.calculateRandomNodes()
				self.t_object.health -= self.damage
				self.t_object.flash()
				
	def draw(self,Surface):
		
		if self.t_object is not None and self.is_firing:
			if len(self.nodes_lists):
				pygame.draw.lines(Surface,(0,190,255),False,self.nodes_lists,3)
			
			if len(self.nodes_lists):
				pygame.draw.lines(Surface,(255,255,255),False,self.nodes_lists)
		
		if self.t_object is not None:
			pygame.draw.circle(Surface,(240,140,140),self.t_object.rect.center,10,1)
			#for node in self.nodes_lists:
			#	pygame.draw.circle(Surface,(255,255,255),node,2)
			
class BoomerangGun(object):
	def __init__(self,orb):
		
		self.orb = orb
		self.x = self.orb.rect.x
		self.y = self.orb.rect.y
		self.boomerang_image = pygame.image.load("images\\boomerang.png").convert_alpha()
		self.image_to_draw = self.boomerang_image.copy()
		self.rot_rect = self.boomerang_image.get_rect()
		self.rect = self.boomerang_image.get_rect()
		self.rect.topleft = (self.x,self.y) 
		self.follower = steer.Steerable("DArriveMovement",(self.orb.x,self.orb.y),8,8)
		self.follower.setTarget(self.orb.owner.weapon_target)
		self.dx = 0
		self.dy = 0
		
		self.spin_angle = 0
		self.spin_speed = 5
		self.is_firing = False
		self.launch_velocity = 6.0
		
	def launch(self):
		
		# get launch direction
		launch_dir = self.orb.owner.firing_angle
		launch_x = math.cos(launch_dir*(math.pi/180))
		launch_y = math.sin(launch_dir*(math.pi/180))
		
		launch_x *= self.launch_velocity
		launch_y *= self.launch_velocity
		self.x = self.orb.rect.x
		self.y = self.orb.rect.y
		
		self.dx += launch_x
		self.dy += launch_y
		self.is_firing = True
		
	def update(self,timepassed):
		
		self.follower.x = self.x
		self.follower.y = self.y
		
		self.follower.update(timepassed)
		
		self.spin_angle += self.spin_speed
		
		#if self.is_firing:
		self.image_to_draw = pygame.transform.rotate(self.boomerang_image,self.spin_angle)
		self.rot_rect = self.image_to_draw.get_rect(center=self.rect.center)	
		if not self.is_firing:
			self.x = self.orb.rect.x
			self.y = self.orb.rect.y
		
		#print self.follower.velocity
		self.dx += (self.follower.velocity.x * 0.03 )
		self.dy += (self.follower.velocity.y * 0.03 )
		self.x += self.dx
		self.y += self.dy
		
		self.dx *= 0.97
		self.dy *= 0.97
		
		self.rect.topleft = (self.x,self.y)
		
	def draw(self,Surface):
		#if self.is_firing:
		pass	
		#Surface.blit(self.image_to_draw,self.rot_rect)
		
				
class Orb(object):
	def __init__(self,target,owner):
		self.owner = owner
		self.x = target.position.x
		self.y = target.position.y
		self.controller = steer.Steerable("DArriveMovement",(self.x,self.y),8,8)
		self.controller.setTarget(target)
		self.image = pygame.image.load("images\\orb.png").convert()
		self.image.set_colorkey((255,0,255))
		self.image.set_alpha(210)
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.x,self.y)
		self.gun = BoomerangGun(self)	
			
	def update(self,timepassed):
		self.controller.update(timepassed)
		self.x = self.controller.x
		self.y = self.controller.y
		self.rect.topleft = (self.x,self.y)
		
		self.gun.update(timepassed)
		
	def draw(self,Surface):
		Surface.blit(self.image,self.rect)
		
		self.gun.draw(Surface)
