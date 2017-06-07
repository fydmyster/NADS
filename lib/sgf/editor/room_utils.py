import pygame,math,os.path
from sgf.const import*
import sgf.collision.gen_collision as gc
import sgf.utils.g_utils as utils
import sgf.gameobjects.physics_objects as phys

font = fullpath = os.path.abspath(__file__)
d = os.path.split(fullpath)[0]
e = os.path.split(d)[0]
f = os.path.split(e)[0]
g = os.path.split(f)[0]
g = os.path.join(g,"fonts")
default_font = os.path.join(g,"PressStart2P.ttf")

class Node(object):
	"""Is a vertex that indicates a particles position in the room editor"""
	def __init__(self,parent,x,y):
		self.parent = parent
		self.x = x
		self.y = y
		self.mass = utils.StrObject(1.0)
		self.draw_radius = 2
		self.over_radius = 4
		self.mouse_over = False
		self.radius = self.draw_radius
		self.picked = False
		self.color = (255,255,200)
		self.picked_color = (255,10,10)
		self.event_list = []
		self.drag = False
		self.alive = True
		self.fill = 0
		
		self.parent.nodes_list.append(self)
		
	def addEvent(self,event):
		self.event_list.append(event)
	
	def testCollision(self,mx,my):
		"""Checks if mouse collides with Node"""
		# get distance from node center
		dx = mx - self.x
		dy = my - self.y
		
		distance = math.sqrt(dx*dx + dy*dy)
		
		if distance < self.over_radius + 1:
			return True
		else:
			return False
		
	def updatePosition(self,timepassed):
		pass
	
	def handleEvents(self,mx,my):
		
		if self.testCollision(mx,my):
			self.mouse_over = True
		else:
			self.mouse_over = False

		for event in self.event_list:
			if event == LMOUSE_DOWN:
				if self.mouse_over:
					self.picked = True
					if self.parent is not None:
						self.parent.ed.picked_node = self
						self.parent.ed.mass_entry.setText(self.mass)
					
					self.drag = True
				else:
					self.picked = False
					
			if event == LMOUSE_UP:
				self.drag = False
			
			if event == RMOUSE_UP:
				if self.mouse_over:
					self.alive = False
		
		self.event_list = []
		
	def update(self,mx,my):
	
		self.handleEvents(mx,my)
		
		if self.mouse_over:
			self.radius = self.over_radius
			self.fill = 0
		else:
			self.radius = self.draw_radius
			self.fill = 1
			
	def draw(self,Surface):
		
		pygame.draw.circle(Surface,self.color,(self.x,self.y),self.radius,self.fill)
		
		if self.picked:
			pygame.draw.circle(Surface,self.picked_color,(self.x,self.y),3)
		
class Constraint(object):
	def __init__(self,parent,start_index,end_index):
		"""A constraints between 2 particles"""
		# @param length is calculated internally
		self.event_list = []
		self.parent = parent
		self.start_index = start_index
		self.end_index = end_index 
		self.alive = True
		self.stiffness = utils.StrObject(1.0)
		self.picked_color = (200,10,20)
		self.norm_color = (255,200,100)
		self.picked = False
		
		
		self.mouse_over = False
		if self.parent is not None:
			self.linepos1 = (self.parent.nodes_list[self.start_index].x,self.parent.nodes_list[self.start_index].y)
			self.linepos2 = (self.parent.nodes_list[self.end_index].x,self.parent.nodes_list[self.end_index].y)
		
		dx = self.linepos2[0] - self.linepos1[0]
		dy = self.linepos2[1] - self.linepos1[1]
		self.length = math.sqrt(dx*dx + dy*dy)
		
		self.parent.constraints_list.append(self)
		self.collision_line = gc.Line(self.linepos1,self.linepos2)
	
	def testCollision(self,mx,my):
		"""Checks if mouse collides with line constraint"""
		# create a teensie line over mouse position
		m_line1 = (mx-2,my)
		m_line2 = (mx+2,my)
		
		if self.collision_line.calculateIntersectPoint(m_line1,m_line2,self.linepos1,self.linepos2) is not None:
			return True
		else:
			return False
		
	def draw(self,Surface):
		
		# draw a line between particles
		#linepos1 = (self.parent.nodes_list[self.start_index].x,self.parent.nodes_list[self.start_index].y)
		#linepos2 = (self.parent.nodes_list[self.end_index].x,self.parent.nodes_list[self.end_index].y)
		
		if self.picked:
			pygame.draw.line(Surface,self.picked_color,self.linepos1,self.linepos2,2)
		elif self.mouse_over:
			pygame.draw.line(Surface,self.norm_color,self.linepos1,self.linepos2,3)
		else:
			pygame.draw.line(Surface,self.norm_color,self.linepos1,self.linepos2)
	
	def handleEvents(self,mx,my):
		
		if self.testCollision(mx,my):
			self.mouse_over = True
		else:
			self.mouse_over = False

		for event in self.event_list:
			if event == LMOUSE_DOWN:
				if self.mouse_over:
					self.picked = True
					if self.parent is not None:
						self.parent.ed.picked_constraint = self
						self.parent.ed.stiffness_entry.setText(self.stiffness)
					
					
				else:
					self.picked = False
					
			if event == LMOUSE_UP:
				pass
				
			if event == RMOUSE_UP:
				if self.mouse_over:
					self.alive = False
		
		self.event_list = []
		
	def update(self,mx,my):
		
		self.handleEvents(mx,my)
		
		if self.parent is not None:
			self.linepos1 = (self.parent.nodes_list[self.start_index].x,self.parent.nodes_list[self.start_index].y)
			self.linepos2 = (self.parent.nodes_list[self.end_index].x,self.parent.nodes_list[self.end_index].y)
		
		dx = self.linepos2[0] - self.linepos1[0]
		dy = self.linepos2[1] - self.linepos1[1]
		self.length = math.sqrt(dx*dx + dy*dy)
		
		
class PhysSystem(object):
	def __init__(self,parent,n_list=None,c_list=None):
		
		self.ed = parent
		
		if n_list is not None:
			self.nodes_list = n_list
		else:
			self.nodes_list = []
		
		if c_list is not None:
			self.constraints_list = c_list
		else:
			self.constraints_list = []
		
	def updatePosition(self,timepassed):
		
		for item in self.nodes_list:
			if not item.alive:
				self.nodes_list.remove(item)
	
		for item in self.constraints_list:
			if not item.alive:
				self.constraints_list.remove(item)
	
	def addEvent(self,event):
		for item in self.nodes_list:
			item.event_list.append(event)
		
		for item in self.constraints_list:
			item.event_list.append(event)
	
	def draw(self,Surface):
	
		for item in self.nodes_list:
			item.draw(Surface)
	
		for item in self.constraints_list:
			item.draw(Surface)
	
	def createPhysicsObjectFrom(self):
		"""creates a physics object from the node and constraint configuration"""
		# make particle list argument
		particle_args = []
		constraint_args = []
		
		if len(self.nodes_list) < 1:
			return
		
		for node in self.nodes_list:
			mass = float(node.mass.getVal())
			p_args = [(node.x,node.y),mass]
			particle_args.append(p_args)
			
		for constraint in self.constraints_list:
			stiffness = float(constraint.stiffness.getVal())
			c_args = [float(constraint.length),(constraint.start_index,constraint.end_index),stiffness]
			constraint_args.append(c_args)
			
		new_object = phys.PhysicsObject(particle_args,constraint_args)
		return new_object
		
class CodeObjectHolder(object):
	def __init__(self):
		self.code_objects = []
		
	def addObject(self,ob):
		self.code_objects.append(ob)
		
	def removeObject(self,ob):
		self.code_objects.remove(ob)
		
		
class CodeObject(object):
	def __init__(self,index,ID,x,y,w,h,rotation,scale,alpha):
		self.ID = ID
		self.index = index		# used for modifying this object later
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.rotation = rotation
		self.scale = scale
		self.alpha = alpha
		
class CodeObjectVisual(object):
	def __init__(self,index,ID,x,y,w,h):
		self.index = index
		self.ID = ID
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.text_color = (230,230,255)
		self.rect_color = (50,50,240)
		self.picked = False
		self.rect = pygame.Rect(self.x,self.y,self.w,self.h)
		self.font = pygame.font.SysFont(default_font,12)
		self.text_surf = self.font.render(str(self.ID),False,self.text_color)
		self.text_rect = self.text_surf.get_rect()
		self.text_rect.center = self.rect.center
		
	def updatePosition(self,timepassed):
		
		self.rect.topleft = (self.x,self.y)
		self.text_rect.center = self.rect.center
		
	def draw(self,Surface):
		
		pygame.draw.rect(Surface,self.rect_color,self.rect,2)
		Surface.blit(self.text_surf,self.text_rect)
		
		
	
		