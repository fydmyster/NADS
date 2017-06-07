import pygame,copy,cPickle, math
from pygame.locals import*

def saveRoomData(room,room_filename):
	"""Pickles the RoomDataHolder to a specified file"""
	# create RoomDataHolder object
	room_data = RoomDataHolder()
	room_data.getData(room)
		
	# pickle the object
	f = file(room_filename,"w")
	cPickle.dump(room_data,f)
	f.close()
		
	print "Saved room as %s" % room_filename

def loadRoomData(room_filename,editor_parent=None):
		"""unPickles the RoomDataHolder from the specified file"""
		f = file(room_filename)
		room_data = cPickle.load(f)
		f.close()
		
		# use room data to create room object
		new_room = room_data.loadData(editor_parent)
		
		return new_room

def importObjectsModule(module):
		# IMPORT FILE THAT CONTAINS THE SPRITE DEFINITIONS
		c = compile("import %s" % module, "<string>", "exec")
		eval(c,globals())	# you have to call this  with globals or it wont find the module
							# this imports into the global namespace
		#__import__(self.import_file,globals(),locals(),[])
		#print jgamesprites
		#execfile(self.import_file,globals(),locals())
		
		# evaluate the module name 
		module_object = eval(module)
		
		return module_object
		
class SpriteDataHolder(object):
	def __init__(self,object_type,imageloader_func,x,y):
		"""Used for storing a sprites data in a form that can be pickled"""
		self.object_type = object_type
		self.imageloader_func = imageloader_func
		self.x = x
		self.y = y
		
	def setData(self,object_type,imageloader_func,x,y):
		"""Overwrites data with new values"""
		self.object_type = object_type
		self.imageloader_func = imageloader_func
		self.x = x
		self.y = y

class PhysDataHolder(object):
	def __init__(self,object_type,nodes_list,constraints_list):
		"""Used for storing a sprites data in a form that can be pickled"""
		self.object_type = object_type	
		self.nodes_list = nodes_list
		self.constraints_list = constraints_list
		
		for node in self.nodes_list:
			node.parent = None
		for constraint in self.constraints_list:
			constraint.parent = None
		
	def setData(self,object_type,nodes_list,constraints_list):
		"""Overwrites data with new values"""
		self.object_type = object_type
		self.nodes_list = nodes_list
		self.constraints_list = constraints_list
		
		for node in self.nodes_list:
			node.parent = None
		for constraint in self.constraints_list:
			constraint.parent = None
		
class RoomDataHolder(object):
	def __init__(self):
		"""Used for loading and storing room data for persistence"""
		self.import_file = None
		self.background_objects_data = []
		self.mid_objects_data = []
		self.fore_objects_data = []
		self.physics_objects_data = []
		self.width_data = None
		self.height_data = None
		
	def getData(self,room):
		"""Retrieves data from room and stores said data in self"""
		self.import_file = room.import_file
		
		self.width_data = room.width
		self.height_data = room.height
		
		for object in room.background_objects:
			spriteData = SpriteDataHolder(type(object),object.imageloader_func,object.x,object.y)
			self.background_objects_data.append(spriteData)
		
		for object in room.mid_objects:
			spriteData = SpriteDataHolder(type(object),object.imageloader_func,object.x,object.y)
			self.mid_objects_data.append(spriteData)
		
		for object in room.fore_objects:
			spriteData = SpriteDataHolder(type(object),object.imageloader_func,object.x,object.y)
			self.fore_objects_data.append(spriteData)
		
		for object in room.physics_objects:
			physData = PhysDataHolder(type(object),object.nodes_list,object.constraints_list)
			self.physics_objects_data.append(physData)

	def loadData(self,room_parent=None):
		"""Retrieves data from self and returns a room object with that data"""
		room = Room(self.width_data,self.height_data,self.import_file)
		
		for spriteData in self.background_objects_data:
			sprite = spriteData.object_type(spriteData.imageloader_func,spriteData.x,spriteData.y)
			room.background_objects.append(sprite)
	
		for spriteData in self.mid_objects_data:
			sprite = spriteData.object_type(spriteData.imageloader_func,spriteData.x,spriteData.y)
			room.mid_objects.append(sprite)
		
		for spriteData in self.fore_objects_data:
			sprite = spriteData.object_type(spriteData.imageloader_func,spriteData.x,spriteData.y)
			room.fore_objects.append(sprite)
		
		for physData in self.physics_objects_data:
			physics_object = physData.object_type(room_parent,physData.nodes_list,physData.constraints_list)
			
			for node in physics_object.nodes_list:
				node.parent = physics_object
			for constraint in physics_object.constraints_list:
				constraint.parent = physics_object
		
			room.physics_objects.append(physics_object)
		
		return room
		
class Room(object):
	"""Is the data structure used by the room editor to hold sprites and various game objects"""
	def __init__(self,width,height,import_file,fill_color=(255,0,255)):
	
		self.width = width
		self.height = height
		self.import_file = import_file
		self.surface = pygame.Surface((self.width,self.height))		# use a non per pixel alpha surface by default
		self.surface_rect = self.surface.get_rect()
		self.x = 0
		self.y = 0
		self.timepassed = 0		# in game this is passed in from the game class
		self.fill_color = fill_color
		
		self.ppa = False		# flag that indicates whether we are using per pixel alpha
		
		# camera shake vars
		# x
		self.default_intensity_x = 4.0
		self.angle_x = 0
		self.shake_intensity_x = 4.0
		self.shake_speed_x = 80
		self.is_shaking_x = False
		self.shake_length_x = 0.3
		
		# y
		self.default_intensity_y = 4.0
		self.angle_y = 0
		self.shake_intensity_y = 4.0
		self.shake_speed_y = 80
		self.is_shaking_y = False
		self.shake_length_y = 0.3
		
		# motion blur vars
		self.is_blur = False
		self.blur_strength = 0
		
		# import the sprite definitions this room uses
		self.module = importObjectsModule(self.import_file)
		
		self.background_objects = []
		self.mid_objects = []
		self.fore_objects = []
		self.physics_objects = []
		self.visual_code_objects = []
		
	def initPhysics(self):
		"""Gets editor items in physics_object and turns them into gameplay objects"""
		temp_objects = []
		for item in self.physics_objects:
			new_ob = item.createPhysicsObjectFrom()
			if new_ob is not None:
				temp_objects.append(new_ob)
			
		self.physics_objects = temp_objects
	
	def setBlur(self,flag,strength = 200):
		"""Sets whether to enable motion blur or not; Only applied to moving objects in the room
		param flag -> True or False ; False to disable blur; True to enable
		param strength -> the strength of the blur effect; an integer value between 0 and 255
		NOTE: Only works on per pixel alpha surfaces for now. So its a tad slow old boy"""
		
		self.is_blur = flag
		self.blur_strength = strength
	
	def draw(self,Surface):
		"""Draws the room to a Surface"""
			
			#self.surface.fill((255,0,255,10),None,BLEND_RGBA_SUB)
		if self.ppa:
			if self.is_blur:
				self.surface.fill((self.fill_color[0],self.fill_color[1],self.fill_color[2],self.blur_strength),None,BLEND_RGBA_MULT)	
				# fucking cool trail effect discovered here
				# only works for stuff that moves/changes position in the room
			else:
				self.surface.fill((0,0,0,0))
		else:
			self.surface.fill(self.fill_color)
		
		for object in self.background_objects:
			object.draw(self.surface)
		
		for object in self.mid_objects:
			object.draw(self.surface)
		
		for object in self.fore_objects:
			object.draw(self.surface)
		
		for object in self.physics_objects:
			object.draw(self.surface)
		
		for object in self.visual_code_objects:
			object.draw(self.surface)
		
		
		Surface.blit(self.surface,self.surface_rect)
	
	def handleShake(self):
		"""Is called internally in the update method to handle camera shaking"""
		if not self.is_shaking_x:
			pass
			
		else:
			self.angle_x += self.shake_speed_x
			self.shake_intensity_x -= self.shake_length_x
			
			if self.shake_intensity_x > 0:
				self.x += self.shake_intensity_x * math.sin(self.angle_x *(math.pi/180))
			
			else:
				self.is_shaking_x = False
				self.shake_intensity_x = self.default_intensity_x
		
		if not self.is_shaking_y:
			pass
			
		else:
			self.angle_y += self.shake_speed_y
			self.shake_intensity_y -= self.shake_length_y
			
			if self.shake_intensity_y > 0:
				self.y += self.shake_intensity_y * math.cos(self.angle_y *(math.pi/180))
			
			else:
				self.is_shaking_y = False
				self.shake_intensity_y = self.default_intensity_y
	
	###
	# x_params : list containing [shake_intensity_x ,shake_speed_x,shake_length_x ] or None if no x axis shake required
	# y_params : list containing [shake_intensity_y ,shake_speed_y,shake_length_y ] or None if no x axis shake required
	# shake_intensity should be a float usually between 1.0 - 10.0 is good
	# shake_speed an int or float (is practically an angle - 80 is good figure for it)
	# shake_length : is a float describing how much we reduce the intensity by(therefore it affect how long the effect spans in time)
	
	def shake(self,x_params,y_params):
		"""Shakes the room surface for a judder camera effect
		Best to use the one on steer objects cause I haven't gotten to fixing this one yet
		Yeah just steer clear of shaking the room surface for now"""
		if x_params != None:
			self.shake_intensity_x = x_params[0]
			self.shake_speed_x = x_params[1]
			self.shake_length_x = x_params[2]
			self.is_shaking_x = True
	
		if y_params != None:
			self.shake_intensity_y = y_params[0]
			self.shake_speed_y = y_params[1]
			self.shake_length_y = y_params[2]
			self.is_shaking_y = True
	
	def setColorkey(self):
		"""Use this if not in room editor to allow for see through areas in the room surface"""
		# also only use it if  you don't want to use any transparent sprites in the room
		self.surface.set_colorkey((255,0,255))
	
	def usePerPixelAlphaSurf(self):
		"""Enables a room surface that allows for transparent sprites
		This allow you to use sprites whose transparency you wish to alter
		As with most nice this things, it comes at a high computational cost
		It will abuse your framerate; Use only in times of great need"""
		self.surface = pygame.Surface((self.width,self.height),SRCALPHA)
		self.surface_rect = self.surface.get_rect()
		self.ppa = True
		
	def updatePosition(self,timepassed):
		"""Only call this externally in the room editor"""
		self.surface_rect.x = self.x
		self.surface_rect.y = self.y
		
		for object in self.background_objects:
			object.updatePosition(timepassed)
		
		for object in self.mid_objects:
			object.updatePosition(timepassed)
		
		for object in self.fore_objects:
			object.updatePosition(timepassed)
		
		for object in self.physics_objects:
			object.updatePosition(timepassed)
		
		for object in self.visual_code_objects:
			object.updatePosition(timepassed)
		
		
	def update(self,timepassed):
		
		self.handleShake()
		
		self.surface_rect.x = self.x
		self.surface_rect.y = self.y
		
		for object in self.background_objects:
			object.update(timepassed)
		
		for object in self.mid_objects:
			object.update(timepassed)
		
		for object in self.fore_objects:
			object.update(timepassed)

		for object in self.physics_objects:
			object.update(timepassed)
