import pygame,math,sys
from pygame.locals import*
import sgf.utils.Vector2d as Vector2d

WIDTH = 200
HEIGHT = 200

class PhysicsObject(object):
	def __init__(self,particle_list,constraint_list,color=(10,0,250)):
		"""Particle system that creates rigid bodies"""
		
		# @param particle_list : a list of lists; with each inner list having the following
		# format : [(x,y),invmass] - an invmass of 0 makes the  particle immovable
		# @param constraint_list : a list containing inner lists of the format
		# : [length,(start_index,end_index),stiffness] - indices here refer to the particles which the constraint
		# forms between
		
		self.type = "dynamic"
		self.current_particle_pos = []
		self.old_particle_pos = []
		self.acc_particle_forces = []
		self.particle_masses = []
		self.collision_type = "poly"
		self.color = color
		
		self.particle_list = particle_list
		self.constraint_list = constraint_list
		
		# mass used for collision resolution
		self.delta_mass = 1.0
		self.in_contact = False
		
		self.gravity = Vector2d.Vector2(0.0,0.05)
		self.wind = Vector2d.Vector2(-0.001,0.0)
		self.timestep = 0.0
		
		for point,mass in self.particle_list:
			new_particle = Vector2d.Vector2(point[0],point[1])	# create new particle
			new_accforce = Vector2d.Vector2()					# create a force vector for the particle
			
			# append particles to appropriate lists
			self.current_particle_pos.append(new_particle)
			self.old_particle_pos.append(new_particle)
			self.acc_particle_forces.append(new_accforce)
			self.particle_masses.append(mass)
			
		self.NUM_PARTICLES = len(self.current_particle_pos)
		
	def Verlet(self):
		for i in range(self.NUM_PARTICLES):
		
			x = self.current_particle_pos[i]
			temp = x
			oldx = self.old_particle_pos[i]
			
			a = self.acc_particle_forces[i]
			
			velocity = x - oldx
			x += (velocity + a)  
			oldx = temp
			
			# update lists
			self.current_particle_pos[i] = x
			self.old_particle_pos[i] = oldx
					
	def AccumulateForces(self):
		for i in range(self.NUM_PARTICLES):
			self.acc_particle_forces[i] = self.gravity + self.wind
			
	def SatisfyConstraints(self):
		for i in range(1):
			#cube constrain
		
			for point in self.current_particle_pos:
				if point.x<0:
					point.x=0
				elif point.x>WIDTH:
					point.x=WIDTH
			
				if point.y<0:
					point.y=0
				elif point.y>HEIGHT:
					point.y=HEIGHT
			
			for i in range(len(self.constraint_list)):
				
				length,indices,stiffness = self.constraint_list[i]
				start,end = indices
				invmass1 = self.particle_masses[start]
				invmass2 = self.particle_masses[end]
				
				delta = self.current_particle_pos[end] - self.current_particle_pos[start]
				x1 = self.current_particle_pos[start]
				x2 = self.current_particle_pos[end]
		
				deltalength = math.sqrt(delta.dotProduct(delta))
				diff = (length - deltalength)/(deltalength * (invmass1+invmass2))
				diff *= stiffness
				
				x1 -= delta * invmass1 * diff
				x2 += delta * invmass2 * diff
	
				self.current_particle_pos[start] = x1
				self.current_particle_pos[end] = x2
		
	def SetState(self,wrappingFlag,mass,*args):
		pass
		
	def update(self,timepassed=0):
		self.AccumulateForces()
		self.Verlet()
		self.SatisfyConstraints()
	
	def draw(self,Surface):
		for i in range(self.NUM_PARTICLES):
			#pygame.draw.circle(Surface,self.color,(self.current_particle_pos[i].x,self.current_particle_pos[i].y),2)
		
			# will see if this is necessary later
			for constraint in self.constraint_list:
				s_i = constraint[1][0]
				e_i = constraint[1][1]
				
				
				pos1x = self.current_particle_pos[s_i].x
				pos1y = self.current_particle_pos[s_i].y
				
				
				#print "this is thre pos",pos1x,pos1y
				pos2x = self.current_particle_pos[e_i].x
				pos2y = self.current_particle_pos[e_i].y
				
				pygame.draw.aaline(Surface,self.color,(pos1x,pos1y),(pos2x,pos2y),0)

			
			
