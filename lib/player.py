import pygame,math
from pygame.locals import*
import weapons
import projectile
from cnst import*
import sgf.utils.g_utils as gutils
import sgf.gameobjects.g_objects as gobs
import sgf.utils.helpers as helpers
import sgf.behaviours.steering_behaviours as sbv
import sgf.collision.sat_collision as SAT
from sgf.collision.gen_collision import Line
import sgf.gameobjects.particle_objects as po

class State(object):
	def __init__(self,player_ref):
		self.owner = player_ref
	
	def runBehaviour(self,timepassed):
		pass

class StandState(State):
	def __init__(self,player_ref):
	
		super(StandState,self).__init__(player_ref)
			
	def runBehaviour(self,timepassed):
		
		if not self.owner.animator.anim_started:
			self.owner.id = self.owner.STAND
			if self.owner.last_dir == 0:
				self.owner.frame = 0
			else:
				self.owner.frame = 1

class RunUpState(State):
	def __init__(self,player_ref):
		super(RunUpState,self).__init__(player_ref)
			
	def runBehaviour(self,timepassed):
		
		if not self.owner.animator.anim_started:
		
			self.owner.id = self.owner.RUN_UP
			self.owner.animator.play(self.owner.RUN_UP,timepassed)
			self.owner.frame = self.owner.animator.getFrame()[1]

class RunDownState(State):
	def __init__(self,player_ref):
		super(RunDownState,self).__init__(player_ref)
			
	def runBehaviour(self,timepassed):
		
		if not self.owner.animator.anim_started:
		
			self.owner.id = self.owner.RUN_DOWN
			self.owner.animator.play(self.owner.RUN_DOWN,timepassed)
			self.owner.frame = self.owner.animator.getFrame()[1]

			
class RunLeftState(State):
	def __init__(self,player_ref):
		super(RunLeftState,self).__init__(player_ref)
			
	def runBehaviour(self,timepassed):
		
		self.owner.dx -= self.owner.speed
		self.owner.last_dir = 0
		
		if not self.owner.animator.anim_started:
		
			self.owner.id = self.owner.RUN_LEFT
			self.owner.animator.play(self.owner.RUN_LEFT,timepassed)
			self.owner.frame = self.owner.animator.getFrame()[1]
		
class RunRightState(State):
	def __init__(self,player_ref):
		super(RunRightState,self).__init__(player_ref)
			
	def runBehaviour(self,timepassed):
		
		self.owner.dx += self.owner.speed
		self.owner.last_dir = 1 
		
		if not self.owner.animator.anim_started:
		
			self.owner.id = self.owner.RUN_RIGHT
			self.owner.animator.play(self.owner.RUN_RIGHT,timepassed)
			self.owner.frame = self.owner.animator.getFrame()[1]
		
class Effect(object):
	def __init__(self,x,y,image_path,alpha_dec = 8):
		self.x = x
		self.y = y
		self.image = pygame.image.load(image_path).convert()
		self.image.set_colorkey((255,0,255))
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.x,self.y)
		self.alpha = 255
		self.alpha_dec = alpha_dec
		self.alive = True
		
	def update(self):
		self.alpha -= self.alpha_dec
		if self.alpha < 0:
			self.alpha = 0
			self.alive = False
			
		self.image.set_alpha(self.alpha)
		
	def draw(self,Surface):
		Surface.blit(self.image,self.rect)
	
class Player(object):
	
	def __init__(self,run_flag,x,y,enemyList,tileList,effects,itemList,images_dict,sound_manager):
		
		self.sound_manager = sound_manager
		self.run_flag = run_flag
		self.STAND = 0
		self.RUN_LEFT = 1
		self.RUN_RIGHT = 2
		self.RUN_UP = 3
		self.RUN_DOWN = 4
		self.HIT_LEFT = 5
		self.HIT_RIGHT =6
		
		# little tweaks after the long journey
		self.can_draw_orb = True
		self.fire_angle = 270
		self.aim_speed = 8
		
		self.enemyList = enemyList
		self.tileList = tileList
		self.itemList = itemList
		self.images_dict = images_dict
		self.weapon_id = 0
		self.weapons_list = [weapons.BasicGun(self),
								weapons.DualGun(self),
								weapons.BounceGun(self),
								weapons.LightningGun(self),
								weapons.FlameGun(self),
								weapons.WaveyGun(self),
								weapons.PiercerGun(self),
								weapons.RandomGun(self)]
								
		self.cur_weapon = self.weapons_list[self.weapon_id]
		self.mana_amount = 100
		
		self.left_is_down = False
		self.right_is_down = False
		self.up_is_down = False
		self.down_is_down = False
		self.room_key = None
		
		stand_s = StandState(self)
		runleft_s = RunLeftState(self)
		runright_s = RunRightState(self)
		runup_s  = RunUpState(self)
		rundown_s = RunDownState(self)
		
		self.effects_list = []
		self.effects = effects
		
		self.states = [stand_s,runleft_s,runright_s,runup_s,rundown_s]
		self.cur_state = self.states[0]
		
		self.x = x
		self.y = y
		self.w = 16
		self.h = 16
		self.hx = self.w / 2
		self.hy = self.h / 2
		self.health = 100
		
		self.dx = 0
		self.dy = 0
		self.speed = 0.06
		self.friction = 0.935
		self.id = 0 
		self.frame = 0
		self.target = sbv.Target((self.x-10,self.y))
		self.cam_target = sbv.Target((self.x,self.y))
		self.cam_tracker = None
		
		self.firing_angle = 0
		self.firing_vector = (0,0)
		
		self.bullets_list = []
		
		self.time_since_dash = 0
		self.is_dashing = False
		self.dash_waittime = 1500
		self.dash_vel = 2.8
		self.exit_status = 0		# 1 for next room, -1 for escape exit
		
		self.trail_positions = []
		self.trail_len = 5
		
		# flags
		self.is_run_left = False
		self.is_run_right = False
		self.last_dir = 0 		# 0 for left ;1 for right
		self.last_dir_v = 0 	# 0 for up ; 1 for down
		self.gamestate = None
		self.is_slashing = False
		
		self.rect = pygame.Rect(self.x,self.y,16,16)
		self.col_rect = pygame.Rect(self.x,self.y,16,16)
		self.shooter_rect = pygame.Rect(self.x,self.y,25,25)
		self.pointer_radius = 10
		
		# blending stuff
		self.is_flashing = False
		self.flash_duration = 800
		self.flash_acctime = 5000
		
		self.blink_acctime = 0
		self.blink_updatetime = 50
		self.is_blend_visible = False
		
		self.blendimage = None
		self.blendcolor = (255,0,0)
		
		self.alive = True
		self.killed_effect = None
		self.time_since_killed = 0
		self.end_duration = 2500
		
		# load images
		params = [2,3,3,3,3,5,5]
		stand_list = gutils.sliceSheetColKey(16,16,"images\\aris_stand.png")
		runleft_list = gutils.sliceSheetColKey(16,16,"images\\aris_runleft.png")
		runright_list = gutils.sliceSheetColKey(16,16,"images\\aris_runright.png")
		runup_list = gutils.sliceSheetColKey(16,16,"images\\aris_runup.png")
		rundown_list = gutils.sliceSheetColKey(16,16,"images\\aris_rundown.png")
		hitleft_list = gutils.sliceSheetColKey(16,16,"images\\mage_hit_left.png")
		hitright_list = gutils.sliceSheetColKey(16,16,"images\\mage_hit_right.png")
		
		self.dead_list = gutils.sliceSheetColKey(16,16,"images\\aris_poof.png")
		
		self.image_master = [stand_list,runleft_list,runright_list,runup_list,rundown_list,hitleft_list,hitright_list]
		self.animator = helpers.AnimManager(params,6)
		
		self.image = self.image_master[self.id][self.frame]
		self.trail_image = self.image.copy()
		
		self.pointer_surf = pygame.image.load("images\\pointer.png").convert()
		self.pointer_surf.set_colorkey((255,0,255))
		self.pointer_surf.set_alpha(100)
		
		
		self.pointer_image = self.pointer_surf.copy()
		self.pointer_image_rect = self.pointer_image.get_rect()
		self.pointer_image_rot_rect = self.pointer_image.get_rect()
		
		self.weapon_target = sbv.Target((self.rect.centerx,self.rect.centery))
		self.magic_orb = weapons.Orb(self.target,self)
		
		self.line_collider = Line(self.rect.topleft,self.rect.topright,(0,0,0))
		
		topline = ((float(self.rect.left),float(self.rect.top)),(float(self.rect.right),float(self.rect.top)))
		bottomline = ((float(self.rect.left),float(self.rect.bottom)),(float(self.rect.right),float(self.rect.bottom)))
		leftline = ((float(self.rect.left),float(self.rect.top)),(float(self.rect.left),float(self.rect.bottom)))
		rightline = ((float(self.rect.right),float(self.rect.top)),(float(self.rect.right),float(self.rect.bottom)))
		
		self.lines = [rightline,topline,leftline,bottomline]
		
		
	def use(self):
		
		for item in self.itemList:
			if item.kind == "DoorTile":
				if item.is_open:
					self.run_flag[0] = False
					self.gamestate.exit_status = 1
					self.gamestate.room_number += 1 
	
	def attachGameState(self,gamestate):
		self.gamestate = gamestate
	
	def setState(self,cam_tracker):
		
		self.cam_tracker = cam_tracker
	
	def fireSecondary(self):
		self.magic_orb.gun.launch()
	
	def firePrimary(self):
		self.cur_weapon.fire()
			
			#self.cam_tracker.shake([abs(self.firing_vector[0])*5.0,60,0.2],[abs(self.firing_vector[1])*5.0,60,0.2])
	
	def handleFlashing(self):
		
		if self.flash_acctime < self.flash_duration: 
			self.is_flashing = True
		else:
			self.is_flashing = False
		
		if self.is_flashing:
			self.blendimage = self.image.copy().convert_alpha()
			self.blendimage.fill((0,0,0,240), None, BLEND_RGBA_MULT)
			self.blendimage.fill(self.blendcolor[0:3] + (0,), None, BLEND_RGBA_ADD)
		
	
	def flash(self):
		
		if not self.is_flashing:
			self.flash_acctime = 0
	
	def calculateFireAngle(self):
		
		self.fire_angle = self.fire_angle % 360
		
		if self.left_is_down:
			
			xvec1 = math.cos(90 * (DEGTORAD))
			yvec1 = math.sin(90 * (DEGTORAD))
		
			xvec2 = math.cos(self.fire_angle * (DEGTORAD))
			yvec2 = math.sin(self.fire_angle * (DEGTORAD))
			
			dotprod = ((xvec1*xvec2)+(yvec1*yvec2))
			dotprod *= self.aim_speed
		
			
			#if dotprod < 0:
				#self.fire_angle += 3
			#else: 
			self.fire_angle += dotprod
				
		if self.right_is_down:
			
			xvec1 = math.cos(270 * (DEGTORAD))
			yvec1 = math.sin(270 * (DEGTORAD))
		
			xvec2 = math.cos(self.fire_angle * (DEGTORAD))
			yvec2 = math.sin(self.fire_angle * (DEGTORAD))
			
			dotprod = ((xvec1*xvec2)+(yvec1*yvec2))
			
			dotprod *= self.aim_speed
			
			self.fire_angle += dotprod
			#if dotprod < 0:
			#	self.fire_angle += 3
			#else: 
			#	self.fire_angle -= 3
			
		
		if self.up_is_down:
		 
			xvec1 = math.cos(180 * (DEGTORAD))
			yvec1 = math.sin(180 * (DEGTORAD))
		
			xvec2 = math.cos(self.fire_angle * (DEGTORAD))
			yvec2 = math.sin(self.fire_angle * (DEGTORAD))
			
			dotprod = ((xvec1*xvec2)+(yvec1*yvec2))
			
			dotprod *= self.aim_speed
			
			self.fire_angle += dotprod
			#if dotprod <= 0:
			#	self.fire_angle += 3
			#else: 
			#	self.fire_angle -= 3		
		
		if self.down_is_down:
		 
			xvec1 = math.cos(0 * (DEGTORAD))
			yvec1 = math.sin(0 * (DEGTORAD))
		
			xvec2 = math.cos(self.fire_angle * (DEGTORAD))
			yvec2 = math.sin(self.fire_angle * (DEGTORAD))
			
			dotprod = ((xvec1*xvec2)+(yvec1*yvec2))
			
			dotprod *= self.aim_speed
			
			self.fire_angle += dotprod
			
	def dash(self):
			
		#print self.left_is_down and self.down_is_down
		
		if self.time_since_dash > self.dash_waittime:
			self.time_since_dash = 0
			
			self.sound_manager.play("dash.ogg")
		
			if self.down_is_down and self.left_is_down:
				# down left only
				self.dy += self.dash_vel
				self.dx -= self.dash_vel
			
			elif self.down_is_down and self.right_is_down:
				# down right only
				self.dy += self.dash_vel
				self.dx += self.dash_vel
			
			
			elif self.left_is_down and not self.up_is_down and not self.down_is_down:
				# left only
				self.dx -= self.dash_vel
		
			elif self.right_is_down and not self.up_is_down and not self.down_is_down:
				# right only
				self.dx += self.dash_vel
		
			elif self.up_is_down and not self.left_is_down and not self.right_is_down:
				# up only
				self.dy -= self.dash_vel
		
			elif self.down_is_down and not self.left_is_down and not self.right_is_down:
				# up only
				self.dy += self.dash_vel
			
			elif self.up_is_down and self.left_is_down and not self.down_is_down:
				# up left only
				self.dy -= self.dash_vel
				self.dx -= self.dash_vel
			
			elif self.up_is_down and self.right_is_down and not self.down_is_down:
				# up right only
				self.dy -= self.dash_vel
				self.dx += self.dash_vel
		else:
			self.sound_manager.play("nodash.ogg")
		
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
				self.dx = 0.01
				self.x = plat.rect.left - (self.w-1)
				#print "colliding left"
					
			else:
			#push right
				if abs(self.dx)>1:
					self.dx = 0.01
				self.x = plat.rect.right-1
				#print "colliding right"
					
		elif minpen==ypen and x_intersect > 0:
			# project out along y axis
			if ydist > 0:
				# push up
				self.dy = 0
				self.y = plat.rect.top-(self.h-1)	# push up but leave 1px in tile
				#print "colliding top"
				
			else:
				#push down
				self.dy = 0
				self.y = plat.rect.bottom
				#print "colliding bottom"
	
	def swapWeapon(self,dir):
		if dir < 0:
			self.weapon_id = (self.weapon_id-1) % len(self.weapons_list)
		else:
			self.weapon_id = (self.weapon_id+1) % len(self.weapons_list)
		
		self.sound_manager.play("select.ogg")
					
		
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
		
	def slash(self):
		pass
		
	def updateBullets(self,timepassed):
		
		for bullet in self.bullets_list:
			bullet.update(timepassed)
	
	def drawBullets(self,Surface):
		for bullet in self.bullets_list:
			bullet.draw(Surface)
	
	
	def update(self,timepassed):
		
		if self.health > 100:
			self.health = 100
		
		if self.health <= 0 and self.alive:
			#self.run_flag[0] = False
			#self.gamestate.exit_status = 0
			self.alive = False
			params = [self.images_dict["p_kill"][0],1,12]
			killed_effect = gobs.AnimObject(params,self.rect.x-24,self.rect.y-24,0,0,1)
			emitter1 = po.ParticleEmitter(self.rect.centerx,self.rect.centery,
									strength = 0.4 ,mode = ("stream",120),direction=270,friction=1.01)
	
			self.effects.append(killed_effect)
			self.effects.append(emitter1)
			self.time_since_killed = 0
			
			# tweaks
			self.can_draw_orb = False
			self.is_flashing = False
			
		if not self.alive:
			self.time_since_killed += timepassed
			
			if self.time_since_killed > self.end_duration:
				self.run_flag[0] = False
				self.gamestate.exit_status = 0
			
			if self.last_dir == 0:
				self.image = self.dead_list[0]
			else:
				self.image = self.dead_list[1]
			
			return
			
		self.cur_state.runBehaviour(timepassed)
		self.time_since_dash += timepassed
		self.flash_acctime += timepassed
		self.blink_acctime += timepassed
		
		if self.blink_acctime > self.blink_updatetime:
			self.blink_acctime = 0
			self.is_blend_visible = not(self.is_blend_visible)
		
		self.cur_weapon = self.weapons_list[self.weapon_id]
		
		if self.up_is_down:
			self.dy -= self.speed
			if not self.left_is_down or not self.right_is_down:
				self.cur_state = self.states[3]
				
		elif self.down_is_down:
			self.dy += self.speed
			if not self.left_is_down or not self.right_is_down:
				self.cur_state = self.states[4]
			
		if self.left_is_down:
			self.cur_state = self.states[1]	
		
		elif self.right_is_down:
			self.cur_state = self.states[2]	
		
		else:
			if not self.up_is_down and not self.down_is_down:
				#print "this shouldnt run"
				self.cur_state = self.states[0]
		
		if self.last_dir == 0:
			self.target.position.x = self.rect.centerx - 4
			self.target.position.y = self.rect.centery
		else: 
			self.target.position.x = self.rect.centerx - 4
			self.target.position.y = self.rect.centery
		
		self.weapon_target.position.x = self.rect.centerx
		self.weapon_target.position.y = self.rect.centery
		
		self.magic_orb.update(timepassed)
		
		if self.animator.anim_started:
			self.id,self.frame,a_s = self.animator.getFrame()
			self.animator.setFps(12)
		else:
			self.animator.setFps(8)
		
		for effect in self.effects_list:
			effect.update()
			
		for effect in self.effects_list:
			if not effect.alive:
				self.effects_list.remove(effect)
		
		# get firing_angle and vector
		self.calculateFireAngle()
		self.firing_angle = self.fire_angle
		
		xvec =  self.rect.centerx - self.shooter_rect.centerx 
		yvec =  self.rect.centery - self.shooter_rect.centery 
		
		magnitude = math.sqrt(xvec*xvec + yvec*yvec)
		
		if magnitude != 0:
			xvec /= magnitude
			yvec /= magnitude
		
		self.firing_vector = (xvec,yvec)
		# calculate pointer image position
		p_xpos = self.magic_orb.rect.centerx + (self.pointer_radius * math.cos(self.firing_angle*(DEGTORAD)))
		p_ypos = self.magic_orb.rect.centery + (self.pointer_radius * math.sin(self.firing_angle*(DEGTORAD)))
		
		self.pointer_image_rect.center = (p_xpos,p_ypos)
		
		self.pointer_image = pygame.transform.rotate(self.pointer_surf,180-self.firing_angle)
		#self.pointer_image.set_alpha(100)
		self.pointer_image_rot_rect = self.pointer_image.get_rect(center=self.pointer_image_rect.center)
		
		# update gun 
		self.cur_weapon.update(timepassed)
		
		self.updateBullets(timepassed)
		
		for bullet in self.bullets_list:
			for enemy in self.enemyList:
				if bullet.col_rect.colliderect(enemy.rect):
					if bullet.kind != "FlameBullet":
						bullet.alive = False
		
					# make enemy blink here
					enemy.flash()
					# damage enemy
					enemy.health -= self.cur_weapon.damage
					self.sound_manager.play("hurt_hit.ogg")
		
		for bullet in self.bullets_list:
			for wall in self.tileList:
				if bullet.kind == "BounceBullet":
			
					if bullet.can_collide:
						if bullet.col_rect.colliderect(wall.col_rect):
							
							if bullet.acc_rebounds < bullet.max_rebounds:
								bullet.resolveCollisions(wall)
								bullet.cool_acctime = 0
								bullet.acc_rebounds += 1
								self.sound_manager.play("bounce_w.ogg")
								break
							else:
								# kill bullet
								bullet.alive = False
				
				if bullet.kind == "PiercerBullet":
			
					if bullet.rect.right <0 or bullet.rect.right > PLAY_W or\
					bullet.rect.bottom <0 or bullet.rect.top > PLAY_H:
						bullet.alive = False
				
				else:
					if bullet.col_rect.colliderect(wall.col_rect):
						bullet.alive = False
					
			for item in self.itemList:
				if item.kind == "FireCrate":
					if bullet.kind == "BounceBullet":
			
						if bullet.can_collide:
							if bullet.col_rect.colliderect(item.col_rect):
							
								if bullet.acc_rebounds < bullet.max_rebounds:
									bullet.resolveCollisions(item)
									bullet.cool_acctime = 0
									bullet.acc_rebounds += 1
									self.sound_manager.play("bounce_w.ogg")
									break
								else:
									# kill bullet
									bullet.alive = False
								
					else:
						if bullet.col_rect.colliderect(item.col_rect):
							bullet.alive = False
							item.health -= self.cur_weapon.damage
			
		for bullet in self.bullets_list:
			if not bullet.alive:
				self.bullets_list.remove(bullet)
				
				if bullet.kind != "FlameBullet":
					# add collision effect
					params = [self.images_dict["hit"][0],1,10]
					new_effect = gobs.AnimObject(params,bullet.rect.centerx,bullet.rect.centery,0,0,1)
					self.effects.append(new_effect)
					#print self.effects
					
		
		self.dy *= self.friction
		self.dx *= self.friction
		
		self.x += self.dx
		self.y += self.dy
		
		self.rect.topleft = (self.x,self.y)
		
		# update line colliders
		topline = ((float(self.rect.left),float(self.rect.top)),(float(self.rect.right),float(self.rect.top)))
		bottomline = ((float(self.rect.left),float(self.rect.bottom)),(float(self.rect.right),float(self.rect.bottom)))
		leftline = ((float(self.rect.left),float(self.rect.top)),(float(self.rect.left),float(self.rect.bottom)))
		rightline = ((float(self.rect.right),float(self.rect.top)),(float(self.rect.right),float(self.rect.bottom)))
		
		self.lines = [rightline,topline,leftline,bottomline]
		
		# update camera target
		'''
		if self.last_dir == 0:
			self.cam_target.position.x = self.rect.centerx - 64
		else: 
			self.cam_target.position.x = self.rect.centerx + 64
			
		if self.last_dir_v == 0:
			self.cam_target.position.y = self.rect.centery - 64
		else: 
			self.cam_target.position.y = self.rect.centery + 64
		
		'''
		self.cam_target.position.x = self.rect.centerx
		self.cam_target.position.y = self.rect.centery
		
		self.trail_positions.append((self.x,self.y))
		
		
		if len(self.trail_positions)> self.trail_len:
			self.trail_positions.pop(0)
		
		if self.rect.left < self.shooter_rect.left:
			self.shooter_rect.left = self.rect.left
		
		if self.rect.right > self.shooter_rect.right:
			self.shooter_rect.right = self.rect.right
		
		if self.rect.top < self.shooter_rect.top:
			self.shooter_rect.top = self.rect.top
			
		if self.rect.bottom > self.shooter_rect.bottom:
			self.shooter_rect.bottom = self.rect.bottom
		
		
		self.col_rect.x = self.x + self.dx 
		self.col_rect.y = self.y + self.dy
		
		# resolve collisions
		self.checkCollisions()
		
		self.animator.update(timepassed)
		
		self.image = self.image_master[self.id][self.frame]
		self.handleFlashing()
		
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)
		
		if self.is_flashing:
			if self.is_blend_visible:
				Surface.blit(self.blendimage,self.rect)
		
		for effect in self.effects_list:
			effect.draw(Surface)
		
		if self.can_draw_orb:
			self.magic_orb.draw(Surface)
			Surface.blit(self.pointer_image,self.pointer_image_rot_rect)
		
		# draw trail 
		if self.time_since_dash < 600:
			self.blendimage = self.image.copy().convert_alpha()
			self.blendimage.fill((0,0,0,40), None, BLEND_RGBA_MULT)
			self.blendimage.fill((30,250,10)[0:3] + (0,), None, BLEND_RGBA_ADD)
		
			self.trail_image = self.blendimage.copy()
			self.trail_image.set_alpha(60)
			
			for pos in self.trail_positions:
				Surface.blit(self.trail_image,(pos[0],pos[1]))
			
			#Surface.blit(self.blendimage,(pos[0],pos[1]))
				
		self.drawBullets(Surface)
		self.cur_weapon.draw(Surface)
		
		#self.col_rect.draw(Surface)
		# debug
		#pygame.draw.rect(Surface,(200,50,0),self.shooter_rect,1)