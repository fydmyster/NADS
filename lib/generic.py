import pygame,random,math,os
import sgf.gameobjects.steer_objects as steer
import sgf.gameobjects.g_objects as gobs
import sgf.utils.g_utils as gutils

class Mana(object):
	def __init__(self,x,y,target):
		self.x = x
		self.y = y
		self.trail_list = []
		self.max_traillen = 4
		
		self.kind = "Mana"
		self.controller = steer.Steerable("KSeekMovement",(self.x,self.y),8,8)
		self.controller.current_steering_behaviour.setMaxSpeed(1.6)
		
		self.controller.setTarget(target)
		
		self.image_paths = ["images\\blue_mana.png",
							"images\\green_mana.png",
							"images\\orange_mana.png",
							"images\\red_mana.png"]
		
		self.rand_int = random.randint(0,2)
		self.mana_choice = self.image_paths[self.rand_int]
		
		if self.rand_int == 0:
			self.mana_value = random.randint(20,30)
		
		elif self.rand_int == 1:
			self.mana_value = random.randint(40,60)
		
		elif self.rand_int == 2:
			self.mana_value = random.randint(50,70)
		
		elif self.rand_int == 3:
			self.mana_value = random.randint(60,80)
		
		
		self.image = pygame.image.load(self.mana_choice).convert()
		self.image.set_colorkey((255,0,255))
		
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.x,self.y)
		
	def update(self,timepassed):
		self.controller.update(timepassed)
		
		self.trail_list.append((self.x,self.y))
		
		if len(self.trail_list) > self.max_traillen:
			self.trail_list.pop(0)
		
		self.x = self.controller.x
		self.y = self.controller.y
		
		self.rect.topleft = (self.x,self.y)
		
		
	def draw(self,Surface):
		Surface.blit(self.image,self.rect)
		
		trail_image = self.image.copy()
		trail_image.set_alpha(50)
		for pos in self.trail_list:
			Surface.blit(trail_image,pos)
 
 
class HealthBar(object):
	def __init__(self,x,y,max_health):
		
		self.x = x
		self.y = y
		self.cur_health = max_health
		self.max_health = max_health
		self.outer_image = pygame.image.load("images\\lifebar_hud.png").convert()
		self.outer_image.set_colorkey((255,0,255))
		self.outer_image_rect = self.outer_image.get_rect()
		self.outer_image_rect.topleft = (self.x,self.y)
		
		self.bar_image = pygame.Surface((self.outer_image_rect.w-2,self.outer_image_rect.h-2))
		self.bar_image_rect = self.bar_image.get_rect()
		self.bar_image_rect.center = self.outer_image_rect.center
		self.color_2 = (0,20,240)
		self.color_1 = (240,10,0)
		self.bar_color = self.color_2
		
	def setCurHealth(self,health):
		self.cur_health = health
	
	def update(self,timepassed=0):
		
		ratio = self.cur_health/float(self.max_health)
		
		if ratio < 0:
			ratio = 0.0
		if ratio > 1:
			ratio = 1
			
		self.bar_color = gutils.colorLerp(self.color_1,self.color_2,ratio)
		draw_rect_w = self.outer_image_rect.w * ratio
		
		self.bar_image.fill((0,0,0))
		pygame.draw.rect(self.bar_image,self.bar_color,(0,0,draw_rect_w,self.bar_image_rect.h))
		
	def draw(self,Surface):
		
		Surface.blit(self.bar_image,self.bar_image_rect)
		Surface.blit(self.outer_image,self.outer_image_rect)

class DashBar(object):
	def __init__(self,x,y,max_updatetime):
		
		self.x = x
		self.y = y
		self.cur_time = max_updatetime
		self.max_updatetime = max_updatetime
		self.outer_image = pygame.image.load("images\\dash_hud.png").convert()
		self.outer_image.set_colorkey((255,0,255))
		
		self.outer_image_rect = self.outer_image.get_rect()
		self.outer_image_rect.topleft = (self.x,self.y)
		
		self.bar_image = pygame.Surface((self.outer_image_rect.w-2,self.outer_image_rect.h-2))
		self.bar_image_rect = self.bar_image.get_rect()
		self.bar_image_rect.center = self.outer_image_rect.center
		self.color_2 = (0,255,10)
		self.color_1 = (240,10,0)
		self.bar_color = self.color_2
		
	def setCurTime(self,cur_time):
		self.cur_time = cur_time
	
	def update(self,timepassed=0):
		
		ratio = self.cur_time/float(self.max_updatetime)
		
		if ratio < 0:
			ratio = 0.0
			
		if ratio < 1:
			self.bar_color = self.color_1
		else:
			self.bar_color = self.color_2
		
		draw_rect_w = self.outer_image_rect.w * ratio
		
		self.bar_image.fill((0,0,0))
		pygame.draw.rect(self.bar_image,self.bar_color,(0,0,draw_rect_w,self.bar_image_rect.h))
		
	def draw(self,Surface):
		
		Surface.blit(self.bar_image,self.bar_image_rect)
		Surface.blit(self.outer_image,self.outer_image_rect)
		
class RoomKey(object):
	def __init__(self,x,y):
		
		self.x = x
		self.y = y
		self.kind = "RoomKey"
		self.image = pygame.image.load("images\\key.png").convert()
		self.image.set_colorkey((255,0,255))
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.x,self.y)
		self.sin_angle = 0
		self.sin_speed = 10
		
	def update(self,timepassed=0):
		
		self.sin_angle += self.sin_speed
		self.y += 1.1 * math.sin(self.sin_angle * (math.pi/180))
		self.rect.topleft = (self.x,self.y)
		
	def draw(self,Surface):
		Surface.blit(self.image,self.rect)
		
class FireCrate(object):
	def __init__(self,x,y,w,h):
		
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.hx = self.w / 2
		self.hy = self.h / 2
		self.collidable = True
		self.x_coord = self.x/w
		self.y_coord = self.y/h
		
		self.kind = "FireCrate"
		image_path = "images\\fire_crate.png"
		self.master_images = gutils.sliceSheetColKey(w,h,image_path)
		self.anim_object = gobs.AnimObject([self.master_images,-1,6],x,y,0,0,1)
		self.health = 10
		self.alive = True
		
		self.image = self.anim_object.image
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.x,self.y)
		self.col_rect = pygame.Rect(0,0,14,14)
		self.col_rect.center = self.rect.center
	
	def update(self,timepassed):
		
		if self.health < 0:
			self.alive = False
		
		self.anim_object.update(timepassed)
		self.image = self.anim_object.image
		
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)

class SoundManager(object):
	def __init__(self,state):
		
		self.state = state
		self.sounds = {}
		files = os.listdir("sounds")
		
		for item in files:
			# load the sound
			sound_object = pygame.mixer.Sound("sounds\\"+item)
			self.sounds[item] = sound_object
			
	def play(self,file):
		if self.state.play_sounds:
			self.sounds[file].play()