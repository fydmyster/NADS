import pygame,math,sys,os.path
from pygame.locals import*
from sgf.const import*
import sgf.utils.g_utils as utils

fullpath = os.path.abspath(__file__)
d = os.path.split(fullpath)[0]
e = os.path.split(d)[0]
f = os.path.split(e)[0]
g = os.path.split(f)[0]
g = os.path.join(g,"fonts")
default_font = os.path.join(g,"PressStart2P.ttf")
default_font_ico = os.path.join(g,"icon-works-webfont.ttf")

# todo : Add non activity to some menu options
# add outline to Frame
# make menu objects lose focus after command is executed
# make SelectionPane only objects active on a frame when pane is showing
# make list box delete items and reorder

class MenuHorizontal(object):
	"""A typical drop down menu widget"""
	def  __init__(self,text,parent=None,**kwargs):
		# Menus can only go 3 levels deep because debugging this shit is too intensive cause the entire code
		# was guesswork on my part
		# It also becomes a pain for the user to manage after 3 depths because of how unwieldy the interface is
		
		# parent is a tuple : (parent_menu,index_of_option)
		
		self.text_images =  []
		self.hit_images = []
		self.command_list = []
		self.in_focus = False
		self.parent = parent
		self.text = text
		
		self.child_indices = []
		self.event_list = []
		
		self.valid_kwargs = {
			"x" : 0,
			"y" : 0,
			"text_size" : 10,
			"font" : default_font,
			"text_color": (0,0,0),
			"text_fill" : (200,200,100),
			"button_color" : (20,200,0),
			"fill_color" : (0,200,200),
			"x_margin" : 5,
			"y_margin" : 3,
			"name" : None,
			"ancestor" : None
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
		
		self.font = pygame.font.Font(self.font,self.text_size)
		
		# STATES
		self.mouse_over = False
		
		self.text_image = self.font.render(self.text,False,self.text_color)
		self.text_rect = self.text_image.get_rect()
		#self.text_rect.topleft = (self.x,self.y)
		w,h = self.text_image.get_size()
		
		self.button_rect = pygame.Rect(self.x,self.y,w+6,h+2)
		self.text_rect.center = self.button_rect.center
		
		self.panel_image = None
		self.panel_image_rect = None
		self.draw_panel = False
		self.child_menus = []
		
		
	def init(self):
		"""Call this after adding all buttons"""
		
		# determine max size of panel
		max_size = 30
		
		for image,image_size,t in self.text_images:
			if image_size[0] + (self.x_margin*2) > max_size:
				max_size = image_size[0] + (self.x_margin*2)
		
		panel_width = max_size
		panel_height = ((self.y_margin*2) + image_size[1]) * len(self.text_images)
		
		rect_height = panel_height/len(self.text_images)
		
		rect_y = 0
		
		# create panel image
		self.panel_image = pygame.Surface((panel_width,panel_height))
		self.panel_image.fill((self.button_color))
		self.panel_image_rect = self.panel_image.get_rect()
		
		if self.parent != None:
			parent_obj,index = self.parent
			
			parent_rect = parent_obj.hit_images[index][1]
			self.panel_image_rect.topleft = (parent_rect.right,parent_rect.top)
		else:	
			self.panel_image_rect.topleft = (self.button_rect.right,self.button_rect.top)
		
		# create rects images
		for i in range(len(self.text_images)):
			surf = pygame.Surface((panel_width,rect_height))
			surf.fill(self.button_color)
			surf_rect = surf.get_rect()
			surf_rect.y = rect_y
			
			surf_rect.x += self.panel_image_rect.left
			surf_rect.y += self.panel_image_rect.top
			
			self.hit_images.append((surf,surf_rect))
			
			rect_y += rect_height
		
		for i in range(len(self.text_images)):
			image_rect = self.text_images[i][2]
			t_rect = self.hit_images[i][1]
			
			image_rect.centery = t_rect.centery
			image_rect.left = t_rect.left + self.x_margin
		
	def addButton(self,text,command=None,child=False,ancestor=None):
		"""Adds an option to the menu options. If child is True then the option will be a menu object itself"""
		image = self.font.render(text,False,self.text_color)	# this is the image I need to draw an arrow onto
		image_size = image.get_size()
		image_rect = image.get_rect()
		
		self.text_images.append([image,image_size,image_rect])
		self.command_list.append(command)
		
		index = len(self.command_list)-1
		 
		if ancestor != None:
			self.temp_valid_kwargs = dict(self.valid_kwargs)
			self.temp_valid_kwargs["ancestor"] = ancestor
		else:
			self.temp_valid_kwargs = self.valid_kwargs 
			
		if child:	
			cascade_menu = MenuHorizontal(text,(self,index),**self.temp_valid_kwargs)
			self.child_menus.append(cascade_menu)
			self.child_indices.append(index)
			
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
		
		# take care of informing child_menus of events too
		for child in self.child_menus:
			child.event_list.append(event)
			for grand_child in child.child_menus:
				grand_child.event_list.append(event)
		
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		mx,my,timepassed = mouse_point			# mouse_point :(x,y,timepassed)
		
		if self.parent != None:
			parent_obj,index = self.parent
			
			active_num = 0
			# check for still in focus child menus
			active_children = False
			for child in self.child_menus:
				if child.in_focus:
					active_num +=1
					#active_children = True
					
				for grand_child in child.child_menus:
					if grand_child.in_focus:
						active_num +=1
						#active_children = True
						#break
					
					for great_child in grand_child.child_menus:
						if great_child.in_focus:
							active_num +=1
							#active_children = True
							#break
				
			if active_num > 0:
				active_children = True
			
			parent_rect = parent_obj.hit_images[index][1]
			
			if parent_rect.collidepoint(mx,my) and parent_obj.mouse_over:
				self.mouse_over=True
			else:
				if self.draw_panel or active_children:
					pass
				else:
					self.mouse_over=False
		
			if self.panel_image_rect.collidepoint(mx,my) or parent_rect.collidepoint(mx,my):
				self.draw_panel = True
			else:
				self.draw_panel = False
			
		else:
			
			active_num = 0
			# check for still in focus child menus
			active_children = False
			for child in self.child_menus:
				if child.in_focus:
					active_num +=1
					#active_children = True
					
				for grand_child in child.child_menus:
					if grand_child.in_focus:
						active_num +=1
						#active_children = True
						#break
					
					for great_child in grand_child.child_menus:
						if great_child.in_focus:
							active_num +=1
							#active_children = True
							#break
				
			if active_num > 0:
				active_children = True
			
			
			if self.button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				if self.draw_panel or active_children:
					pass
				else:
					self.mouse_over=False
		
			if self.panel_image_rect.collidepoint(mx,my) or self.button_rect.collidepoint(mx,my):
				self.draw_panel = True
			else:
				self.draw_panel = False
		
		for surf,surf_rect in self.hit_images:
			if surf_rect.collidepoint(mx,my):
				surf.fill(self.fill_color)
			else:
				surf.fill(self.button_color)
		
		# process user events
		for event in self.event_list:
			if self.in_focus:
				if event == LMOUSE_DOWN:
					index = self.testClick(mx,my)
					
					if index != None:
						# run command
						if self.ancestor != None:
							if self.ancestor.mouse_over:
								if self.command_list[index] != None:
									self.command_list[index]()
						else:
							if self.mouse_over:
								if self.command_list[index] != None:
									self.command_list[index]()
						
						if self.ancestor != None:
							self.ancestor.mouse_over = False
							self.mouse_over= False
							#self.in_focus = False
							#self.draw_panel = False
							#mx,my = 1000,1000
						
						else:	
							if index in self.child_indices:
								pass
							else:
								self.mouse_over = False
						
						if self.parent!= None and not index in self.child_indices:
							self.parent[0].mouse_over = False
							
		# clear event queue
		self.event_list = []
		
		# handle all child_menus events too 
		#for child in self.child_menus:
		#	child.handleEvents(mouse_point)
		
	def testClick(self,mx,my):
		"""Returns index of the clicked on option; Returns None if nothing was clicked on"""
		for i in range(len(self.text_images)):
			if self.hit_images[i][1].collidepoint(mx,my):
				return i
	
	def draw(self,Surface):
		"""Draws the widget"""
		# draw button_color background
		
		if self.parent:
			pass
			#if self.mouse_over:
			#	pygame.draw.rect(Surface,self.fill_color,self.button_rect)
			#else:
			#	pygame.draw.rect(Surface,self.button_color,self.button_rect)
			
			#Surface.blit(self.text_image,self.text_rect)
		
		else:
			if self.mouse_over:
				pygame.draw.rect(Surface,self.fill_color,self.button_rect)
			else:
				pygame.draw.rect(Surface,self.button_color,self.button_rect)
			
			Surface.blit(self.text_image,self.text_rect)
		
			
		if (self.mouse_over and len(self.text_images)>0):
			# draw panel based on number of options
			
			Surface.blit(self.panel_image,self.panel_image_rect)
			
			# draw hit_images onto panel
			for surf,surf_rect in self.hit_images:
				
				Surface.blit(surf,(surf_rect.x,surf_rect.y))
			
			for text,size,rect in self.text_images:
				Surface.blit(text,rect)
		
		# handle all child_menus draw method
		for child in self.child_menus:
			child.draw(Surface)
		
	def update(self,mouse_point):
		"""Updates the state of the widget"""
		
		self.handleEvents(mouse_point)
		
		if self.mouse_over:
			self.text_image = self.font.render(self.text,False,self.text_fill)
		else:	
			self.text_image = self.font.render(self.text,False,self.text_color)
		
		
		if self.draw_panel :
			self.in_focus = True
		else:
			self.in_focus = False
		
		#if self.parent != None:
		#	parent_obj = self.parent[0]
			
		#	if not parent_obj.draw_panel:
		#		self.draw_panel = False
			
		# handle all child_menus 
		for child in self.child_menus:
			child.update(mouse_point)
		
class MenuVertical(object):
	"""A typical drop down menu widget"""
	def  __init__(self,text,parent=None,**kwargs):
		# Menus can only go 3 levels deep because debugging this shit is too intensive cause the entire code
		# was guesswork on my part
		# It also becomes a pain for the user to manage after 3 depths because of how unwieldy the interface is
		
		# parent is a tuple : (parent_menu,index_of_option)
		
		self.text_images =  []
		self.hit_images = []
		self.command_list = []
		self.in_focus = False
		self.parent = parent
		self.text = text
		
		self.child_indices = []
		self.event_list = []
		
		self.valid_kwargs = {
			"x" : 0,
			"y" : 0,
			"text_size" : 10,
			"font" : default_font,
			"text_color": (0,0,0),
			"text_fill" : (200,200,100),
			"button_color" : (20,200,0),
			"fill_color" : (0,200,200),
			"x_margin" : 5,
			"y_margin" : 3,
			"name" : None,
			"ancestor" : None
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
		
		self.font = pygame.font.Font(self.font,self.text_size)
		
		# STATES
		self.mouse_over = False
		
		self.text_image = self.font.render(self.text,False,self.text_color)
		self.text_rect = self.text_image.get_rect()
		#self.text_rect.topleft = (self.x,self.y)
		w,h = self.text_image.get_size()
		
		self.button_rect = pygame.Rect(self.x,self.y,w+6,h+2)
		self.text_rect.center = self.button_rect.center
		
		self.panel_image = None
		self.panel_image_rect = None
		self.draw_panel = False
		self.child_menus = []
			
	def init(self):
		"""Call this after adding all buttons. Initialises the widget to a usable state"""
		
		# determine max size of panel
		max_size = 30
		
		for image,image_size,t in self.text_images:
			if image_size[0] + (self.x_margin*2) > max_size:
				max_size = image_size[0] + (self.x_margin*2)
		
		panel_width = max_size
		panel_height = ((self.y_margin*2) + image_size[1]) * len(self.text_images)
		
		rect_height = panel_height/len(self.text_images)
		
		rect_y = 0
		
		# create panel image
		self.panel_image = pygame.Surface((panel_width,panel_height))
		self.panel_image.fill((self.button_color))
		self.panel_image_rect = self.panel_image.get_rect()
		
		if self.parent != None:
			parent_obj,index = self.parent
			
			parent_rect = parent_obj.hit_images[index][1]
			self.panel_image_rect.topleft = (parent_rect.right,parent_rect.top)
		else:	
			self.panel_image_rect.topleft = (self.button_rect.left,self.button_rect.bottom)
		
		# create rects images
		for i in range(len(self.text_images)):
			surf = pygame.Surface((panel_width,rect_height))
			surf.fill(self.button_color)
			surf_rect = surf.get_rect()
			surf_rect.y = rect_y
			
			surf_rect.x += self.panel_image_rect.left
			surf_rect.y += self.panel_image_rect.top
			
			self.hit_images.append((surf,surf_rect))
			
			rect_y += rect_height
		
		for i in range(len(self.text_images)):
			image_rect = self.text_images[i][2]
			t_rect = self.hit_images[i][1]
			
			image_rect.centery = t_rect.centery
			image_rect.left = t_rect.left + self.x_margin
		
	def addButton(self,text,command=None,child=False,ancestor=None):
		"""Adds an option to the menu options. If child is True then the option will be a menu object itself"""
		image = self.font.render(text,False,self.text_color)
		image_size = image.get_size()
		image_rect = image.get_rect()
		
		self.text_images.append([image,image_size,image_rect])
		self.command_list.append(command)
		
		index = len(self.command_list)-1
		
		if ancestor != None:
			self.temp_valid_kwargs = dict(self.valid_kwargs)
			self.temp_valid_kwargs["ancestor"] = ancestor
		else:
			self.temp_valid_kwargs = self.valid_kwargs 
			
		if child:	
			cascade_menu = MenuHorizontal(text,(self,index),**self.temp_valid_kwargs)
			self.child_menus.append(cascade_menu)
			self.child_indices.append(index)
			
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
		
		for child in self.child_menus:
			child.event_list.append(event)
			for grand_child in child.child_menus:
				grand_child.event_list.append(event)
				
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		mx,my,timepassed = mouse_point
		
		if self.parent != None:
			parent_obj,index = self.parent
			
			active_num = 0
			# check for still in focus child menus
			active_children = False
			for child in self.child_menus:
				if child.in_focus:
					active_num +=1
					#active_children = True
					
				for grand_child in child.child_menus:
					if grand_child.in_focus:
						active_num +=1
						#active_children = True
						#break
					
					for great_child in grand_child.child_menus:
						if great_child.in_focus:
							active_num +=1
							#active_children = True
							#break
				
			if active_num > 0:
				active_children = True
			
			parent_rect = parent_obj.hit_images[index][1]
			
			if parent_rect.collidepoint(mx,my) and parent_obj.mouse_over:
				self.mouse_over=True
			else:
				if self.draw_panel or active_children:
					pass
				else:
					self.mouse_over=False
		
			if self.panel_image_rect.collidepoint(mx,my) or parent_rect.collidepoint(mx,my):
				self.draw_panel = True
			else:
				self.draw_panel = False
			
		else:
			active_num = 0
			# check for still in focus child menus
			active_children = False
			for child in self.child_menus:
				if child.in_focus:
					active_num +=1
					#active_children = True
					
				for grand_child in child.child_menus:
					if grand_child.in_focus:
						active_num +=1
						#active_children = True
						#break
					
					for great_child in grand_child.child_menus:
						if great_child.in_focus:
							active_num +=1
							#active_children = True
							#break
				
			if active_num > 0:
				active_children = True
			
			if self.button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				if self.draw_panel or active_children:
					pass
				else:
					self.mouse_over=False
		
			if self.panel_image_rect.collidepoint(mx,my) or self.button_rect.collidepoint(mx,my):
				self.draw_panel = True
			else:
				self.draw_panel = False
		
		for surf,surf_rect in self.hit_images:
			if surf_rect.collidepoint(mx,my):
				surf.fill(self.fill_color)
			else:
				surf.fill(self.button_color)
		
		# process user events
		for event in self.event_list:
			if self.in_focus:
				if event == LMOUSE_DOWN:
					index = self.testClick(mx,my)
					
					if index != None:
						# run command
						if self.ancestor != None:
							if self.ancestor.mouse_over:
								if self.command_list[index] != None:
									self.command_list[index]()
						else:
							if self.mouse_over:
								if self.command_list[index] != None:
									self.command_list[index]()
						
						if self.ancestor != None:
							self.ancestor.mouse_over = False
							self.mouse_over= False
							#self.in_focus = False
							#self.draw_panel = False
							#mx,my = 1000,1000
						
						else:	
							if index in self.child_indices:
								pass
							else:
								self.mouse_over = False
						
						if self.parent!= None and not index in self.child_indices:
							self.parent[0].mouse_over = False
						
		# clear event queue
		self.event_list = []
		
		# handle all child_menus 
		#for child in self.child_menus:
		#	child.handleEvents(mouse_point)
		
	def testClick(self,mx,my):
		"""Returns index of the clicked on option; Returns None if nothing was clicked on"""
		for i in range(len(self.text_images)):
			if self.hit_images[i][1].collidepoint(mx,my):
				return i
	
	def draw(self,Surface):
		"""Draws the widget"""
		# draw button_color background
		
		if self.parent:
			pass
			#if self.mouse_over:
			#	pygame.draw.rect(Surface,self.fill_color,self.button_rect)
			#else:
			#	pygame.draw.rect(Surface,self.button_color,self.button_rect)
			
			#Surface.blit(self.text_image,self.text_rect)
		
		else:
			if self.mouse_over:
				pygame.draw.rect(Surface,self.fill_color,self.button_rect)
			else:
				pygame.draw.rect(Surface,self.button_color,self.button_rect)
			
			Surface.blit(self.text_image,self.text_rect)
		
			
		if (self.mouse_over and len(self.text_images)>0):
			# draw panel based on number of options
			
			Surface.blit(self.panel_image,self.panel_image_rect)
			
			# draw hit_images onto panel
			for surf,surf_rect in self.hit_images:
				
				Surface.blit(surf,(surf_rect.x,surf_rect.y))
			
			for text,size,rect in self.text_images:
				Surface.blit(text,rect)
		
		# handle all child_menus 
		for child in self.child_menus:
			child.draw(Surface)
		
	def update(self,mouse_point):
		
		self.handleEvents(mouse_point)
		
		if self.mouse_over:
			self.text_image = self.font.render(self.text,False,self.text_fill)
		else:	
			self.text_image = self.font.render(self.text,False,self.text_color)
		
		
		if self.draw_panel :
			self.in_focus = True
		else:
			self.in_focus = False
		
		#if self.parent != None:
		#	parent_obj = self.parent[0]
			
		#	if not parent_obj.draw_panel:
		#		self.draw_panel = False
			
		# handle all child_menus 
		for child in self.child_menus:
			child.update(mouse_point)

class Slider(object):
	def __init__(self,parent,**kwargs):
		
		self.parent = parent
		self.event_list = []
		
		self.valid_kwargs = {
			"x":0,
			"y":0,
			"w":50,
			"h":20,
			"max_value" : 100,
			"variable" : utils.IntObject(10),
			"button_color":(50,80,200),
			"fill_color" : (200,90,100),
			"text_size" : 12,
			"text_color" : (0,0,0),
			"outline_color" : (50,250,100),
			"draw_outline" : False,
			"font" : default_font,
			"x_margin":2,
			"y_margin":2,
			"name" : None
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
		
		self.font = pygame.font.Font(self.font,self.text_size)
		
		# STATES
		self.mouse_over = False
		self.mouse_down = False
		self.active = True
		self.cur_value = self.variable.getVal()
		
		# CURRENT COLORS
		self.b_color = self.button_color
		self.t_color = self.text_color
		self.o_color = self.outline_color
		
		# extra colors 
		self.light_outline = utils.saturateColor(self.b_color,0.2)
		self.dark_outline = utils.desaturateColor(self.b_color,0.2)
		
		self.text_image = self.font.render(str(self.cur_value),False,self.t_color)
		self.text_rect = self.text_image.get_rect()
		
		self.button_image = pygame.Surface((self.w,self.h))
		self.button_rect = self.button_image.get_rect()
		self.button_image.fill(self.b_color)
		
		self.fill_rect_max_w = self.button_rect.w - (self.x_margin*2)
		self.fill_rect_max_h = self.button_rect.h - (self.y_margin*2)
		
		self.fill_rect = pygame.Rect(0,0,self.fill_rect_max_w,self.fill_rect_max_h)
		self.fill_rect.w = self.fill_rect_max_w * (self.cur_value/float(self.max_value))
		
		# draw extra details
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(self.button_rect.w,0),2)
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(0,self.button_rect.h),2)
		pygame.draw.line(self.button_image,self.dark_outline,(0,self.button_rect.h-2),(self.button_rect.w,self.button_rect.h-2),2)
		pygame.draw.line(self.button_image,self.dark_outline,(self.button_rect.w-2,0),(self.button_rect.w-2,self.button_rect.h),2)
		
		self.text_rect.center = self.button_rect.center
		
		if self.draw_outline:
			pygame.draw.rect(self.button_image,self.o_color,(0,0,self.button_rect.w,self.button_rect.h),1)
		
		self.button_rect.topleft = (self.x,self.y)
		self.fill_rect.centery = self.button_rect.centery
		self.fill_rect.x = self.button_rect.x + self.x_margin
		
		self.true_button_rect = pygame.Rect(0,0,self.button_rect.w,self.button_rect.h)
		self.true_fill_rect = pygame.Rect(0,0,self.button_rect.w,self.button_rect.h)
		
		if self.parent != None:
			# add this object to parent widget under a hash name
			if self.name == None:
				# add this object to parent widget under a hash name
				self.parent.widgets["widget"+str(self.parent.name_counter)] = self
				self.parent.name_counter += 1
			else:
				# add this object to parent widget under a hash name
				self.parent.widgets[self.name] = self
			
	def testClick(self,mx,my):
		"""Returns True if the button was clicked on; Returns False otherwise"""
		
		if self.parent != None:
			if self.true_button_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
		else:
			if self.button_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
		
	def getVal(self):
		"""Retrieves value in the entry box"""
		return self.variable.getVal()
			
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		mx,my,timepassed = mouse_point
		
		if self.parent != None:
			self.true_button_rect.topleft = (self.button_rect.x + self.parent.background_rect.x,self.button_rect.y + self.parent.background_rect.y)
			self.true_fill_rect.centery = self.true_button_rect.centery
			self.true_fill_rect.x = self.true_button_rect.x + self.x_margin
		
		if self.parent != None:
			#self.event_list = self.parent.event_list[:]		# use the parent Frame's event_list
			if not self.parent.minimized and self.true_button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
		
		else:
			if self.button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
		
		# process user events
		for event in self.event_list:
			if self.active:
				if event == LMOUSE_DOWN:
					if self.testClick(mx,my):
						# depress the button
						self.mouse_down = True
							
				if event == LMOUSE_UP:
					self.mouse_down = False
						
		# clear event queue
		self.event_list = []
		
	def update(self,mouse_point):
		"""Updates the buttons state based on user events"""
		
		self.handleEvents(mouse_point)
		mx,my,timepassed = mouse_point
		
		self.variable.setVal(self.cur_value)
		
		if self.mouse_down:
			if self.parent != None:
				# calculate fill_rect width
				dist = mx - self.true_fill_rect.x
			else:
				# calculate fill_rect width
				dist = mx - self.fill_rect.x
				
			ratio = dist/float(self.fill_rect_max_w)
			
			if dist < 0:
				self.cur_value = 0
				self.fill_rect.w = 1
			elif ratio > 1:
				self.cur_value = self.max_value
				self.fill_rect.w = self.fill_rect_max_w
			else:
				self.cur_value = int(self.max_value * ratio)
				self.fill_rect.w = self.fill_rect_max_w * ratio
				
		# update positions
		
		self.text_image = self.font.render(str(self.cur_value),False,self.t_color)
		self.text_rect = self.text_image.get_rect()
		
		self.button_rect.topleft = (self.x,self.y)
		self.text_rect.center = self.button_rect.center
		self.fill_rect.centery = self.button_rect.centery
		self.fill_rect.x = self.button_rect.x + self.x_margin
		
	def draw(self,Surface):
		"""Draws the button to the screen or parent widget"""
		Surface.blit(self.button_image,self.button_rect)
		pygame.draw.rect(Surface,self.fill_color,self.fill_rect)
		Surface.blit(self.text_image,self.text_rect)

class Listbox(object):
	def __init__(self,parent,**kwargs):
		
		self.parent = parent
		self.event_list = []
		self.options_list = []
		self.text_images = []
		self.collision_rects = []
		self.true_collision_rects = []
		self.draw_rects = []
		self.cur_index = None
		
		self.drag_point = None
		self.drag_topleft = None
		self.drag = False
		self.scroll_ratio = 0
		self.y_overlap = 0
		self.add_y = 0
		
		self.pane_height = 0
		self.valid_kwargs = {
			"x":0,
			"y":0,
			"w":120,
			"h":100,
			"button_color":(50,80,200),
			"fill_color" : (200,90,100),
			"text_size" : 12,
			"text_color" : (0,0,0),
			"text_fill" : (240,240,240),
			"outline_color" : (50,250,100),
			"draw_outline" : True,
			"font" : default_font,
			"x_margin" : 4,
			"y_margin" : 2,
			"x_margin_pane" : 3,
			"scrollbar_width" : 10,
			"min_scrollbar_height" : 10,
			"scrollbar_color" : (20,200,20),
			"scrollbar_bg_color" : (230,230,200),
			"name" : None
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
		
		self.font = pygame.font.Font(self.font,self.text_size)
		self.scrollbar_height = self.h
		self.true_scroll_rect = None
		self.scroll_y = self.y
		
		# STATES
		self.mouse_down_bar = False
		self.mouse_over_bar = False
		self.mouse_over = False
		self.mouse_down = False
		self.active = True
		self.d = 0
		
		# CURRENT COLORS
		self.b_color = self.button_color
		self.t_color = self.text_color
		self.o_color = self.outline_color
		
		# extra colors 
		self.light_outline = utils.saturateColor(self.b_color,0.2)
		self.dark_outline = utils.desaturateColor(self.b_color,0.2)
		
		self.button_height = self.font.get_height() + (self.y_margin*2)
		self.button_width = self.w
		
		self.background = pygame.Surface((self.w,self.h))
		self.background.fill(self.button_color)
		self.background_rect = self.background.get_rect()
		
		if self.draw_outline:
			pygame.draw.rect(self.background,self.outline_color,(0,0,self.background_rect.w,self.background_rect.h),1)
		
		self.background_rect.topleft = (self.x,self.y)
		self.true_background_rect = pygame.Rect(0,0,self.background_rect.w,self.background_rect.h)
		
		# setup scrollbar
		self.scrollbar_image = pygame.Surface((self.scrollbar_width,self.scrollbar_height))
		self.scrollbar_image.fill((self.scrollbar_color))
		self.scrollbar_rect = self.scrollbar_image.get_rect()
		self.scrollbar_rect.left = self.background_rect.right
		self.scrollbar_rect.y = self.scroll_y
		
		self.true_scroll_rect = pygame.Rect(0,0,self.scrollbar_rect.w,self.scrollbar_rect.h)
		
		if self.parent != None:
			# add this object to parent widget under a hash name
			if self.name == None:
				# add this object to parent widget under a hash name
				self.parent.widgets["widget"+str(self.parent.name_counter)] = self
				self.parent.name_counter += 1
			else:
				# add this object to parent widget under a hash name
				self.parent.widgets[self.name] = self
	
	def insert(self,button_text,index=None):
		"""Adds an option to the options_list"""
		
		if index is None:
			self.options_list.append(button_text)
		
		else:
			if index > len(self.options_list):
				self.options_list.append(button_text)
			else:
				self.options_list.insert(index,button_text)
	
	def moveUp(self,index):
		if index > 0 and index < len(self.options_list):
			item = self.options_list.pop(index)
			# place it back
			self.options_list.insert(index-1,item)
		else: print "Cant push up any further or given index invalid"
	
	def moveDown(self,index):
		if index >= 0 and index < len(self.options_list):
			item = self.options_list.pop(index)
			# place it back
			self.options_list.insert(index+1,item)
		else: print "given index invalid"
	
	def remove(self,index):
		"""Remove an element at given index from the options_list"""
		if index < len(self.options_list):
			del self.options_list[index]
			
			if self.cur_index >0:
				self.cur_index -=1
			
			# This is a hack will fix it when I get a chance
			# Its meant to fix any alignment errors on scrollbar
			if (len(self.options_list)+1) > 0:
				min_y = self.d / float(len(self.options_list)+1)
				self.scroll_y -= (min_y+(min_y/2.0))
		else:
			print "Invalid index given"
		
		
		
	def testClick(self,mx,my):
		"""Returns True if the button was clicked on; Returns False otherwise"""
		
		if self.parent != None:
			if self.true_background_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
		else:
			if self.background_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
	
	def getSelected(self):
		"""Returns the index of the selected options"""
		if len(self.options_list) > 0:
			return self.cur_index
		else:
			return None
		
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		mx,my,timepassed = mouse_point
		
		if self.parent != None:
			self.true_background_rect.topleft = (self.background_rect.x + self.parent.background_rect.x,self.background_rect.y + self.parent.background_rect.y)
			self.true_scroll_rect.topleft = (self.scrollbar_rect.x + self.parent.background_rect.x, self.scrollbar_rect.y + self.parent.background_rect.y)
			
			for i in range(len(self.collision_rects)):
				
				true_r = self.true_collision_rects[i]
				real_r = self.collision_rects[i]
				
				true_r.topleft = (real_r.x + self.parent.background_rect.x,real_r.y + self.parent.background_rect.y)
				
		if self.parent != None:
			#self.event_list = self.parent.event_list[:]		# use the parent Frame's event_list
			if not self.parent.minimized and self.true_background_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
			
			if not self.parent.minimized and self.true_scroll_rect.collidepoint(mx,my):
				self.mouse_over_bar=True
			else:
				self.mouse_over_bar=False
			
			
		else:
			if self.background_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
			
			if self.scrollbar_rect.collidepoint(mx,my):
				self.mouse_over_bar=True
			else:
				self.mouse_over_bar=False
			
		# process user events
		for event in self.event_list:
			if self.active:
				if event == LMOUSE_DOWN:
					if self.testClick(mx,my):
						# depress the button
						self.mouse_down = True
						
					if self.parent is None:
						if self.mouse_over_bar:
							self.drag = True
							self.drag_point = (mx,my)
							self.drag_topleft = self.scrollbar_rect.topleft
					else:
						if self.mouse_over_bar:
							self.drag = True
							self.drag_point = (mx,my)
							self.drag_topleft = self.scrollbar_rect.topleft
							
				if event == LMOUSE_UP:
					self.drag = False
					if self.testClick(mx,my):
						self.mouse_down = False
						
						for i in range(len(self.collision_rects)):
							if self.parent is None:
								if self.collision_rects[i].collidepoint(mx,my):
									self.cur_index = i
									break
									
							else:
								if self.true_collision_rects[i].collidepoint(mx,my):
									self.cur_index = i
									break
								
		# clear event queue
		self.event_list = []
		
	def update(self,mouse_point):
		"""Updates the buttons state based on user events"""
		
		# update sizes
		if len(self.draw_rects) > 0:
			#self.pane_height = self.draw_rects[-1].bottom
			self.pane_height = len(self.draw_rects) * self.button_height 
			
		# calculate overlap 
		if self.pane_height > self.background_rect.h:
			self.y_overlap = self.pane_height - self.background_rect.h
		
		
		self.add_y = self.y_overlap * self.scroll_ratio
		
		#for rect in self.collision_rects:
		#	rect.y -= 100
		# update collision_rects and text_images
		y = 0
		del self.collision_rects[:]
		del self.true_collision_rects[:]
		del self.draw_rects[:]
		del self.text_images[:]
		for option in self.options_list:
			collision_rect = pygame.Rect(0,y,self.w,self.button_height)
			collision_rect2 = pygame.Rect(0,y,self.w,self.button_height)
			collision_rect3 = pygame.Rect(0,y,self.w,self.button_height)
			
			collision_rect2.x += self.x
			collision_rect2.y += (self.y-self.add_y)
			
			collision_rect.x += self.x
			collision_rect.y += (self.y-self.add_y)
			
			# make draw rect a little shorter in width and height
			collision_rect3.x +=1
			collision_rect3.y +=1
			collision_rect3.w -= 2
			collision_rect3.h -= 2
			
			collision_rect3.y += (0 - self.add_y)
			
			# create text_image
			text_image = self.font.render(option,False,self.text_color)
			text_rect = text_image.get_rect()
			text_rect.centery = collision_rect3.centery
			text_rect.x = self.x_margin_pane
			
			self.collision_rects.append(collision_rect)
			self.true_collision_rects.append(collision_rect2)
			self.draw_rects.append(collision_rect3)
			self.text_images.append((text_image,text_rect))
			y += collision_rect.h
		
		
		
		# update scrollbar
		if self.pane_height > 0:
			self.scrollbar_height = (self.h / float(self.pane_height)) * self.h
		else:
			self.scrollbar_height = self.h
		
		if self.scrollbar_height > self.h:
			self.scrollbar_height = self.h
		elif self.scrollbar_height < self.min_scrollbar_height:
			self.scrollbar_height = self.min_scrollbar_height

		self.scrollbar_image = pygame.Surface((self.scrollbar_width,self.scrollbar_height))
		self.scrollbar_image.fill((self.scrollbar_color))
		self.scrollbar_rect = self.scrollbar_image.get_rect()
		self.scrollbar_rect.left = self.background_rect.right
		self.scrollbar_rect.y = self.scroll_y
		
		self.true_scroll_rect = pygame.Rect(0,0,self.scrollbar_rect.w,self.scrollbar_rect.h)
			
		self.handleEvents(mouse_point)
		
		if self.mouse_over:
			self.t_color = self.text_fill
			self.b_color = self.fill_color
	
		else:
			self.t_color = self.text_color
			self.b_color = self.button_color
			
		self.background_rect.topleft = (self.x,self.y)
		
		if self.drag:
			# calculate mouse position on titlebar
			dmx,dmy = self.drag_point
			true_mx,true_my,timepassed = mouse_point
			#pos_on_bar = (mx-self.x,my-self.y)
			diff_x,diff_y = (dmx-self.drag_topleft[0],dmy-self.drag_topleft[1])
			
			newx = true_mx - diff_x
			newy = true_my - diff_y
			
			
			if newy < self.y:
				newy = self.y
			elif newy >= self.h - self.scrollbar_height+self.y:
				newy = self.h - self.scrollbar_height+self.y
			
			self.scroll_y = newy
			
		# calculate scroll_ratio
		delta_y = self.background_rect.h - self.scrollbar_height
		
		dist = self.scrollbar_rect.top - self.background_rect.top
		self.d = dist
		if delta_y == 0:
			self.scroll_ratio = 0
		else:
			self.scroll_ratio = dist / delta_y
			
		#print self.y_overlap
		#for r in self.true_collision_rects:
		#	print r.topleft
		
			
	def draw(self,Surface):
		"""Draws the button to the screen or parent widget"""
		
		self.background.fill(self.button_color)
		
		for i in range(len(self.collision_rects)):
			rect = self.draw_rects[i]
			
			if i == self.cur_index:
				pygame.draw.rect(self.background,self.fill_color,rect)
			else:
				pygame.draw.rect(self.background,self.button_color,rect)
				
		for image,rect in self.text_images:
			self.background.blit(image,rect)
		
		
		Surface.blit(self.background,self.background_rect)
		
		pygame.draw.rect(Surface,self.scrollbar_bg_color,(self.background_rect.right,self.background_rect.top,self.scrollbar_width,self.background_rect.h))
		
		Surface.blit(self.scrollbar_image,self.scrollbar_rect)
		
class SelectionPane(object):
	"""Button that shows a pane of options to choose from when clicked on. Can drop the pane up or down"""
	def __init__(self,options_list,parent,**kwargs):
		
		self.options_list = options_list
		self.collision_rects = []
		self.draw_rects = []
		self.true_collision_rects = []
		self.text_images = []
		self.parent = parent
		self.event_list = []
		
		self.valid_kwargs = {
			"x":30,
			"y":100,
			"w":60,				
			"h":None,						# if this is None, the height is decided by the font height + margins given
			"variable": utils.IntObject(0),
			"pane_width" : 73,
			"pane_height" : None, 			# if this is None, pane_height equals to the button_heights
			"index" : 0,
			"drop_down" : True,				# if False panel drops up
			"img_rect_color" : (10,0,30),
			"img_rect_w" : 12,
			"button_color":(50,80,200),
			"pointer_color" : (240,240,240),
			"fill_color" : (200,90,100),
			"click_button_fill" : (255,255,255),
			"click_text_fill" : (0,50,0),
			"text_size" : 12,
			"text_color" : (0,0,0),
			"text_fill" : (240,240,240),
			"outline_color" : (50,250,100),
			"outline_color_fill" : (50,50,100),
			"draw_outline" : False,
			"font" : default_font,
			"x_margin" : 4,
			"y_margin" : 2,
			"x_margin_pane" : 3,
			"name" : None
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
		
		self.font = pygame.font.Font(self.font,self.text_size)
		
		# STATES
		self.mouse_over = False
		self.mouse_down = False
		
		self.mouse_over_pane = False
		self.mouse_down_pane = False
		self.mouse_over_button = False
		self.active = True
		self.cur_index = self.variable.getVal()
		self.mouse_over_index = self.cur_index
		self.pane_open = False
		
		# CURRENT COLORS
		self.b_color = self.button_color
		self.t_color = self.text_color
		self.o_color = self.outline_color
		
		self.font_height = self.font.get_height()
		self.pane_height = self.font_height + (self.y_margin*2)
		
		# init collision_rects
		start_y = 0
		for string in self.options_list:
			collision_rect = pygame.Rect(0,start_y,self.pane_width,self.pane_height)
			collision_rect2 = pygame.Rect(0,start_y,self.pane_width,self.pane_height)
			collision_rect3 = pygame.Rect(0,start_y,self.pane_width,self.pane_height)
			self.collision_rects.append(collision_rect)
			self.draw_rects.append(collision_rect3)
			self.true_collision_rects.append(collision_rect2)
			start_y += self.pane_height
		
		
		# init text images
		for i in range(len(self.options_list)):
			string = self.options_list[i]
			text_image = self.font.render(string,False,self.t_color)
			text_rect = text_image.get_rect()
			text_rect.centery = self.collision_rects[i].centery
			text_rect.x = self.x_margin_pane
			
			self.text_images.append([text_image,text_rect])
		
		
		# create drop pane
		self.drop_down_height = self.collision_rects[-1].bottom
		self.drop_down_pane_image = pygame.Surface((self.pane_width,self.drop_down_height))
		self.drop_down_pane_image.fill(self.button_color)
		self.drop_down_rect = self.drop_down_pane_image.get_rect()
			
		# extra colors 
		self.light_outline = utils.saturateColor(self.b_color,0.2)
		self.dark_outline = utils.desaturateColor(self.b_color,0.2)
		
		self.text_image = self.text_images[self.cur_index][0]
		self.text_rect = self.text_image.get_rect()
		
		self.button_height = self.font.get_height() + (self.y_margin*2)
		self.button_width = self.w + (self.x_margin*2) + 10 
		
		
		self.button_image = pygame.Surface((self.button_width,self.button_height))
		self.button_rect = self.button_image.get_rect()
		self.button_image.fill(self.b_color)
		
		self.img_rect_h = self.button_height
		self.img = pygame.Surface((self.img_rect_w,self.img_rect_h))
		self.img.fill(self.img_rect_color)
		self.img_rect = self.img.get_rect()
		self.img_rect.right = self.button_rect.w 
		
		# draw pointer
		pointer_height = self.img_rect.h/3
		centerx = self.img_rect.w/2
		centery = self.img_rect.h/2
		
		if not self.drop_down:
			pygame.draw.line(self.img,self.pointer_color,(2,pointer_height*2),(centerx-1,centery-1),2)
			pygame.draw.line(self.img,self.pointer_color,(centerx,centery),(self.img_rect.w-3,pointer_height*2),2)
		
		else:	
			pygame.draw.line(self.img,self.pointer_color,(2,pointer_height),(centerx-1,centery+1),2)
			pygame.draw.line(self.img,self.pointer_color,(centerx,centery),(self.img_rect.w-3,pointer_height),2)
		
			
		# draw extra details
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(self.button_rect.w,0),2)
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(0,self.button_rect.h),2)
		pygame.draw.line(self.button_image,self.dark_outline,(0,self.button_rect.h-2),(self.button_rect.w,self.button_rect.h-2),2)
		pygame.draw.line(self.button_image,self.dark_outline,(self.button_rect.w-2,0),(self.button_rect.w-2,self.button_rect.h),2)
		
		self.button_image.blit(self.img,self.img_rect)
		
		# get delimit the area the widget's text is drawn in 
		self.delimit_rect = pygame.Rect(0,0,self.img_rect.left,self.font_height)
		
		self.text_rect.center = (self.button_rect.w/2,self.button_rect.h/2)
		
		self.button_image.blit(self.text_image,self.text_rect)
		
		if self.draw_outline:
			pygame.draw.rect(self.button_image,self.o_color,(0,0,self.button_rect.w,self.button_rect.h),1)
		
		self.button_rect.topleft = (self.x,self.y)
		self.true_button_rect = pygame.Rect(0,0,self.button_rect.w,self.button_rect.h)
		self.true_drop_down_rect = pygame.Rect(0,0,self.drop_down_rect.w,self.drop_down_rect.h)
		
		if not self.drop_down:
			self.drop_down_rect.bottomleft = (self.x,self.button_rect.top)
		else:
			self.drop_down_rect.topleft = (self.x,self.button_rect.bottom)
		
		
		# adjust collision rects
		bh = self.button_rect.h
		ph = self.drop_down_rect.h
		
		for rect in self.collision_rects:
			if self.drop_down:
				rect.x += self.button_rect.x
				rect.y += (bh+self.button_rect.y)
				#pass
			else:
				rect.x += self.button_rect.x
				rect.y += (self.button_rect.y-ph)
				
		if self.parent != None:
			# add this object to parent widget under a hash name
			if self.name == None:
				# add this object to parent widget under a hash name
				self.parent.widgets["widget"+str(self.parent.name_counter)] = self
				self.parent.name_counter += 1
			else:
				# add this object to parent widget under a hash name
				self.parent.widgets[self.name] = self
		
	def testClick(self,mx,my):
		"""Returns True if the button was clicked on; Returns False otherwise"""
		
		if self.parent != None:
			if self.true_button_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
		else:
			if self.button_rect.collidepoint(mx,my):
				return True
			else:
				return False
		
	def getVal(self):
		"""Retrieves value in the entry box"""
		return self.variable.getVal()
			
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
		
		
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		mx,my,timepassed = mouse_point
		
		if self.parent != None:
			self.true_button_rect.topleft = (self.button_rect.x + self.parent.background_rect.x,self.button_rect.y + self.parent.background_rect.y)
			
			for i in range(len(self.true_collision_rects)):
					self.true_collision_rects[i].topleft = (self.collision_rects[i].x + self.parent.background_rect.x,self.collision_rects[i].y + self.parent.background_rect.y)
				
			self.true_drop_down_rect.topleft = (self.drop_down_rect.x + self.parent.background_rect.x,self.drop_down_rect.y + self.parent.background_rect.y)
			
		if self.parent != None:
			#self.event_list = self.parent.event_list[:]		# use the parent Frame's event_list
			if not self.parent.minimized and self.true_button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
			
			if not self.parent.minimized and self.true_drop_down_rect.collidepoint(mx,my) and self.pane_open:
				self.mouse_over_pane=True
			else:
				self.mouse_over_pane=False
			
			# test collision_rects
			counter = 0
			if self.mouse_over_pane:
				for i in range(len(self.true_collision_rects)):
					if self.true_collision_rects[i].collidepoint(mx,my):
						self.mouse_over_button = True
						self.mouse_over_index = i
						counter+=1
						break
			if counter<1:
				self.mouse_over_button = False
		else:
			if self.button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
			
			if self.drop_down_rect.collidepoint(mx,my) and self.pane_open:
				self.mouse_over_pane=True
			else:
				self.mouse_over_pane=False
			
			counter = 0
			if self.mouse_over_pane:
				for i in range(len(self.collision_rects)):
					if self.collision_rects[i].collidepoint(mx,my):
						self.mouse_over_button = True
						self.mouse_over_index = i
						counter+=1
						break
			if counter<1:
				self.mouse_over_button = False
				
		# process user events
		for event in self.event_list:
			if self.active:
				if event == LMOUSE_DOWN:
					if self.testClick(mx,my):
						# depress the button
						self.mouse_down = True
						if not self.pane_open:
							self.pane_open = True
						
						else:
							self.pane_open = False
						
					else:
						if not self.mouse_over_button:
							self.pane_open = False
						
				if event == LMOUSE_UP:
					if self.testClick(mx,my):
						self.mouse_down = False
						
					if self.mouse_over_button:
							self.cur_index = self.mouse_over_index
							self.pane_open = False
							
		# clear event queue
		self.event_list = []
		
	def update(self,mouse_point):
		"""Updates the buttons state based on user events"""
		
		self.handleEvents(mouse_point)
		
		# update variable
		self.variable.setVal(self.cur_index)
		
		if self.mouse_over and not self.mouse_down:
			self.t_color = self.text_fill
			self.b_color = self.fill_color
			self.o_color = self.outline_color_fill
		elif self.mouse_over and self.mouse_down:	
			self.t_color = self.click_text_fill
			self.b_color = self.click_button_fill
		else:
			self.t_color = self.text_color
			self.b_color = self.button_color
			self.o_color = self.outline_color
		
		self.light_outline = utils.saturateColor(self.b_color,0.2)
		self.dark_outline = utils.desaturateColor(self.b_color,0.2)
		
		self.text_image = self.text_images[self.cur_index][0]
		self.text_rect = self.text_image.get_rect()
		
		#self.button_height = self.font.get_height() + (self.y_margin*2)
		#self.button_width = self.text_image.get_size()[0] + (self.x_margin*2) + 10 
		
		self.button_image = pygame.Surface((self.button_width,self.button_height))
		self.button_rect = self.button_image.get_rect()
		self.button_image.fill(self.b_color)
		
		# draw extra details
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(self.button_rect.w,0),2)
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(0,self.button_rect.h),2)
		pygame.draw.line(self.button_image,self.dark_outline,(0,self.button_rect.h-2),(self.button_rect.w,self.button_rect.h-2),2)
		pygame.draw.line(self.button_image,self.dark_outline,(self.button_rect.w-2,0),(self.button_rect.w-2,self.button_rect.h),2)
		
		self.button_image.blit(self.img,self.img_rect)
		
		# draw drop pointer direction
		#pygame.draw.polygon(self.button_image,(0,0,0),[(self.button_rect.w-2,(self.button_rect.h/3)*2),(self.button_rect.w-7,(self.button_rect.h/3)*2),(self.button_rect.w-4,(self.button_rect.h/3))])
		# draw drop pointer direction
		#pygame.draw.polygon(self.button_image,(0,0,0),[(self.button_rect.w-2,(self.button_rect.h/3)*2),(self.button_rect.w-8,(self.button_rect.h/2.5)*2),(self.button_rect.w-4,(self.button_rect.h/2.5))])
		
		
		self.text_rect.centery = self.button_rect.h/2
		self.text_rect.x = self.x_margin
		
		self.button_image.blit(self.text_image,self.text_rect,self.delimit_rect)
		
		if self.draw_outline:
			pygame.draw.rect(self.button_image,self.o_color,(0,0,self.button_rect.w,self.button_rect.h),1)
		
		self.button_rect.topleft = (self.x,self.y)
		#print self.cur_index
		#print self.collision_rects[0].topleft
		
		
	def draw(self,Surface):
		"""Draws the button to the screen or parent widget"""
		Surface.blit(self.button_image,self.button_rect)
		
		if self.pane_open:
			self.drop_down_pane_image.fill(self.button_color)
			# draw collision_rects
			for i in range(len(self.collision_rects)):
				
				if self.mouse_over_index == i:
					# draw a filled rect
					pygame.draw.rect(self.drop_down_pane_image,self.fill_color,self.draw_rects[i])
				else:
					pygame.draw.rect(self.drop_down_pane_image,self.button_color,self.draw_rects[i])
					
			# draw text
			for i in range(len(self.text_images)):
				self.drop_down_pane_image.blit(self.text_images[i][0],self.text_images[i][1])
					
			Surface.blit(self.drop_down_pane_image,self.drop_down_rect)
			
class CheckButton(object):
	def __init__(self,parent,**kwargs):
		
		self.parent = parent
		self.event_list = []
		
		self.valid_kwargs = {
			"x":0,
			"y":0,
			"w":12,
			"h":12,
			"check_width":6,
			"check_height":6,
			"variable" : utils.IntObject(0),
			"button_color":(150,150,150),
			"fill_color" : (20,20,10),
			"outline_color" : (250,250,250),
			"outline_color_fill" : (50,50,100),
			"draw_outline" : True,
			"name" : None
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
		
		
		self.checked = self.variable.getVal()
		
		# STATES
		self.mouse_over = False
		self.mouse_down = False
		self.active = True
		
		# extra colors 
		self.light_outline = utils.saturateColor(self.button_color,0.2)
		self.dark_outline = utils.desaturateColor(self.button_color,0.2)
		
		self.button_image = pygame.Surface((self.w,self.h))
		self.button_rect = self.button_image.get_rect()
		self.button_image.fill(self.button_color)
		
		self.check_rect = pygame.Rect(0,0,self.check_width,self.check_height)
		self.check_rect.center = self.button_rect.center
		
		# draw extra details
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(self.button_rect.w,0),2)
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(0,self.button_rect.h),2)
		pygame.draw.line(self.button_image,self.dark_outline,(0,self.button_rect.h-2),(self.button_rect.w,self.button_rect.h-2),2)
		pygame.draw.line(self.button_image,self.dark_outline,(self.button_rect.w-2,0),(self.button_rect.w-2,self.button_rect.h),2)
		
		
		if self.draw_outline:
			pygame.draw.rect(self.button_image,self.outline_color,(0,0,self.button_rect.w,self.button_rect.h),1)
		
		self.button_rect.topleft = (self.x,self.y)
		self.true_button_rect = pygame.Rect(0,0,self.button_rect.w,self.button_rect.h)
		
		if self.parent != None:
			# add this object to parent widget under a hash name
			if self.name == None:
				# add this object to parent widget under a hash name
				self.parent.widgets["widget"+str(self.parent.name_counter)] = self
				self.parent.name_counter += 1
			else:
				# add this object to parent widget under a hash name
				self.parent.widgets[self.name] = self
			
	def testClick(self,mx,my):
		"""Returns True if the button was clicked on; Returns False otherwise"""
		
		if self.parent != None:
			if self.true_button_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
		else:
			if self.button_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
	
	def getVal(self):
		"""Retrieves value in the entry box"""
		return self.variable.getVal()
		
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		mx,my,timepassed = mouse_point
		
		if self.parent != None:
			self.true_button_rect.topleft = (self.button_rect.x + self.parent.background_rect.x,self.button_rect.y + self.parent.background_rect.y)
		
		
		if self.parent != None:
			#self.event_list = self.parent.event_list[:]		# use the parent Frame's event_list
			if not self.parent.minimized and self.true_button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
		
		else:
			if self.button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
		
		# process user events
		for event in self.event_list:
			if self.active:
				if event == LMOUSE_DOWN:
					if self.testClick(mx,my):
						# depress the button
						self.mouse_down = True
							
				if event == LMOUSE_UP:
					if self.testClick(mx,my):
						self.mouse_down = False
						# check/deselect
						self.checked = not(self.checked)
						
		# clear event queue
		self.event_list = []
		
	def update(self,mouse_point):
		"""Updates the buttons state based on user events"""
		
		self.handleEvents(mouse_point)
		
		
		self.light_outline = utils.saturateColor(self.button_color,0.2)
		self.dark_outline = utils.desaturateColor(self.button_color,0.2)
		
		self.button_image = pygame.Surface((self.w,self.h))
		self.button_rect = self.button_image.get_rect()
		self.button_image.fill(self.button_color)
		
		# draw extra details
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(self.button_rect.w,0),2)
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(0,self.button_rect.h),2)
		pygame.draw.line(self.button_image,self.dark_outline,(0,self.button_rect.h-2),(self.button_rect.w,self.button_rect.h-2),2)
		pygame.draw.line(self.button_image,self.dark_outline,(self.button_rect.w-2,0),(self.button_rect.w-2,self.button_rect.h),2)
		
		
		if self.draw_outline:
			pygame.draw.rect(self.button_image,self.outline_color,(0,0,self.button_rect.w,self.button_rect.h),1)
		
		self.button_rect.topleft = (self.x,self.y)
		self.check_rect.center = self.button_rect.center
		
		if self.checked:
			self.variable.setVal(1)
		else:
			self.variable.setVal(0)
		
	def draw(self,Surface):
		"""Draws the button to the screen or parent widget"""
		Surface.blit(self.button_image,self.button_rect)
		
		if self.checked:
			pygame.draw.rect(Surface,self.fill_color,self.check_rect)

class StateButton(object):
	"""Similar to CheckButton functionality except it can be used in ButtonGrid widgets"""
	def __init__(self,text,parent,**kwargs):
		
		self.parent = parent
		self.event_list = []
		self.text = text
		
		self.valid_kwargs = {
			"x":0,
			"y":0,
			"w":12,
			"h":12,
			"text_color" : (0,0,0),
			"text_fill" : (200,200,200),
			"text_size" : 12,
			"variable" : utils.IntObject(0),
			"button_color":(0,150,150),
			"fill_color" : (20,20,10),
			"outline_color" : (250,250,250),
			"outline_color_fill" : (50,50,100),
			"draw_outline" : True,
			"index":0,			# used by button grid
			"grouped": False,			# if this is True it will have its state amended by a ButtonGrid object
			"font" : default_font_ico,
			"name" : None
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
		
		self.font = pygame.font.Font(self.font,self.text_size)
		self.checked = self.variable.getVal()
		
		# CURRENT COLORS
		self.b_color = self.button_color
		self.t_color = self.text_color
		self.o_color = self.outline_color
		
		# STATES
		self.mouse_over = False
		self.mouse_down = False
		self.active = True
		
		# extra colors 
		self.light_outline = utils.saturateColor(self.b_color,0.2)
		self.dark_outline = utils.desaturateColor(self.b_color,0.2)
		
		self.button_image = pygame.Surface((self.w,self.h))
		self.button_rect = self.button_image.get_rect()
		self.button_image.fill(self.b_color)
		
		self.text_image = self.font.render(self.text,False,self.t_color)
		self.text_rect = self.text_image.get_rect()
		self.text_rect.center = (self.button_rect.w/2,self.button_rect.h/2)
		
		self.button_image.blit(self.text_image,(self.text_rect))
		
		# draw extra details
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(self.button_rect.w,0),2)
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(0,self.button_rect.h),2)
		pygame.draw.line(self.button_image,self.dark_outline,(0,self.button_rect.h-2),(self.button_rect.w,self.button_rect.h-2),2)
		pygame.draw.line(self.button_image,self.dark_outline,(self.button_rect.w-2,0),(self.button_rect.w-2,self.button_rect.h),2)
		
		
		if self.draw_outline:
			pygame.draw.rect(self.button_image,self.o_color,(0,0,self.button_rect.w,self.button_rect.h),1)
		
		self.button_rect.topleft = (self.x,self.y)
		self.true_button_rect = pygame.Rect(0,0,self.button_rect.w,self.button_rect.h)
		
		if self.parent != None:
			# add this object to parent widget under a hash name
			if self.name == None:
				# add this object to parent widget under a hash name
				self.parent.widgets["widget"+str(self.parent.name_counter)] = self
				self.parent.name_counter += 1
			else:
				# add this object to parent widget under a hash name
				self.parent.widgets[self.name] = self
			
	def testClick(self,mx,my):
		"""Returns True if the button was clicked on; Returns False otherwise"""
		
		if self.parent != None:
			if self.true_button_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
		else:
			if self.button_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
	def getVal(self):
		"""Retrieves value in the entry box"""
		return self.variable.getVal()
	
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
		
		
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		mx,my,timepassed = mouse_point
		
		if self.parent != None:
			if type(self.parent) == Frame:
				#print "type is" , type(self.parent)
				self.true_button_rect.topleft = (self.button_rect.x + self.parent.background_rect.x,self.button_rect.y + self.parent.background_rect.y)
		
			elif type(self.parent) == ButtonGrid:
				#print self.parent.parent.x,self.parent.parent.y
				if self.parent.parent is None:
					self.true_button_rect.topleft = (self.button_rect.x + self.parent.background_rect.x,self.button_rect.y + self.parent.background_rect.y)
		
				else:
					self.true_button_rect.topleft = (self.button_rect.x + self.parent.background_rect.x+self.parent.parent.x,
						self.button_rect.y + self.parent.background_rect.y + self.parent.parent.y)
		
		
		if self.parent != None:
			#self.event_list = self.parent.event_list[:]		# use the parent Frame's event_list
			if not self.parent.minimized and self.true_button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
		
		else:
			if self.button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
		
		# process user events
		for event in self.event_list:
			if self.active:
				if event == LMOUSE_DOWN:
					if self.testClick(mx,my):
						# depress the button
						self.mouse_down = True
							
				if event == LMOUSE_UP:
					if self.testClick(mx,my):
						self.mouse_down = False
						# check/deselect
						self.checked = not(self.checked)
						if self.parent is not None and self.grouped:
							self.parent.addEvent(("select",self.index))
						
		# clear event queue
		self.event_list = []
		
	def update(self,mouse_point):
		"""Updates the buttons state based on user events"""
		
		self.handleEvents(mouse_point)
		
		if self.checked:
			self.t_color = self.text_fill
			self.b_color = self.fill_color
			self.o_color = self.outline_color_fill
		else:
			self.t_color = self.text_color
			self.b_color = self.button_color
			self.o_color = self.outline_color
			
		self.light_outline = utils.saturateColor(self.b_color,0.2)
		self.dark_outline = utils.desaturateColor(self.b_color,0.2)
		
		self.button_image = pygame.Surface((self.w,self.h))
		self.button_rect = self.button_image.get_rect()
		self.button_image.fill(self.b_color)
		
		self.text_image = self.font.render(self.text,False,self.t_color)
		self.text_rect = self.text_image.get_rect()
		self.text_rect.center = (self.button_rect.w/2,self.button_rect.h/2)
		
		self.button_image.blit(self.text_image,(self.text_rect))
		
		# draw extra details
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(self.button_rect.w,0),2)
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(0,self.button_rect.h),2)
		pygame.draw.line(self.button_image,self.dark_outline,(0,self.button_rect.h-2),(self.button_rect.w,self.button_rect.h-2),2)
		pygame.draw.line(self.button_image,self.dark_outline,(self.button_rect.w-2,0),(self.button_rect.w-2,self.button_rect.h),2)
		
		if self.draw_outline:
			pygame.draw.rect(self.button_image,self.o_color,(0,0,self.button_rect.w,self.button_rect.h),1)
		
		self.button_rect.topleft = (self.x,self.y)
		
		if self.checked:
			self.variable.setVal(1)
		else:
			self.variable.setVal(0)
		
	def draw(self,Surface):
		"""Draws the button to the screen or parent widget"""
		Surface.blit(self.button_image,self.button_rect)
		
class ButtonGrid(object):
	"""Manages a grid of StateButton objects. Returns indices of all the checked buttons"""
	def __init__(self,parent,**kwargs):
		
		self.parent = parent
		self.event_list = []
		
		if self.parent != None:
			self.minimized = self.parent.minimized
		else:
			self.minimized = False
		
		self.widgets = {}
		self.name_counter = 0
		self.id = 0
		
		self.cur_item = None
		self.temp_widgets_list = []
		self.checked_indices = []
		
		self.valid_kwargs = {
			"x":0,
			"y":0,
			"color_keyed":True,
			"button_width" : 16,
			"button_height" : 16,
			"max_rows":2,
			"max_columns":2,
			"text_color" : (0,0,0),
			"text_fill" : (200,200,200),
			"text_size" : 12,
			"variable" : utils.IntObject(0),
			"button_color":(0,150,150),
			"fill_color" : (20,20,10),
			"outline_color" : (250,250,250),
			"outline_color_fill" : (50,50,100),
			"draw_outline" : True,
			"font" : default_font_ico,
			"name" : None
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
		
		self.font_path = self.font
		self.font = pygame.font.Font(self.font,self.text_size)
		self.widgets_list = []		# use this to know the order buttons are added since dicts are unordered
		self.cur_col = 0
		self.cur_row = 0
		
		self.grid_image = None
		self.grid_rect = None
		
		self.background_rect = pygame.Rect(self.x,self.y,10,10)
		
		# init widgets_list
		for row in range(self.max_rows):
			t = []
			for col in range(self.max_columns):
				t.append(0)
			self.widgets_list.append(t)
			
		#print len(self.widgets_list)
		
		if self.parent != None:
			
			self.background_rect.topleft = (self.parent.background_rect.x + self.x,self.parent.background_rect.y + self.y)
			# add this object to parent widget under a hash name
			if self.name == None:
				# add this object to parent widget under a hash name
				self.parent.widgets["widget"+str(self.parent.name_counter)] = self
				self.parent.name_counter += 1
			else:
				# add this object to parent widget under a hash name
				self.parent.widgets[self.name] = self
		
	def addButton(self,text,in_group=True,color=None):
		"""Adds a state button to the grid. If grouped == True then button is affected by the state
		of others contained in the grid."""
		
		if self.cur_row < self.max_rows:
			
			if color is not None:
			
				new_button = StateButton(text,self,text_color=self.text_color,
											text_fill = self.text_fill,
											x = 0,
											y = 0,
											w = self.button_width,
											h = self.button_height,
											text_size = self.text_size,
											button_color = color,
											fill_color = color,
											outline_color = self.outline_color,
											outline_color_fill = self.outline_color_fill,
											draw_outline = True,
											font = self.font_path,
											grouped = in_group,
											index = self.id,
											name = None)
			else:
			
				new_button = StateButton(text,self,text_color=self.text_color,
											text_fill = self.text_fill,
											x = 0,
											y = 0,
											w = self.button_width,
											h = self.button_height,
											text_size = self.text_size,
											button_color = self.button_color,
											fill_color = self.fill_color,
											outline_color = self.outline_color,
											outline_color_fill = self.outline_color_fill,
											draw_outline = self.draw_outline,
											font = self.font_path,
											grouped = in_group,
											index = self.id,
											name = None)
										
			self.widgets_list[self.cur_row][self.cur_col] = new_button
			#self.widgets["widget"+str(self.name_counter)] = new_button
			self.temp_widgets_list.append(new_button)
			self.id += 1
			
			self.name_counter += 1
			self.cur_col += 1
			
			if self.cur_col >= self.max_columns:
				self.cur_row += 1
				self.cur_col = 0
		
		else:
			print "Grid rows are now full. Can't add new_button"
		
	def init(self):
		"""Call this after adding buttons to get the widget into a working state"""
		
		# create grid_image
		grid_width = self.max_columns * self.button_width
		grid_height = self.max_rows * self.button_height
		
		self.grid_image = pygame.Surface((grid_width,grid_height))
		
		if self.color_keyed:
			self.grid_image.set_colorkey((255,0,255))
			self.grid_image.fill((255,0,255))
		else:	
			self.grid_image.fill((0,0,0))
			
		self.grid_rect = self.grid_image.get_rect()
		self.grid_rect.topleft = (self.x,self.y)
		
		# set up button positions
		for row in range(self.max_rows):
			for col in range(self.max_columns):
				
				widget = self.widgets_list[row][col]
				if widget != 0:
					widget.x = col * self.button_width
					widget.y = row * self.button_height
		
		for row in range(self.max_rows):
			for col in range(self.max_columns):
				
				widget = self.widgets_list[row][col]
				if widget != 0:
					widget.draw(self.grid_image)
		
	def testClick(self,mx,my):
		"""Returns True if the button was clicked on; Returns False otherwise"""
		
		if self.parent != None:
			if self.true_button_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
		else:
			if self.button_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
	def getButtonState(self,index):
		"""Returns True if the button at the given index is checked"""
		return bool(self.temp_widgets_list[index].checked)
	
	def getSelected(self):
		"""Returns the indices of all the checked options. If no checked option, returns an empty tuple"""
		return tuple(self.checked_indices)
	
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
		
		# also give to the kids
		for widget in self.widgets.values():
			widget.addEvent(event)
		
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		mx,my,timepassed = mouse_point
		
		for event in self.event_list:
			if type(event) == tuple:
				if event[0] == "select":
					self.cur_item = event[1]
		
		# clear event queue
		self.event_list = []
		
	def update(self,mouse_point):
		"""Updates the buttons state based on user events"""
		
		
		if self.parent != None:
			self.minimized = self.parent.minimized
		else:
			self.minimized = False
		
		self.handleEvents(mouse_point)
		
		self.checked_indices = []
		for i in range(len(self.temp_widgets_list)):
			widget = self.temp_widgets_list[i]
			if widget.checked:
				self.checked_indices.append(i)
		
		
		# set all other except cur_item to unchecked if they are grouped
		if self.cur_item != None:
			for i in range(len(self.temp_widgets_list)):
				if i != self.cur_item:
					if self.temp_widgets_list[i].grouped:
						self.temp_widgets_list[i].checked = False
		
		if self.color_keyed:
			self.grid_image.fill((255,0,255))
		else:
			self.grid_image.fill((0,0,0))
			
		for row in range(self.max_rows):
			for col in range(self.max_columns):
				
				widget = self.widgets_list[row][col]
				if widget != 0:
					widget.draw(self.grid_image)
		
		self.grid_rect.topleft = (self.x,self.y)
		
		# update the kids
		for widget in self.widgets.values():
			widget.update(mouse_point)
			#print widget.mouse_down
		
		#print len(self.widgets)
	def draw(self,Surface):
		"""Draws the button to the screen or parent widget"""
		Surface.blit(self.grid_image,self.grid_rect)
	
	
class Label(object):
	def __init__(self,text,parent=None,**kwargs):
		
		self.text = text
		self.parent = parent
		self.event_list = []
		
		self.valid_kwargs = {
			"x":0,
			"y":0,
			"bg_color":None,
			"text_size" : 12,
			"text_color" : (0,0,0),
			"font" : default_font,
			"x_margin":5,
			"y_margin":5,
			"name" : None
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
		
		self.font = pygame.font.Font(self.font,self.text_size)
		self.background = None
		self.background_rect = None
		
		# STATES
		self.active = True
		
		# CURRENT COLORS
		
		self.text_image = self.font.render(self.text,False,self.text_color)
		self.text_rect = self.text_image.get_rect()
		
		if self.bg_color != None:
			self.background = pygame.Surface((self.text_rect.w + (self.x_margin*2),self.text_rect.h + (self.y_margin*2)))
			self.background_rect = self.background.get_rect()
			self.background.fill(self.bg_color)
		
		self.text_rect.topleft = (self.x,self.y)
		
		if self.parent != None:
			# add this object to parent widget under a hash name
			if self.name == None:
				# add this object to parent widget under a hash name
				self.parent.widgets["widget"+str(self.parent.name_counter)] = self
				self.parent.name_counter += 1
			else:
				# add this object to parent widget under a hash name
				self.parent.widgets[self.name] = self
			
	def testClick(self,mx,my):
		"""This does nothing"""
		pass
		
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
		
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		#mx,my,timepassed = mouse_point
		
		# clear event queue
		self.event_list = []
		
	def update(self,mouse_point):
		"""Updates the buttons state based on user events"""
		
		self.handleEvents(mouse_point)
		
		self.text_rect.topleft = (self.x,self.y)
		
		if self.bg_color != None:
			self.background_rect.center = self.text_rect.center
			
		
	def draw(self,Surface):
		"""Draws the button to the screen or parent widget"""
		if self.bg_color != None:
			Surface.blit(self.background,self.background_rect)
		
		Surface.blit(self.text_image,self.text_rect)

			
class TextEntry(object):
	def __init__(self,parent,**kwargs):
		
		self.parent = parent
		self.event_list = []
		
		self.valid_kwargs = {
			"x":0,
			"y":0,
			"w":90,
			"text_variable" : utils.StrObject("empty"),		# can also pass in a reference to an already existing data object
			"highlight_color":(50,80,200),
			"bg_color" : (255,255,255),
			"text_size" : 12,
			"text_color" : (0,0,0),
			"text_fill" : (240,240,240),
			"inactive_color" : (50,50,50),		# for text
			"outline_color" : (20,20,20),
			"font" : default_font,
			"x_margin" : 4,
			"y_margin" : 2,
			"in_focus" : True,
			"name" : None
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
		
		self.font = pygame.font.Font(self.font,self.text_size)
		self.collision_rects = []
		self.true_collision_rects = []
		
		# STATES
		self.mouse_over = False
		self.mouse_down = False
		self.caret_visible = False
		self.blink_updatetime = 300
		self.blink_acctime = 0
		
		self.active = True
		# COLORS
		self.t_color = self.text_color
		self.appended_str = list(self.text_variable.getVal())
		self.entry_string = "".join(self.appended_str)
		
		self.caret_index = 0
		self.step = None
		text_w,text_h = self.font.size(self.entry_string)
		self.text_metrics = self.font.metrics(self.entry_string)
		
		self.start_index = self.caret_index
		self.end_index = self.caret_index
		self.hilit = False
		self.shift_isdown = False
		
		self.text_image = self.font.render(self.entry_string,False,self.t_color)
		self.text_rect = self.text_image.get_rect()
		
		self.caret_image = pygame.Surface((2,self.text_rect.h))
		self.caret_rect = self.caret_image.get_rect()
		self.caret_image.fill((0,0,0))
		
		self.bg_height = self.font.get_height() + (self.y_margin*2) + 2
		self.bg_width = self.w + 2
		self.outline_height = self.bg_height - 2
		self.outline_width = self.w
		

		self.background = pygame.Surface((self.bg_width,self.bg_height))
		self.background_rect = self.background.get_rect()
		self.background.fill(self.bg_color)
		
		# draw outline
		pygame.draw.rect(self.background,self.outline_color,(2,2,self.outline_width,self.outline_height),1)
		
		self.background_rect.topleft = (self.x,self.y)
		self.true_background_rect = pygame.Rect(0,0,self.background_rect.w,self.background_rect.h)
		
		self.text_rect.centery = self.background_rect.centery
		self.text_rect.x = self.background_rect.x + self.x_margin
		
		# create collision rects by checking font metrics
		rect_x = self.text_rect.x
		rect_y = self.text_rect.y

		for i in range(len(self.entry_string)):
			char_width = self.text_metrics[i][4]
			new_rect = pygame.Rect(rect_x,rect_y,char_width,self.text_rect.h)
			
			if self.parent != None:
				true_rect = pygame.Rect(rect_x + self.parent.background_rect.x,rect_y+self.parent.background_rect.y,char_width,self.text_rect.h)
				self.true_collision_rects.append(true_rect)
				
			self.collision_rects.append(new_rect)
			rect_x += char_width
			
			if i == len(self.entry_string)-1:
				# add an extra rect for the rest of the area
				char_width = abs(self.background_rect.right - self.collision_rects[i].right) 
				extra_rect = pygame.Rect(rect_x,rect_y,char_width,self.text_rect.h)
			
				if self.parent != None:
					extra_true_rect = pygame.Rect(rect_x + self.parent.background_rect.x,rect_y+self.parent.background_rect.y,char_width,self.text_rect.h)
					self.true_collision_rects.append(extra_true_rect)
				
				self.collision_rects.append(extra_rect)
				#rect_x += char_width
			
		if self.parent != None:
			if self.name == None:
				# add this object to parent widget under a hash name
				self.parent.widgets["widget"+str(self.parent.name_counter)] = self
				self.parent.name_counter += 1
			else:
				# add this object to parent widget under a hash name
				self.parent.widgets[self.name] = self
	
	def setText(self,variable):
		"""Sets the appended_str to text"""
		self.appended_str = list(variable.getVal())
		self.text_variable = variable
		
		self.caret_index = self.start_index = self.end_index = 0
	
	def testClick(self,mx,my):
		"""Returns True if the button was clicked on; Returns False otherwise"""
		
		if self.parent != None:
			if self.true_background_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
		else:
			if self.background_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
		
		
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		mx,my,timepassed = mouse_point
		
		if self.parent != None:
			self.true_background_rect.topleft = (self.background_rect.x + self.parent.background_rect.x,self.background_rect.y + self.parent.background_rect.y)
		
		
		if self.parent != None:
			#self.event_list = self.parent.event_list[:]		# use the parent Frame's event_list
			if not self.parent.minimized and self.true_background_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
		
		else:
			if self.background_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
		
		# process user events
		for event in self.event_list:
			if self.active:
				if event == LMOUSE_DOWN:
					if self.testClick(mx,my):
						# depress the button
						self.mouse_down = True
						
						if not self.in_focus:
							# highlight all the text
							self.start_index = 0
							self.end_index = len(self.entry_string)-1
						else:
							for i in range(len(self.collision_rects)):
								if self.parent != None:
									if self.true_collision_rects[i].collidepoint(mx,my):
										self.start_index = i
										
								else:
									if self.collision_rects[i].collidepoint(mx,my):
										self.start_index = i
										
						self.in_focus = True
					else:
						self.in_focus = False
						self.start_index = 0
						self.end_index = 0
						
					# place caret
					for i in range(len(self.collision_rects)):
						
						#print self.collision_rects[i].topleft
						if self.parent != None:
							if self.true_collision_rects[i].collidepoint(mx,my):
								self.caret_index = i
								
						else:
							if self.collision_rects[i].collidepoint(mx,my):
								self.caret_index = i
										
				if event == LMOUSE_UP:
					if self.testClick(mx,my):
						self.mouse_down = False
							
				if type(event) == PYGAME_EVENT_TYPE:
				
					'''if event.type == KEYUP and self.in_focus:
						if event.key == K_RSHIFT:
							self.shift_isdown = False
							self.start_index = self.caret_index
							self.end_index = self.start_index
					'''	
					if event.type == KEYDOWN and self.in_focus:
						key_states = (event.unicode,event.mod,event.key)
						
						'''if event.key == K_RSHIFT:
							self.shift_isdown = True
							self.start_index = self.caret_index
							self.end_index = self.start_index
						'''	
						if event.key == K_LEFT:
							if self.caret_index > 0:
								self.caret_index -= 1
								
							if event.mod in (1,2):
								if self.end_index > 0:
									self.end_index -= 1
							else:
								self.start_index = self.end_index = self.caret_index
							
							#print(self.start_index,self.end_index)
							if self.start_index > self.end_index:
								self.step = -1
							else:
								self.step = 1
		
						elif event.key == K_RIGHT:
							if self.caret_index < len(self.appended_str):
								self.caret_index += 1
								
							if event.mod in (1,2):
								if self.end_index < len(self.appended_str):
									self.end_index += 1
							else:
								self.start_index = self.end_index = self.caret_index
							# print(self.start_index,self.end_index)
							
							if self.start_index > self.end_index:
								self.step = -1
							else:
								self.step = 1
		
							
						elif event.key == K_BACKSPACE:
							if not self.hilit:
								if self.caret_index>0:
									self.appended_str.pop(self.caret_index-1)
									self.caret_index -= 1
									self.start_index = self.end_index = self.caret_index
							else:
								#if self.step == -1:
								#	self.end_index -= 1
									
								
								if self.step == -1:
									
									#print "GOing left"
									#print (self.start_index,self.end_index)
									#temp = self.appended_str[self.end_index:self.start_index]
									#print temp
									del self.appended_str[self.end_index:self.start_index]
								else:
									#print "GOing right"
									#print (self.start_index,self.end_index)
									del self.appended_str[self.start_index:self.end_index:self.step]
									
								if self.step == -1:
									self.caret_index = self.end_index
								else:
									self.caret_index = self.start_index
									
								self.start_index = self.end_index = self.caret_index
						else:
							# we are adding valid strings
							if len(event.unicode) > 0:
								self.appended_str.insert(self.caret_index,event.unicode)
								self.caret_index += 1
								self.start_index = self.end_index = self.caret_index
					
							
		# clear event queue
		self.event_list = []
		
	def getVal(self):
		"""Retrieves value in the entry box"""
		return self.text_variable.getVal()
		
	def update(self,mouse_point):
		"""Updates the buttons state based on user events"""
		
		if self.start_index > self.end_index:
			self.step = -1
		else:
			self.step = 1
		
		self.handleEvents(mouse_point)
		mx,my,timepassed = mouse_point
		
		if abs(self.start_index - self.end_index) >0:
			self.hilit = True
		else:
			self.hilit = False
		
		if self.in_focus and self.mouse_down:
			for i in range(len(self.collision_rects)):
				if self.parent != None:
					if self.true_collision_rects[i].collidepoint(mx,my):
						self.end_index = i
										
				else:
					if self.collision_rects[i].collidepoint(mx,my):
						self.end_index = i
						
		
		if self.in_focus:
			self.blink_acctime += timepassed
			
			if self.blink_acctime > self.blink_updatetime:
			
				self.caret_visible = not(self.caret_visible)
				self.blink_acctime = 0
				
		
		self.entry_string = "".join(self.appended_str)
		self.text_variable.setVal(self.entry_string)
		self.text_metrics = self.font.metrics(self.entry_string)
		
		self.text_image = self.font.render(self.entry_string,False,self.t_color)
		self.text_rect = self.text_image.get_rect()
		
		self.caret_image = pygame.Surface((2,self.text_rect.h))
		self.caret_rect = self.caret_image.get_rect()
		self.caret_image.fill((0,0,0))
		
		self.bg_height = self.font.get_height() + (self.y_margin*2) + 2
		self.bg_width = self.w + 2
		self.outline_height = self.bg_height - 2
		self.outline_width = self.w
		
		
		self.background = pygame.Surface((self.bg_width,self.bg_height))
		self.background_rect = self.background.get_rect()
		self.background.fill(self.bg_color)
		
		self.background_rect.topleft = (self.x,self.y)
		
		# draw outline
		pygame.draw.rect(self.background,self.outline_color,(1,1,self.outline_width,self.outline_height),1)
		
		self.text_rect.centery = self.background_rect.centery
		self.text_rect.x = self.background_rect.x + self.x_margin
		
		# create collision rects by checking font metrics
		rect_x = self.text_rect.x
		rect_y = self.text_rect.y
		
		self.collision_rects = []
		self.true_collision_rects = []
		for i in range(len(self.entry_string)):
			char_width = self.text_metrics[i][4]
			new_rect = pygame.Rect(rect_x,rect_y,char_width,self.text_rect.h)
			
			if self.parent != None:
				true_rect = pygame.Rect(rect_x + self.parent.background_rect.x,rect_y+self.parent.background_rect.y,char_width,self.text_rect.h)
				self.true_collision_rects.append(true_rect)
				
			self.collision_rects.append(new_rect)
			rect_x += char_width
			
			if i == len(self.entry_string)-1:
				# add an extra rect for the rest of the area
				char_width = abs(self.background_rect.right - self.collision_rects[i].right) 
				extra_rect = pygame.Rect(rect_x,rect_y,char_width,self.text_rect.h)
			
				if self.parent != None:
					extra_true_rect = pygame.Rect(rect_x + self.parent.background_rect.x,rect_y+self.parent.background_rect.y,char_width,self.text_rect.h)
					self.true_collision_rects.append(extra_true_rect)
				
				self.collision_rects.append(extra_rect)
				#rect_x += char_width
				
		# set caret position
		self.caret_rect.centery = self.background_rect.centery
		
		if len(self.collision_rects)>0: 
			self.caret_rect.right = self.collision_rects[self.caret_index].left				
		else:
			self.caret_rect.right = self.text_rect.left + 1
			
	def draw(self,Surface):
		"""Draws the button to the screen or parent widget"""
		Surface.blit(self.background,self.background_rect)
		
		
		#for rect in self.collision_rects:
		#	pygame.draw.rect(Surface,(0,40,70),rect,1)
		
		if self.step >0:
			for i in range(self.start_index,self.end_index,self.step):
				if len(self.collision_rects) > 0:
					pygame.draw.rect(Surface,self.highlight_color,self.collision_rects[i])
		else:
			for i in range(self.start_index-1,self.end_index-1,self.step):
				if len(self.collision_rects) > 0:
					pygame.draw.rect(Surface,self.highlight_color,self.collision_rects[i])
		
		Surface.blit(self.text_image,self.text_rect)
		
		if self.in_focus:
			if self.caret_visible:
				Surface.blit(self.caret_image,self.caret_rect)
		
class Button(object):
	def __init__(self,text,parent,**kwargs):
		
		self.text = text
		self.parent = parent
		self.event_list = []
		
		self.valid_kwargs = {
			"x":0,
			"y":0,
			"command" : None,
			"button_color":(50,80,200),
			"fill_color" : (200,90,100),
			"click_button_fill" : (255,255,255),
			"click_text_fill" : (0,50,0),
			"text_size" : 12,
			"text_color" : (0,0,0),
			"text_fill" : (240,240,240),
			"outline_color" : (50,250,100),
			"outline_color_fill" : (50,50,100),
			"draw_outline" : False,
			"font" : default_font,
			"x_margin" : 4,
			"y_margin" : 2,
			"name" : None
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
		
		self.font = pygame.font.Font(self.font,self.text_size)
		
		# STATES
		self.mouse_over = False
		self.mouse_down = False
		self.active = True
		
		# CURRENT COLORS
		self.b_color = self.button_color
		self.t_color = self.text_color
		self.o_color = self.outline_color
		
		# extra colors 
		self.light_outline = utils.saturateColor(self.b_color,0.2)
		self.dark_outline = utils.desaturateColor(self.b_color,0.2)
		
		self.text_image = self.font.render(self.text,False,self.t_color)
		self.text_rect = self.text_image.get_rect()
		
		self.button_height = self.font.get_height() + (self.y_margin*2)
		self.button_width = self.text_image.get_size()[0] + (self.x_margin*2)
		
		
		self.button_image = pygame.Surface((self.button_width,self.button_height))
		self.button_rect = self.button_image.get_rect()
		self.button_image.fill(self.b_color)
		
		# draw extra details
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(self.button_rect.w,0),2)
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(0,self.button_rect.h),2)
		pygame.draw.line(self.button_image,self.dark_outline,(0,self.button_rect.h-2),(self.button_rect.w,self.button_rect.h-2),2)
		pygame.draw.line(self.button_image,self.dark_outline,(self.button_rect.w-2,0),(self.button_rect.w-2,self.button_rect.h),2)
		
		self.text_rect.center = (self.button_rect.w/2,self.button_rect.h/2)
		
		self.button_image.blit(self.text_image,self.text_rect)
		
		if self.draw_outline:
			pygame.draw.rect(self.button_image,self.o_color,(0,0,self.button_rect.w,self.button_rect.h),1)
		
		self.button_rect.topleft = (self.x,self.y)
		self.true_button_rect = pygame.Rect(0,0,self.button_rect.w,self.button_rect.h)
		
		if self.parent != None:
			# add this object to parent widget under a hash name
			if self.name == None:
				# add this object to parent widget under a hash name
				self.parent.widgets["widget"+str(self.parent.name_counter)] = self
				self.parent.name_counter += 1
			else:
				# add this object to parent widget under a hash name
				self.parent.widgets[self.name] = self
			
	def testClick(self,mx,my):
		"""Returns True if the button was clicked on; Returns False otherwise"""
		
		if self.parent != None:
			if self.true_button_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
		else:
			if self.button_rect.collidepoint(mx,my):
				return True
			else:
				return False
	
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
		
		
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		mx,my,timepassed = mouse_point
		
		if self.parent != None:
			self.true_button_rect.topleft = (self.button_rect.x + self.parent.background_rect.x,self.button_rect.y + self.parent.background_rect.y)
		
		
		if self.parent != None:
			#self.event_list = self.parent.event_list[:]		# use the parent Frame's event_list
			if not self.parent.minimized and self.true_button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
		
		else:
			if self.button_rect.collidepoint(mx,my):
				self.mouse_over=True
			else:
				self.mouse_over=False
		
		# process user events
		for event in self.event_list:
			if self.active:
				if event == LMOUSE_DOWN:
					if self.testClick(mx,my):
						# depress the button
						self.mouse_down = True
							
				if event == LMOUSE_UP:
					if self.testClick(mx,my):
						self.mouse_down = False
						# run command
						if self.command != None:
							self.command()
		
		# clear event queue
		self.event_list = []
		
	def update(self,mouse_point):
		"""Updates the buttons state based on user events"""
		
		self.handleEvents(mouse_point)
		
		if self.mouse_over and not self.mouse_down:
			self.t_color = self.text_fill
			self.b_color = self.fill_color
			self.o_color = self.outline_color_fill
		elif self.mouse_over and self.mouse_down:	
			self.t_color = self.click_text_fill
			self.b_color = self.click_button_fill
		else:
			self.t_color = self.text_color
			self.b_color = self.button_color
			self.o_color = self.outline_color
		
		self.light_outline = utils.saturateColor(self.b_color,0.2)
		self.dark_outline = utils.desaturateColor(self.b_color,0.2)
		
		self.text_image = self.font.render(self.text,False,self.t_color)
		self.text_rect = self.text_image.get_rect()
		
		self.button_height = self.font.get_height() + (self.y_margin*2)
		self.button_width = self.text_image.get_size()[0] + (self.x_margin*2)
		
		
		self.button_image = pygame.Surface((self.button_width,self.button_height))
		self.button_rect = self.button_image.get_rect()
		self.button_image.fill(self.b_color)
		
		# draw extra details
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(self.button_rect.w,0),2)
		pygame.draw.line(self.button_image,self.light_outline,(0,0),(0,self.button_rect.h),2)
		pygame.draw.line(self.button_image,self.dark_outline,(0,self.button_rect.h-2),(self.button_rect.w,self.button_rect.h-2),2)
		pygame.draw.line(self.button_image,self.dark_outline,(self.button_rect.w-2,0),(self.button_rect.w-2,self.button_rect.h),2)
		
		
		self.text_rect.center = (self.button_rect.w/2,self.button_rect.h/2)
		
		self.button_image.blit(self.text_image,self.text_rect)
		
		if self.draw_outline:
			pygame.draw.rect(self.button_image,self.o_color,(0,0,self.button_rect.w,self.button_rect.h),1)
		
		self.button_rect.topleft = (self.x,self.y)
		
	def draw(self,Surface):
		"""Draws the button to the screen or parent widget"""
		Surface.blit(self.button_image,self.button_rect)
		
class Frame(object):
	"""Creates a basic window"""
	def __init__(self,**kwargs):
		
		self.event_list = []
		self.name_counter = 0
		self.widgets = {}
		
		self.valid_kwargs = {
			"x" : 0,
			"y" : 0,
			"w" : 130,
			"h" : 90,
			"title_color1":(50,80,200),
			"title_color2" : (200,90,100),
			"text" : "untitled",
			"minimize" : False,
			"text_size" : 12,
			"text_color" : (0,0,0),
			"text_fill" : (240,240,240),
			"outline_color" : (50,250,100),
			"button_color" : (200,10,10),
			"click_button_fill" : (50,50,50),
			"symbol_color" : (0,0,0),
			"fill_color" : (200,200,200),		# for buttons on the titlebar
			"bg_color" : (150,150,150),
			"draw_outline" : True,
			"font" : default_font,
			"x_margin" : 5,
			"y_margin" : 2
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
		
		self.font = pygame.font.Font(self.font,self.text_size)
		self.active = True
		
		self.alive = True	# we haven't clicked on the close button yet
		self.minimized = False
		self.mouse_down_x = False
		self.mouse_over_x = False
		self.mouse_down_min = False
		self.mouse_over_min = False
		self.mouse_over_bar = False
		self.drag = False
		self.drag_point = (0,0)
		self.drag_topleft = (0,0)
		
		self.b_color_min = self.button_color
		self.b_color_x = self.button_color
		
		# create text image
		self.text_image = self.font.render(self.text,False,self.text_color)
		self.text_rect = self.text_image.get_rect()
		
		# create titlebar surface
		self.titlebar_height = self.text_rect.h + (self.y_margin*2)
		self.titlebar_surface = pygame.Surface((self.w,self.titlebar_height))
		self.titlebar_rect = self.titlebar_surface.get_rect()
		self.titlebar_rect.topleft = (self.x,self.y)
		
		# color the surface
		utils.fillGradient(self.titlebar_surface,self.title_color1,self.title_color2,vertical=False)
		
		self.text_rect.centery = self.titlebar_rect.h/2
		self.text_rect.x = self.x_margin
		
		self.titlebar_surface.blit(self.text_image,self.text_rect)
		
		# create background are in which child widgets are placed
		self.background = pygame.Surface((self.w,self.h))
		self.background.fill(self.bg_color)
		self.background_rect = self.background.get_rect()
		self.background_rect.topleft = (self.titlebar_rect.left,self.titlebar_rect.bottom)
		
		# create titlebar button images
		button_height = self.titlebar_height-4
		self.close_image = pygame.Surface((button_height,button_height))
		self.close_rect = self.close_image.get_rect()
		self.close_rect.centery = self.titlebar_rect.centery
		self.close_rect.right = self.titlebar_rect.right - 4
		
		self.close_image.fill(self.b_color_x)
		pygame.draw.line(self.close_image,self.symbol_color,(4,4),(self.close_rect.w-4,self.close_rect.h-4),2)
		pygame.draw.line(self.close_image,self.symbol_color,(self.close_rect.w-4,4),(4,self.close_rect.h-4),2)
		
		if self.minimize:
			self.min_image = pygame.Surface((button_height,button_height))
			self.min_rect = self.min_image.get_rect()
			self.min_rect.centery = self.titlebar_rect.centery
			self.min_rect.right = self.close_rect.left - 3
			
			self.min_image.fill(self.b_color_min)
			
			if not self.minimized:
				pygame.draw.line(self.min_image,self.symbol_color,(4,self.min_rect.h-4),(self.min_rect.w-4,self.min_rect.h-4),2)
			else:
				pygame.draw.rect(self.min_image,self.symbol_color,(3,4,self.min_rect.w-6,self.min_rect.h-6),1)
		
	def addEvent(self,event):
		"""Call this for communicating mouse events"""
		self.event_list.append(event)
		
		for widget in self.widgets.values():
			widget.addEvent(event)
		
		
	def handleEvents(self,mouse_point):
		"""handles events for all menus and child_menus"""
		mx,my,timepassed = mouse_point
		
		if self.titlebar_rect.collidepoint(mx,my):
			self.mouse_over_bar = True
		else:
			self.mouse_over_bar = False
			
		if self.close_rect.collidepoint(mx,my):
			self.mouse_over_x = True
		else:
			self.mouse_over_x = False
		
		if self.minimize:
			if self.min_rect.collidepoint(mx,my):
				self.mouse_over_min = True
			else:
				self.mouse_over_min = False
		
		
		# process user events
		for event in self.event_list:
			
			if self.active:
				if event == LMOUSE_DOWN:
					if self.mouse_over_x:
						# depress the button
						self.mouse_down_x = True
						#print "this happens"
					
					if self.minimize:	
						if self.mouse_over_min:
							self.mouse_down_min = True
						
					# check if we are not over any buttons
					if not self.minimize:
						if self.mouse_over_bar and not self.mouse_over_x:			
							self.drag = True
							self.drag_point = (mx,my)
							self.drag_topleft = (self.x,self.y)
					else:
						if self.mouse_over_bar and not self.mouse_over_x and not self.mouse_over_min:			
							self.drag = True
							self.drag_point = (mx,my)
							self.drag_topleft = (self.x,self.y)
						
				if event == LMOUSE_UP:
					self.drag = False
				
					if self.mouse_over_x:	
						self.alive = False
					
					if self.minimize:
						if self.minimized:
							if self.mouse_over_min:
								self.minimized = False
						else:
							if self.mouse_over_min:
								self.minimized = True
					
					# set mouse down for both buttons to False
					self.mouse_down_x = False
					
					if self.minimize:
						self.mouse_down_min = False
						
		# clear event queue
		self.event_list = []
		
	def update(self,mouse_point):
		"""Updates the buttons state based on user events"""
		
		self.handleEvents(mouse_point)
		
		if self.mouse_over_x and not self.mouse_down_x:
			self.b_color_x = self.fill_color
		
		elif self.mouse_over_x and self.mouse_down_x:	
			self.b_color_x = self.click_button_fill
			#print "this runs"
		else:
			self.b_color_x = self.button_color
		
		if self.minimize:
			if self.mouse_over_min and not self.mouse_down_min:
				self.b_color_min = self.fill_color
		
			elif self.mouse_over_min and self.mouse_down_min:	
				self.b_color_min = self.click_button_fill
			else:
				self.b_color_min = self.button_color
		
		#print self.drag
		
		# create titlebar button images
		button_height = self.titlebar_height-4
		self.close_image = pygame.Surface((button_height,button_height))
		self.close_rect = self.close_image.get_rect()
		self.close_rect.centery = self.titlebar_rect.centery
		self.close_rect.right = self.titlebar_rect.right - 4
		
		self.close_image.fill(self.b_color_x)
		pygame.draw.line(self.close_image,self.symbol_color,(4,4),(self.close_rect.w-4,self.close_rect.h-4),2)
		pygame.draw.line(self.close_image,self.symbol_color,(self.close_rect.w-4,4),(4,self.close_rect.h-4),2)
		
		if self.minimize:
			self.min_image = pygame.Surface((button_height,button_height))
			self.min_rect = self.min_image.get_rect()
			self.min_rect.centery = self.titlebar_rect.centery
			self.min_rect.right = self.close_rect.left - 3
			
			self.min_image.fill(self.b_color_min)
			
			if not self.minimized:
				pygame.draw.line(self.min_image,self.symbol_color,(4,self.min_rect.h-4),(self.min_rect.w-4,self.min_rect.h-4),2)
			else:
				pygame.draw.rect(self.min_image,self.symbol_color,(3,4,self.min_rect.w-6,self.min_rect.h-6),1)
		
		if self.drag:
			# calculate mouse position on titlebar
			dmx,dmy = self.drag_point
			true_mx,true_my,timepassed = mouse_point
			#pos_on_bar = (mx-self.x,my-self.y)
			diff_x,diff_y = (dmx-self.drag_topleft[0],dmy-self.drag_topleft[1])
			self.x = true_mx - diff_x
			self.y = true_my - diff_y
		
		# update positions
		self.titlebar_rect.topleft = (self.x,self.y)
		self.background_rect.topleft = (self.titlebar_rect.left,self.titlebar_rect.bottom)
		self.close_rect.centery = self.titlebar_rect.centery
		self.close_rect.right = self.titlebar_rect.right - 4
		
		if self.minimize:
			self.min_rect.centery = self.titlebar_rect.centery
			self.min_rect.right = self.close_rect.left - 3
			
		for widget in self.widgets.values():
			widget.update(mouse_point)
		
		# clear event queue
		#self.event_list = []
		
		
	def draw(self,Surface):
		"""Draws the window to the screen"""
		
		Surface.blit(self.titlebar_surface,self.titlebar_rect)
		
		Surface.blit(self.close_image,self.close_rect)
		
		self.background.fill(self.bg_color)
		
		for widget in self.widgets.values():
			widget.draw(self.background)
		
		if self.minimize:
			Surface.blit(self.min_image,self.min_rect)
		
		if not self.minimized:
			Surface.blit(self.background,self.background_rect)
	
class OKCancelDialog(Frame):
	"""Creates a basic dialog box"""
	def __init__(self,text,button1_command,button2_command,button1_text="OK",button2_text="Cancel",text_size=8,**kwargs):
		"""A wrapper around a Frame widget"""
		super(OKCancelDialog,self).__init__(**kwargs)
		# As you can see default argument variables dont interfere with kwargs which is awesomesauce
		
		# create label and buttons
		buttony = (self.h / 3) * 2
		button1x = self.w/6
		button2x = button1x * 3
		
		label = Label(text,self,text_size=text_size,x=self.w/6,y=self.h/3.0)
		button1 = Button(button1_text,self,x=button1x,y=buttony,command=button1_command)
		button2 = Button(button2_text,self,x=button2x,y=buttony,command=button2_command)
		
class MessageDialog(Frame):
	"""Creates a basic dialog box"""
	def __init__(self,text,text_size=8,**kwargs):
		"""A wrapper around a Frame widget"""
		super(MessageDialog,self).__init__(**kwargs)
		# As you can see default argument variables dont interfere with kwargs which is awesomesauce
			
		# create label and buttons
		buttony = (self.h / 3) * 2
		buttonx = (self.w/2)- 30
		
		label = Label(text,self,text_size=text_size,x=self.w/6,y=self.h/3.0)
		close_button = Button("Close",self,x=buttonx,y=buttony,command= self.close)
	
	def close(self):
		self.alive = False
	