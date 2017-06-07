import sgf.gameobjects.steer_objects as steer

class Camera(object):
	"""A wrapper around a steering coordinate generator. It must track a target object that each
	game must own least one instance of"""
	def __init__(self,x,y,steer_type,target):
		
		self.x = x
		self.y = y
		self.steer_object = steer.Steerable(steer_type,(x,y),10,10)
		self.steer_object.setTarget(target)
	
	def setNewTarget(self,target):
	
		self.steer_object.setTarget(target)
	
	def update(self,timepassed=0):
		
		self.steer_object.update(0)
		self.x = self.steer_object.x
		self.y = self.steer_object.y
		
class CameraManager(object):
	"""Class that moves a rect that all gameobjects must carry a reference to in order to be drawn
	based on the camera positions this manager generates."""
	def __init__(self,origin_rect,screen_width,screen_height,min_x,max_x,min_y,max_y,object_to_track,parallax_rects_list=None):
			
		# parallax_rects_list should be a list(of arbitrary length) of tuples 
		# each tuple should contain a reference to an images surface rect and index[0]
		# - at index[1] should be a factor which is a point decimal indicating the amount we move the 
		# - surface rect at index [0] e.g a factor of 1.0 moves the rect same as the room surface ; 2.0 twice the amount
	
		self.x = 0
		self.y = 0
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.origin = origin_rect					# the surface gameobjects must carry
		self.object_to_track = object_to_track		# the object the camera follows
		self.min_x = min_x
		self.max_x = max_x
		self.min_y = min_y
		self.max_y = max_y
		self.parallax_rects_list = parallax_rects_list
		self.parallax_positions = []
		if self.parallax_rects_list is not None:
			for rect,factor in self.parallax_rects_list:
				pos = [rect.x,rect.y]
				self.parallax_positions.append(pos)
				
	def update(self):
		
		temp_x = self.origin.x
		temp_y = self.origin.y
		
		true_x = self.object_to_track.x + self.origin.x
		true_y = self.object_to_track.y + self.origin.y
		
		dx = dy = 0
		
		if true_x > self.max_x:
			# keep within screen range
			if self.origin.right > self.screen_width:
				dx = true_x - self.max_x 
				temp_x -= int(abs(dx)) 
				
			# also move parallax_rects_list if provided
			if self.parallax_rects_list != None:
				for i in range(len(self.parallax_rects_list)):
					rect,factor = self.parallax_rects_list[i]
					# get how much to move the parallax surface
					p_xdist = int(abs(dx)) * factor
						
					self.parallax_positions[i][0] -= p_xdist
				
				
		elif true_x < self.min_x:
			# keep within screen range
			if self.origin.x < 0:
				dx = true_x - self.min_x
				temp_x += int(abs(dx)) 
				
			
			# also move parallax_rects_list if provided
			if self.parallax_rects_list != None:
				for i in range(len(self.parallax_rects_list)):
					rect,factor = self.parallax_rects_list[i]
					# get how much to move the parallax surface
					p_xdist = int(abs(dx)) * factor
						
					self.parallax_positions[i][0] += p_xdist
			
				
		if true_y > self.max_y:
			# keep within screen range
			if self.origin.bottom > self.screen_height:
				dy = true_y - self.max_y
				temp_y -= int(abs(dy))
				
			
			# also move parallax_rects_list if provided
			if self.parallax_rects_list != None:
				for i in range(len(self.parallax_rects_list)):
					rect,factor = self.parallax_rects_list[i]
					# get how much to move the parallax surface
					p_ydist = int(abs(dy)) * factor
					
					self.parallax_positions[i][1] -= p_ydist
			
			
		elif true_y < self.min_y:
			# keep within screen range
			if self.origin.y < 0:
				dy = true_y - self.min_y
				temp_y += int(abs(dy))
			
			# also move parallax_rects_list if provided
			if self.parallax_rects_list != None:
				for i in range(len(self.parallax_rects_list)):
					rect,factor = self.parallax_rects_list[i]
					# get how much to move the parallax surface
					p_ydist = int(abs(dy)) * factor
					
					self.parallax_positions[i][1] += p_ydist
				
			
		self.origin.topleft = (temp_x,temp_y)
		
		if self.parallax_rects_list is not None:
			for i in range(len(self.parallax_rects_list)):
				rect,factor = self.parallax_rects_list[i]
				rect.x = self.parallax_positions[i][0]
				rect.y = self.parallax_positions[i][1]
		
		#print self.origin.right,self.origin.w
		#print self.x,self.y