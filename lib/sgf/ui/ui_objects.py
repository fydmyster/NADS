import pygame,math,textwrap
from pygame.locals import*

#from sgf.gameobjects.g_objects import*
import sgf.utils.g_utils as u
import sgf.gameobjects.g_objects as g
#####
# TextLabel param_list structure is as follows:
# [fontname,size,systemfont,text,color,alpha]
# NOTE: Very compatible with room editor use
		
class TextLabel(object):
	def __init__(self,param_list,x=0,y=0,xvel=0.0,yvel=0.0,color=(255,255,255)):
		self.x = x
		self.y = y
		self.param_list = param_list
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.font_name = self.param_list[0]
		self.font_size = self.param_list[1]
		
		if self.param_list[2] == True:
			# load systemfont
			self.font = pygame.font.SysFont(self.font_name,self.font_size)
		else:
			# load user fonts
			self.font = pygame.font.Font(self.font_name,self.font_size)
		
		self.def_text = self.param_list[3]
		self.text = self.param_list[3]
		self.color = self.param_list[4]
		self.alpha = self.param_list[5]
		
		self.image = self.font.render(self.text,False,self.color)
		self.image.set_alpha(self.alpha)
		
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.x,self.y)
		self.xvel = xvel
		self.yvel = yvel
		self.friction = 0.928
		self.maxLiveTime = 2500
		self.acctime = 0
		self.alive = True
		
		self.alpha_per_tick = 0
		self.is_fading_in = False
		self.is_fading_out = False
		self.fade_in_reached = False
		self.fade_out_reached = False
		
		self.parse_complete = False
		
		self.parse_acctime = 0
		self.parse_updatetime = 0
		self.normal_parse_updatetime = 0
		self.fast_parse_updatetime = 0
		
		self.text_index = len(self.def_text)
		self.is_parsing = False
	
	def initParseState(self,normal_parse_updatetime,fast_parse_updatetime):
		"""Sets the text to an empty string so we can parse it cumulatively
		Call this if you want to use text parsing before any draw/update calls"""
		# param : parse_updatetime -> milliseconds that must pass before a character is appended to the string
		self.parse_updatetime = normal_parse_updatetime
		self.normal_parse_updatetime = normal_parse_updatetime
		self.fast_parse_updatetime = fast_parse_updatetime
		
		self.text_index = 0
		
		self.image = self.font.render(self.def_text[:self.text_index],False,self.color)
		self.rect = self.image.get_rect()
		self.image.set_alpha(self.alpha)
	
	def speedUpParse(self):
		self.parse_updatetime = self.fast_parse_updatetime
		
	def slowDownParse(self):
		self.parse_updatetime = self.normal_parse_updatetime
	
	def startParse(self):
		self.is_parsing = True
	
	def stopParse(self):
		self.is_parsing = False
	
	def parse(self,timepassed):
		if self.is_parsing:
			
			self.parse_acctime += timepassed
			
			if self.parse_acctime > self.parse_updatetime:
				self.parse_acctime = 0
				
				if self.text_index < len(self.def_text):
					self.text_index += 1
				else:
					self.is_parsing = False
					self.parse_complete = True
					
	def startFadeIn(self,alpha_per_tick):
		self.alpha_per_tick = alpha_per_tick
		self.is_fading_in = True
		self.is_fading_out = False
	
	def stopFadeIn(self):
		self.is_fading_in = False
	
	def fadeIn(self):
	
		if self.is_fading_in:
			if self.alpha < 255:
				self.alpha += self.alpha_per_tick
				
			else:
				self.alpha = 255
				self.is_fading_in = False
				self.fade_in_reached = True
				
	def startFadeOut(self,alpha_per_tick):
		self.alpha_per_tick = alpha_per_tick
		self.is_fading_out = True
		self.is_fading_in = False
		
	def stopFadeOut(self):
		self.is_fading_out = False
	
	def fadeOut(self):
	
		if self.is_fading_out:
			if self.alpha > 0:
				self.alpha -= self.alpha_per_tick
				
			else:
				self.alpha = 0
				self.is_fading_out = False
				self.fade_out_reached = True
	
	def updatePosition(self,timepassed):
		self.rect.topleft = (self.x,self.y)
	
	def update(self,timepassed):
		
		self.acctime+=timepassed
		if self.acctime>self.maxLiveTime:
			self.alive=False
		
		self.fadeIn()
		self.fadeOut()
		self.parse(timepassed)	
		
		self.image = self.font.render(self.def_text[:self.text_index],False,self.color)
		self.rect = self.image.get_rect()
		self.image.set_alpha(self.alpha)
		
		self.x += self.xvel
		self.y += self.yvel
		
		self.updatePosition(timepassed)
		
		self.yvel *= self.friction
		self.xvel *= self.friction
	
	def draw(self,Surface):
		Surface.blit(self.image,self.rect)

#####
# Meter param_list structure is as follows:
# [orientation,size,color,bg_color,border_color,alpha,optional_image]
# param orientation ; string either 'horizontal' or 'vertical'
# param color ; The color of the bar:can be a list of two values(that are tuples) - for lerping, or list of a single tuple
# param bg_color ; The color of background to the bar
# param size ; tuple (width,height) 
# optional_image should be None if not required	; only support per pixel alpha images
# NOTE: Very compatible with room editor use

		
class Meter(object):
	def __init__(self,param_list,x=0,y=0):
		self.x = x
		self.y = y
		self.param_list = param_list
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.lerp_color1 = None
		self.lerp_color2 = None
		
		# main variables that manage bar state
		self.bar_max_val = None
		self.data_holder = None
		self.state_set = False
		
		self.orientation = param_list[0]
		self.width = param_list[1][0]
		self.height = param_list[1][1]
		
		# check the color argument
		if len(param_list[2]) == 1:
			# only 1 color in list ; set as self.color
			self.color = param_list[2][0]
			
		elif len(param_list[2]) == 2:
			# set lerping colors too
			self.color = param_list[2][1]
			self.lerp_color1 = param_list[2][0]
			self.lerp_color2 = param_list[2][1]
		
		
		self.bg_color = param_list[3]
		self.border_color = param_list[4]
		self.alpha = param_list[5]
		self.optional_image = param_list[6]
		
		# construct bar
		self.bar_rect = pygame.Rect(0,0,self.width,self.height) 
		self.enclosing_rect = pygame.Rect(0,0,self.width,self.height)
		self.enclosing_rect.center = self.bar_rect.center
		
		# create image surface
		self.image = pygame.Surface((self.width,self.height))
		self.image.fill((255,0,255))
		self.image.set_colorkey((255,0,255))
	
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.x, self.y)
		
		# create optional_image if given
		if self.optional_image != None:
			self.border_image = pygame.image.load(self.optional_image).convert_alpha()
			self.border_image_rect = self.border_image.get_rect()
			
			self.border_image_rect.center = self.rect.center
		else:
			self.border_image = None
		
		pygame.draw.rect(self.image,self.color,self.bar_rect)
		pygame.draw.rect(self.image,self.border_color,self.enclosing_rect,3)
	
	
	def updateBarState(self):
		"""Manages the bar length"""
		
		# update the bar length state
		val = self.data_holder.getVal()
		
		if val < 0 :
			val = 0
		if val > self.bar_max_val:
			val = self.bar_max_val
		
		ratio = val / float(self.bar_max_val)
		
		if self.orientation == "horizontal":
			# update the width of bar_rect
			self.bar_rect.width  = self.width * ratio
		
		elif self.orientation == "vertical":
			# update the height of bar_rect
			self.bar_rect.height  = self.height * ratio
		
		# update the color if lerp_color1 available
		if self.lerp_color1 != None:
			self.color = u.colorLerp(self.lerp_color1,self.lerp_color2,ratio)
	
	def updatePosition(self,timepassed):
		self.rect.topleft = (self.x,self.y)
	
	def update(self,timepassed):
		
		if self.state_set:
			self.updateBarState()
		
		self.updatePosition(timepassed)
		
		if self.border_image != None:
			self.border_image_rect.center = self.rect.center
		
		if self.orientation == "vertical":
			self.bar_rect.bottomleft = (0,self.rect.height)
		
		# refresh image
		self.image.fill((255,0,255))
		pygame.draw.rect(self.image,self.bg_color,self.enclosing_rect)
		pygame.draw.rect(self.image,self.color,self.bar_rect)
		pygame.draw.rect(self.image,self.border_color,self.enclosing_rect,3)
		
		self.image.set_alpha(self.alpha)
		
	def draw(self,Surface):
		
		Surface.blit(self.image,self.rect)
		
		if self.border_image != None:
			Surface.blit(self.border_image,self.border_image_rect)
		
	def setState(self,bar_max_val,data_holder):
		"""Call this before any draw/update calls"""
		# sets up the bar to react to changes in data holder
		# param bar_max_val -> the maximum value that represents a full bar
		# param data_holder -> a g_utils DataOBject:the variable it holds represents percentage of a full bar
		
		self.bar_max_val = bar_max_val
		self.data_holder = data_holder
		
		self.state_set = True

#####
# TextDisplaySimple param_list structure is as follows:		
# [font_config,size,main_color,font_color,max_lines]
# param font_config ; list containing filename of the font to be used at index 0,
#	-  and the font_size
#	-  and at index 2 a boolean whether to use systemfont or not
# param size ; tuple (width,height) of the surface that holds the text  
# param font_color ; the font RGB color tuple
# param main_color ; the widgets background RGB color tuple; if you pass in (255,0,255,[alpha]) the bg will be transparent
# param max_lines ; max number of lines to get drawn before a scroll up is triggered

class TextDisplaySimple(object):
	"""Basic widget for displaying text with different display options 
	This one is a bit bare bones and must be composed with other stuff to get acceptable behaviour"""
	def __init__(self,param_list,x=0,y=0,y_spacing=0,x_padding=8,y_padding=5):
		self.x = x
		self.y = y
		
		self.param_list = param_list
		# create font object
		self.font_name = self.param_list[0][0]
		self.font_size = self.param_list[0][1]
		self.use_system_font = self.param_list[0][2]
		self.width,self.height = self.param_list[1]
		self.main_color = self.param_list[2]
		self.font_color = self.param_list[3]
		self.max_lines = self.param_list[4]
		
		self.image = pygame.Surface((self.width,self.height),SRCALPHA)	# create a per pixel alpha surface
		# because drawing transparent surfaces on colorkey-ed ones acts funny
		
		self.rect = self.image.get_rect()
		
		if self.main_color == (255,0,255):
			#self.image.set_colorkey(self.main_color)
			self.transparent = True
		else:
			self.transparent = False
		
		self.x_padding = x_padding
		self.y_padding = y_padding
		self.y_spacing = y_spacing
		
		self.typestring = None
		self.scroll_speed = None
		self.norm_alpha_per_tick = None
		self.fast_alpha_per_tick = None
		self.acctime = 0
		self.waittime = None
		
		self.cur_page = 0
		self.cur_line = 0
		
		self.used_scroll = False
		self.is_scrolling = False
		self.is_updating = False
		self.y_diff = None
		
		self.speed_up = False
		
		self.labels_master = []
		
	def setState(self,typestring,scroll_speed,param_list):
		"""Here we define the widget's display behaviour"""
		# param_list is as follows:
		# scroll_speed is the amount of pixels the text scrolls up when widget is filled
		
		# if typestring == 'fade': the param_list should contain [(norm_alpha_per_tick,fast_alpha_per_tick),waittime]
		# param alpha_per_tick -> the amount of alpha added on fade ins
		# fast_alpha_per_tick is not used so you can just pass in None (excuse this fugly interface chaps)
		# waittime -> the time in milliseconds we wait before we render the next line
		
		# if typestring == 'parse': the param_list should contain [(normal_parse_updatetime,fast_parse_updatetime)]
		# param alpha_per_tick -> the amount of alpha added on fade ins
		
		self.typestring = typestring
		
		# check the behaviour we're requesting
		if self.typestring == "fade":
			self.norm_alpha_per_tick = param_list[0][0]
			self.fast_alpha_per_tick = param_list[0][1]
			self.waittime = param_list[1]
		
		elif self.typestring == "parse":
			self.normal_parse_updatetime = param_list[0][0]
			self.fast_parse_updatetime = param_list[0][1]
		
		self.scroll_speed = scroll_speed
		
	def loadStrings(self,commands):
		"""Call this after setState; commands is a list of tuples
		Each tuple must contain strings
		If the number of strings in tuple > max_lines then a scroll up is triggered 
		Each tuple represent a page; when a page has been fully rendered a prompt is displayed
		to alert the user the need to supply input to go to the next page
		"""
		# create the labels from commands
		for page in commands:
			y_pos = self.y_padding
			l = []
			for string in page:
			
				if self.typestring == "fade":
					# make a TextLabel instance for each string
					params = [self.font_name,self.font_size,self.use_system_font,string,self.font_color,0]
					new_label = TextLabel(params,self.x_padding,y_pos)
					
					font_height = new_label.font.get_height()
					y_pos += (self.y_spacing + font_height)
					l.append(new_label)
				
				elif self.typestring == "parse":
					# make a TextLabel instance for each string
					params = [self.font_name,self.font_size,self.use_system_font,string,self.font_color,255]
					new_label = TextLabel(params,self.x_padding,y_pos)
					new_label.initParseState(self.normal_parse_updatetime,self.fast_parse_updatetime)
					
					font_height = new_label.font.get_height()
					y_pos += (self.y_spacing + font_height)
					l.append(new_label)
				
			self.labels_master.append(l)		
			
	def draw(self,Surface):
		
		if self.transparent:
			self.image.fill((0,0,0,0))
		else:
			self.image.fill(self.main_color)
			
		for label in self.labels_master[self.cur_page]:
			#label.image.fill((250,0,0,0),None,BLEND_MULT)		# inverts image(could find a use for this)
			label.draw(self.image)
			
		#Surface.blit(self.image,self.rect,None,BLEND_MULT)
		Surface.blit(self.image,self.rect)
		
	def updatePosition(self,timepassed):
		self.rect.topleft = (self.x,self.y)
	
	def startAction(self):
		self.is_updating = True
		
		if self.typestring == "fade":
			self.labels_master[self.cur_page][self.cur_line].startFadeIn(self.norm_alpha_per_tick)
		
		elif self.typestring == "parse":
			self.labels_master[self.cur_page][self.cur_line].startParse()
			print "do thid"
			
	def stopAction(self):
		self.is_updating = False
	
	def speedUp(self):
		"""Simple helper function that speeds up the parsing/fading of TextLabel"""
		self.speed_up = True
		
	def slowDown(self):
		"""Simple helper function thats slows down the parsing/fading of TextLabel"""
		self.speed_up = False
	
	def scrollUp(self):
		if self.is_scrolling:
			# subtract from scroll_val incrementally and subtract this from a the labels in cur_page
			#print "Yeah djj"
			
			if self.scroll_speed > self.scroll_val:				
				# move everything instantly
				for item in self.labels_master[self.cur_page]:
					item.y -= self.scroll_val
					
				self.is_scrolling = False
			else:
				# move gradually
				self.used_scroll -= self.scroll_speed
				
				for item in self.labels_master[self.cur_page]:
					item.y -= self.scroll_speed
				
				if self.used_scroll <= 0:
					self.is_scrolling = False
		
	def update(self,timepassed):
		
		self.labels_to_draw = self.labels_master[self.cur_page]
		
		self.updatePosition(timepassed)
		
		if self.is_updating:
			
			if self.typestring == "fade": 
				
				cur_label = self.labels_master[self.cur_page][self.cur_line]
				cur_label.startFadeIn(self.norm_alpha_per_tick)
			
				for label in self.labels_master[self.cur_page]:
					label.update(timepassed)
				
				if cur_label.fade_in_reached:
					self.acctime += timepassed
				
				if cur_label.fade_in_reached and self.acctime > self.waittime:
					self.cur_line += 1
					self.acctime = 0
					
					if self.cur_line > (self.max_lines - 1) and self.cur_line <= len(self.labels_master[self.cur_page])-1:
						self.is_scrolling = True
						self.scroll_val = self.labels_master[self.cur_page][1].y - self.labels_master[self.cur_page][0].y
						self.used_scroll = self.scroll_val
						
					if self.cur_line > len(self.labels_master[self.cur_page])-1:
						self.cur_page += 1
						#print "wtf"
						self.cur_line = 0
					
						if self.cur_page > len(self.labels_master)-1:
							self.cur_page -= 1
							self.is_updating = False
			
			elif self.typestring == "parse": 
				
				cur_label = self.labels_master[self.cur_page][self.cur_line]
				cur_label.startParse()
				
				for label in self.labels_master[self.cur_page]:
					label.update(timepassed)
				
				if cur_label.parse_complete:
					self.cur_line += 1
					
					#if self.cur_line == len(self.labels_master[self.cur_page]):
					#	pass
					#else:	
					#	self.labels_master[self.cur_page][self.cur_line].startParse()
		
					if self.cur_line > (self.max_lines - 1) and self.cur_line <= len(self.labels_master[self.cur_page])-1:
						self.is_scrolling = True
						self.scroll_val = self.labels_master[self.cur_page][1].y - self.labels_master[self.cur_page][0].y
						self.used_scroll = self.scroll_val
						
					if self.cur_line > len(self.labels_master[self.cur_page])-1:
						self.cur_page += 1
						self.cur_line = 0
					
						if self.cur_page > len(self.labels_master)-1:
							self.cur_page -= 1
							self.is_updating = False
			
			self.scrollUp() 
			
			if self.speed_up:
				if self.typestring == "parse":
					self.labels_master[self.cur_page][self.cur_line].speedUpParse()
				
				if self.typestring == "fade":
					self.labels_master[self.cur_page][self.cur_line].alpha = 255
			else:
				if self.typestring == "parse":
					self.labels_master[self.cur_page][self.cur_line].slowDownParse() 
	
#####	
# TextDisplayPrompt param_list structure is as follows:
# [font_config,size,main_color,font_color,border_color,optional_image]
# param font_config ; list containing filename of the font to be used at index 0,
#	-  and the font_size
#	-  and at index 2 a boolean whether to use systemfont or not 
# param color ; the font RGB color tuple
# param main_color ; the widgets background RGB color tuple
# # param border_color ; the border of the widget's RGB color tuple ; None if no border required
# param size ; tuple (max number of characters per line,max number of lines) 
# optional_image ; an image_filename and a string in a tuple/list : 'normal','alpha','colorkey' ;should be None if not required	

# @usage
# call set state to init the strings to be displayed first
# after that you can call startParse to begin printing text onto the widget
# calling stopParse halts the process
# calling speedUpParse speed up the parse process
# calling slowDownParse slows the parse process
# NOTE: Not compatible with room editor use

class TextDisplayPrompt(object):
	"""Simple interface that parses and displays given text interactively"""
	def __init__(self,param_list,x=0,y=0):
		
		self.x = x
		self.y = y
		
		self.param_list = param_list
		# create font object
		self.font_name = self.param_list[0][0]
		self.font_size = self.param_list[0][1]
		self.use_system_font = self.param_list[0][2]
		self.max_line_width, self.max_lines = self.param_list[1]
		self.main_color = self.param_list[2]
		self.font_color = self.param_list[3]
		self.border_color = self.param_list[4]
		self.image_name = self.param_list[5]
		self.alive = True
		
		if self.use_system_font == True:
			# load systemfont
			self.font = pygame.font.SysFont(self.font_name,self.font_size)
		else:
			# load user fonts
			self.font = pygame.font.Font(self.font_name,self.font_size)
		
		if self.image_name != None:
			if self.image_name[1] == "normal":
				self.pattern_image = pygame.image.load(self.image_name[0]).convert()
				
			elif self.image_name[1] == "colorkey":
				self.pattern_image = pygame.image.load(self.image_name[0]).convert()
				self.pattern_image.set_colorkey((255,0,255))
				
			elif self.image_name[1] == "alpha":
				self.pattern_image = pygame.image.load(self.image_name[0]).convert_alpha()
		
		else:
			self.pattern_image = None
			
		# CONFIG VARIABLES
		self.x_padding = 15			# didnt use these padding variables at all
		self.y_padding = 15			# will remove them eventually
		self.y_spacing = 5
		
		# text padding
		self.xmargin = 8
		self.ymargin = 4
		
		self.strings_list = []
		self.strings_images_list=[]
		self.strings_image_rect_list=[]
		
		
		self.command_strings = None
		self.parse_acctime = 0
		self.parse_updatetime = 250
		self.is_parsing = False
		self.prompt_is_showing = False
		
		self.normal_parse_updatetime = None
		self.fast_parse_updatetime = None
		
		self.cur_index = 0
		self.cur_line = 0
		self.cur_line_len = 0
		self.cur_page = 0
		self.max_pages = None
		self.end_reached = False		# this shows if we have gone through all the pages
			
		
		# create empty strings to hold the text data
		for i in range(self.max_lines):
			empty_string = ""
			self.strings_list.append(empty_string)
			
		# create test dummy string so we can get the idea of the max width for the widget
		
		test_string = "D" * self.max_line_width
		self.font_height = self.font.get_height()
		self.surface_width = self.font.size(test_string)[0]
		self.surface_height = (self.font_height + self.y_spacing) * (self.max_lines)
		
		self.prompt_text = "Press Enter"
		
		# the surface we draw stuff on 
		self.image = pygame.Surface((self.surface_width,self.surface_height))
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.x, self.y)
		self.image.set_colorkey((255,0,255))
		
		# a second surface that we apply colors to to accomadate alpha blitting of the widget
		self.alpha_image = pygame.Surface((self.surface_width,self.surface_height))
		self.alpha_image.set_colorkey((255,0,255))
		
		self.prompt_surface = self.font.render(self.prompt_text,False,self.font_color)
		self.prompt_rect  = self.prompt_surface.get_rect()
		
		# set up border if provided
		if self.border_color != None:
			self.border_rect = pygame.Rect(0,0,self.surface_width,self.surface_height)
	
	def setAlpha(self,alpha):
		self.alpha_image.set_alpha(alpha)
	
	def setState(self,parse_speeds,prompt_text,commands):
		"""parse_speeds is a tuple containing normal speed at [0] and fast speed at [1] (speeds are given in milliseconds)
		prompt_text is the text that is shown to prompt the user after each page display
		commands is a list of tuples ; Each containing string values 
		The number of string values must match the max_lines attribute
		Each tuple represents a single page to be displayed by the widget before a prompt is shown
		"""
		
		self.normal_parse_updatetime = parse_speeds[0]
		self.fast_parse_updatetime = parse_speeds[1]
		self.parse_updatetime = self.normal_parse_updatetime
		
		self.prompt_text = prompt_text
		self.command_strings = commands
		self.cur_line_len = len(self.command_strings[self.cur_page][self.cur_line])
		self.max_pages = len(self.command_strings)
			
	def startParse(self):
		"""Initiates the parsing process"""
		self.is_parsing = True
	
	def stopParse(self):
		"""Halts the parsing process"""
		self.is_parsing  = False
	
	def speedUpParse(self):
		"""Speed up the parsing process"""
		self.parse_updatetime = self.fast_parse_updatetime
	
	def slowDownParse(self):
		"""Slows down the parsing process"""
		self.parse_updatetime = self.normal_parse_updatetime
	
	def killPrompt(self):
		"""Call this to banish the prompt and clear the text or close the widget(if cur_page is on final index)"""
		if self.prompt_is_showing:
		
			if self.end_reached:
				# that was the last page; kill the widget
				self.alive = False
		
			else:
				# reset all the strings
				self.resetStrings()
				self.startParse()
		
			self.prompt_is_showing = False
			
	def parse(self,timepassed):
		"""Runs the parse process that gets string slices from the appropriate command_strings"""
		if self.is_parsing:
			# parse and command_strings and update self.strings_list
			self.parse_acctime += timepassed
			
			if self.parse_acctime > self.parse_updatetime:
				
				self.cur_index += 1
				self.parse_acctime = 0
				
				if self.cur_index > self.cur_line_len - 1:
					# go to next line
					self.cur_line +=1
					self.cur_index = 0
					
					if self.cur_line > self.max_lines - 1:
						self.cur_page += 1
						self.cur_line = 0
						
						if self.cur_page > self.max_pages -1:
							self.end_reached = True
							self.cur_page = self.max_pages -1
							
						# show prompt here
						self.stopParse()
						self.prompt_is_showing = True
	
	def resetStrings(self):
		"""Sets default values to the strings_list; Thereby refreshing the widget"""
		self.strings_list = []
		# create empty strings to hold the text data
		for i in range(self.max_lines):
			empty_string = ""
			self.strings_list.append(empty_string)
		
	def updateStrings(self):
		"""updates the strings_list and image surfaces"""
		self.strings_list[self.cur_line] = self.command_strings[self.cur_page][self.cur_line][:self.cur_index]
		
		self.strings_images_list=[]
		self.strings_image_rect_list=[]
		for i in range(self.max_lines):
			string_image = self.font.render(self.strings_list[i],False,self.font_color)
			string_rect = string_image.get_rect()
			string_rect.topleft = (self.xmargin,((self.font_height+2)* i) + self.ymargin ) # 4 is the gap between text and top of widget 
			
			self.strings_images_list.append(string_image)
			self.strings_image_rect_list.append(string_rect)
		
		self.prompt_surface = self.font.render(self.prompt_text,False,self.font_color)
		self.prompt_rect  = self.prompt_surface.get_rect()
		
		
	def draw(self,Surface):
		"""Draws the widget to the specified Surface"""
		# clear the surfaces we draw upon
		if not self.prompt_is_showing:
		
			if self.pattern_image != None:
				# pattern image was provided ; draw it
				self.alpha_image.fill((255,0,255))
				self.alpha_image.blit(self.pattern_image,(0,0))	
			else:
				# just do a solid fill instead
				self.alpha_image.fill(self.main_color)
		
		self.image.fill((255,0,255))
		
		# draw border if arguments provided
		if self.border_color != None:
			pygame.draw.rect(self.alpha_image,self.border_color,self.border_rect,3)
		
		# draw strings
		for i in range(self.max_lines):
			self.image.blit(self.strings_images_list[i],self.strings_image_rect_list[i])
		
		if self.prompt_is_showing:
			# draw prompt text
			self.prompt_rect.right = self.rect.width - 4
			self.image.blit(self.prompt_surface,self.prompt_rect)
		
		Surface.blit(self.alpha_image,self.rect)
		Surface.blit(self.image,self.rect)
		
	def update(self,timepassed):
		"""Update the entire widget components"""
		# update position
		self.rect.topleft = (self.x, self.y)
		
		self.parse(timepassed)
		
		self.updateStrings()

#####
# YesNoPrompt param_list structure is as follows:
# [options,font_config,font_color,main_color,border_color]
# options is a list containing 2 strings ; index 0 represents yes_text, index 1 represents no_text
# - yes_text ; string that will represent choice 1
# - no_text ; string that will represent choice 0
# param font_config ; list containing filename of the font to be used at index 0,
#	-  and the font_size
#	-  and at index 2 a boolean whether to use systemfont or not
# param border_color ; the border of the widget's RGB color tuple ; None if no border required
# pointer_image ; an image_filename and a string in a tuple/list : 'normal','alpha','colorkey'	
# NOTE: Not compatible with room editor use

class YesNoDialog(object):
	"""Offers the user a choice selection from two objects"""
	def __init__(self,param_list,pointer_image,x,y,w,h):
		
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.yes_text = param_list[0][0]
		self.no_text = param_list[0][1]
		self.font_name = param_list[1][0]
		self.font_size = param_list[1][1]
		self.use_system_font = param_list[1][2]
		self.font_color = param_list[2]
		self.main_color = param_list[3]
		self.border_color = param_list[4]
		self.alive = True
		
		self.main_surface = pygame.Surface((self.w,self.h))
		self.main_surface_rect = self.main_surface.get_rect()
		
		self.xmargin = 5
		self.selection = 0
		
		if self.use_system_font == True:
			# load systemfont
			self.font = pygame.font.SysFont(self.font_name,self.font_size)
		else:
			# load user fonts
			self.font = pygame.font.Font(self.font_name,self.font_size)
		
		if pointer_image[1] == "normal":
			self.pointer_image = pygame.image.load(pointer_image[0]).convert()
		
		elif pointer_image[1] == "alpha":
			self.pointer_image = pygame.image.load(pointer_image[0]).convert_alpha()
		
		elif pointer_image[1] == "colorkey":
			self.pointer_image = pygame.image.load(pointer_image[0]).convert()
			self.pointer_image.set_colorkey((255,0,255))
			
		self.pointer_image_rect = self.pointer_image.get_rect()
		
		# create text surfaces
		self.yes_text_surface = self.font.render(self.yes_text,False,self.font_color)
		self.yes_text_rect = self.yes_text_surface.get_rect()
		self.yes_text_rect.centery = self.h/2
		
		self.no_text_surface = self.font.render(self.no_text,False,self.font_color)
		self.no_text_rect = self.yes_text_surface.get_rect()
		self.no_text_rect.centery = self.h/2
		
		# work out text x positions
		yes_text_x = self.pointer_image_rect.width + (self.xmargin*2)
		no_text_x = yes_text_x + (self.main_surface_rect.width/2)
		
		# set the positions
		self.yes_text_rect.left = yes_text_x
		self.no_text_rect.left = no_text_x
		
		self.pointer_positions = [(self.xmargin,self.h/2),((self.w/2) + self.xmargin, self.h/2)]
		self.pointer_xy = self.pointer_positions[self.selection]
		
	def draw(self,Surface):
		"""Draws the widget to the specified Surface"""
		self.main_surface.fill(self.main_color)
		# draw the text surfaces
		self.main_surface.blit(self.yes_text_surface,self.yes_text_rect)
		self.main_surface.blit(self.no_text_surface,self.no_text_rect)
		
		# draw the pointer_image
		self.main_surface.blit(self.pointer_image, self.pointer_image_rect)
		
		# draw border if border_color provided
		if self.border_color != None:
			pygame.draw.rect(self.main_surface,self.border_color,(0,0,self.w,self.h),4)
		
		Surface.blit(self.main_surface,self.main_surface_rect)
	
	def scrollSelectionLeft(self):
		"""Moves the pointer_image left"""
		if self.selection > 0:
			self.selection -=1
	
	def scrollSelectionRight(self):
		"""Moves the pointer_image right"""
		if self.selection < 1:
			self.selection +=1
	
	def getSelection(self):
		"""Returns the selected option
		If 0 : yes_text was selected ; if 1 : no_text was selected"""
		# if yes chosen returns 0, I know it's effing backwards, don't judge me
		
		return self.selection
	
	def update(self,timepassed):
		"""Update the entire widget components"""
		# update position	
		self.main_surface_rect.topleft = (self.x,self.y)
	
		self.pointer_xy = self.pointer_positions[self.selection]
		self.pointer_image_rect.centery = self.pointer_xy[1]
		self.pointer_image_rect.x = self.pointer_xy[0]
		
#####
# ScrollingTextWidget param_list structure is as follows:
# [text,font_config,font_color,main_color,border_color]
# text is one (giant) string that contains the text to display
# param font_config ; list containing filename of the font to be used at index 0,
#	-  and the font_size
#	-  and at index 2 a boolean whether to use systemfont or not
# param border_color ; the border of the widget's RGB color tuple ; None if no border required	
# NOTE: Not compatible with room editor use
	
class ScrollingTextWidget(object):
	"""Displays vertically scrolling text"""
	def __init__(self,param_list,x,y,w,h,xmargin=30,ymargin=30,y_spacing=0):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.text = param_list[0]
		self.font_name = param_list[1][0]
		self.font_size = param_list[1][1]
		self.use_system_font = param_list[1][2]
		self.font_color = param_list[2]
		self.main_color = param_list[3]
		self.border_color = param_list[4]
		self.alive = True
		self.alpha = 255
		
		if self.use_system_font == True:
			# load systemfont
			self.font = pygame.font.SysFont(self.font_name,self.font_size)
		else:
			# load user fonts
			self.font = pygame.font.Font(self.font_name,self.font_size)
		
		self.scroll_dir = None
		self.scroll_speed = None
		self.is_scrolling = False
		self.num_loops = None
		
		self.xmargin = xmargin
		self.ymargin = ymargin
		self.y_spacing = y_spacing
		
		self.main_surface = pygame.Surface((self.w-self.xmargin,self.h-self.ymargin))
		self.main_surface_rect = self.main_surface.get_rect()
		
		self.main_surface.set_colorkey((255,0,255))
		
		# a second surface that we apply colors to to accomadate alpha blitting of the widget
		self.alpha_image = pygame.Surface((self.w,self.h))
		self.alpha_image.set_colorkey((255,0,255))
		self.alpha_image_rect = self.alpha_image.get_rect()
		self.alpha_image.convert()
		
		self.alpha_image_rect.topleft = (self.x,self.y)
		self.main_surface_rect.center = self.alpha_image_rect.center
		self.alpha_image.set_alpha(self.alpha)
		
		# calculate the size of one text character
		char_size = self.font.size("D")
		num_chars_per_line = self.main_surface_rect.width / char_size[0]
		print "num_chars_per_line :",num_chars_per_line
		
		# create text wrapper
		c = textwrap.TextWrapper(width = num_chars_per_line, break_long_words = False)
		strings_list = c.wrap(self.text)
		
		print strings_list
		
		#starting_text_pos = self.main_surface.height
		starting_text_pos = 0
		font_height = self.font.get_height()
		self.strings_images_list = []
		self.strings_image_rect_list = []
		
		# for each string create a text surface
		for string in strings_list:
			text_surface = self.font.render(string,False,self.font_color)
			text_rect = text_surface.get_rect()
			
			# calculate new y position
			text_rect.y = starting_text_pos
			
			# append the newly created data
			self.strings_images_list.append(text_surface)
			self.strings_image_rect_list.append(text_rect)
			
			# update y position
			starting_text_pos += (font_height + self.y_spacing)
	
	def setState(self,scroll_dir,scroll_speed,num_loops):
		"""Initialises the widget to a usable state
		Call this before any draw or update calls"""
		# @param scroll_dir : A string either 'up' or 'down' indicating scroll direction
		# @param scroll_speed : A float indicating how many pixels the text moves by each tick
		# @loops the number of times the text is shown as an iteration
		# - loops can be any integer > 1 : indicating the number of iterations
		# - 0 : doesnt loop at all(pointless really)
		# - -1 : loops indefinitely until destroyed
		
		self.scroll_dir = scroll_dir
		self.scroll_speed = scroll_speed
		self.num_loops = num_loops
		
		# calculate the size of one text character
		char_size = self.font.size("D")
		num_chars_per_line = self.main_surface_rect.width / char_size[0]
		#print "num_chars_per_line :",num_chars_per_line
		
		# create text wrapper
		c = textwrap.TextWrapper(width = num_chars_per_line, break_long_words = False)
		strings_list = c.wrap(self.text)
		#print strings_list
		font_height = self.font.get_height()
		self.strings_images_list = []
		self.strings_image_rect_list = []
		self.positions_list = []		# holds the text_rect y values that we add scroll_speed to directly
										# this is to prevent the rounding error that occurs when directly modifying rect positions
		
		if self.scroll_dir == "up":
			starting_text_pos = self.main_surface_rect.height	
				
			# for each string create a text surface
			for string in strings_list:
				text_surface = self.font.render(string,False,self.font_color)
				text_rect = text_surface.get_rect()
			
				# calculate new y position
				text_rect.y = starting_text_pos
				text_y = starting_text_pos
				
				# append the newly created data
				self.strings_images_list.append(text_surface)
				self.strings_image_rect_list.append(text_rect)
				self.positions_list.append(text_y)
				
				# update y position
				starting_text_pos += (font_height + self.y_spacing)
		
		elif self.scroll_dir == "down":
			starting_text_pos = 0 - font_height
			
			for i in range(len(strings_list)-1,-1,-1):
				text_surface = self.font.render(strings_list[i],False,self.font_color)
				text_rect = text_surface.get_rect()
			
				# calculate new y position
				text_rect.y = starting_text_pos
				text_y = starting_text_pos
				
				# append the newly created data
				self.strings_images_list.append(text_surface)
				self.strings_image_rect_list.append(text_rect)
			
				# update y position
				starting_text_pos -= (font_height + self.y_spacing)
				self.positions_list.append(text_y)
				
	def startScroll(self):
		"""Initiates the scrolling process"""
		self.is_scrolling = True
	
	def stopScroll(self):
		"""Halts the scrolling process"""
		self.is_scrolling  = False
			
	def update(self,timepassed):
		"""updates the widget"""
		# update position
		
		for i in range(len(self.positions_list)):
			self.strings_image_rect_list[i].y = self.positions_list[i]
		
		self.alpha_image_rect.topleft = (self.x,self.y)
		self.main_surface_rect.center = self.alpha_image_rect.center
		
		self.scroll()
		self.checkScrollState()
		
		#print self.is_scrolling
		
	def checkScrollState(self):
		"""Checks to see if we have exceeded our iteration quota"""
		if self.scroll_dir == "up":
			# check if the last text_surface has gone higher than main_surface
			if self.strings_image_rect_list[-1].y < 0 - self.strings_image_rect_list[-1].height:
				# entire text has been displayed
				if self.num_loops == -1:
					# reset to  default starting conditions
					self.setState(self.scroll_dir,self.scroll_speed,-1)
				
				else:
					self.num_loops -= 1
					self.setState(self.scroll_dir,self.scroll_speed,self.num_loops)
				
		elif self.scroll_dir == "down":
			# check if the first text_surface has gone lower than main_surface
			if self.strings_image_rect_list[-1].y >  self.main_surface_rect.height:
				# entire text has been displayed
				if self.num_loops == -1:
					# reset to  default starting conditions
					self.setState(self.scroll_dir,self.scroll_speed,-1)
				
				else:
					self.num_loops -= 1
					self.setState(self.scroll_dir,self.scroll_speed,self.num_loops)
				
					
		# if num_loops have been exhausted
		if self.num_loops == 0:
			self.is_scrolling = False
			self.alive = False
		
	def scroll(self):
		"""Moves the text surfaces"""
		if self.is_scrolling:
			# check if we're scrolling up or down
			if self.scroll_dir == "up":
				# move all surfaces up
				for i in range(len(self.positions_list)):
					self.positions_list[i] = self.positions_list[i] - self.scroll_speed
					
			elif self.scroll_dir == "down":
				# move all surfaces up
				for i in range(len(self.positions_list)):
					self.positions_list[i] = self.positions_list[i] + self.scroll_speed
				
				
	def draw(self,Surface):
		"""Draws the widget to the provided Surface"""
		self.main_surface.fill((255,0,255))
		
		if self.main_color != None:
			self.alpha_image.fill(self.main_color)
		else:
			self.alpha_image.fill((255,0,255))
		
		# draw border if provided
		if self.border_color != None:
			pygame.draw.rect(self.alpha_image,self.border_color,(0,0,self.alpha_image_rect.width,self.alpha_image_rect.height),4)
		
		# draw strings onto main_surface
		#self.main_surface.blit(self.alpha_image,(0,0))
		for i in range(len(self.strings_image_rect_list)):
			self.main_surface.blit(self.strings_images_list[i],self.strings_image_rect_list[i])
		
		# draw main_surface
		Surface.blit(self.alpha_image,self.alpha_image_rect)
		Surface.blit(self.main_surface,self.main_surface_rect)

#####
# MenuSelectionWidget param_list structure is as follows:
# [selection_options_text,font_config,font_color,main_color,border_color]
# selection_options_text is a list that contains strings(the text for each selection option)
# param font_config ; list containing filename of the font to be used at index 0,
#	-  and the font_size
#	-  and at index 2 a boolean whether to use systemfont or not
# param font_color is an RGB tuple
# param main_color is the widgets bg_color ; None if transparent
# param border_color ; the border of the widget's RGB color tuple ; None if no border required	
# NOTE: Not compatible with room editor use
		
class MenuSelectionWidget(object):
	"""A widget that allows for selection of an option from multiple entries"""
	def __init__(self,param_list,x,y,w,h,font_highlight = None,pointer_image = None,label_color = None,xmargin = 8):
		# param font_highlight : the color to make the selected text if not passed None
		# pointer_image : an image_filename and a string in a tuple/list : 'normal','alpha','colorkey' at
		# -index [2] of pointer_image : None indicating use of a single static image
		# - or a list containing the width and height of a single image on the sprite sheet
		
		# label_color : a list/tuple containing the color to make the bg of the button at index 0
		# - at index 1 a RGB tuple indicating the color to lerp the bg of the button; or None indicating
		# - no lerping
		# - at index 2 : the lerp factor we add each frame ; or None
		
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.pointer_xmargin = xmargin
		
		self.selection_options_text = param_list[0]
		self.selection_options_rect = []
		self.selection_options_surf = []
		self.selection_options_color = []
		
		self.label_rects_list = []
		
		# the main var that indicates the selected option
		self.selection = 0
		
		self.font_name = param_list[1][0]
		self.font_size = param_list[1][1]
		self.use_system_font = param_list[1][2]
		self.font_color = param_list[2]
		self.main_color = param_list[3]
		self.border_color = param_list[4]
		
		if self.use_system_font == True:
			# load systemfont
			self.font = pygame.font.SysFont(self.font_name,self.font_size)
		else:
			# load user fonts
			self.font = pygame.font.Font(self.font_name,self.font_size)
		
		self.font_highlight = font_highlight
		self.pointer_image = pointer_image
		self.pointer_options = pointer_image
		self.label_color = label_color
		
		self.num_options = len(self.selection_options_text)
		
		self.factor_behaviour = "add"		# can be 'add' or 'sub' : determines whether we add or subtract the lerp factor
		
		# create pointer_image if available
		if self.pointer_image != None:
			if self.pointer_options[2] == None:
				# load a single image
				if pointer_image[1] == "normal":
					self.pointer_image = pygame.image.load(pointer_image[0]).convert()
		
				elif pointer_image[1] == "alpha":
					self.pointer_image = pygame.image.load(pointer_image[0]).convert_alpha()
		
				elif pointer_image[1] == "colorkey":
					self.pointer_image = pygame.image.load(pointer_image[0]).convert()
					self.pointer_image.set_colorkey((255,0,255))
			
				self.pointer_image_rect = self.pointer_image.get_rect()
			
			else:
				# load a list of images from spriteSheet
				animoptions = self.pointer_image[2]
				w, h = animoptions
				
				if pointer_image[1] == "normal":
					self.pointer_images_list = sliceSheetNorm(w,h,pointer_image[0])
		
				elif pointer_image[1] == "alpha":
					self.pointer_images_list = sliceSheetAlpha(w,h,pointer_image[0])
		
				elif pointer_image[1] == "colorkey":
					self.pointer_images_list = sliceSheetColKey(w,h,pointer_image[0])
					
				# create AnimObject
				self.anim_ob = g.AnimObject([self.pointer_images_list,-1,8],0,0)
				
		# create main_surface
		self.main_surface = pygame.Surface((self.w,self.h))
		self.main_surface.set_colorkey((255,0,255))
		
		self.main_surface_rect = self.main_surface.get_rect()
		self.main_surface_rect.topleft = (self.x,self.y)
		
		# append colors
		for i in range(self.num_options):
			self.selection_options_color.append(self.font_color)
		
		# create the text surfaces to draw
		for i in range(self.num_options):
			text_surface = self.font.render(self.selection_options_text[i],False,self.selection_options_color[i])
			text_rect = text_surface.get_rect()
			
			self.selection_options_surf.append(text_surface)
			self.selection_options_rect.append(text_rect)
		
		# create background label rects used to align and subdivide the widgets text_rect
		rect_height = self.h / self.num_options
		for i in range(self.num_options):
			label_rect = pygame.Rect(0,i * rect_height, self.w ,rect_height)
			self.label_rects_list.append(label_rect)
		
		# check if lerping was requested 
		if self.label_color[1] != None:
			# lerp requested
			self.factor = 0.0
			self.lerp_draw_color = None
		
	def scrollSelectionUp(self):
		"""Moves up the selection options"""
		self.selection = (self.selection - 1) % self.num_options
	
	def scrollSelectionDown(self):
		"""Moves down the selection options"""
		self.selection = (self.selection + 1) % self.num_options
	
	def getSelection(self):
		"""Returns the index of the selected option"""
		
		return self.selection
	
	def update(self,timepassed):
		
		if self.label_color[1] != None:
			'''
			self.factor = (self.factor + self.label_color[2]) % 1.0
			self.lerp_draw_color = u.colorLerp(self.label_color[0],self.label_color[1],self.factor)
			'''
			if self.factor_behaviour == "add":
				self.factor = (self.factor + self.label_color[2])
				
				if self.factor > 1:
					self.factor = 1
					self.factor_behaviour = "sub"
			
			elif self.factor_behaviour == "sub":
				self.factor = (self.factor - self.label_color[2])
				
				if self.factor < 0:
					self.factor = 0
					self.factor_behaviour = "add"
			
			self.lerp_draw_color = u.colorLerp(self.label_color[0],self.label_color[1],self.factor)
			
		if self.font_highlight != None:
			# recreate the surfaces to show change in selected option font color
			
			# set the selected option index color to font_highlight
			for i in range(self.num_options):
				if i == self.selection:
					self.selection_options_color[i] = self.font_highlight
				else:
					self.selection_options_color[i] = self.font_color
				
			self.selection_options_rect = []
			self.selection_options_surf = []
			
			for i in range(self.num_options):
				text_surface = self.font.render(self.selection_options_text[i],False,self.selection_options_color[i])
				text_rect = text_surface.get_rect()
			
				self.selection_options_surf.append(text_surface)
				self.selection_options_rect.append(text_rect)
		
		# update the anim_ob if available
		if self.pointer_options != None:
			if self.pointer_options[2] != None:
				self.anim_ob.x = self.pointer_xmargin
				self.anim_ob.y = self.label_rects_list[self.selection].centery - (self.anim_ob.rect.height / 2)
			
				self.anim_ob.update(timepassed)
			
		# update text_rect positions
		for i in range(self.num_options):
			self.selection_options_rect[i].center = self.label_rects_list[i].center
		
		# update main_surface
		self.main_surface_rect.topleft = (self.x,self.y)
		
	def draw(self,Surface):
		
		# draw main_surface
		if self.main_color != None:
			self.main_surface.fill(self.main_color)
		else:
			# make transparent
			self.main_surface.fill((255,0,255))
		
		# draw label_color if available
		if self.label_color != None:
			if self.label_color[1] == None:
				pygame.draw.rect(self.main_surface,self.label_color[0],self.label_rects_list[self.selection])
			
			else:
				# lerp the colors
				pygame.draw.rect(self.main_surface,self.lerp_draw_color,self.label_rects_list[self.selection])
			
		# draw text_surface 
		for i in range(self.num_options):
			self.main_surface.blit(self.selection_options_surf[i],self.selection_options_rect[i])
		
		# draw pointer_image if available
		if self.pointer_options != None:
			
			if self.pointer_options[2] == None:
				# draw single static image
				self.pointer_image_rect.centery = self.label_rects_list[self.selection].centery
				self.pointer_image_rect.left = self.pointer_xmargin
				
				self.main_surface.blit(self.pointer_image,self.pointer_image_rect)
			
			else:
				self.anim_ob.draw(self.main_surface)
			
		# draw border if available
		if self.border_color != None:
			pygame.draw.rect(self.main_surface,self.border_color,(0,0,self.w,self.h),4)
		
		Surface.blit(self.main_surface,self.main_surface_rect)

#####
# SlideShowWidget param_list structure is as follows:
# [options,main_color,border_color]
# param options = [(typestring,items,loops/milliseconds),.... more optional(typestring,items) ]

# param options : typestring is a string either 'anim' or 'static'
# - if typestring == 'anim' then options[1] should be a list of images surface; options[2] = num_loops to play the anim
# - if typestring == 'static' then options[1] should be a list containing a SINGLE surface ; options[2] = milliseconds to show image

# param main_color is the widgets bg_color ; None if transparent
# param border_color ; the border of the widget's RGB color tuple ; None if no border required	
# NOTE: Not compatible with room editor use
		
class SlideShowWidget(object):
	"""Class that displays images and/or animations in sequence with transitions
	Make sure you draw it onto a non colorkey surface in the background"""
	def __init__(self,param_list,x,y,w,h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.param_list = param_list
		self.options = param_list[0]
		self.main_color = param_list[1]
		self.border_color = param_list[2]
		
		self.surface = pygame.Surface((self.w,self.h))
		self.rect = self.surface.get_rect()
		self.rect.topleft = (self.x,self.y)
		
		self.surface.set_colorkey((255,0,255))
		self.alive = True
		self.slide_items_dict = {}
		self.current_display_key = 0 	# used as a key to the dictionary
		
		self.fade_out_reached = False
		self.fade_in_reached = False
		self.is_fading_out = False
		self.is_fading_in = False
		self.alpha = 255
		
		self.alpha_per_tick = 4		# the amount of transition alpha we apply on each iteration		
		self.show_acctime = 0
		self.show_updatetime = None
		
		for i in range(len(self.options)):
			
			if self.options[i][0] == "anim":
				# create AnimObject and store it in slide_items_dict
				# this one plays based on loops
				anim = g.AnimObject([self.options[i][1],self.options[i][2],8],0,0)
				self.slide_items_dict[i] = ("loop",anim)
				
			elif self.options[i][0] == "static":
				# create AnimObject and store it in slide_items_dict
				# this one plays based on milliseconds passed
				anim = g.AnimObject([self.options[i][1],1,8],0,0)
				self.slide_items_dict[i] = (self.options[i][2],anim)	# add the ms and anim to the dict
			
		# get the first item to be displayed
		self.cur_item = self.slide_items_dict[self.current_display_key]
		self.max_slides = len(self.slide_items_dict.keys())
	
	
	def setTransitionSpeed(self,alpha_per_tick):
		self.alpha_per_tick = alpha_per_tick
	
	def fadeOut(self):
			
		if self.is_fading_out and not self.is_fading_in:
			if self.alpha > 0:
				self.alpha -= self.alpha_per_tick
			else:
				self.alpha = 0
				self.is_fading_out = False
				self.current_display_key += 1
				
				if self.current_display_key > self.max_slides -1:
					self.alive = False
				
				self.show_acctime = 0
				self.is_fading_in = True
				
	def fadeIn(self):
	
		if self.is_fading_in and not self.is_fading_out:
			if self.alpha < 255:
				self.alpha += self.alpha_per_tick
				
			else:
				self.alpha = 255
				self.is_fading_in = False
				
	def update(self,timepassed):
		
		if self.alive:
		
			self.cur_item = self.slide_items_dict[self.current_display_key]
		
			self.rect.topleft = (self.x,self.y)
			self.cur_item[1].update(timepassed)
		
			if self.cur_item[0] == "loop":
				if not self.cur_item[1].alive:
					# start fade out
					if not self.is_fading_in:
						self.is_fading_out = True
		
			else:
				self.show_acctime += timepassed
				self.show_updatetime = self.cur_item[0] 
			
				if self.show_acctime > self.show_updatetime:
					# start fade out
					if not self.is_fading_in:
						self.is_fading_out = True
				
			#print self.alive
			self.fadeOut()
			self.fadeIn()
		
	def draw(self,Surface):
		
		if self.main_color != None:
			self.surface.fill(self.main_color)		
		else:
			self.surface.fill((255,0,255))
		self.surface.set_alpha(self.alpha)
			
		
		# draw current slide onto onto widgets surface
		self.cur_item[1].draw(self.surface)
		
		Surface.blit(self.surface,self.rect)