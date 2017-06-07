import pygame,sys,math,cPickle
from pygame.locals import*
import room_objects 
import sgf.utils.g_utils
from Tkinter import*

pygame.init()

class CreateLoadForm(Frame):
	"""Shows the form that prompts Room loading/creation"""
	def __init__(self,owner,master=None):
		Frame.__init__(self,master)
		self.owner = owner
		self.grid()
		self.createWidgets()
		self.runApp=True
		self.master.title("Create/Load Room")
		
	def createWidgets(self):
		"""Draws the forms widgets to the frame"""
		self.createButton = Button(self, text = "Create", command = self.createNewRoom)
		self.createButton.grid()
		self.loadButton = Button(self, text = "Load", command = self.loadExistingRoom)
		self.loadButton.grid()
		
		self.quitButton = Button(self, text= "Quit", command = self.quit)
		self.quitButton.grid()
		
	def createNewRoom(self):
		"""Callback function that takes user to room creation options form"""
		print "Show new room form"
		self.owner.next_form = "new"
		self.grid_forget()
		
		Frame.quit(self)
		self.runApp=False
		
	def loadExistingRoom(self):
		"""Callback function that takes user to room loading options form"""
		print "show load room form"
		self.owner.next_form = "load"
		self.grid_forget()
		
		Frame.quit(self)
		self.runApp=False
		
	def quit(self):
		"""Closes the Frame"""
		self.owner.next_form = "quit"
		Frame.quit(self)
		self.runApp=False
		
class CreateSaveForm(Frame):
	"""Shows the form that prompts Room saving to file"""
	def __init__(self,owner,master=None):
		Frame.__init__(self,master)
		self.owner = owner
		self.grid()
		self.createWidgets()
		self.runApp=True
		self.master.title("Save Room")
		
	def createWidgets(self):
		"""Draws the forms widgets to the frame"""
		self.filenameVar = StringVar()
		self.filenameVar.set("room0.dat")
		
		# filename label
		self.filename_label = Label(self, text = "Save Room As")
		self.filename_label.grid(column = 0, row = 0)
		
		self.filename_entry = Entry(self, textvariable = self.filenameVar)
		self.filename_entry.grid(column = 1, row = 0)
		
		
		self.createButton = Button(self, text = "Save", command = self.saveData)
		self.createButton.grid(column = 0, row = 1)
		self.loadButton = Button(self, text = "Cancel", command = self.Cancel)
		self.loadButton.grid(column = 1, row = 1)
		
	def saveData(self):
		"""Callback function that calls file pickling to file"""
		# save to data file
		self.owner.saveRoomData(self.filenameVar.get())
		
		self.grid_forget()
		Frame.quit(self)
		self.runApp=False
		
	def Cancel(self):
		"""Quits the Frame"""
		self.grid_forget()
		Frame.quit(self)
		self.runApp=False
		
	def quit(self):
		"""Quits the Frame"""
		self.owner.next_form = "quit"
		Frame.quit(self)
		self.runApp=False

class LoadRoomForm(Frame):
	"""Shows the form that prompts loading room from file"""
	def __init__(self,owner,master=None):
		Frame.__init__(self,master)
		self.owner = owner
		self.grid()
		self.createWidgets()
		self.runApp=True
		self.master.title("Load Room")
		
		
	def createWidgets(self):
		"""Draws the forms widgets to the frame"""
		self.filenameVar = StringVar()
		
		# filename label
		self.filename_label = Label(self, text = "Open Room")
		self.filename_label.grid(column = 0, row = 0)
		
		self.filename_entry = Entry(self, textvariable = self.filenameVar)
		self.filename_entry.grid(column = 1, row = 0)
		
		self.okButton = Button(self, text = "OK", command = self.Accept)
		self.okButton.grid(column = 0, row = 1)
		self.cancelButton = Button(self, text = "Cancel", command = self.Cancel)
		self.cancelButton.grid(column = 1, row = 1)
	
	def Accept(self):
		"""Callback from clicking OK Button"""
		self.owner.next_form = "editor"
		
		self.owner.room_filename = self.filenameVar.get()
		
		self.grid_forget()
		self.runApp=False
		Frame.quit(self)
		print "Accept params"
		
		
	def Cancel(self):
		"""Callback from clicking Cancel Button"""
		
		# closes the Frame
		self.owner.next_form = "quit"
		self.grid_forget()
		Frame.quit(self)
		self.runApp=False
	
		
class NewRoomForm(Frame):
	"""Shows the form that prompts entry of new Room configuration details"""
	def __init__(self,owner,master=None):
		Frame.__init__(self,master)
		self.owner = owner
		self.grid()
		self.createWidgets()
		self.runApp=True
		self.master.title("Define Room")
		
		
	def createWidgets(self):
		"""Draws widgets to Frame"""
		self.importVar = StringVar()
		self.widthVar = IntVar()
		self.heightVar = IntVar()
		self.filenameVar = StringVar()
		
		self.widthVar.set(200)
		self.heightVar.set(200)
		self.filenameVar.set("untitled")
		self.importVar.set("jgamesprites")
		
		# import label
		self.importfile_label = Label(self, text = "import")
		self.importfile_label.grid(column = 0, row = 0)
		
		self.import_entry = Entry(self, textvariable = self.importVar)
		self.import_entry.grid(column = 1, row = 0)
		
		# filename label
		self.filename_label = Label(self, text = "Save Room As")
		self.filename_label.grid(column = 0, row = 1)
		
		self.filename_entry = Entry(self, textvariable = self.filenameVar)
		self.filename_entry.grid(column = 1, row = 1)
		
		# width label
		self.width_label = Label(self, text = "Room width")
		self.width_label.grid(column = 0, row = 2)
		
		self.width_entry = Entry(self, textvariable = self.widthVar)
		self.width_entry.grid(column = 1, row = 2)
		
		# height label
		self.height_label = Label(self, text = "Room height")
		self.height_label.grid(column = 0, row = 3)
		
		self.height_entry = Entry(self, textvariable = self.heightVar)
		self.height_entry.grid(column = 1, row = 3)
		
		
		
		self.okButton = Button(self, text = "OK", command = self.Accept)
		self.okButton.grid()
		self.cancelButton = Button(self, text = "Cancel", command = self.Cancel)
		self.cancelButton.grid()
		
		self.quitButton = Button(self, text= "Quit", command = self.quit)
		self.quitButton.grid()
		
	def Accept(self):
		"""Callback from clicking the OK Button"""
		self.owner.next_form = "editor"
		
		# set owner room creation variables
		self.owner.room_width = self.widthVar.get()
		self.owner.room_height = self.heightVar.get()
		self.owner.import_file = self.importVar.get()
		self.owner.room_filename = self.filenameVar.get()
		
		self.grid_forget()
		self.runApp=False
		Frame.quit(self)
		print "Accept params"
		
		
	def Cancel(self):
		"""Callback from clicking the Cancel Button"""
		# closes the Frame
		self.owner.next_form = "quit"
		self.grid_forget()
		Frame.quit(self)
		self.runApp=False
		
	
	def quit(self):
		"""Quits the current Frame"""
		self.owner.next_form = "quit"
		Frame.quit(self)
		self.runApp=False

class GridTile(object):
	"""Used for visual effect and to get placement position when snapping is enabled"""
	def __init__(self,x,y,w,h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		
		self.rect = pygame.Rect(self.x,self.y,self.w,self.h)
	
	def update(self):
		
		self.rect.topleft = (self.x, self.y)
	
	def draw(self,Surface):
		
		pygame.draw.rect(Surface,(50,50,50),self.rect,1)
	
class RoomEditor(object):
	"""Facilitates the arbitrary placement of sprites on a Room surface"""
	def __init__(self):
		self.room = None
		self.myfont = pygame.font.SysFont("Arial",15)
		
		# COLORS
		self.WHITE = (255,255,255)
		self.BLACK = (0,0,0)
		
		self.screen = None
		self.screen_width = 640
		self.screen_height = 480
		self.clock = pygame.time.Clock()
		self.runEdit = True
		
		self.current_form = None 
		self.next_form = None
		self.grid_tiles = []
		self.grid_show = False
		
		self.showCreateLoadForm()
		
		if self.next_form == "new":
			# show create new room form
			self.showNewRoomForm()
			
			# init video
			pygame.display.set_caption("Room Editor")
			self.screen = pygame.display.set_mode((self.screen_width,self.screen_height))
			
			if self.next_form == "editor":
				# create room object and enter edit loop
				self.room = room_objects.Room(self.room_width,self.room_height,self.import_file)
				
				self.module_object = self.room.module
				
		elif self.next_form == "load":
			# show load room form
			self.showLoadRoomForm()
			
			# init video
			pygame.display.set_caption("Room Editor")
			self.screen = pygame.display.set_mode((self.screen_width,self.screen_height))
		
			# use filename to unpickle room
			self.room = self.loadRoomData(self.room_filename)
			self.module_object = self.room.module
			
	def addSpriteToRoom(self,sprite,depth):
		"""Adds sprite to room in corresponding depth associated list"""
	
		if depth == 0:
			# add to background objects
			self.room.background_objects.append(sprite)
		elif depth == 1:
			# add to mid objects
			self.room.mid_objects.append(sprite)
		elif depth == 2:
			# add to fore objects
			self.room.fore_objects.append(sprite)
	
	def getSpriteToMove(self,mouse_x,mouse_y):
		"""Returns a sprite from room that collides with the mouse pointer"""
		
		# walk lists in reverse seeking offending sprite
		
		for object in range(len(self.room.fore_objects),0,-1):
			if self.room.fore_objects[object-1].rect.collidepoint(mouse_x,mouse_y):
				
				return self.room.fore_objects[object-1]
		
		for object in range(len(self.room.mid_objects),0,-1):
			if self.room.mid_objects[object-1].rect.collidepoint(mouse_x,mouse_y):

				return self.room.mid_objects[object-1]
		
		for object in range(len(self.room.background_objects),0,-1):
			if self.room.background_objects[object-1].rect.collidepoint(mouse_x,mouse_y):
			
				return self.room.background_objects[object-1]
		
		return None
		
	def removeSpriteFromRoom(self,mouse_x,mouse_y):
		"""Removes a sprite from room that collides with the mouse pointer"""
		
		# walk all the game objects lists in reverse 
		# remove first offending sprite
		
		for object in range(len(self.room.fore_objects),0,-1):
			if self.room.fore_objects[object-1].rect.collidepoint(mouse_x,mouse_y):
				self.room.fore_objects.remove(self.room.fore_objects[object-1])
				return
		
		for object in range(len(self.room.mid_objects),0,-1):
			if self.room.mid_objects[object-1].rect.collidepoint(mouse_x,mouse_y):
				self.room.mid_objects.remove(self.room.mid_objects[object-1])
				return
		
		for object in range(len(self.room.background_objects),0,-1):
			if self.room.background_objects[object-1].rect.collidepoint(mouse_x,mouse_y):
				self.room.background_objects.remove(self.room.background_objects[object-1])
				return
		
	def saveRoomData(self,room_filename):
		"""Pickles the RoomDataHolder to a specified file"""
		# create RoomDataHolder object
		room_data = RoomDataHolder()
		room_data.getData(self.room)
		
		# pickle the object
		f = file(room_filename,"w")
		cPickle.dump(room_data,f)
		f.close()
		
		print "Saved room as %s" % room_filename
	
	def createGrid(self,snapping_value):
		"""Creates the tile objects for showing snapping placement"""
		self.grid_tiles = []
		for row in range(0,self.room.height,snapping_value):
			for col in range(0,self.room.width,snapping_value):
				tile = GridTile(col,row,snapping_value,snapping_value)
				self.grid_tiles.append(tile)
	
	def drawGrid(self,Surface):
		if self.grid_show == True:
			for tile in self.grid_tiles:
				tile.draw(Surface)
	
	def loadRoomData(self,room_filename):
		"""unPickles the RoomDataHolder from the specified file"""
		f = file(room_filename)
		room_data = cPickle.load(f)
		f.close()
		
		# use room data to create room object
		new_room = room_data.loadData()
		
		return new_room
	
	def showEditMode(self):
		"""The actual loop where sprites are added to room"""
		
		# mouse variables
		mouse_x = 0
		mouse_y = 0
		
		snapping_options = [[0,"None"],[8,"8px"],[16,"16px"],[32,"32px"],[64,"64px"]] 
		snapping_ID = 0
		
		ctrl_down = False
		
		# camera position tracking variables
		camera_x = 0
		camera_y = 0
		
		true_mouse_x = mouse_x - camera_x
		true_mouse_y = mouse_y - camera_y
		
		draw_mouse_x = 0
		draw_mouse_y = 0
		
		pan_left = False
		pan_right = False
		pan_up = False
		pan_down = False
		pan_speed = 0.7
		
		# editor variables
		current_sprite_ID = 0
		master_sprites = self.module_object.master_sprites
		
		sprite_to_move = None
		
		current_spritedata = master_sprites[current_sprite_ID]
		current_spritetodraw = current_spritedata[0](current_spritedata[1],mouse_x,mouse_y)
		previewObjectWidth=current_spritetodraw.rect.width
		previewObjectHeight=current_spritetodraw.rect.height
		previewObjectSurface=pygame.Surface((previewObjectWidth,previewObjectHeight))
		previewObjectSurface.fill(self.WHITE)
		
		# draw object to surface
		previewObjectSurface.blit(current_spritetodraw.image,(0,0))
		
		# make transparent
		previewObjectSurface.set_alpha(80)
		
		sprite_depth_dict = {0:"background", 1:"mid", 2:"fore"}
		
		sprite_depth = 1		# mid object are added by default
		max_sprite_depth = 3
		
		while self.runEdit:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
					self.runEdit = False
					
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						pygame.quit()
						sys.exit()
						self.runEdit = False
					
					if event.key == K_LCTRL or event.key == K_RCTRL :
						ctrl_down = True
					
					if event.key == K_LEFT:
						# cycle through sprites
						current_sprite_ID = (current_sprite_ID - 1) % len(master_sprites)
						
						current_spritedata = master_sprites[current_sprite_ID]
						current_spritetodraw = current_spritedata[0](current_spritedata[1],mouse_x,mouse_y)
						previewObjectWidth=current_spritetodraw.rect.width
						previewObjectHeight=current_spritetodraw.rect.height
						previewObjectSurface=pygame.Surface((previewObjectWidth,previewObjectHeight))
						previewObjectSurface.fill(self.WHITE)
		
						# draw object to surface
						previewObjectSurface.blit(current_spritetodraw.image,(0,0))
						# make transparent
						previewObjectSurface.set_alpha(80)
		
					if event.key == K_RIGHT:
						# cycle through sprites
						current_sprite_ID = (current_sprite_ID + 1) % len(master_sprites)
						
						current_spritedata = master_sprites[current_sprite_ID]
						current_spritetodraw = current_spritedata[0](current_spritedata[1],mouse_x,mouse_y)
						previewObjectWidth=current_spritetodraw.rect.width
						previewObjectHeight=current_spritetodraw.rect.height
						previewObjectSurface=pygame.Surface((previewObjectWidth,previewObjectHeight))
						previewObjectSurface.fill(self.WHITE)
		
						# draw object to surface
						previewObjectSurface.blit(current_spritetodraw.image,(0,0))
						# make transparent
						previewObjectSurface.set_alpha(80)
						
					if event.key == K_UP:
						# cycle through depths
						sprite_depth = (sprite_depth - 1) % max_sprite_depth
						
					if event.key == K_DOWN:
						# cycle through depths
						sprite_depth = (sprite_depth + 1) % max_sprite_depth
					
					if event.key == K_RETURN:
						# save room to dat file
						self.showSaveRoomForm()
					
					if event.key == K_z:
						# cycle through snapping options
						snapping_ID = (snapping_ID - 1) % len(snapping_options)
						
					if event.key == K_x:
						# cycle through snapping options
						snapping_ID = (snapping_ID + 1) % len(snapping_options)
					
					
					
					# camera input
					if event.key == K_j:
						pan_left = True
					
					if event.key == K_l:
						pan_right = True
					
					if event.key == K_i:
						pan_up = True
					
					if event.key == K_k:
						pan_down = True
					
				if event.type == KEYUP:
					# camera input
					if event.key == K_j:
						pan_left = False
					
					if event.key == K_l:
						pan_right = False
					
					if event.key == K_i:
						pan_up = False
					
					if event.key == K_k:
						pan_down = False
					
					if event.key == K_LCTRL or event.key == K_RCTRL :
						ctrl_down = False
					
				
				if event.type == MOUSEMOTION:
					mouse_x, mouse_y = event.pos
				
				if event.type == MOUSEBUTTONDOWN:
					if event.button == 1:
						
						if not ctrl_down:
							# add sprite at position
							# find the grid tile true mouse positions are in
							
							if self.grid_show:
								for tile in self.grid_tiles:	
									if tile.rect.collidepoint((true_mouse_x,true_mouse_y)):
										# set sprite to topleft of tile
										new_sprite = current_spritedata[0](current_spritedata[1],tile.rect.left,tile.rect.top)
										self.addSpriteToRoom(new_sprite, sprite_depth)
							
							else:			
								new_sprite = current_spritedata[0](current_spritedata[1],true_mouse_x,true_mouse_y)
								self.addSpriteToRoom(new_sprite, sprite_depth)
						
						elif ctrl_down:
							sprite_to_move = self.getSpriteToMove(true_mouse_x,true_mouse_y)
						
					if event.button == 3:
						# remove sprite
						self.removeSpriteFromRoom(true_mouse_x,true_mouse_y)
					
				if event.type == MOUSEBUTTONUP:
					if event.button == 1:
						sprite_to_move = None
						
			# update editor
			
			if pan_left:
				camera_x += pan_speed
			if pan_right:
				camera_x -= pan_speed
			if pan_up:
				camera_y += pan_speed
			if pan_down:
				camera_y -= pan_speed
			
			
			self.room.x = camera_x
			self.room.y = camera_y
			
			true_mouse_x = mouse_x - camera_x
			true_mouse_y = mouse_y - camera_y
			
			draw_mouse_x = mouse_x 			
			draw_mouse_y = mouse_y 
			
			if snapping_ID != 0:
				# snap to 8 pixels
				self.createGrid(snapping_options[snapping_ID][0])
				self.grid_show = True
				
			else:
				self.grid_tiles = []
				self.grid_show = False
				
			# update current_spritetodraw
			current_spritetodraw.rect.topleft = (mouse_x,mouse_y)
			
			# move sprite 
			if sprite_to_move != None:
				sprite_to_move.x = true_mouse_x - sprite_to_move.rect.width/2
				sprite_to_move.y = true_mouse_y - sprite_to_move.rect.height/2
			
			
			# draw snapping text to screen
			snaptext_surf = self.myfont.render("snap = %s" % snapping_options[snapping_ID][1],False,self.WHITE)
			snaptext_rect = snaptext_surf.get_rect()
			snaptext_rect.topleft = (8,self.screen_height-20)
			
			# draw depth text to screen
			depthtext_surf = self.myfont.render("depth = %s" % sprite_depth_dict[sprite_depth],False,self.WHITE)
			depthtext_rect = depthtext_surf.get_rect()
			depthtext_rect.topleft = (120,self.screen_height-20)
			
			
			self.room.update()
			
			#print true_mouse_x,true_mouse_y
			
			self.screen.fill(self.BLACK)
			
			self.room.draw(self.screen)
			
			# draw grid if grid_show is True
			self.drawGrid(self.room.surface)
			# blit it to screen
			self.screen.blit(self.room.surface,self.room.surface_rect)
			
			if not ctrl_down:
				# draw current_spritetodraw
					
				self.screen.blit(previewObjectSurface,(draw_mouse_x,draw_mouse_y))
			
			self.screen.blit(snaptext_surf,snaptext_rect)
			self.screen.blit(depthtext_surf,depthtext_rect)
			
			pygame.display.flip()
			self.clock.tick(45)
			
	def showCreateLoadForm(self):
		"""Shows and manages display of a form"""
		self.current_form = CreateLoadForm(self)
		
		while self.current_form.runApp:
			self.current_form.update()
	
	def showNewRoomForm(self):
		"""Shows and manages display of a form"""
		self.current_form = NewRoomForm(self)
		
		while self.current_form.runApp:
			self.current_form.update()
	
	def showLoadRoomForm(self):
		"""Shows and manages display of a form"""
		self.current_form = LoadRoomForm(self)
		
		while self.current_form.runApp:
			self.current_form.update()
	
	def showSaveRoomForm(self):
		"""Shows and manages display of a form"""
		self.current_form = CreateSaveForm(self)
		#self.current_form.focus_set()
		
		while self.current_form.runApp:
			self.current_form.update()
	
	
if __name__ == "__main__":	

	ed = RoomEditor()
	ed.showEditMode()
	