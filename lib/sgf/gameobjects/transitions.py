import pygame,sys
from pygame.locals import*
from tween_objects import*

class ScrollLeftTrans(object):
	"""Scrolls current screen left with the new screen coming in from the right"""
	def __init__(self,duration,easing_function,w,h):
		"""Scroll transition effect
		param -> w,h is the top level surface width,height(practically it can be anything but this is best)
		param -> easing_function : string depicting any of the Tweenable class easing methods
		param -> duration : the length the transition takes to complete"""
		
		self.type = 'double'
		self.in_transition = True
		
		self.width = w
		self.height = h
		self.time_since_start = 0.0
		self.duration = duration
		
		# these tween_objects don't get draw, we only require their rect positions
		self.left_shutter = Tweenable((0,0),w,h,(0,0,0))
		self.right_shutter = Tweenable((0,0),w,h,(0,0,0))
		
		self.left_shutter.rect.topleft = (0,0)
		self.right_shutter.rect.topleft = (w,0)
		self.easing_function = easing_function
	
	def runTransition(self,Surface,old_surface,new_surface):
		
		clock = pygame.time.Clock()
		timepassed = 0
		while self.in_transition:
			# clear event queue
			pygame.event.get()
			
			getattr(self.left_shutter,self.easing_function)(0-self.width,0,self.duration,timepassed)
			getattr(self.right_shutter,self.easing_function)(0,0,self.duration,timepassed)
					
			if not self.left_shutter.startSet and not self.left_shutter.startSet:
				self.in_transition = False
		
				# return value to show we are done
				return 1
				
			# clear the overlay surface
			Surface.fill((0,0,0))
			
			Surface.blit(old_surface,self.left_shutter.rect)
			Surface.blit(new_surface,self.right_shutter.rect)
			
			
			# draw onto overlay
			#self.left_shutter.draw(Surface)
			#self.right_shutter.draw(Surface)
			
			pygame.display.update()
			timepassed = clock.tick(45)
	
class ScrollRightTrans(object):
	"""Scrolls current screen right with the new screen coming in from the left"""
	def __init__(self,duration,easing_function,w,h):
		"""Scroll transition effect
		param -> w,h is the top level surface width,height(practically it can be anything but this is best)
		param -> easing_function : string depicting any of the Tweenable class easing methods
		param -> duration : the length the transition takes to complete"""
		
		self.type = 'double'
		self.in_transition = True
		
		self.width = w
		self.height = h
		self.time_since_start = 0.0
		self.duration = duration
		
		# these tween_objects don't get draw, we only require their rect positions
		self.left_shutter = Tweenable((0,0),w,h,(0,0,0))
		self.right_shutter = Tweenable((0,0),w,h,(0,0,0))
		
		self.left_shutter.rect.topleft = (0-w,0)
		self.right_shutter.rect.topleft = (0,0)
		self.easing_function = easing_function
	
	def runTransition(self,Surface,old_surface,new_surface):
		
		clock = pygame.time.Clock()
		timepassed = 0
		while self.in_transition:
			# clear event queue
			pygame.event.get()
			
			getattr(self.left_shutter,self.easing_function)(0,0,self.duration,timepassed)
			getattr(self.right_shutter,self.easing_function)(self.width,0,self.duration,timepassed)
					
			if not self.left_shutter.startSet and not self.left_shutter.startSet:
				self.in_transition = False
		
				# return value to show we are done
				return 1
				
			# clear the overlay surface
			Surface.fill((0,0,0))
			
			Surface.blit(old_surface,self.right_shutter.rect)
			Surface.blit(new_surface,self.left_shutter.rect)
			
			
			# draw onto overlay
			#self.left_shutter.draw(Surface)
			#self.right_shutter.draw(Surface)
			
			pygame.display.update()
			timepassed = clock.tick(45)

	
class PixelateTrans(object):
	def __init__(self,duration,w,h):
		
		"""Pixelate transition style
		param -> duration : length of the transition in FRAMES not milliseconds"""
		
		self.type = 'double'
		self.width = w
		self.height = h
		
		self.frame = 0
		self.total = duration
		self.inc = 0
		self.in_transition = True
		
		self.clock = pygame.time.Clock()
		
	def runTransition(self,Surface,old_surface,new_surface):
		
		timepassed = 0
		while self.in_transition:
			
			# clear event queue
			pygame.event.get()
			
			self.inc += 1
			self.frame += 1
			if self.frame >= self.total:
				self.in_transition = False
				
			f = self.frame
			t = self.total
			t2 = t/2
        
			if f < t2:
				i = old_surface
				w = max(2,self.width * (t2-f) / t2)
				i = pygame.transform.scale(i,(w,self.height*w/self.width))
			else:
				f = t2-(f-t2)
				i = new_surface
				w = max(2,self.width * (t2-f) / t2)
				i = pygame.transform.scale(i,(w,self.height*w/self.width))
            
			i = pygame.transform.scale(i,(self.width,self.height))
			
			Surface.fill((0,0,0))
			Surface.blit(i,(0,0))
			pygame.display.flip()
			
			timepassed = self.clock.tick(45)
	    
class FadeInTrans(object):
	def __init__(self,color,duration,w,h):
		"""param color -> the color we fade to
		param duration -> the length of the transition in milliseconds"""
		self.color = color
		self.type = 'single'
		self.duration = duration
		self.time_since_start = 0
		self.in_transition = True
		self.alpha = 255
		self.cur_alpha = 0
		self.bg_surface = pygame.Surface((w,h))
		self.bg_rect = self.bg_surface.get_rect()
		self.bg_surface.fill(self.color)
		
		
	def runTransition(self,Surface,old_surface):
		"""Updates the transition"""
		
		timepassed = 0
		clock = pygame.time.Clock()
		while self.in_transition:
			
			# clear event queue
			pygame.event.get()
			
			self.time_since_start += timepassed
			
			ratio = self.time_since_start / float(self.duration)
			
			if ratio <= 1:
				self.cur_alpha = self.alpha * ratio
			else:
				self.in_transition = False
			
				# return value to show we are done
				return 1
				
			Surface.fill((0,0,0))
			Surface.blit(old_surface,(0,0))
			
			self.bg_surface.set_alpha(self.cur_alpha)
			
			# draw onto overlay
			Surface.blit(self.bg_surface,self.bg_rect)
			
			pygame.display.update()
			timepassed = clock.tick(45)
			
class FadeOutTrans(object):
	def __init__(self,color,duration,w,h):
		"""param color -> the color we fade to
		param duration -> the length of the transition in milliseconds"""
		self.type = 'single'
		self.color = color
		self.duration = duration
		self.time_since_start = 0
		self.in_transition = True
		self.alpha = 255
		self.cur_alpha = 0
		self.bg_surface = pygame.Surface((w,h))
		self.bg_rect = self.bg_surface.get_rect()
		self.bg_surface.fill(self.color)
		
		
	def runTransition(self,Surface,new_surface):
		"""Updates the transition"""
		
		timepassed = 0
		clock = pygame.time.Clock()
		while self.in_transition:
			
			# clear event queue
			pygame.event.get()
			
			self.time_since_start += timepassed
			
			ratio = self.time_since_start / float(self.duration)
			
			if ratio <= 1:
				neg_alpha = self.alpha * ratio
				self.cur_alpha = self.alpha - neg_alpha
			
			else:
				self.in_transition = False
			
				# return value to show we are done
				return 1
				
			Surface.fill((0,0,0))
			Surface.blit(new_surface,(0,0))
			
			self.bg_surface.set_alpha(self.cur_alpha)
			
			# draw onto overlay
			Surface.blit(self.bg_surface,self.bg_rect)
			
			pygame.display.update()
			timepassed = clock.tick(45)

class ShutterInXTrans(object):
	"""Draws a shutter closing in effect transition"""
		
	def __init__(self,color,duration,easing_function,w,h):
		"""Shutter transition effect
		param -> w,h is the top level surface width,height(practically it can be anything but this is best)
		param -> easing_function : string depicting any of the Tweenable class easing methods
		param -> duration : the length the transition takes to complete
		param -> color : the shutter color """
		self.type = 'single'
		self.in_transition = True
		self.color = color
		
		self.width = w
		self.height = h
		self.time_since_start = 0.0
		self.duration = duration
		self.left_shutter = Tweenable((0,0),w/2,h,self.color)
		self.right_shutter = Tweenable((0,0),w/2,h,self.color)
		
		self.left_shutter.rect.topright = (0,0)
		self.right_shutter.rect.topleft = (w,0)
		self.easing_function = easing_function
		
	def runTransition(self,Surface,old_surface):
		
		clock = pygame.time.Clock()
		timepassed = 0
		while self.in_transition:
			# clear event queue
			pygame.event.get()
			
			getattr(self.left_shutter,self.easing_function)(0,0,self.duration,timepassed)
			getattr(self.right_shutter,self.easing_function)(self.width/2,0,self.duration,timepassed)
					
			if not self.left_shutter.startSet and not self.left_shutter.startSet:
				self.in_transition = False
		
				# return value to show we are done
				return 1
				
			# clear the overlay surface
			Surface.fill((0,0,0))
			
			Surface.blit(old_surface,(0,0))
			
			# draw onto overlay
			self.left_shutter.draw(Surface)
			self.right_shutter.draw(Surface)
			
			pygame.display.update()
			timepassed = clock.tick(45)
		
class ShutterOutXTrans(object):
	"""Draws a shutter opening out effect transition"""
		
	def __init__(self,color,duration,easing_function,w,h):
		"""Shutter transition effect
		param -> w,h is the top level surface width,height(practically it can be anything but this is best)
		param -> easing_function : string depicting any of the Tweenable class easing methods
		param -> duration : the length the transition takes to complete
		param -> color : the shutter color """
		self.type = 'single'
		self.in_transition = True
		self.color = color
		
		self.width = w
		self.height = h
		self.time_since_start = 0.0
		self.duration = duration
		
		self.left_shutter = Tweenable((0,0),self.width/2,self.height,self.color)
		self.right_shutter = Tweenable((0,0),self.width/2,self.height,self.color)
		
		self.left_shutter.rect.topleft = (0,0)
		self.right_shutter.rect.topleft = (self.width/2,0)
		
		self.easing_function = easing_function
		
	def runTransition(self,Surface,new_surface):
		
		clock = pygame.time.Clock()
		timepassed = 0
		while self.in_transition:
			# clear event queue
			pygame.event.get()
			
			getattr(self.left_shutter,self.easing_function)(-self.left_shutter.rect.width,0,self.duration,timepassed)
			getattr(self.right_shutter,self.easing_function)(self.width,0,self.duration,timepassed)
			
			if not self.left_shutter.startSet and not self.left_shutter.startSet:
				self.in_transition = False
		
				# return value to show we are done
				return 1
				
			# clear the overlay surface
			Surface.fill((0,0,0))
			
			Surface.blit(new_surface,(0,0))
			
			# draw onto overlay
			self.left_shutter.draw(Surface)
			self.right_shutter.draw(Surface)
			
			pygame.display.update()
			timepassed = clock.tick(45)

class ShutterInYTrans(object):
	"""Draws a shutter closing in effect transition"""
		
	def __init__(self,color,duration,easing_function,w,h):
		"""Shutter transition effect
		param -> w,h is the top level surface width,height(practically it can be anything but this is best)
		param -> easing_function : string depicting any of the Tweenable class easing methods
		param -> duration : the length the transition takes to complete
		param -> color : the shutter color """
		self.type = 'single'
		self.in_transition = True
		self.color = color
		
		self.width = w
		self.height = h
		self.time_since_start = 0.0
		self.duration = duration
		
		self.top_shutter = Tweenable((0,0),self.width,self.height/2,self.color)
		self.bottom_shutter = Tweenable((0,0),self.width,self.height/2,self.color)
		
		self.top_shutter.rect.bottomleft = (0,0)
		self.bottom_shutter.rect.topleft = (0,self.height)
		
		self.easing_function = easing_function
		
	def runTransition(self,Surface,old_surface):
		
		clock = pygame.time.Clock()
		timepassed = 0
		while self.in_transition:
			# clear event queue
			pygame.event.get()
			
			getattr(self.top_shutter,self.easing_function)(0,0,self.duration,timepassed)
			getattr(self.bottom_shutter,self.easing_function)(0,self.height/2,self.duration,timepassed)
					
			if not self.top_shutter.startSet and not self.bottom_shutter.startSet:
				self.in_transition = False
		
				# return value to show we are done
				return 1
				
			# clear the overlay surface
			Surface.fill((0,0,0))
			
			Surface.blit(old_surface,(0,0))
			
			# draw onto overlay
			self.top_shutter.draw(Surface)
			self.bottom_shutter.draw(Surface)
			
			pygame.display.update()
			timepassed = clock.tick(45)
		
class ShutterOutYTrans(object):
	"""Draws a shutter closing in effect transition"""
		
	def __init__(self,color,duration,easing_function,w,h):
		"""Shutter transition effect
		param -> w,h is the top level surface width,height(practically it can be anything but this is best)
		param -> easing_function : string depicting any of the Tweenable class easing methods
		param -> duration : the length the transition takes to complete
		param -> color : the shutter color """
		self.type = 'single'
		self.in_transition = True
		self.color = color
		
		self.width = w
		self.height = h
		self.time_since_start = 0.0
		self.duration = duration
		
		self.top_shutter = Tweenable((0,0),self.width,self.height/2,self.color)
		self.bottom_shutter = Tweenable((0,0),self.width,self.height/2,self.color)
		
		self.top_shutter.rect.bottomleft = (0,self.height/2)
		self.bottom_shutter.rect.topleft = (0,self.height/2)
		
		self.easing_function = easing_function
		
	def runTransition(self,Surface,new_surface):
		
		clock = pygame.time.Clock()
		timepassed = 0
		while self.in_transition:
			# clear event queue
			pygame.event.get()
			
			getattr(self.top_shutter,self.easing_function)(0,-self.top_shutter.rect.height,self.duration,timepassed)
			getattr(self.bottom_shutter,self.easing_function)(0,self.height,self.duration,timepassed)
					
			if not self.top_shutter.startSet and not self.bottom_shutter.startSet:
				self.in_transition = False
		
				# return value to show we are done
				return 1
				
			# clear the overlay surface
			Surface.fill((0,0,0))
			
			Surface.blit(new_surface,(0,0))
			
			# draw onto overlay
			self.top_shutter.draw(Surface)
			self.bottom_shutter.draw(Surface)
			
			pygame.display.update()
			timepassed = clock.tick(45)
					
class TransitionManager(object):
	"""Does screen transitions in a more decoupled way than MasterSurface"""
	def __init__(self,main_screen,old_surface,new_surface,trans_in_object,trans_out_object,waittime = None):
		"""param old_surface -> a copy of the current surface being drawn on screen
		param new_surface -> a copy of the surface thats to be displayed after the transition
		param main_screen -> the top level pygame window surface
		param waittime -> the time in milliseconds to wait between in and out transitions or None if not required"""
		
		# TODO add a waittime between transitions # edit FIXED!
		
		self.main_screen = main_screen
		self.old_surface = old_surface
		self.new_surface = new_surface
		self.waittime = waittime
		
		self.trans_in_object = trans_in_object
		self.trans_out_object = trans_out_object
		self.alive = True		# use this to check if transition is running and terminate the instance
		
	def run(self):
		"""updates the transitions selected"""	
		if self.alive:
			if self.trans_in_object != None:
				if self.trans_in_object.type == "single":
					self.trans_in_object.runTransition(self.main_screen,self.old_surface)
				elif self.trans_in_object.type == "double":
					self.trans_in_object.runTransition(self.main_screen,self.old_surface,self.new_surface)
			
			# for some reason this effs up the frame rate when I leave the function
			if self.waittime != None:
				pygame.time.wait(self.waittime)
			
			if self.trans_out_object != None:
				self.trans_out_object.runTransition(self.main_screen,self.new_surface)
	
			self.alive = False