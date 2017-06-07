import sys,pygame,math
import sgf.utils.Vector2d as Vector2d
import gen_collision as gc
from pygame.locals import*

def checkCollideSAT(polyA,polyB):
	"""Detects a collision between 2 convex polygons using SAT"""
	
	if polyA.collision_type == "poly" and polyB.collision_type == "poly":
		axesToTest=[]
		minOverlap=100
	
		# get lh normals for all egdes
		# these are the axes we'll project onto
		for edge in polyA.edgelist:
			tempAxisA=Vector2d.Vector2(-(edge.y),edge.x)
			tempAxisA.normalize()
			axesToTest.append(tempAxisA)
	
		for edge in polyB.edgelist:
			tempAxisB=Vector2d.Vector2(-(edge.y),edge.x)
			tempAxisB.normalize()
			axesToTest.append(tempAxisB)
		
		for axis in axesToTest:
		
			min1=axis.dotProduct(polyA.pointlist[0])
			max1=min1
		
			min2=axis.dotProduct(polyB.pointlist[0])
			max2=min2
		
			for vertex in polyA.pointlist:
				projA=axis.dotProduct(vertex)
				#projDot=Vector2d.Vector2(axis.x*proj,axis.y*proj)
			
				if projA<min1:
					min1=projA
				if projA>max1:
					max1=projA
			
			for vertex in polyB.pointlist:
				projB=axis.dotProduct(vertex)
			
				if projB<min2:
					min2=projB
				if projB>max2:
					max2=projB
		
			test1=min1-max2
			test2=min2-max1
		
			if test1>0 or test2>0 :
				return (False,)
		
			test1Interval=abs(test1)
			test2Interval=abs(test2)
		
			if test1Interval<minOverlap:
				minOverlap=test1Interval
				pDirection=axis
		
			if test2Interval<minOverlap:
				minOverlap=test2Interval
				pDirection=axis
					
		return (True,minOverlap,pDirection)

	elif "circle" in (polyA.collision_type,polyB.collision_type):
		
		if polyA.collision_type == "circle":
			circle = polyA
			polygon = polyB
		else:
			circle = polyB
			polygon = polyA
			
		# get axes to test against
		axesToTest=[]
		minOverlap=100
	
		# get lh normals for all egdes
		# these are the axes we'll project onto
		for edge in polygon.edgelist:
			tempAxisA=Vector2d.Vector2(-(edge.y),edge.x)
			tempAxisA.normalize()
			axesToTest.append(tempAxisA)
		
		# find closest vertice to circle in polygon
		distances = []
		for p in polygon.pointlist:
			vec = Vector2d.Vector2.from_points((p.x,p.y),(circle.x,circle.y))
			dist = vec.get_magnitude()
			axis = [dist,vec]
			distances.append(axis)
		
		min_dist = distances[0]
		for dist,axis in distances:
			if dist < min_dist[0]:
				min_dist = (dist,axis)
		
		tempAxisB = min_dist[1]
		tempAxisB.normalize()
		axesToTest.append(tempAxisB)
		
		# calculate circles pointlist
		circle_pointslist = [Vector2d.Vector2(circle.x,circle.y),Vector2d.Vector2(circle.x,circle.y)]
		
		for axis in axesToTest:
		
			min1=axis.dotProduct(polygon.pointlist[0])
			max1=min1
		
			min2=axis.dotProduct(circle_pointslist[0])
			max2=min2
		
			for vertex in polygon.pointlist:
				projA=axis.dotProduct(vertex)
				#projDot=Vector2d.Vector2(axis.x*proj,axis.y*proj)
			
				if projA<min1:
					min1=projA
				if projA>max1:
					max1=projA
			
			for i in range(len(circle_pointslist)):
				if i == 0:
					projB = (axis.dotProduct(circle_pointslist[i])) + circle.radius
					
					if projB<min2:
						min2=projB
					if projB>max2:
						max2=projB
				
				else:
					projB = (axis.dotProduct(circle_pointslist[i])) - circle.radius
					
					if projB<min2:
						min2=projB
					if projB>max2:
						max2=projB
				
			test1=min1-max2
			test2=min2-max1
		
			if test1>0 or test2>0 :
				return (False,)
		
			test1Interval=abs(test1)
			test2Interval=abs(test2)
		
			if test1Interval<minOverlap:
				minOverlap=test1Interval
				pDirection=axis
		
			if test2Interval<minOverlap:
				minOverlap=test2Interval
				pDirection=axis
					
		return (True,minOverlap,pDirection)
	
def resolveCollisionSAT(result,shape1,shape2,resolvetype,derivative_objects=None):
	"""Resolves collision along axis of least penetration"""
	# derivative_objects is a list containing 2 items that will be indirectly affected
	# by the collision resolution
	# derivative_objects allow us to move the SPRITE; not the collision shape itself
	# the indices of derivative_objects directly relate to the shape1,shape2 arguments
	# so to assign a derivative object for shape1 only use : [object1,None]
	# so to assign a derivative object for shape2 only use : [None,object2]
	# so to assign a derivative object for both shape1 and shape2 use : [object1,object2]
	
	overlap=(math.fabs(result[1]))				#is the penetration amount
	dir=(result[2])                           #is the penetration direction
	d=shape1.center-shape2.center
	if d.dotProduct(dir) <0:
		dir=-dir
	
	# check that if we're dealing with physics based collision polygons or not
	if shape1.type == "static" and shape2.type == "static":
	
		# these are objects that are manipulated indirectly the same way as the polygons are
		if derivative_objects != None:
		
			d_object_shape1 = derivative_objects[0]
			d_object_shape2 = derivative_objects[1]
			
		else:
			d_object_shape1 = None
			d_object_shape2 = None
		
		if resolvetype=="both":
		
			dir*=(overlap * 0.5)
		
			# move second shape out the way
			shape2.x -= dir.x
			shape2.y -= dir.y
		
			if d_object_shape2 != None:
				# a derivative was given, manipulate its position
				d_object_shape2.x -= dir.x
				d_object_shape2.y -= dir.y
		
			# if moving the other shape negate the operator acting on dir
			# move both shapes
			shape1.x += dir.x
			shape1.y += dir.y
		
			if d_object_shape1 != None:
				# a derivative was given, manipulate its position
				d_object_shape1.x += dir.x
				d_object_shape1.y += dir.y
		
		elif resolvetype=="self":
		
			dir *= overlap
		
			shape1.x += dir.x
			shape1.y += dir.y
		
			if d_object_shape1 != None:
				# a derivative was given, manipulate its position
				d_object_shape1.x += dir.x
				d_object_shape1.y += dir.y
		
		elif resolvetype=="other":
		
			dir *= overlap
		
			shape2.x -= dir.x
			shape2.y -= dir.y
		
			if d_object_shape2 != None:
				# a derivative was given, manipulate its position
				d_object_shape2.x -= dir.x
				d_object_shape2.y -= dir.y
		
	elif "static" in [shape1.type,shape2.type] and "dynamic" in [shape1.type,shape2.type]:
		# a physics object collides with a static polygon
		
		if shape1.type == "dynamic":
			dyn = shape1
			stat = shape2
		else:
			dyn = shape2
			stat = shape1
		
		dir *= overlap
		
		dyn.currentParticlePos[0].x+=dir.x
		dyn.currentParticlePos[0].y+=dir.y
	
	else:
		# both shapes are dynamic physics objects
		if resolvetype=="both":
		
			# calculate combined masses
			combinedMass = shape1.deltaMass + shape2.deltaMass
			print shape1.deltaMass/combinedMass
		
			# determine how much to push each shape based on mass
			dirShape1 = dir *(overlap * (shape1.deltaMass/combinedMass))
			dirShape2 = dir *(overlap * (shape2.deltaMass/combinedMass))
		
			# move second shape out the way
			shape2.currentParticlePos[0].x-=dirShape1.x
			shape2.currentParticlePos[0].y-=dirShape1.y
		
			# if moving the other shape negate the operator acting on dir
			# move both shapes
			shape1.currentParticlePos[0].x+=dirShape2.x
			shape1.currentParticlePos[0].y+=dirShape2.y
		
		elif resolvetype=="self":
			shape1.currentParticlePos[0].x+=dir.x
			shape1.currentParticlePos[0].y+=dir.y
	
		elif resolvetype=="other":
			shape2.currentParticlePos[0].x-=dir.x
			shape2.currentParticlePos[0].y-=dir.y
	
		
class DEG45LU(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
		
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
			
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
class DEG45RU(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
		
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
	
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)

class DEG45LD(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
		
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
	
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)

class DEG45RD(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
		
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
	
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)

class DEG22LU(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w, self.h/2)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
			
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
	
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)

class DEG22RU(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w, self.h/2)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
	
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
	
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)

class DEG22LD(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w, self.h/2)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
		
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
	
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
class DEG22RD(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w, self.h/2)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
		
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
	
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)

class DEG67LU(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w/2, self.h)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
		
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
	
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)

class DEG67RU(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w/2, self.h)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
		
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
	
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.bottomleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.bottom + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)

class DEG67LD(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w/2, self.h)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
		
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
	
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topright, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.right + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.right, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
class DEG67RD(object):
	def __init__(self,param_list,x,y):
		
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the rect
		# param_list : [width,height,color]
		# width and height should be equal ideally
		# width,height are the length and the breadth of the rect area
		# color can be an RGB tuple or None ; if None the polygon is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		
		self.rect = pygame.Rect(self.x, self.y, self.w/2, self.h)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(3):
				if i==2:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
		
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
	
	def update(self,timepassed):
	
		# update rect
		self.rect.topleft = (self.x, self.y)
		
		# calculate shape center
		vector_to_center = Vector2d.Vector2.from_points(self.rect.topleft, self.rect.center)
		distance_to_center = vector_to_center.get_magnitude()
		
		# normalize vector_to_center
		vector_to_center.normalize()
		vector_to_center *= (distance_to_center/2)
		
		centerx = self.rect.left + vector_to_center.x
		centery = self.rect.top + vector_to_center.y
		
		self.center=Vector2d.Vector2(centerx,centery)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.rect.left, self.rect.top)
		self.p1 = Vector2d.Vector2(self.rect.right, self.rect.top)
		self.p2 = Vector2d.Vector2(self.rect.left, self.rect.bottom)
		self.pointlist=[]
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.position.x,self.position.y))
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)

		
class Line(object):
	def __init__(self,point1,point2):
		# @param point1 and point2 are tuples
		self.x=point1[0]
		self.y=point1[1]
		
		self.x2=point2[0]
		self.y2=point2[1]
		
		self.type = "static"
		self.collision_type = "poly"
		
		# calculate x and y distances between points for use in the update method for movement
		self.xdistance=self.x2-self.x
		self.ydistance=self.y2-self.y
		
		# points of shapes represented as vectors
		
		self.pos=Vector2d.Vector2(self.x,self.y)
		self.p1=Vector2d.Vector2(self.x2,self.y2)
		
		self.pointlist=[]
		self.pointlist.append(self.pos)
		self.pointlist.append(self.p1)
		
		
		# create edge
		self.egde=Vector2d.Vector2.from_points((self.pos.x,self.pos.y),(self.p1.x,self.p1.y))
		
		self.edgelist=[]
		self.edgelist.append(self.egde)
		
		self.ML=False
		self.MR=False
		self.MU=False
		self.MD=False
		
	def draw(self,SCREEN):
		pygame.draw.line(SCREEN,BLACK,(self.pointlist[0].x,self.pointlist[0].y),(self.pointlist[1].x,self.pointlist[1].y))
		
	
	def update(self):
	
		self.pos=Vector2d.Vector2(self.x,self.y)
		self.p1=Vector2d.Vector2(self.pos.x+self.xdistance,self.pos.y+self.ydistance)
		
		self.pointlist=[]
		self.pointlist.append(self.pos)
		self.pointlist.append(self.p1)
		
		# create edges
		self.egde=Vector2d.Vector2.from_points((self.pos.x,self.pos.y),(self.p1.x,self.p1.y))
		self.edgelist=[]
		self.edgelist.append(self.egde)
		
	def move(self):
		if self.ML:
			self.x-=1
		elif self.MR:
			self.x+=1
		elif self.MU:
			self.y-=1
		elif self.MD:
			self.y+=1

class Point(object):
	def __init__(self,point1):
		# @param point1 is an (x,y) tuple
		self.x=point1[0]
		self.y=point1[1]
		
		self.type = "static"
		self.collision_type = "poly"
		# points of shapes represented as vectors
		
		self.pos=Vector2d.Vector2(self.x,self.y)
		
		self.pointlist=[]
		self.pointlist.append(self.pos)
		
		# create edge
		self.egde=Vector2d.Vector2.from_points((self.pos.x,self.pos.y),(self.pos.x+0.0001,self.pos.y+0.0001))
		
		self.edgelist=[]
		self.edgelist.append(self.egde)
		
	def draw(self,SCREEN):
		pygame.draw.rect(SCREEN,BLACK,(self.pointlist[0].x,self.pointlist[0].y,2,2))
		
	def update(self):
		self.pos=Vector2d.Vector2(self.x,self.y)
		
		self.pointlist=[]
		self.pointlist.append(self.pos)
		
		# create edge
		self.egde=Vector2d.Vector2.from_points((self.pos.x,self.pos.y),(self.pos.x,self.pos.y))
		
		self.edgelist=[]
		self.edgelist.append(self.egde)

class CircleSAT(object):
	"""Collision rect used for SAT collision detection (can only test against polygons, not other CircleSAT objects)"""
	def __init__(self,center_point,radius=20,color = (255,0,0)):
		
		self.x, self.y = center_point
		self.collision_type = "circle"
		self.radius = radius
		self.color = color
		self.center=Vector2d.Vector2(self.x,self.y)
	
	def draw(self,Surface):
		
		pygame.draw.circle(Surface,self.color,(self.x,self.y),self.radius+1,1)
		
	def update(self):
		self.center = Vector2d.Vector2(self.x,self.y)
				
class RectSAT(object):
	def __init__(self,param_list,x,y):
		"""Collision rect used for SAT collision detection"""
		# @params x,y are the topleft position of the box
		# param_list : [width,height,color]
		# width,height are the length and the breadth of the box
		# color can be an RGB tuple or None ; if None the rect is not drawn(useful in room editor)
		
		self.imageloader_func = param_list		# imageloader_func is an alias for param_list used by room data loaders
		
		self.collision_type = "poly"
		self.type = "static"
		self.x = x
		self.y = y
		self.w = param_list[0]
		self.h = param_list[1]
		self.color = param_list[2]
		self.xw = self.w / 2
		self.yw = self.h / 2
		
		self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
		
		self.center=Vector2d.Vector2(self.x + self.xw, self.y + self.yw)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.x, self.y)	# this is the registration point of the entire shape
		self.p1 = Vector2d.Vector2(self.position.x + self.w ,self.position.y)
		self.p2 = Vector2d.Vector2(self.p1.x, self.p1.y + self.h)
		self.p3 = Vector2d.Vector2(self.p2.x - self.w, self.p2.y)
		self.pointlist = []
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		self.pointlist.append(self.p3)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.p3.x,self.p3.y))
		self.egde4=Vector2d.Vector2.from_points((self.p3.x,self.p3.y),(self.position.x,self.position.y))
		
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		self.edgelist.append(self.egde4)
		
		# create image
		self.image = pygame.Surface((self.rect.width+1,self.rect.height+1))
		self.image.set_colorkey((255,0,255))
		self.image.fill((255,0,255))
		
		# resolve points to origin
		draw_points_list = []
		
		for item in self.pointlist:
			draw_x = item.x - self.x
			draw_y = item.y - self.y
			draw_vector = Vector2d.Vector2(draw_x,draw_y)
			draw_points_list.append(draw_vector)
		
		if self.color != None:
			for i in range(4):
				if i==3:
					j=0
				else:
					j=i+1
				pygame.draw.line(self.image,self.color,(draw_points_list[i].x,draw_points_list[i].y),(draw_points_list[j].x,draw_points_list[j].y))
				i+=1
		
	def draw(self,Surface):
		
		if self.color != None:
			Surface.blit(self.image,self.rect)
		
	def update(self,timepassed):
		
		self.rect.topleft = (self.x,self.y)
		
		self.center=Vector2d.Vector2(self.x + self.xw, self.y + self.yw)
		# points of shapes represented as vectors
		
		self.position = Vector2d.Vector2(self.x, self.y)	# this is the registration point of the entire shape
		self.p1 = Vector2d.Vector2(self.position.x + self.w ,self.position.y)
		self.p2 = Vector2d.Vector2(self.p1.x, self.p1.y + self.h)
		self.p3 = Vector2d.Vector2(self.p2.x - self.w, self.p2.y)
		self.pointlist = []
		self.pointlist.append(self.position)
		self.pointlist.append(self.p1)
		self.pointlist.append(self.p2)
		self.pointlist.append(self.p3)
		
		# create edges
		self.egde1=Vector2d.Vector2.from_points((self.position.x,self.position.y),(self.p1.x,self.p1.y))
		self.egde2=Vector2d.Vector2.from_points((self.p1.x,self.p1.y),(self.p2.x,self.p2.y))
		self.egde3=Vector2d.Vector2.from_points((self.p2.x,self.p2.y),(self.p3.x,self.p3.y))
		self.egde4=Vector2d.Vector2.from_points((self.p3.x,self.p3.y),(self.position.x,self.position.y))
		
		self.edgelist=[]
		self.edgelist.append(self.egde1)
		self.edgelist.append(self.egde2)
		self.edgelist.append(self.egde3)
		self.edgelist.append(self.egde4)

def getOffendingPoints(test_object,collision_shape):
	# gets the points of test_object colliding with the collision_shape 
	# returns points as respective indices that refer to the points of currentParticlePos list
	offending_indices = []
	test_points_list = []
	index = 0
	for point in test_object.currentParticlePos:
		new_point = Point((point.x,point.y))
		test_points_list.append((new_point,index))
		index += 1
		
	for point_object,id in test_points_list:
		result = checkCollideSAT(point_object,collision_shape)
		if result[0]:
			offending_indices.append(id)
			
	return offending_indices

def getOffendingLines(test_object,collision_shape):
	# gets the points of test_object colliding with the collision_shape 
	# returns points as respective indices that refer to the points of currentParticlePos list
	offending_indices = []
	test_lines_list = []
	id = None
	
	for i in range(len(test_object.currentParticlePos)):
		
		if i < len(test_object.currentParticlePos)-2:
			p1 = test_object.currentParticlePos[i]
			p2 = test_object.currentParticlePos[i+1]
		
			new_line = Line((p1.x,p1.y),(p2.x,p2.y))
			id = (i,i+1)
			test_lines_list.append((new_line,id))
		
		elif i == len(test_object.currentParticlePos)-1:
			p1 = test_object.currentParticlePos[i]
			p2 = test_object.currentParticlePos[0]
			
			new_line = Line((p1.x,p1.y),(p2.x,p2.y))
			id = (i,0)
			test_lines_list.append((new_line,id))
		
	for line,id in test_lines_list:
		result = checkCollideSAT(line,collision_shape)
		if result[0]:
			offending_indices.append(id[0])
			offending_indices.append(id[1])
			
	return offending_indices

def getContacts(shape1,shape2):
	"""finds contact points from collision through line seg intersection"""
	if shape2.type == "dynamic":
		return
	
	shape1_lines = []
	shape2_lines = []
	
	# get physics object line segments
	for i in range(len(shape1.currentParticlePos)):
		
		if i < len(shape1.currentParticlePos)-2:
			p1 = shape1.currentParticlePos[i]
			p2 = shape1.currentParticlePos[i+1]
		
			new_line = gc.Line((p1.x,p1.y),(p2.x,p2.y))
			id = (i,i+1)
			shape1_lines.append((new_line,id))
		
		elif i == len(shape1.currentParticlePos)-1:
			p1 = shape1.currentParticlePos[i]
			p2 = shape1.currentParticlePos[0]
			
			new_line = gc.Line((p1.x,p1.y),(p2.x,p2.y))
			id = (i,0)
			shape1_lines.append((new_line,id))
	
	# get collision object lines
	for i in range(len(shape2.pointlist)):
		
		if i < len(shape2.pointlist)-2:
			p1 = shape2.pointlist[i]
			p2 = shape2.pointlist[i+1]
		
			new_line = gc.Line((p1.x,p1.y),(p2.x,p2.y))
			id = (i,i+1)
			shape2_lines.append((new_line,id))
		
		elif i == len(shape2.pointlist)-1:
			p1 = shape2.pointlist[i]
			p2 = shape2.pointlist[0]
			
			new_line = gc.Line((p1.x,p1.y),(p2.x,p2.y))
			id = (i,0)
			shape2_lines.append((new_line,id))
	
	# test shape1 lines segments for intersection against collision object
	for i in range(len(shape1_lines)):
		line = shape1_lines[i][0]
		line_id = shape1_lines[i][1]
		for col_line in shape2_lines:
			result = line.calculateIntersectPoint(line.p1,line.p2,col_line[0].p1,col_line[0].p2)
			
			if result != None:
				
				# append the particle indices along with an intersection ratio between the particles
				# calculate distance ratio
				delta_particle_vec = shape1.currentParticlePos[line_id[1]] - shape1.currentParticlePos[line_id[0]] 
				delta_particle_dist = delta_particle_vec.get_magnitude()
				contact_vec = Vector2d.Vector2(result[0],result[1])
				part_vec = contact_vec - shape1.currentParticlePos[line_id[0]]
				part_dist = part_vec.get_magnitude()
				
				ratio = part_dist/delta_particle_dist
				#print ratio
				point1_ratio = ratio
				point2_ratio = 1 - ratio
				
				#if shape1.contacts_dict[line_id[0]] == 1:
				shape1.contacts_dict[line_id[0]] = point1_ratio
				#if shape1.contacts_dict[line_id[1]] == 1:
				shape1.contacts_dict[line_id[1]] = point2_ratio
				
				return
				