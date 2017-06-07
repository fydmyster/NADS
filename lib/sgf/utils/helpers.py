import math,sys

class AnimManager(object):
	"""Outputs indices that relate to animations on sprite sheets as a helper to Sprites"""
	def __init__(self,anim_list,fps = 12):
		"""Initialises the manager with the correct references"""
		# param: anim_list - a list with each item referring to an animation sheet
		# each item should be an integer indicating the number of frames in each animation
		self.anim_started = False
		self.cur_anim_frame = 0
		self.cur_anim_index = 0
		self.loops_left = None
		self.anim_max_frames = anim_list
		self.fps = fps
		self.update_time = 1000/self.fps
		self.acc_time = 0
		self.infiloop = False
		self.reverse = False
	
	def setFps(self,fps):
		"""Sets the speed at which hte animation plays"""
		self.fps = fps
		self.update_time = 1000/self.fps
		
	def play(self, anim_index, timepassed, reverse = False):
		"""Simulates playing an animation indefinitely you stop running this function"""
		if self.cur_anim_index != anim_index or self.cur_anim_index == None:
			# current_imagelist has changed
			# reset self.frame
			self.cur_anim_frame = 0 
			self.acc_time = 0
		
		# set current_imagelist to the current animation
		self.cur_anim_index = anim_index
		
		self.acc_time += timepassed
		
		if self.acc_time > self.update_time:
			self.acc_time = 0
			# go to next frame
			if not reverse:
				self.cur_anim_frame = (self.cur_anim_frame + 1) % self.anim_max_frames[self.cur_anim_index]
			else:
				self.cur_anim_frame = (self.cur_anim_frame - 1) % self.anim_max_frames[self.cur_anim_index]
				
	def playRepeat(self,anim_index,loops = 1,reverse = False):
		"""Plays an animation a set number of times"""
		if not self.anim_started:
			self.loops_left = loops
			self.anim_started = True
			self.reverse = reverse
			if loops < 0:
				# loop infinitely
				self.infiloop = True
			else:
				self.infiloop = False
			
		
		if self.cur_anim_index != anim_index or self.cur_anim_index == None:
			# current_imagelist has changed
			# reset self.frame
			self.cur_anim_frame = 0 
			self.acc_time = 0
			
		# set current_imagelist to the current animation
		self.cur_anim_index = anim_index
	
	def stop(self):
		"""Explicitly stops any infinitely looping animations"""
		self.anim_started = 0
		self.cur_anim_frame = 0 
		self.acc_time = 0
		self.infiloop = False
		
	def update(self,timepassed):
		"""Handles looping animations"""
		
		if self.anim_started:
			self.acc_time += timepassed
		
			if self.acc_time > self.update_time:
				self.acc_time = 0
				# go to next frame
				if not self.reverse:
					self.cur_anim_frame = (self.cur_anim_frame + 1) % self.anim_max_frames[self.cur_anim_index]
				else:
					self.cur_anim_frame = (self.cur_anim_frame - 1) % self.anim_max_frames[self.cur_anim_index]
					
				if self.cur_anim_frame == 0:
					# then we've completed a loop
					self.loops_left -= 1
				
				if not self.infiloop:
					if self.loops_left < 1:
						self.anim_started = False
						self.loops_left = None
				
	def getFrame(self):
		"""Returns the frame index of the current animation at anim_index"""
		# returns a tuple of 3 elements : [0] the index pointing to the last played animation
		# [1] the current frame the manager is relaying
		# [2] a flag indicating whether a repeating anim is currently playing
		return (self.cur_anim_index,self.cur_anim_frame,self.anim_started)