import pygame,random,math
from pygame.locals import*
import sgf.gameobjects.steer_objects as steer
import sgf.utils.g_utils as gutils
import sgf.gameobjects.g_objects as gobs
import sgf.behaviours.steering_behaviours as sb
import sgf.utils.helpers as helpers
import projectile
from cnst import*

TILESIZE = TILE_W

class Enemy(object):
	def __init__(self,x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed = 0.2,health=30):
		
		self.itemList = itemList
		self.tileList = tileList
		self.grid = grid
		self.x = x
		self.y = y
		self.w = 16
		self.h = 16
		self.hx = self.w / 2
		self.hy = self.h / 2
		self.alive = True
		self.has_died = False
		self.health = health
		self.x_moverange = 40
		self.y_moverange = 40
		self.dx = 0
		self.dy = 0
		self.damage = 5
		self.holds_key = False
	
		self.speed = speed
		self.rect = pygame.Rect(self.x,self.y,self.w,self.h)
		self.col_rect = pygame.Rect(self.x,self.y,self.w,self.h)
		
		self.controller = steer.Steerable("KSeekMovement",(self.x,self.y),16,16)
		self.controller.current_steering_behaviour.setMaxSpeed(self.speed)
		
		self.targ = sb.Target((self.x,self.y))
		self.controller.setTarget(self.targ)
		self.is_moving = False
		self.is_flashing = False
		self.flash_duration = 600
		self.flash_acctime = 5000
		
		self.blink_acctime = 0
		self.blink_updatetime = 50
		self.is_blend_visible = False
		
		
		self.blendimage = None
		self.blendcolor = (255,0,0)
		
		
		
		self.acctime_duration = 0
		self.move_duration = 2000
		self.acctime_to_move = 0
		self.move_updatetime = 2000
		self.good_guys = good_guys
		self.effects = effects
		self.images_dict = images_dict
	
	def setKey(self):
		self.holds_key = True
	
	def resolveCollisions(self,plat):
		"""Resolves but has jitter"""
		
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
				self.dx = 0
				self.controller.x = plat.rect.left - (self.w)
				#print "colliding left"
					
			else:
			#push right
				if abs(self.dx)>1:
					self.dx = 0
				self.controller.x = plat.rect.right
				#print "colliding right"
					
		elif minpen==ypen and x_intersect > 0:
			# project out along y axis
			if ydist > 0:
				# push up
				self.dy = 0
				self.controller.y = plat.rect.top-(self.h)	# push up but leave 1px in tile
				#print "colliding top"
				
			else:
				#push down
				self.dy = 0
				self.controller.y = plat.rect.bottom
				#print "colliding bottom"
	
	def flash(self):
		pass
	
	def checkCollisions(self):
		
		#grid_xpos = int(math.floor((self.x/16)))
		#grid_ypos = int(math.floor((self.y/16)))
		
		grid_xpos = int(self.x)/16
		grid_ypos = int(self.y)/16
		
		for wall in self.tileList:
			if wall.collidable:
				#wallgrid_xpos = int(math.floor((wall.x/16)))
				#wallgrid_ypos = int(math.floor((wall.y/16)))
			
				wallgrid_xpos = int(wall.x)/16
				wallgrid_ypos = int(wall.y)/16
			
			
				if wallgrid_xpos in range(grid_xpos,grid_xpos+2) and\
					wallgrid_ypos in range(grid_ypos,grid_ypos+2):
			
					if self.col_rect.colliderect(wall.rect):
						self.resolveCollisions(wall)
		
		for item in self.itemList:
			if item.kind == "FireCrate":
				
				crategrid_xpos = int(item.x)/16
				crategrid_ypos = int(item.y)/16
			
				if crategrid_xpos in range(grid_xpos-2,grid_xpos+2) and\
					crategrid_ypos in range(grid_ypos-2,grid_ypos+2):
			
					if self.col_rect.colliderect(item.rect):
						self.resolveCollisions(item)
		
		
	def getValidMovePositions(self):
		
		valid_spaces = []
		for row in self.grid.rows:
			for square in row:
				if not square.blocked:
					if square.coord[0] in xrange((int(self.x)-self.x_moverange)/TILESIZE,(int(self.x)+self.x_moverange)/TILESIZE) and\
					square.coord[1] in xrange((int(self.y)-self.y_moverange)/TILESIZE,(int(self.y)+self.y_moverange)/TILESIZE):
						valid_spaces.append((square.coord[0]*TILESIZE,square.coord[1]*TILESIZE))
		
		return valid_spaces
		
	def moveTo(self):
		
		if self.acctime_to_move > self.move_updatetime:
			self.acctime_to_move = 0
			
			valid_spaces = self.getValidMovePositions()
			
			if len(valid_spaces)>0:
				move_pos = random.choice(valid_spaces)
				
				self.targ.position.x = move_pos[0]
				self.targ.position.y = move_pos[1]
				
	
	def update(self,timepassed):
		
		if self.health <= 0:
			self.alive = False
		
		self.acctime_to_move += timepassed
		
		self.moveTo()
		
		self.controller.update(timepassed)
		
		self.x,self.y = (self.controller.x,self.controller.y)
		
		self.checkCollisions()
		
		self.rect.topleft = (self.x,self.y)
		self.col_rect.topleft = (self.x,self.y)
	
	def draw(self,Surface):
		pygame.draw.rect(Surface,(0,200,0),self.rect)
		

class Boneman(Enemy):
	def __init__(self,x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed = 0.2,health=30):
		
		super(Boneman,self).__init__(x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed,health)
		self.damage = 10
		
		stand_list = gutils.sliceSheetColKey(self.w,self.h,"images\\boneman_stand.png")
		moveleft_list = gutils.sliceSheetColKey(self.w,self.h,"images\\boneman_moveleft.png")
		moveright_list = gutils.sliceSheetColKey(self.w,self.h,"images\\boneman_moveright.png")
		
		
		self.proj_images = "images\\bone_proj.png"
		
		params = [2,2,2]
		
		self.id = 0
		self.frame = 0
		
		self.image_master = [stand_list,moveleft_list,moveright_list]
		self.animator = helpers.AnimManager(params,6)
		self.image = self.image_master[self.id][self.frame]
		
		self.bullets_list = []
		self.fire_acctime = 0
		self.fire_updatetime = random.randrange(1000,6000)
		
	def fire(self):
		
		if self.fire_acctime > self.fire_updatetime:
			
			# get dir_to_player
			player = self.good_guys[0]
			
			x = int(self.rect.x)
			y = int(self.rect.y)
			
			if player.rect.x in range(x-100, x+100) and\
				player.rect.y in range(y-100, y+100):
				
				self.fire_acctime = 0
				self.fire_updatetime = random.randrange(1000,6000)
			
				xvec = player.rect.centerx - self.rect.centerx
				yvec = player.rect.centery - self.rect.centery
			
				dir_to_player = math.atan2(yvec,xvec) * (180/math.pi)
			
				# launch projectile
				new_bullet = projectile.AnimatedBullet(self.proj_images,self.rect.centerx,
													self.rect.centery,12,12,dir_to_player,speed=1.2)
				self.bullets_list.append(new_bullet)
				
	def updateBullets(self,timepassed):
		
		for bullet in self.bullets_list:
			bullet.update(timepassed)
	
	def drawBullets(self,Surface):
		for bullet in self.bullets_list:
			bullet.draw(Surface)
	
	def update(self,timepassed):
		
		self.fire_acctime += timepassed
		self.flash_acctime += timepassed
		self.blink_acctime += timepassed
		super(Boneman,self).update(timepassed)
		
		player = self.good_guys[0]
		
		if self.blink_acctime > self.blink_updatetime:
			self.blink_acctime = 0
			self.is_blend_visible = not(self.is_blend_visible)
		
		if self.controller.current_steering_behaviour.vel.x > 0.1:
			self.id = 2
			self.animator.play(self.id,timepassed)
			self.frame = self.animator.getFrame()[1]
		
		elif self.controller.current_steering_behaviour.vel.x < -0.05:
			self.id = 1
			self.animator.play(self.id,timepassed)
			self.frame = self.animator.getFrame()[1]
		
		
		self.image = self.image_master[self.id][self.frame]
		self.handleFlashing()
		
		self.fire()
		
		# check against walls
		self.updateBullets(timepassed)
		for bullet in self.bullets_list:	
			for wall in self.tileList:
				if bullet.col_rect.colliderect(wall.col_rect):
					bullet.alive = False
		
		# check against items
		for bullet in self.bullets_list:	
			for item in self.itemList:
				if item.kind == "FireCrate":
					if bullet.col_rect.colliderect(item.col_rect):
						bullet.alive = False
		
		for bullet in self.bullets_list:
			if not player.is_flashing:
				if bullet.col_rect.colliderect(player.rect):
					bullet.alive = False
					player.flash()
					player.health -= self.damage
					
					player.sound_manager.play("lose.ogg")
					
		for bullet in self.bullets_list:
			if not bullet.alive:
				self.bullets_list.remove(bullet)
		
				# add collision effect
				params = [self.images_dict["hit"][0],1,10]
				new_effect = gobs.AnimObject(params,bullet.rect.centerx,bullet.rect.centery,0,0,1)
				self.effects.append(new_effect)
				#print self.effects
	
	def handleFlashing(self):
		
		if self.flash_acctime < self.flash_duration: 
			self.is_flashing = True
		else:
			self.is_flashing = False
		
		if self.is_flashing:
			self.blendimage = self.image.copy().convert_alpha()
			self.blendimage.fill((0,0,0,150), None, BLEND_RGBA_MULT)
			self.blendimage.fill(self.blendcolor[0:3] + (0,), None, BLEND_RGBA_ADD)
		
	
	def flash(self):
		
		if not self.is_flashing:
			self.flash_acctime = 0
			
				
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)
		
		if self.is_flashing:
			if self.is_blend_visible:
				Surface.blit(self.blendimage,self.rect)
		
		self.drawBullets(Surface)
		
class Sprout(Enemy):
	def __init__(self,x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed = 0.4,health=30):
		
		super(Sprout,self).__init__(x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed,health)
		self.damage = 4
		
		stand_list = gutils.sliceSheetColKey(self.w,self.h,"images\\sprout_stand.png")
		moveleft_list = gutils.sliceSheetColKey(self.w,self.h,"images\\sprout_moveleft.png")
		moveright_list = gutils.sliceSheetColKey(self.w,self.h,"images\\sprout_moveright.png")
		
		
		sprout_proj_images = gutils.sliceSheetColKey(12,12,"images\\sprout_proj.png")
		
		params = [2,2,2]
		
		self.id = 0
		self.frame = 0
		
		self.image_master = [stand_list,moveleft_list,moveright_list]
		self.animator = helpers.AnimManager(params,6)
		self.image = self.image_master[self.id][self.frame]
		
		self.bullets_list = []
		self.fire_acctime = 0
		self.fire_updatetime = random.randrange(2000,6000)
		self.x_moverange = 70
		self.y_moverange = 70
		
	def fire(self):
		
		if self.fire_acctime > self.fire_updatetime:
			
			# get dir_to_player
			player = self.good_guys[0]
			
			x = int(self.rect.x)
			y = int(self.rect.y)
			
			if player.rect.x in range(x-100, x+100) and\
				player.rect.y in range(y-100, y+100):
				
				self.fire_acctime = 0
				self.fire_updatetime = random.randrange(2000,6000)
			
				dirs = [0,45,90,135,180,225,270,315]
				
				# launch projectile
				for dir in dirs:
					new_bullet = projectile.AnimatedBullet("images\\sprout_proj.png",self.rect.centerx,
														self.rect.centery,12,12,dir,speed=2.0,rotate=True,trail=True)
					self.bullets_list.append(new_bullet)
				
	def updateBullets(self,timepassed):
		
		for bullet in self.bullets_list:
			bullet.update(timepassed)
	
	def drawBullets(self,Surface):
		for bullet in self.bullets_list:
			bullet.draw(Surface)
	
	def update(self,timepassed):
		
		self.fire_acctime += timepassed
		self.flash_acctime += timepassed
		self.blink_acctime += timepassed
		super(Sprout,self).update(timepassed)
		
		player = self.good_guys[0]
		
		if self.blink_acctime > self.blink_updatetime:
			self.blink_acctime = 0
			self.is_blend_visible = not(self.is_blend_visible)
		
		if self.controller.current_steering_behaviour.vel.x > 0.1:
			self.id = 2
			self.animator.play(self.id,timepassed)
			self.frame = self.animator.getFrame()[1]
		
		elif self.controller.current_steering_behaviour.vel.x < -0.05:
			self.id = 1
			self.animator.play(self.id,timepassed)
			self.frame = self.animator.getFrame()[1]
		
		
		self.image = self.image_master[self.id][self.frame]
		self.handleFlashing()
		
		self.fire()
		
		self.updateBullets(timepassed)
		for bullet in self.bullets_list:	
			for wall in self.tileList:
				if bullet.rect.colliderect(wall.rect):
					bullet.alive = False
		
		# check against items
		for bullet in self.bullets_list:	
			for item in self.itemList:
				if item.kind == "FireCrate":
					if bullet.col_rect.colliderect(item.col_rect):
						bullet.alive = False
		
		for bullet in self.bullets_list:
			if not player.is_flashing:
				if bullet.rect.colliderect(player.rect):
					bullet.alive = False
					player.flash()
					player.health -= self.damage
					player.sound_manager.play("lose.ogg")
					
		for bullet in self.bullets_list:
			if not bullet.alive:
				self.bullets_list.remove(bullet)
		
				# add collision effect
				params = [self.images_dict["hit"][0],1,10]
				new_effect = gobs.AnimObject(params,bullet.rect.centerx,bullet.rect.centery,0,0,1)
				self.effects.append(new_effect)
				#print self.effects
	
	def handleFlashing(self):
		
		if self.flash_acctime < self.flash_duration: 
			self.is_flashing = True
		else:
			self.is_flashing = False
		
		if self.is_flashing:
			self.blendimage = self.image.copy().convert_alpha()
			self.blendimage.fill((0,0,0,150), None, BLEND_RGBA_MULT)
			self.blendimage.fill(self.blendcolor[0:3] + (0,), None, BLEND_RGBA_ADD)
		
	
	def flash(self):
		
		if not self.is_flashing:
			self.flash_acctime = 0
			
				
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)
		
		if self.is_flashing:
			if self.is_blend_visible:
				Surface.blit(self.blendimage,self.rect)
		
		self.drawBullets(Surface)
		
class Buzzer(Enemy):
	def __init__(self,x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed = 0.6,health=30):
		
		super(Buzzer,self).__init__(x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed,health)
		self.damage = 5
		
		moveleft_list = gutils.sliceSheetColKey(self.w,self.h,"images\\buzzer_moveleft.png")
		moveright_list = gutils.sliceSheetColKey(self.w,self.h,"images\\buzzer_moveright.png")
		
		sprout_proj_images = gutils.sliceSheetColKey(12,12,"images\\sprout_proj.png")
		
		params = [2,2,2]
		
		self.id = 0
		self.frame = 0
		
		self.image_master = [moveleft_list,moveright_list]
		self.animator = helpers.AnimManager(params,24)
		self.image = self.image_master[self.id][self.frame]
		
		self.bullets_list = []
		self.fire_acctime = 0
		self.fire_updatetime = random.randrange(2000,6000)
		self.x_moverange = 70
		self.y_moverange = 70
		self.sin_angle = 0
		self.wave_speed = 20
		self.wave_strength = 2.0
		
	def fire(self):
		
		if self.fire_acctime > self.fire_updatetime:
			
			# get dir_to_player
			player = self.good_guys[0]
			
			x = int(self.rect.x)
			y = int(self.rect.y)
			
			if player.rect.x in range(x-100, x+100) and\
				player.rect.y in range(y-100, y+100):
				
				self.fire_acctime = 0
				self.fire_updatetime = random.randrange(2000,6000)
			
				dirs = [0,180,90,270]
				facing = random.choice(dirs)
					
				# launch projectile
				for i in range(8):
					dir = random.randrange(facing-15,facing+15)
					new_bullet = projectile.AnimatedBullet("images\\fly_proj.png",self.rect.centerx,
														self.rect.centery,8,8,dir,friction=1.01,speed=1.98,rotate=True)
					self.bullets_list.append(new_bullet)
				
	def updateBullets(self,timepassed):
		
		for bullet in self.bullets_list:
			bullet.update(timepassed)
	
	def drawBullets(self,Surface):
		for bullet in self.bullets_list:
			bullet.draw(Surface)
	
	def update(self,timepassed):
		
		self.fire_acctime += timepassed
		self.flash_acctime += timepassed
		self.blink_acctime += timepassed
		super(Buzzer,self).update(timepassed)
		
		player = self.good_guys[0]
		
		if self.blink_acctime > self.blink_updatetime:
			self.blink_acctime = 0
			self.is_blend_visible = not(self.is_blend_visible)
		
		if self.controller.current_steering_behaviour.vel.x >= 0:
			self.id = 1
			self.animator.play(self.id,timepassed)
			self.frame = self.animator.getFrame()[1]
		
		elif self.controller.current_steering_behaviour.vel.x < 0:
			self.id = 0
			self.animator.play(self.id,timepassed)
			self.frame = self.animator.getFrame()[1]
		
		
		self.image = self.image_master[self.id][self.frame]
		self.handleFlashing()
		
		self.fire()
		
		self.updateBullets(timepassed)
		for bullet in self.bullets_list:	
			for wall in self.tileList:
				if bullet.rect.colliderect(wall.rect):
					bullet.alive = False
		
		# check against items
		for bullet in self.bullets_list:	
			for item in self.itemList:
				if item.kind == "FireCrate":
					if bullet.col_rect.colliderect(item.col_rect):
						bullet.alive = False
		
		for bullet in self.bullets_list:
			if not player.is_flashing:
				if bullet.rect.colliderect(player.rect):
					bullet.alive = False
					player.flash()
					player.health -= self.damage
					player.sound_manager.play("lose.ogg")
					
		for bullet in self.bullets_list:
			if not bullet.alive:
				self.bullets_list.remove(bullet)
		
				# add collision effect
				params = [self.images_dict["hit"][0],1,10]
				new_effect = gobs.AnimObject(params,bullet.rect.centerx,bullet.rect.centery,0,0,1)
				self.effects.append(new_effect)
				#print self.effects
		
		self.sin_angle += self.wave_speed
		
		self.y += self.wave_strength * math.sin(self.sin_angle * (math.pi/180))
		self.rect.topleft = (self.x,self.y)
		self.col_rect.topleft = self.rect.topleft
		
	def handleFlashing(self):
		
		if self.flash_acctime < self.flash_duration: 
			self.is_flashing = True
		else:
			self.is_flashing = False
		
		if self.is_flashing:
			self.blendimage = self.image.copy().convert_alpha()
			self.blendimage.fill((0,0,0,150), None, BLEND_RGBA_MULT)
			self.blendimage.fill(self.blendcolor[0:3] + (0,), None, BLEND_RGBA_ADD)
		
	
	def flash(self):
		
		if not self.is_flashing:
			self.flash_acctime = 0
			
				
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)
		
		if self.is_flashing:
			if self.is_blend_visible:
				Surface.blit(self.blendimage,self.rect)
		
		self.drawBullets(Surface)
		
class Ghost(Enemy):
	def __init__(self,x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed = 0.4,health=20):
		
		super(Ghost,self).__init__(x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed,health)
		self.damage = 8
		
		stand_list = gutils.sliceSheetColKey(self.w,self.h,"images\\ghost_stand.png")
		moveleft_list = gutils.sliceSheetColKey(self.w,self.h,"images\\ghost_moveleft.png")
		moveright_list = gutils.sliceSheetColKey(self.w,self.h,"images\\ghost_moveright.png")
		
		
		self.ray_colors = [(255,0,0),(255,255,255),(0,255,0),(255,255,0)]
		self.color_id = 0
		self.can_draw_ray = False
		self.ray_draw_acctime = 5000
		self.ray_draw_duration = 2500
		self.hit_tile = None
		
		sprout_proj_images = gutils.sliceSheetColKey(12,12,"images\\sprout_proj.png")
		
		params = [2,2,2]
		
		self.id = 0
		self.frame = 0
		
		self.image_master = [stand_list,moveleft_list,moveright_list]
		self.animator = helpers.AnimManager(params,6)
		self.image = self.image_master[self.id][self.frame]
		
		self.bullets_list = []
		self.fire_acctime = 0
		self.fire_updatetime = random.randrange(3000,6000)
		self.x_moverange = 70
		self.y_moverange = 70
		
	def fire(self):
		
		if self.fire_acctime > self.fire_updatetime:
			
			# get dir_to_player
			player = self.good_guys[0]
			
			x = int(self.rect.x)
			y = int(self.rect.y)
			
			if player.rect.x in range(x-100, x+100) and\
				player.rect.y in range(y-100, y+100):
			
				self.fire_acctime = 0
				self.fire_updatetime = random.randrange(3000,6000)
			
				ppos = player.rect.center
				spos = self.rect.center
			
				result = self.grid.raycast(spos,ppos,16)
			
				if result:
					# draw a line to the tile
				
					for wall in self.tileList:
						if wall.x == result[1] * 16 and wall.y == result[0] *16:
							self.hit_tile = wall
							break
						
					self.ray_draw_acctime = 0
				
	def updateBullets(self,timepassed):
		
		for bullet in self.bullets_list:
			bullet.update(timepassed)
	
	def drawBullets(self,Surface):
		for bullet in self.bullets_list:
			bullet.draw(Surface)
	
	def update(self,timepassed):
		
		if self.health <= 0:
			self.alive = False
		
		self.fire_acctime += timepassed
		self.flash_acctime += timepassed
		self.blink_acctime += timepassed
		self.ray_draw_acctime += timepassed
	
		self.acctime_to_move += timepassed
		
		self.moveTo()
		
		if self.ray_draw_acctime > self.ray_draw_duration:
			self.controller.update(timepassed)
		
		self.x,self.y = (self.controller.x,self.controller.y)
		
		self.checkCollisions()
		
		self.rect.topleft = (self.x,self.y)
		self.col_rect.topleft = (self.x,self.y)
	
		
		if self.ray_draw_acctime > 1000 and self.ray_draw_acctime < self.ray_draw_duration:
			self.can_draw_ray = True
		else:
			self.can_draw_ray = False
		
		if self.blink_acctime > self.blink_updatetime:
			self.blink_acctime = 0
			self.is_blend_visible = not(self.is_blend_visible)
		
		if self.controller.current_steering_behaviour.vel.x > 0.1:
			self.id = 2
			self.animator.play(self.id,timepassed)
			self.frame = self.animator.getFrame()[1]
		
		elif self.controller.current_steering_behaviour.vel.x < -0.05:
			self.id = 1
			self.animator.play(self.id,timepassed)
			self.frame = self.animator.getFrame()[1]
		
		
		self.image = self.image_master[self.id][self.frame]
		self.handleFlashing()
		
		self.fire()
		
		self.updateBullets(timepassed)
		for bullet in self.bullets_list:	
			for wall in self.tileList:
				if bullet.rect.colliderect(wall.rect):
					bullet.alive = False
		
		# test ray collision with player
		player = self.good_guys[0]
		if self.can_draw_ray:
			ray_point1 = (float(self.hit_tile.rect.centerx),float(self.hit_tile.rect.centery))
			ray_point2 = (float(self.rect.centerx),float(self.rect.centery))
			if not player.is_flashing:
				for line in player.lines:
					result = player.line_collider.calculateIntersectPoint(line[0],line[1],ray_point1,ray_point2)
					if result is not None:
						player.health -= self.damage
						player.flash()
						player.sound_manager.play("lose.ogg")
					
						break
				
		for bullet in self.bullets_list:
			if not bullet.alive:
				self.bullets_list.remove(bullet)
		
				# add collision effect
				params = [self.images_dict["hit"][0],1,10]
				new_effect = gobs.AnimObject(params,bullet.rect.centerx,bullet.rect.centery,0,0,1)
				self.effects.append(new_effect)
				#print self.effects
	
	def renderRay(self,Surface):
		
		if self.can_draw_ray:
			
			self.color_id = (self.color_id + 1) % len(self.ray_colors)
			sizes = [3,4]
			size = random.choice(sizes)
			color = self.ray_colors[self.color_id]
			pygame.draw.line(Surface,color,(self.hit_tile.rect.centerx,self.hit_tile.rect.centery),(self.rect.centerx,self.rect.centery),size)
			#pygame.draw.line(Surface,(250,0,0),(self.hit_tile.rect.centerx,self.hit_tile.rect.centery),(self.rect.centerx,self.rect.centery),1)
		
		if self.ray_draw_acctime >0 and self.ray_draw_acctime <1000:
			pygame.draw.line(Surface,(100,0,0),(self.hit_tile.rect.centerx,self.hit_tile.rect.centery),(self.rect.centerx,self.rect.centery),1)
		
		
	def handleFlashing(self):
		
		if self.flash_acctime < self.flash_duration: 
			self.is_flashing = True
		else:
			self.is_flashing = False
		
		if self.is_flashing:
			self.blendimage = self.image.copy().convert_alpha()
			self.blendimage.fill((0,0,0,150), None, BLEND_RGBA_MULT)
			self.blendimage.fill(self.blendcolor[0:3] + (0,), None, BLEND_RGBA_ADD)
		
	
	def flash(self):
		
		if not self.is_flashing:
			self.flash_acctime = 0
			
				
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)
		
		if self.is_flashing:
			if self.is_blend_visible:
				Surface.blit(self.blendimage,self.rect)
		
		self.renderRay(Surface)
		self.drawBullets(Surface)

class Floorman(Enemy):
	def __init__(self,x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed = 0.4,health=20):
		super(Floorman,self).__init__(x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed,health)
		
		self.damage = 12
		self.speed = 0.8
		self.xvel = 0
		self.yvel = 0
		self.dirs = [0,90,180,270]
				
		self.bullets_list = []
		self.fire_acctime = 0
		self.fire_updatetime = 400
		
		self.move_dir = "left"
		self.image = pygame.image.load("images\\floorman.png").convert()
		self.image.set_colorkey((255,0,255))
		
	def update(self,timepassed):
		
		self.fire_acctime += timepassed
		self.flash_acctime += timepassed
		self.blink_acctime += timepassed
		
		player = self.good_guys[0]
		
		if self.blink_acctime > self.blink_updatetime:
			self.blink_acctime = 0
			self.is_blend_visible = not(self.is_blend_visible)
		
		if self.health <= 0:
			self.alive = False
		
		self.checkCollisions()
		
		if self.move_dir == "left":
			self.xvel = -self.speed
		else:
			self.xvel = self.speed
		
		self.handleFlashing()
		self.fire()
		
		self.updateBullets(timepassed)
		
		for bullet in self.bullets_list:	
			for wall in self.tileList:
				if bullet.rect.colliderect(wall.rect):
					bullet.alive = False
		
		# check against items
		for bullet in self.bullets_list:	
			for item in self.itemList:
				if item.kind == "FireCrate":
					if bullet.col_rect.colliderect(item.col_rect):
						bullet.alive = False
		
		for bullet in self.bullets_list:
			if not player.is_flashing:
				if bullet.rect.colliderect(player.rect):
					bullet.alive = False
					player.flash()
					player.health -= self.damage
					player.sound_manager.play("lose.ogg")
		
		if self.rect.colliderect(player.col_rect):
			player.flash()
			player.health -= self.damage/2
			player.sound_manager.play("lose.ogg")
		
		
		for bullet in self.bullets_list:
			if not bullet.alive:
				self.bullets_list.remove(bullet)
		
				# add collision effect
				params = [self.images_dict["hit"][0],1,10]
				new_effect = gobs.AnimObject(params,bullet.rect.centerx,bullet.rect.centery,0,0,1)
				self.effects.append(new_effect)
				#print self.effects
	
		self.x += self.xvel
		
		self.rect.topleft = (self.x,self.y)
		self.col_rect.topleft = (self.x,self.y)
	
	def resolveCollisions(self,plat):
		"""Resolves but has jitter"""
		
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
				self.dx = 0
				self.x = plat.rect.left - (self.w)
				#print "colliding left"
				self.move_dir = "left"	
			else:
			#push right
				if abs(self.dx)>1:
					self.dx = 0
				self.x = plat.rect.right
				#print "colliding right"
				self.move_dir = "right"
		elif minpen==ypen and x_intersect > 0:
			# project out along y axis
			if ydist > 0:
				# push up
				self.dy = 0
				self.y = plat.rect.top-(self.h)	# push up but leave 1px in tile
				#print "colliding top"
				
			else:
				#push down
				self.dy = 0
				self.y = plat.rect.bottom
				#print "colliding bottom"
	
	def fire(self):
		
		if self.fire_acctime > self.fire_updatetime:
			
			# get dir_to_player
			player = self.good_guys[0]
			
			x = int(self.rect.x)
			y = int(self.rect.y)
			
			if player.rect.x in range(x-250, x+250) and\
				player.rect.y in range(y-250, y+250):
				
				self.fire_acctime = 0
				self.fire_updatetime = random.randrange(800,1800)
				
				xvec = player.rect.centerx - self.rect.centerx
				yvec = player.rect.centery - self.rect.centery
			
				#dir = random.choice(self.dirs)
				dir = math.atan2(yvec,xvec) * (180/math.pi)
				
				fl = random.random()
				rand_int = random.randint(1,2)
				speed = rand_int+fl
				
				# launch projectile
				new_bullet = projectile.AnimatedBullet("images\\fr_proj.png",self.rect.centerx,
													self.rect.centery,12,12,dir,trail=True,speed=speed,fps=15)
				self.bullets_list.append(new_bullet)
				
	def updateBullets(self,timepassed):
		
		for bullet in self.bullets_list:
			bullet.update(timepassed)
	
	def drawBullets(self,Surface):
		for bullet in self.bullets_list:
			bullet.draw(Surface)
	
	def handleFlashing(self):
		
		if self.flash_acctime < self.flash_duration: 
			self.is_flashing = True
		else:
			self.is_flashing = False
		
		if self.is_flashing:
			self.blendimage = self.image.copy().convert_alpha()
			self.blendimage.fill((0,0,0,150), None, BLEND_RGBA_MULT)
			self.blendimage.fill(self.blendcolor[0:3] + (0,), None, BLEND_RGBA_ADD)
		
	
	def flash(self):
		
		if not self.is_flashing:
			self.flash_acctime = 0
			
				
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)
		
		if self.is_flashing:
			if self.is_blend_visible:
				Surface.blit(self.blendimage,self.rect)
		
		self.drawBullets(Surface)
		
class Magus(Boneman):
	def __init__(self,x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed = 0.6,health=30):
		
		super(Magus,self).__init__(x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed,health)
		self.damage = 10
		
		stand_list = gutils.sliceSheetColKey(self.w,self.h,"images\\magus_stand.png")
		moveleft_list = gutils.sliceSheetColKey(self.w,self.h,"images\\magus_moveleft.png")
		moveright_list = gutils.sliceSheetColKey(self.w,self.h,"images\\magus_moveright.png")
		
		self.proj_images = "images\\fr_proj.png"
		
		params = [2,2,2]
		
		self.id = 0
		self.frame = 0
		
		self.image_master = [stand_list,moveleft_list,moveright_list]
		self.animator = helpers.AnimManager(params,6)
		self.image = self.image_master[self.id][self.frame]
		
		self.bullets_list = []
		self.fire_acctime = 0
		self.fire_updatetime = random.randrange(2000,4000)

	def fire(self):
		
		if self.fire_acctime > self.fire_updatetime:
			
			# get dir_to_player
			player = self.good_guys[0]
			
			x = int(self.rect.x)
			y = int(self.rect.y)
			
			if player.rect.x in range(x-200, x+200) and\
				player.rect.y in range(y-200, y+200):
				
				self.fire_acctime = 0
				self.fire_updatetime = random.randrange(2000,4000)
			
				xvec = player.rect.centerx - self.rect.centerx
				yvec = player.rect.centery - self.rect.centery
			
				dir_to_player = math.atan2(yvec,xvec) * (180/math.pi)
			
				# launch projectile
				new_bullet = projectile.AnimatedBullet(self.proj_images,self.rect.centerx,
													self.rect.centery,12,12,dir_to_player-8,speed=1.1,trail=True)
				self.bullets_list.append(new_bullet)
				
				new_bullet = projectile.AnimatedBullet(self.proj_images,self.rect.centerx,
													self.rect.centery,12,12,dir_to_player,speed=0.9,trail=True)
				self.bullets_list.append(new_bullet)
				
				new_bullet = projectile.AnimatedBullet(self.proj_images,self.rect.centerx,
													self.rect.centery,12,12,dir_to_player+8,speed=0.8,trail=True)
				self.bullets_list.append(new_bullet)

class RedMagus(Boneman):
	def __init__(self,x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed = 0.6,health=30):
		
		super(RedMagus,self).__init__(x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed,health)
		self.damage = 15
		
		stand_list = gutils.sliceSheetColKey(self.w,self.h,"images\\redmagus_stand.png")
		moveleft_list = gutils.sliceSheetColKey(self.w,self.h,"images\\redmagus_moveleft.png")
		moveright_list = gutils.sliceSheetColKey(self.w,self.h,"images\\redmagus_moveright.png")
		
		self.proj_images = "images\\fr_proj.png"
		
		params = [2,2,2]
		
		self.id = 0
		self.frame = 0
		
		self.image_master = [stand_list,moveleft_list,moveright_list]
		self.animator = helpers.AnimManager(params,6)
		self.image = self.image_master[self.id][self.frame]
		
		self.bullets_list = []
		self.fire_acctime = 0
		self.fire_updatetime = random.randrange(2000,4000)

	def fire(self):
		
		if self.fire_acctime > self.fire_updatetime:
			
			# get dir_to_player
			player = self.good_guys[0]
			
			x = int(self.rect.x)
			y = int(self.rect.y)
			
			if player.rect.x in range(x-200, x+200) and\
				player.rect.y in range(y-200, y+200):
				
				self.fire_acctime = 0
				self.fire_updatetime = random.randrange(2000,4000)
			
				xvec = player.rect.centerx - self.rect.centerx
				yvec = player.rect.centery - self.rect.centery
			
				dir_to_player = math.atan2(yvec,xvec) * (180/math.pi)
			
				# launch projectile
				new_bullet = projectile.AnimatedBullet(self.proj_images,self.rect.centerx,
													self.rect.centery,12,12,dir_to_player-4,friction=1.01,speed=1.1,trail=True)
				self.bullets_list.append(new_bullet)
				
				new_bullet = projectile.AnimatedBullet(self.proj_images,self.rect.centerx,
													self.rect.centery,12,12,dir_to_player,friction=1.01,speed=1.1,trail=True)
				self.bullets_list.append(new_bullet)
				
				new_bullet = projectile.AnimatedBullet(self.proj_images,self.rect.centerx,
													self.rect.centery,12,12,dir_to_player+4,friction=1.01,speed=1.1,trail=True)
				self.bullets_list.append(new_bullet)

class BentMagus(Boneman):
	def __init__(self,x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed = 0.5,health=22):
		
		super(BentMagus,self).__init__(x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed,health)
		self.damage = 18
		
		stand_list = gutils.sliceSheetColKey(self.w,self.h,"images\\bent_stand.png")
		moveleft_list = gutils.sliceSheetColKey(self.w,self.h,"images\\bent_moveleft.png")
		moveright_list = gutils.sliceSheetColKey(self.w,self.h,"images\\bent_moveright.png")
		
		self.proj_images = "images\\rand_proj.png"
		
		params = [2,2,2]
		
		self.id = 0
		self.frame = 0
		
		self.image_master = [stand_list,moveleft_list,moveright_list]
		self.animator = helpers.AnimManager(params,6)
		self.image = self.image_master[self.id][self.frame]
		
		self.bullets_list = []
		self.fire_acctime = 0
		self.fire_updatetime = random.randrange(2000,4000)

	def fire(self):
		
		if self.fire_acctime > self.fire_updatetime:
			
			# get dir_to_player
			player = self.good_guys[0]
			
			x = int(self.rect.x)
			y = int(self.rect.y)
			
			if player.rect.x in range(x-200, x+200) and\
				player.rect.y in range(y-200, y+200):
				
				self.fire_acctime = 0
				self.fire_updatetime = random.randrange(2000,4000)
			
				xvec = player.rect.centerx - self.rect.centerx
				yvec = player.rect.centery - self.rect.centery
			
				dir_to_player = math.atan2(yvec,xvec) * (180/math.pi)
			
				# launch projectile
				new_bullet = projectile.RandomBullet(self.proj_images,self.rect.centerx,
													self.rect.centery,8,8,player,friction=0.97,speed=0.4,trail=True)
				self.bullets_list.append(new_bullet)
				
				new_bullet = projectile.RandomBullet(self.proj_images,self.rect.centerx,
													self.rect.centery,8,8,self,friction=0.95,speed=0.6,trail=True)
				self.bullets_list.append(new_bullet)
				
class IceWitch(Boneman):
	def __init__(self,x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed = 0.4,health=15):
		
		super(IceWitch,self).__init__(x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed,health)
		self.damage = 4
		
		stand_list = gutils.sliceSheetColKey(self.w,self.h,"images\\icewitch.png")
		moveleft_list = gutils.sliceSheetColKey(self.w,self.h,"images\\icewitch_moveleft.png")
		moveright_list = gutils.sliceSheetColKey(self.w,self.h,"images\\icewitch_moveright.png")
		
		self.proj_images = "images\\ice_proj.png"
		
		params = [2,2,2]
		
		self.id = 0
		self.frame = 0
		
		self.image_master = [stand_list,moveleft_list,moveright_list]
		self.animator = helpers.AnimManager(params,6)
		self.image = self.image_master[self.id][self.frame]
		
		self.bullets_list = []
		self.fire_acctime = 0
		self.fire_updatetime = random.randrange(1500,8000)

	def fire(self):
		
		if self.fire_acctime > self.fire_updatetime:
			
			# get dir_to_player
			player = self.good_guys[0]
			
			x = int(self.rect.x)
			y = int(self.rect.y)
			
			if player.rect.x in range(x-100, x+100) and\
				player.rect.y in range(y-100, y+100):
				
				self.fire_acctime = 0
				self.fire_updatetime = random.randrange(1500,8000)
			
				xvec = player.rect.centerx - self.rect.centerx
				yvec = player.rect.centery - self.rect.centery
			
				dir_to_player = math.atan2(yvec,xvec) * (180/math.pi)
			
				# launch projectile
				for i in range(12):
					dir = random.randint(int(dir_to_player)-40,int(dir_to_player)+40)
					new_bullet = projectile.IceBullet(self.proj_images,self.rect.centerx,
													self.rect.centery,8,8,dir,friction=0.96,speed=2.5,rotate=True)
					self.bullets_list.append(new_bullet)

class Dasher(Boneman):
	def __init__(self,x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed = 0.4,health=22):
		
		super(Dasher,self).__init__(x,y,w,h,grid,tileList,itemList,good_guys,effects,images_dict,speed,health)
		self.damage = 10
		
		stand_list = gutils.sliceSheetColKey(self.w,self.h,"images\\dasher_stand.png")
		moveleft_list = gutils.sliceSheetColKey(self.w,self.h,"images\\dasher_moveleft.png")
		moveright_list = gutils.sliceSheetColKey(self.w,self.h,"images\\dasher_moveright.png")
		
		self.proj_images = "images\\dasher_proj.png"
		
		params = [2,2,2]
		
		self.id = 0
		self.frame = 0
		
		self.image_master = [stand_list,moveleft_list,moveright_list]
		self.animator = helpers.AnimManager(params,6)
		self.image = self.image_master[self.id][self.frame]
		
		self.bullets_list = []
		self.fire_acctime = 0
		self.fire_updatetime = random.randrange(1000,3000)
		
		self.dash_max_vel = 4
		self.dx = 0
		self.dx = 0
		self.friction = 0.95
		self.dash_acctime = 0
		self.dash_updatetime = random.randrange(2000,4000)
		self.x_moverange = 100
		self.y_moverange = 100
		
	def fire(self):
		
		if self.fire_acctime > self.fire_updatetime:
			
			# get dir_to_player
			player = self.good_guys[0]
			
			x = int(self.rect.x)
			y = int(self.rect.y)
			
			if player.rect.x in range(x-190, x+190) and\
				player.rect.y in range(y-100, y+100):
				
				self.fire_acctime = 0
				self.fire_updatetime = random.randrange(4000,8000)
			
				xvec = player.rect.centerx - self.rect.centerx
				yvec = player.rect.centery - self.rect.centery
			
				dir_to_player = math.atan2(yvec,xvec) * (180/math.pi)
			
				# launch projectile
				for i in range(4):
					dir = random.randint(int(dir_to_player)-40,int(dir_to_player)+40)
					new_bullet = projectile.IceBullet(self.proj_images,self.rect.centerx,
													self.rect.centery,8,8,dir,friction=0.987,fps=16,speed=2.3,rotate=True)
					self.bullets_list.append(new_bullet)

	def update(self,timepassed):
		
		self.fire_acctime += timepassed
		self.flash_acctime += timepassed
		self.blink_acctime += timepassed
		self.dash_acctime += timepassed
		
		super(Boneman,self).update(timepassed)
		
		player = self.good_guys[0]
		
		if self.blink_acctime > self.blink_updatetime:
			self.blink_acctime = 0
			self.is_blend_visible = not(self.is_blend_visible)
		
		if self.controller.current_steering_behaviour.vel.x > 0.1:
			self.id = 2
			self.animator.play(self.id,timepassed)
			self.frame = self.animator.getFrame()[1]
		
		elif self.controller.current_steering_behaviour.vel.x < -0.05:
			self.id = 1
			self.animator.play(self.id,timepassed)
			self.frame = self.animator.getFrame()[1]
		
		
		self.image = self.image_master[self.id][self.frame]
		self.handleFlashing()
		
		self.fire()
		
		# check against walls
		self.updateBullets(timepassed)
		for bullet in self.bullets_list:	
			for wall in self.tileList:
				if bullet.col_rect.colliderect(wall.col_rect):
					bullet.alive = False
		
		# check against items
		for bullet in self.bullets_list:	
			for item in self.itemList:
				if item.kind == "FireCrate":
					if bullet.col_rect.colliderect(item.col_rect):
						bullet.alive = False
		
		for bullet in self.bullets_list:
			if not player.is_flashing:
				if bullet.col_rect.colliderect(player.rect):
					bullet.alive = False
					player.flash()
					player.health -= self.damage
					player.sound_manager.play("lose.ogg")
					
		for bullet in self.bullets_list:
			if not bullet.alive:
				self.bullets_list.remove(bullet)
		
				# add collision effect
				params = [self.images_dict["hit"][0],1,10]
				new_effect = gobs.AnimObject(params,bullet.rect.centerx,bullet.rect.centery,0,0,1)
				self.effects.append(new_effect)
				#print self.effects
		
		if self.dash_acctime > self.dash_updatetime:
			self.dash_acctime = 0
			
			r_int = random.randint(0,self.dash_max_vel-1)
			r_float = random.random()
			
			self.dx = r_int+r_float
			
			r_int = random.randint(0,self.dash_max_vel-1)
			r_float = random.random()
			self.dy = r_int+r_float
			
			self.dash_updatetime = random.randrange(4000,8000)
		
		self.checkCollisions()
		
		self.controller.x += self.dx
		self.controller.y += self.dy
		
		self.x,self.y = (self.controller.x,self.controller.y)
		
		self.dx *= self.friction
		self.dy *= self.friction
		
		self.rect.topleft = (self.x,self.y)
		self.col_rect.topleft = (self.x,self.y)
	