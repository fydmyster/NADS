import pygame,sys,random,cPickle
from pygame.locals import*
from cnst import*
import player
import sgf.gameobjects.g_objects as g_obs
import sgf.utils.g_utils as gutils
import enemy as enem
import generic
import level_gen
import pathfind
import sgf.gameobjects.steer_objects as steer
import sgf.gameobjects.particle_objects as po
import sgf.gameobjects.tween_objects as ease

pygame.mixer.pre_init(44100,-16,2,1024)
pygame.init()

font = pygame.font.Font("fonts\\Minecraftia-Regular.ttf",10)
large_font = pygame.font.Font("fonts\\NOTMK___.ttf",12)
huge_font = pygame.font.Font("fonts\\NOTMK___.ttf",36)

class GameState(object):
	def __init__(self):
		# global state
		self.fullscreen = False
		self.room_number = 1
		self.player_health = 100
		self.player_mana = 100
		self.play_sounds = True
		self.play_music = True
		self.exit_status = 0
		self.weapon_id = 0
		self.old_bestscore = 0
		
		self.keys = ["up","down","left","right","shoot","dash","use","swap_left","swap_right"]
		enum = enumerate(self.keys)
		self.map = dict(enum)
		
		# read from dat file for best scores
		try:
			f = file("scores.dat","r")
		
		except IOError:
			#print "File doesnt exist creating new one"
			f = file("scores.dat","w")
			
			self.best_score = 0
			self.controls = {"up" : K_UP,
							"down" : K_DOWN,
							"left" : K_LEFT,
							"right" : K_RIGHT,
							"shoot" : K_z,
							"dash" : K_x,
							"use" : K_c,
							"swap_left" : K_a,
							"swap_right" : K_d}
		
			cPickle.dump([self.best_score,self.controls],f)
			f.close()
			
		else:
			#print "No exception throw so file is there. get score"
			self.best_score,self.controls = cPickle.load(f)
			self.old_bestscore = self.best_score
			#print type(self.best_score)
			
	def saveScore(self,new_score):
		
		try:
			f = file("scores.dat","w")
		
		except IOError:
			print "This shouldnt happen"
		
		else:
			score = [new_score,self.controls]
			self.best_score = new_score
			cPickle.dump(score,f)
			f.close()
			#print "save success"
			
	def reset(self):
		self.room_number = 1
		self.player_health = 100
		self.player_mana = 100
		#self.play_sounds = True
		#self.play_music = True
		self.exit_status = 0
		self.weapon_id = 0

def showPauseScreen(is_running):
	
	is_running = is_running
	p1 = [
			"Game Paused",
			"Press Esc to return to game",
			"Press Q to Quit to Main Menu"
			]
	
	xpos = 40
	ypos = 90
	y_gap = large_font.get_height() + 4
	 
	alpha_surf = pygame.Surface((W,H))
	alpha_surf.fill((0,0,0))	
	alpha_surf.set_alpha(150)
	
	p1_surfaces = []
	
	for i in range(len(p1)):
		
		string = p1[i]
		surf = large_font.render(string,False,(190,20,20))
		rect = surf.get_rect()
		rect.topleft = (xpos,ypos)
		ypos += y_gap
		p1_surfaces.append((surf,rect))
	
	
	for surf,rect in p1_surfaces:
		alpha_surf.blit(surf,rect)
			
	screen.blit(alpha_surf,(0,0))
	
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
				
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					sound_manager.play("select.ogg")
					return
				
				if event.key == K_q:
					sound_manager.play("select.ogg")
					is_running[0] = False
					state.exit_status = -1
					return
			
					
		#screen.fill((0,0,0))
			
		pygame.display.flip()
		
def showCreditsScreen():
	
	p1 = ["A game by Fyeidale Edmond.",
			"fienixgdev@gmail.com",
			"twitter: @fydmyster",
			"Sounds created using Dr Petters sfxr.",
			"Code and stuff done using Python and Pygame.",
			"Feedback is always appreciated.",
			"Shoot me a tweet or email."]
	
	xpos = 10
	ypos = 10
	y_gap = font.get_height() + 2
	 
	p1_surfaces = []
	
	for i in range(len(p1)):
		
		string = p1[i]
		surf = font.render(string,False,(255,240,240))
		rect = surf.get_rect()
		rect.topleft = (xpos,ypos)
		ypos += y_gap
		p1_surfaces.append((surf,rect))
	
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
				
			if event.type == KEYDOWN:
				if event.key in [K_RETURN,K_ESCAPE,K_SPACE]:
					sound_manager.play("select.ogg")
					return

		screen.fill((0,0,0))
		
		for surf,rect in p1_surfaces:
			screen.blit(surf,rect)
			
		pygame.display.flip()

def mapControlsScreen():
	
	p1 = [	"Move Up:  ",
			"Move Down:  ",
			"Move Left:  ",
			"Move Right:  ",
			"Shoot:  ",
			"Dash:  ",
			"Use:  ",
			"Swap Weapon Left: ",
			"Swap Weapon Right: ",
			"Return to Main Menu"]
	
	xpos = W/2
	ypos = 40
	y_gap = font.get_height() + 2
	 
	p1_surfaces = []
	key_surfaces =[]
	blend_images = []
	
	cur_option = 0
	is_setting_key = False
	
	for i in range(len(p1)):
		
		string = p1[i]
		surf = large_font.render(string,False,(255,240,240))
		rect = surf.get_rect()
		rect.center = (xpos,ypos)
		
		size = surf.get_size()
		tsurf = pygame.Surface(size)
		tsurf.fill((255,0,255))
		tsurf.set_colorkey((255,0,255))
		tsurf.blit(surf,(0,0))
		blend_img = tsurf.convert_alpha()
		blend_images.append(blend_img)
		
		ypos += y_gap
		p1_surfaces.append((surf,rect))
	
	
	for i in range(len(p1)-1):
		
		key = state.map[i]
		word_to_display = state.controls[key]
		
		if word_to_display is not None:
			string = pygame.key.name(word_to_display)
		else:
			string = ""
		
		adj_rect = p1_surfaces[i][1]
		
		surf = large_font.render(string,False,(255,240,240))
		rect = surf.get_rect()
		rect.left = adj_rect.right + 10
		rect.centery = adj_rect.centery
		
		key_surfaces.append((surf,rect))
	
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
						
			if event.type == KEYDOWN:
					
				if not is_setting_key:
				
					if event.key == K_UP:		
						cur_option = (cur_option-1) % len(p1)
						sound_manager.play("select.ogg")
							
					if event.key == K_DOWN:
						cur_option = (cur_option+1) % len(p1)
						sound_manager.play("select.ogg")
							
					
					if event.key == K_RETURN:
						if cur_option in range(len(p1)-1):
							# set key
							key = state.map[cur_option]
							state.controls[key] = None
						
							is_setting_key = True
							sound_manager.play("select.ogg")
							
						else:
							# return to menu
							sound_manager.play("select.ogg")
							# save controls
							
							state.saveScore(state.best_score)
							return
					
					if event.key == K_ESCAPE:
						sound_manager.play("select.ogg")
						state.saveScore(state.best_score)	
						return
				
				else:
					# we are setting the key now
					if event.key in [K_ESCAPE,K_RETURN]:
						# dont set anything ;  just leave
						is_setting_key = False
						
					else:
						key = state.map[cur_option]
						state.controls[key] = event.key
						is_setting_key = False
						sound_manager.play("select.ogg")
							
		#print cur_option
		screen.fill((0,0,0))
		
		key_surfaces = []
		for i in range(len(p1)-1):
			key = state.map[i]
			word_to_display = state.controls[key]
		
			if word_to_display:
				string = pygame.key.name(word_to_display)
			else:
				string = ""
		
			adj_rect = p1_surfaces[i][1]
			
			surf = large_font.render(string,False,(255,240,240))
			rect = surf.get_rect()
			rect.left = adj_rect.right + 10
			rect.centery = adj_rect.centery
		
			key_surfaces.append((surf,rect))
	
		
		for surf,rect in p1_surfaces:
			screen.blit(surf,rect)
		
		for surf,rect in key_surfaces:
			screen.blit(surf,rect)
		
		for i in range(len(p1)):
			if i == cur_option:
				t_rect = p1_surfaces[i][1]
						
				b_image = blend_images[i].copy()
				b_image.fill((0,0,0,255), None, BLEND_RGBA_MULT)
				b_image.fill((255,40,10)[0:3] + (0,), None, BLEND_RGBA_ADD)
				screen.blit(b_image,t_rect)
		
		pygame.display.flip()
		
def showDeadScreen(cur_floor):
	
	if  cur_floor> state.best_score:
		new_best = True
	else:
		new_best = False
		
	p1 = ["Ouch:","You Died"]
	
	# Need to understand this
	
	if not new_best:
		p2 = ["Floor Reached : %s" % cur_floor,
				"Best Floor Reached : %s" % state.best_score] 
	else:
		p2 = [  "Congratulations! New Best Reached",
				"Floor Reached : %s" % cur_floor,
				"Best Floor Reached : %s" % cur_floor]

	ypos = 10
	y_gap = font.get_height() + 4
	 
	p1_surfaces = []
	p2_surfaces = []
	
	for i in range(len(p1)):
		
		string = p1[i]
		surf = font.render(string,False,(255,20,10))
		rect = surf.get_rect()
		rect.centerx = W/2
		rect.y = ypos
		ypos += y_gap
		p1_surfaces.append((surf,rect))
		
	ypos = 120
	for i in range(len(p2)):
		
		string = p2[i]
		surf = font.render(string,False,(255,100,100))
		rect = surf.get_rect()
		rect.centerx = W/2
		rect.y = ypos
		ypos += y_gap
		p2_surfaces.append((surf,rect))
	
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
				
			if event.type == KEYDOWN:
				if event.key in [K_RETURN,K_ESCAPE,K_SPACE]:
					sound_manager.play("select.ogg")
					return

		screen.fill((0,0,0))
		
		for surf,rect in p1_surfaces:
			screen.blit(surf,rect)
			
		for surf,rect in p2_surfaces:
			screen.blit(surf,rect)
		
		pygame.display.flip()
		
def showHelpScreen():
	
	p1 = ["Movement:",
				"		I, J, K, L	",
				"Z  : Shoot",
				"X  : Dash",
				"A  : Cycle Weapon left",
				"D  : Cycle Weapon right",
				"C  : Use Door"]
		
	p2 = ["Keys open doors to the next floor",
			"You pick up keys from defeated foes",
			"Only your default weapon has infinite ammo,",
			"Replenish mana to get more ammo by defeating enemies"] 
	
	xpos = 10
	ypos = 10
	y_gap = font.get_height() + 2
	 
	p1_surfaces = []
	p2_surfaces = []
	
	for i in range(len(p1)):
		
		string = p1[i]
		surf = font.render(string,False,(255,240,240))
		rect = surf.get_rect()
		rect.topleft = (xpos,ypos)
		ypos += y_gap
		p1_surfaces.append((surf,rect))
		
	ypos = 150
	for i in range(len(p2)):
		
		string = p2[i]
		surf = font.render(string,False,(255,240,240))
		rect = surf.get_rect()
		rect.topleft = (xpos,ypos)
		ypos += y_gap
		p2_surfaces.append((surf,rect))
	
	
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
				
			if event.type == KEYDOWN:
				if event.key in [K_RETURN,K_ESCAPE,K_SPACE]:
					sound_manager.play("select.ogg")
					return

		screen.fill((0,0,0))
		
		for surf,rect in p1_surfaces:
			screen.blit(surf,rect)
			
		for surf,rect in p2_surfaces:
			screen.blit(surf,rect)
		
		pygame.display.flip()
		
def showMainMenu(state):
	global screen
	
	clock = pygame.time.Clock()
	timepassed = 0
	cur_option = 0
	tweenables = []
	
	textcolor = (230,230,230)
	ypos = 100
	positions = []
	strings = ["Start","Sounds : ","FullScreen : ","Controls","Help","Credits","Exit"]
	y_gap = large_font.get_height() + 2
	surfaces = []
	blend_images = []
	blendcolor = (255,50,0)
	effect_x = 0
	add = True
	alpha = 0
	crate = generic.FireCrate(0,0,16,16)
	
	banner_text = huge_font.render("N.A.D.S",False,(230,10,10))
	banner_rect = banner_text.get_rect()
	banner_rect.centerx = W/2
	banner_rect.y = 20
	
	line_def = font.render("Not Another Dungeon Shooter",False,(230,50,50))
	line_def_rect = line_def.get_rect()
	line_def_rect.centerx = banner_rect.centerx
	line_def_rect.top = banner_rect.bottom + 2
	
	
	emitter1 = po.ParticleEmitter(banner_rect.right + 16,banner_rect.y+10,
									strength = 0.3 ,mode = ("stream",500),direction=270,friction=1.01)
	emitter2 = po.ParticleEmitter(banner_rect.left - 24,banner_rect.y +10,
									strength = 0.3 ,mode = ("stream",500),direction=270,friction=1.01)
	
	for i in range(len(strings)):
		
		new_surf = large_font.render(strings[i],False,textcolor)
		new_rect = new_surf.get_rect()
		new_rect.centerx = W/3
		new_rect.y = ypos
		
		size = new_surf.get_size()
		tsurf = pygame.Surface(size)
		tsurf.fill((255,0,255))
		tsurf.set_colorkey((255,0,255))
		tsurf.blit(new_surf,(0,0))
		blend_img = tsurf.convert_alpha()
		
		blend_images.append(blend_img)
		surfaces.append([new_surf,new_rect])
		ypos += y_gap
	
	# create tween object for each option
	for i in range(len(strings)):
		
		t_rect = surfaces[i][1]
		new_tween = ease.Tweenable((t_rect.x,t_rect.y),t_rect.w,t_rect.h,(0,0,0))
		tweenables.append(new_tween)
	
	if state.play_sounds:
		sound_image = large_font.render("ON",False,(250,250,250))
	else:
		sound_image = large_font.render("OFF",False,(250,250,250))
	
	sound_image_rect = sound_image.get_rect()
	sound_image_rect.left = tweenables[1].rect.right+5
	sound_image_rect.centery = tweenables[1].rect.centery
	
	screen_image_rect = sound_image.get_rect()
	screen_image_rect.left = tweenables[2].rect.right+5
	screen_image_rect.centery = tweenables[2].rect.centery
	
	
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				
				if event.key == K_UP:
					cur_option = (cur_option - 1) % len(strings)
					sound_manager.play("select.ogg")
					
				if event.key == K_DOWN:
					cur_option = (cur_option + 1) % len(strings)
					sound_manager.play("select.ogg")
					
				if event.key == K_RETURN:
					if cur_option == 0:
						return
						
					elif cur_option == 1:
						state.play_sounds = not(state.play_sounds)
					
					elif cur_option == 2:
						if state.fullscreen:
							state.fullscreen = False
							screen = pygame.display.set_mode((W,H),DOUBLEBUF)
						else:
							state.fullscreen = True
							screen = pygame.display.set_mode((W,H),DOUBLEBUF|FULLSCREEN)

					elif cur_option == 3:
						mapControlsScreen()
					
					elif cur_option == 4:
						showHelpScreen()
					
					elif cur_option == 5:
						showCreditsScreen()
					
					elif cur_option == 6:
						pygame.quit()
						sys.exit()
					
				if event.key == K_LEFT:
					pass
				if event.key == K_RIGHT:
					pass
			
			if event.type == KEYUP:
				pass
		
		
		crate.update(timepassed)
		emitter1.update(timepassed)
		emitter2.update(timepassed)
		
		for i in range(len(tweenables)):	
			tween = tweenables[i]
			s_rect = surfaces[i][1]
			
			if add:
				alpha += 0.8 	
				if alpha >= 255:
					alpha = 255
					add = False
			else:
				alpha -= 0.8
				if alpha <= 0:
					alpha = 0
					add = True
				
					
			if cur_option == i:
				
				tween.moveTo(s_rect.x + 30,s_rect.y,300,"easeOutQuad")
			
			else:
				tween.moveTo(s_rect.x ,s_rect.y,300,"easeOutQuad")
			
		for tween in tweenables:
			tween.update(timepassed)
		
		screen.fill((0,0,0))
		
		for i in range(len(strings)):
			t_rect = tweenables[i].rect
			surface = surfaces[i][0]
			screen.blit(surface,t_rect)
		
		for i in range(len(strings)):
			if i == cur_option:
				t_rect = tweenables[i].rect
				
				
				b_image = blend_images[i].copy()
				b_image.fill((0,0,0,alpha), None, BLEND_RGBA_MULT)
				b_image.fill(blendcolor[0:3] + (0,), None, BLEND_RGBA_ADD)
				screen.blit(b_image,t_rect)
		
		if state.play_sounds:
			sound_image = large_font.render("ON",False,(250,250,250))
		else:
			sound_image = large_font.render("OFF",False,(250,250,250))
	
		sound_image_rect = sound_image.get_rect()
		sound_image_rect.left = tweenables[1].rect.right+5
		sound_image_rect.centery = tweenables[1].rect.centery
		
		
		if state.fullscreen:
			screen_image = large_font.render("ON",False,(250,250,250))
		else:
			screen_image = large_font.render("OFF",False,(250,250,250))
	
		screen_image_rect = sound_image.get_rect()
		screen_image_rect.left = tweenables[2].rect.right+5
		screen_image_rect.centery = tweenables[2].rect.centery
		
		screen.blit(screen_image,screen_image_rect)
		
		screen.blit(banner_text,banner_rect)
		screen.blit(line_def,line_def_rect)
		
		crate_image = crate.image.copy()
		crate_image = pygame.transform.scale(crate_image,(32,32))
		
		screen.blit(crate_image,(banner_rect.right + 8,banner_rect.y+10))
		screen.blit(crate_image,(banner_rect.left - 40,banner_rect.y +10))
		emitter1.draw(screen)
		emitter2.draw(screen)
		
		pygame.display.flip()
		
		timepassed = clock.tick(60)
		
		
class Room(object):
	
	def __init__(self,x,y,w,h):
	
		self.x = x
		self.y = y
		self.surface = pygame.Surface((w,h))
		self.surface.convert()
		self.surface_rect = self.surface.get_rect()
		self.surface_rect.topleft = (x,y)
		self.surface.fill((0,0,0))
	
	def clear(self,color=(0,0,0)):
		
		self.surface.fill(color)
	
	def update(self):
		
		self.surface_rect.topleft = (self.x,self.y)
	
W = 320
H = 240

#dW = 640
#dH = 480
state = GameState()

pygame.display.set_caption("B2k")

if state.fullscreen:
	screen = pygame.display.set_mode((W,H),DOUBLEBUF|FULLSCREEN)
else:
	screen = pygame.display.set_mode((W,H),DOUBLEBUF)
	
pygame.mouse.set_visible(False)

res_surf = pygame.Surface((320,240))

clock = pygame.time.Clock()

sound_manager = generic.SoundManager(state)

# load global images
hit_effect_images = gutils.sliceSheetColKey(12,12,"images\\hit_eff.png") 
kill_effect_images = gutils.sliceSheetColKey(22,22,"images\\kill_eff.png") 
break_effect_images = gutils.sliceSheetColKey(16,16,"images\\break_eff.png") 
key_effect_images = gutils.sliceSheetColKey(16,16,"images\\key_eff.png") 
p_killed_images = gutils.sliceSheetColKey(64,64,"images\\killed_boom.png")

images_dict = {
				"hit" : (hit_effect_images,12,12),
				"kill" : (kill_effect_images,22,22),
				"break" : (break_effect_images,16,16),
				"key" : (key_effect_images,16,16),
				"p_kill" : (p_killed_images,64,64)
				
					}

# load hud images
main_hud_image = pygame.Surface((W,42)).convert()
main_hud_image.fill((0,0,0))
main_hud_image.set_alpha(120)
main_hud_rect = main_hud_image.get_rect()

hud_item_image = pygame.image.load("images\\item_hud.png").convert()
hud_item_image.set_colorkey((255,0,255))

hud_item_rect1 = hud_item_image.get_rect()
hud_item_rect1.topleft = (50,4) 

hud_item_rect2 = hud_item_image.get_rect()
hud_item_rect2.topleft = (75,4) 


lifebar_image = pygame.image.load("images\\lifebar_hud.png").convert()
lifebar_image.set_colorkey((255,0,255))
lightning_image = pygame.image.load("images\\lightning_hud.png").convert()
lightning_image.set_colorkey((255,0,255))
basic_image = pygame.image.load("images\\basici_hud.png").convert()
basic_image.set_colorkey((255,0,255))
dual_image = pygame.image.load("images\\dual_hud.png").convert()
dual_image.set_colorkey((255,0,255))
bounce_image = pygame.image.load("images\\bounce_hud.png").convert()
bounce_image.set_colorkey((255,0,255))
wave_image = pygame.image.load("images\\wave_hud.png").convert()
wave_image.set_colorkey((255,0,255))
flame_image = pygame.image.load("images\\flame_hud.png").convert()
flame_image.set_colorkey((255,0,255))
piercer_image = pygame.image.load("images\\piercer_hud.png").convert()
piercer_image.set_colorkey((255,0,255))
rand_image = pygame.image.load("images\\rand_hud.png").convert()
rand_image.set_colorkey((255,0,255))

weapon_image_rect = flame_image.get_rect()
weapon_image_rect.center = hud_item_rect1.center
key_image_rect = pygame.Rect(0,0,12,12)
key_image_rect.center = hud_item_rect2.center
	
hud_images_dict = {
					"BasicGun" : basic_image,
					"DualGun" : dual_image,
					"BounceGun" : bounce_image,
					"WaveyGun" : wave_image,
					"LightningGun" : lightning_image,
					"FlameGun" : flame_image,
					"PiercerGun" : piercer_image,
					"RandomGun" : rand_image
					
					}
				
def runGameLoop():					
	
	is_running = [True]
	timepassed = 0
	fps = 0
	
	enemies = []
	items = []
	tiles = []
	drawables = []
	good_guys = []
	effects = []
	
	room = Room(0,0,LEVEL_W * TILE_W,LEVEL_H * TILE_H)

	level_generator = level_gen.LevelGenerator(LEVEL_W,LEVEL_H)
	level_properties = level_generator.generateLevel()

	# generate room grid for pathfinding
	level_grid = pathfind.Grid(level_properties[0],level_properties[1])

	for row in range(level_properties[1]):
		for col in range(level_properties[0]):
		
			surface = level_properties[2]
			pixel_array = level_properties[3]
		
			if pixel_array[col][row] == surface.map_rgb((255,0,0)) or\
			pixel_array[col][row] == surface.map_rgb((0,255,0)):
				# this is a wall; set square to blocked
				level_grid.set((col,row),True)
			

	level_gen.createLevelFrom(level_properties[0],level_properties[1],
						level_properties[2],level_properties[3],
						enemy_list=enemies,tile_list=tiles,item_list=items,draw_list=drawables,fx=effects,
						pcs=good_guys,images=images_dict,grid=level_grid)
		
	p = player.Player(is_running,40,40,enemies,tiles,effects,items,images_dict,sound_manager)
	p.health = state.player_health
	p.mana_amount = state.player_mana
	p.weapon_id = state.weapon_id
	p.attachGameState(state)
	
	room_number = state.room_number
	cam_ob_to_track = steer.Steerable("KArriveMovement",(p.x,p.x),10,10)
	cam_ob_to_track.current_steering_behaviour.setTimeToTarget(45.0)
	cam_ob_to_track.setTarget(p.cam_target)
	p.setState(cam_ob_to_track)

	good_guys.append(p)

	# set starting state for entities
	enemy_to_hold_key = random.choice(enemies)
	enemy_to_hold_key.setKey()
	
	grad_colors = [
					((40,10,0),(0,0,40)),
					((140,130,0),(0,100,130)),
					((10,100,0),(100,100,0)),
					((40,10,100),(0,100,60)),
					((10,10,90),(100,0,40)),
					((4,80,10),(60,130,40)),
					((19,140,149),(120,0,40)),
					((100,10,50),(0,29,120)),
					((40,30,90),(20,120,10)),
					((0,30,130),(80,10,60)),
					((140,0,90),(20,120,110))
					]
	
	pg = random.choice(grad_colors)
	
	# create ground surface
	ground_image = pygame.Surface((LEVEL_W * TILE_W,LEVEL_H * TILE_H)).convert()
	ground_image_size = ground_image.get_size()
	grad_image1 = pygame.Surface(((LEVEL_W * TILE_W)/2,LEVEL_H * TILE_H)).convert()
	grad_image2 = pygame.Surface(((LEVEL_W * TILE_W)/2,LEVEL_H * TILE_H)).convert()
	gutils.fillGradient(grad_image1,pg[0],pg[1],vertical=False)
	gutils.fillGradient(grad_image2,pg[1],pg[0],vertical=False)
	grad_image1.set_alpha(160)
	grad_image2.set_alpha(160)
	ground_image.fill((0,0,0))

	
	health_bar = generic.HealthBar(20,26,100)
	dash_bar = generic.DashBar(20,34,p.dash_waittime)
	
	for tile in drawables:
		tile.draw(ground_image)

		
	for wall in tiles:
		wall.draw(ground_image)

	# draw gradient	
	ground_image.blit(grad_image1,(0,0))	
	ground_image.blit(grad_image2,(ground_image_size[0]/2,0))	

		
	camera = g_obs.CameraHandler((320,240),room,cam_ob_to_track,delimit=False)
	camera.setState("lock",[(W/2,H/2)])

	while is_running[0]:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					showPauseScreen(is_running)
					
				if event.key == state.controls["left"]:
					p.left_is_down = True
				if event.key == state.controls["right"]:
					p.right_is_down = True
				if event.key == state.controls["up"]:
					p.up_is_down = True
					p.last_dir_v = 0
				if event.key == state.controls["down"]:
					p.down_is_down = True
					p.last_dir_v = 1
				
				if event.key == state.controls["shoot"]:
					p.firePrimary()
				if event.key == state.controls["swap_left"]:
					p.swapWeapon(-1)
				if event.key == state.controls["swap_right"]:
					p.swapWeapon(1)
				if event.key == state.controls["use"]:
					p.use()
				if event.key == state.controls["dash"]:
					p.dash()
				
	
			if event.type == KEYUP:
				if event.key == state.controls["left"]:
					p.left_is_down = False
				if event.key == state.controls["right"]:
					p.right_is_down = False
				if event.key == state.controls["up"]:
					p.up_is_down = False
				if event.key == state.controls["down"]:
					p.down_is_down = False
			
		p.update(timepassed)
	
		for baddie in enemies:
			baddie.update(timepassed)
	
		for item in items:
			item.update(timepassed)
	
		for item in items:
			if item.kind == "Mana":
				if item.rect.colliderect(p.rect):
					p.mana_amount += item.mana_value
					items.remove(item)
					sound_manager.play("mana.ogg")
					
			elif item.kind == "RoomKey":
				if item.rect.colliderect(p.rect):
					p.room_key = item
					items.remove(item)
					
					params = [images_dict["key"][0],1,15]
					new_effect = g_obs.AnimObject(params,p.x,p.y,0,0,1)
					effects.append(new_effect)
					
					sound_manager.play("key.ogg")
			
			elif item.kind == "DoorTile":
				if item.rect.colliderect(p.rect):
					if p.room_key is not None:
						item.is_open = True
						p.room_key = None
						sound_manager.play("door.ogg")
						
			elif item.kind == "FireCrate":
				if not item.alive:
					# add break animation
					params = [images_dict["break"][0],1,15]
					new_effect = g_obs.AnimObject(params,item.x,item.y,0,0,1)
					effects.append(new_effect)
					
					sound_manager.play("crate.ogg")
		
					items.remove(item)
					
		for baddie in enemies:
			if not baddie.alive:
				# add die animation
				params = [images_dict["kill"][0],1,15]
				new_effect = g_obs.AnimObject(params,baddie.rect.x-3,baddie.rect.y-3,0,0,1)
				effects.append(new_effect)
				
				sound_manager.play("ded.ogg")
		
				# if it has key ; drop a key object in item_list
				if baddie.holds_key:
					room_key = generic.RoomKey(*baddie.rect.topleft)
					items.append(room_key)
			
				# try particle emmiter if not too slow
				emitter = po.ParticleEmitter(baddie.rect.centerx,baddie.rect.centery,direction="random")
				emitter.burst()
				effects.append(emitter)
			
				# drop mana
			
				for i in range(random.randint(1,3)):
					xpos = random.randint(baddie.rect.left,baddie.rect.right)
					ypos = random.randint(baddie.rect.top,baddie.rect.bottom)
					mana = generic.Mana(xpos,ypos,p.cam_target)
					items.append(mana)
			
				enemies.remove(baddie)
				
				
		for effect in effects:
			effect.update(timepassed)
		
		health_bar.setCurHealth(p.health)
		health_bar.update()
		
		dash_bar.setCurTime(p.time_since_dash)
		dash_bar.update()
		
		cam_ob_to_track.update(timepassed)
		camera.track()
		
		room.update()
		
		screen.fill((0,0,0))
		room.clear()
		
		room.surface.blit(ground_image,(0,0))
		
		
		for item in items:
			item.draw(room.surface)
		
		p.draw(room.surface)
		
		for baddie in enemies:
			baddie.draw(room.surface)
		
		for effect in effects:
			effect.draw(room.surface)
		
		for effect in effects:
			if not effect.alive:
				effects.remove(effect)
		
		
		screen.blit(room.surface,room.surface_rect)
		
		# draw hud stuff
		main_hud_image.fill((0,0,0))
		main_hud_image.blit(hud_item_image,hud_item_rect1)
		main_hud_image.blit(hud_item_image,hud_item_rect2)
		
		
		
		current_weapon_image = hud_images_dict[p.cur_weapon.kind]
		main_hud_image.blit(current_weapon_image,weapon_image_rect)
		
		if p.room_key is not None:
			main_hud_image.blit(p.room_key.image,key_image_rect)
		
		# mana hud
		mana_surf = font.render("mana : %s" % p.mana_amount,False,(255,255,255))
		mana_rect = mana_surf.get_rect()
		mana_rect.x = hud_item_rect2.right + 6
		mana_rect.centery = hud_item_rect2.centery
		main_hud_image.blit(mana_surf,mana_rect)
		
		# current floor hud
		floor_surf = font.render("floor : %s" % state.room_number,False,(255,25,25))
		floor_rect = floor_surf.get_rect()
		floor_rect.x = mana_rect.right + 6
		floor_rect.centery = hud_item_rect2.centery
		main_hud_image.blit(floor_surf,floor_rect)
		
		health_bar.draw(main_hud_image)
		dash_bar.draw(main_hud_image)
		
		screen.blit(main_hud_image,main_hud_rect)
		
		
		#scale2x_surf = pygame.transform.scale(res_surf,(640,480))
		#screen.blit(scale2x_surf,(0,0))
		
		#print state.best_score
		pygame.display.flip()
		
		timepassed = clock.tick(60)
		#fps = clock.get_fps()
	else:
		
		#print (state.room_number,state.best_score)
		# hold a temp old score to test with showDeadScreen
		#state.old_bestscore = state.best_score
		
		if state.exit_status == 1:
			#print "writing game state"
			state.player_health = (p.health + 7)
			state.player_mana = p.mana_amount
			state.weapon_id = p.weapon_id
		
		elif state.exit_status == 0:
			
			# Theres a save bug here thats bugging me ,I'll check it out later
			showDeadScreen(state.room_number)
			
			if state.room_number > state.best_score:
				state.saveScore(state.room_number)
				#print "is saving"
				#print state.best_score
		
		elif state.exit_status == -1:
			# quit to main menu
			pass
				
def runApp():
	while True:
		if state.exit_status == 0 or state.exit_status == -1:
			state.reset()
			showMainMenu(state)
		
		runGameLoop()
		
runApp()