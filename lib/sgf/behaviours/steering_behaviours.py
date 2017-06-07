import pygame,sys,math,random
import sgf.utils.Vector2d as Vector2d
from pygame.locals import*

def randomBinomial():
	return random.random() - random.random()
	
def mapToRange(rotation):
	rotation %= 360.0
	if abs(rotation) > 180.0:
		if rotation < 0.0:
			rotation+= 360.0
		else:
			rotation-=360.0
	
	return rotation
	
def getNewOrientation(currentOrientation,velocity):
	if velocity.get_magnitude() > 0:
		
		return (math.atan2(-velocity.y,velocity.x)) 
		#return (math.atan2(-self.velocity.x,self.velocity.y)) * ( 180 / math.pi )
	else:
		return currentOrientation
	
class Target(object):
	def __init__(self,pos=(0.0,0.0)):
		self.position=Vector2d.Vector2(pos[0],pos[1])
		self.velocity=Vector2d.Vector2()
		self.friction=0.95
		self.acceleration=0.3
		self.orientation=0.5
		
		self.ml=False
		self.mr=False
		self.mu=False
		self.md=False
		
	def update(self):
		if self.ml:
			self.velocity.x -= self.acceleration
			self.orientation-=0.1
		if self.mr:
			self.velocity.x += self.acceleration
			self.orientation+=0.1
		if self.mu:
			self.velocity.y -= self.acceleration
		if self.md:
			self.velocity.y += self.acceleration
		
		self.velocity *= self.friction
		
		self.position += self.velocity
		
class Kinematic(object):
	def __init__(self,position,target=None):
		self.position = Vector2d.Vector2()
		self.position.x=position[0]
		self.position.y=position[1]
		
		# if no target is passed create a default placeholder one
		if target==None:
			self.target=Target()
		else:
			self.target = target
		
		self.maxSpeed=3.0
		self.orientation = 0.0
		self.velocity = Vector2d.Vector2()
		self.rotation = 0.0
		
		# movement behaviours master list
		self.movementBehaviours=[]
		
		# movement behaviours allowed for object
		self.KSeekMovement=KinematicSeek(self,self.target)
		self.KFleeMovement=KinematicFlee(self,self.target)
		self.KArriveMovement=KinematicArrive(self,self.target)
		self.KWanderMovement=KinematicWander(self)
		# dynamic ones
		self.DSeekMovement=DynamicSeek(self,self.target)
		self.DFleeMovement=DynamicFlee(self,self.target)
		self.DArriveMovement=DynamicArrive(self,self.target)
		self.DAlignMovement=DynamicAlign(self,self.target)
		self.DVelocityMatch=DynamicVelocityMatch(self,self.target)
		self.DPursueMovement=Pursue(self,self.target)
		self.DFaceMovement=Face(self,self.target)
		
		
		self.moveBehaviour=self.DArriveMovement
		
	def update(self):
		self.steering=self.moveBehaviour.getSteering()
		
		if self.steering != None:
			# this is for kinematic movement only
			self.position += self.steering.velocity
			self.orientation += self.steering.rotation
		
		self.position += self.velocity
		self.orientation += self.rotation
		
		if self.steering != None:
			self.velocity += self.steering.linear
			self.orientation += self.steering.angular
		
		if self.velocity.get_magnitude() > self.maxSpeed:
			self.velocity.normalize()
			self.velocity *= self.maxSpeed
		
	def draw(self,Surface):
		pygame.draw.circle(Surface,GREEN,(self.position.x,self.position.y),10)
	
class SteeringOutput(object):
	def __init__(self):
		self.linear = Vector2d.Vector2()
		self.angular =0.0
		self.velocity=Vector2d.Vector2()
		self.rotation=0.0
				
class KinematicSeek(object):
	def __init__(self,char,targ):
		self.type="kinematic"
		self.character=char
		self.target=targ
		self.radius = 1.0
		self.maxSpeed=2.0
		self.vel = Vector2d.Vector2()
		
	def setMaxSpeed(self,maxSpeed):
		self.maxSpeed = float(maxSpeed)
	
	def getSteering(self):
		
		# create output structure
		steering=SteeringOutput()
		
		# get the direction to the target
		steering.velocity = self.target.position - self.character.position
		
		if steering.velocity.get_magnitude() < self.radius:
			return
		
		steering.velocity.normalize()
		steering.velocity *= self.maxSpeed
		self.vel = steering.velocity
		
		# face the direction we want to move
		
		self.character.orientation = getNewOrientation(self.character.orientation,steering.velocity)
		
		# output the steering
		steering.rotation = 0
		return steering
		
class KinematicFlee(object):
	def __init__(self,char,targ):
		self.type="kinematic"
		self.character=char
		self.target=targ
		
		self.maxSpeed=1.0
	
	def setMaxSpeed(self,maxSpeed):
		self.maxSpeed = float(maxSpeed)
	
	def getSteering(self):
		
		# create output structure
		steering=SteeringOutput()
		
		# get the direction to the target
		steering.velocity = self.character.position - self.target.position
		steering.velocity.normalize()
		steering.velocity *= self.maxSpeed
		
		# face the direction we want to move
		
		self.character.orientation = getNewOrientation(self.character.orientation,steering.velocity)
		
		# output the steering
		steering.rotation = 0
		return steering

class KinematicArrive(object):
	def __init__(self,char,target):
		self.character=char
		self.target=target
		
		self.maxSpeed=4.0
		self.radius=1.0
		self.timeToTarget=15.0
		self.vel = Vector2d.Vector2()
		
	def setMaxSpeed(self,maxSpeed):
		self.maxSpeed = float(maxSpeed)
	
	def setTimeToTarget(self,timeToTarget):
		self.timeToTarget = timeToTarget
	
	def getSteering(self):
			
		# create output structure
		steering=SteeringOutput()
		
		# get direction to the target
		steering.velocity = self.target.position - self.character.position
		
		# check if we're within radius
		if steering.velocity.get_magnitude() < self.radius:
			return
			
		# get to our target in timeToTarget seconds
		steering.velocity = steering.velocity / self.timeToTarget

		# if this is too fast clip to maxSpeed
		if steering.velocity.get_magnitude() > self.maxSpeed:
			steering.velocity.normalize()
			steering.velocity *= self.maxSpeed
		
		self.vel = steering.velocity
		
		# face the direction we want to move
		self.character.orientation = getNewOrientation(self.character.orientation,steering.velocity)
		
		# output the steering
		steering.rotation=0
		
		return steering
	
class KinematicWander(object):

	def __init__(self,char):
		self.type="kinematic"
		self.character=char
		
		self.maxSpeed=0.4
		self.maxRotation=0.5
	
	def setMaxSpeed(self,maxSpeed):
		self.maxSpeed = float(maxSpeed)
	
	def getSteering(self):
		# create output structure
		steering=SteeringOutput()
		
		# get the velocity from the orientation
		orientationX = math.cos(self.character.orientation)
		orientationY = math.sin(self.character.orientation)
		orientationVector=Vector2d.Vector2(orientationX,orientationY)
		
		steering.velocity = orientationVector * self.maxSpeed

		# change our orientation randomly
		steering.rotation = randomBinomial() * self.maxRotation
		
		# output the steering
		return steering
		
class DynamicSeek(object):
	def __init__(self,char,targ):
		self.type="dynamic"
		self.character=char
		self.target=targ
		
		self.maxAcceleration=3.5
	
	def setMaxAcceleration(self,maxAcceleration):
		self.maxAcceleration = float(maxAcceleration)
	
	def getSteering(self):
		
		# create output structure
		steering=SteeringOutput()
		
		# get the direction to the target
		steering.linear = self.target.position - self.character.position
		
		# give full acceleration along this direction
		steering.linear.normalize()
		steering.linear *= self.maxAcceleration
		
		# output the steering
		steering.angular = 0
		
		return steering
	
class DynamicFlee(object):
	def __init__(self,char,targ):
		self.type="dynamic"
		self.character=char
		self.target=targ
		
		self.maxAcceleration=0.08
	
	def setMaxAcceleration(self,maxAcceleration):
		self.maxAcceleration = float(maxAcceleration)
	
	def getSteering(self):
		
		# create output structure
		steering=SteeringOutput()
		
		# get the direction to the target
		steering.linear = self.character.position - self.target.position
		
		# give full acceleration along this direction
		steering.linear.normalize()
		steering.linear *= self.maxAcceleration
		
		# output the steering
		steering.angular = 0
		
		return steering

class DynamicArrive(object):
	def __init__(self,char,target):
		self.character=char
		self.target=target
		
		self.maxSpeed=5.0
		self.maxAcceleration=3.5
		self.targetRadius=1.0
		self.slowRadius=15.0
		
		self.timeToTarget=10.0
	
	def setMaxAcceleration(self,maxAcceleration):
		self.maxAcceleration = float(maxAcceleration)
	
	def setMaxSpeed(self,maxSpeed):
		self.maxSpeed = float(maxSpeed)
	
	def getSteering(self):
			
		# create output structure
		steering=SteeringOutput()
		
		# get direction to the target
		direction = self.target.position - self.character.position
		distance = direction.get_magnitude()
		
		# check if we are there ; return no steering
		if distance < self.targetRadius:
			return
		
		# if we are outside the slow radius then go max speed
		if distance > self.slowRadius:
			targetSpeed = self.maxSpeed
			
		# otherwise calculate a scaled speed
		else:
			targetSpeed = self.maxSpeed * distance / self.slowRadius
		
		# the target velocity combines speed and direction
		targetVelocity = direction
		targetVelocity.normalize()
		targetVelocity *= targetSpeed
		
		# acceleration tries to get to the target velocity
		steering.linear = targetVelocity - self.character.velocity
		steering.linear = steering.linear/self.timeToTarget
		
		# check if the acceleration is too fast
		if steering.linear.get_magnitude() > self.maxAcceleration:
			steering.linear.normalize()
			steering.linear *= self.maxAcceleration
			
		# output the steering
		steering.angular = 0
		return steering

class DynamicAlign(object):
	def __init__(self,char,target):
		self.character=char
		self.target=target
		self.maxAngularAccel=0.5
		self.maxRotation=3.5
		self.targetRadius=1.0
		self.slowRadius=8.0
		self.timeToTarget=15.0
		
	def getSteering(self):
		steering = SteeringOutput()
		
		# get direction to target
		rotation = self.target.orientation - self.character.orientation
		
		# the result to (-pi,pi) interval
		rotation = mapToRange(rotation)
		rotationSize = abs(rotation)
		
		# check if we are there ; return no steering
		if rotationSize < self.targetRadius:
			return
			
		# if we're outside the slowRadius then use maxRotation
		if rotationSize > self.slowRadius:
			targetRotation = self.maxRotation
			
		# otherwise calculate a scaled rotation
		else:
			targetRotation = self.maxRotation * rotationSize/self.slowRadius
		
		# the final target rotation combines speed (already in the variable) and direction
		targetRotation *= rotation/rotationSize
		
		# acceleration tries to get to the target rotation
		steering.angular = targetRotation - self.character.rotation
		steering.angular = steering.angular / self.timeToTarget
		
		# check if acceleration is too great
		angularAccel = abs(steering.angular)
		if angularAccel > self.maxAngularAccel:
			steering.angular = steering.angular / angularAccel
			steering.angular *= self.maxAngularAccel
			
		# output the steering
		steering.linear.x,steering.linear.y=(0.0,0.0)
		return steering
		
class DynamicVelocityMatch(object):

	def __init__(self,char,target):
		self.character=char
		self.target=target
		self.maxAcceleration=0.5
		self.timeToTarget=3.5
	
	def setMaxAcceleration(self,maxAcceleration):
		self.maxAcceleration = float(maxAcceleration)
	
	def setTimeToTarget(self,timeToTarget):
		self.timeToTarget = float(timeToTarget)
	
	def getSteering(self):
		# create output structure
		steering=SteeringOutput()
		
		# acceleration tries to get to the target velocity
		steering.linear = self.target.velocity - self.character.velocity
		steering.linear = steering.linear / self.timeToTarget
		
		# check if acceleration is too fast
		if steering.linear.get_magnitude() > self.maxAcceleration:
			steering.linear.normalize()
			steering.linear *= self.maxAcceleration
			
		# output the steering
		steering.angular = 0
		return steering
		
class Pursue(DynamicArrive):
	
	def __init__(self,char,target):
		super(Pursue,self).__init__(char,target)
		self.pursuedTarget=target
		self.maxPrediction=94.5
		
	def getSteering(self):
		# claculate the target to delegate to seek
		# work out distance to target
		direction =  self.pursuedTarget.position - self.character.position
		distance = direction.get_magnitude()
		
		# work out our current speed
		speed = self.character.velocity.get_magnitude()
		
		# check if speed is too small to give a reasonable prediction time
		if speed <= distance/self.maxPrediction:
			prediction = self.maxPrediction
		# otherwise calculate prediction time
		else:
			prediction = distance/speed
			
		# put the target together
		self.target=Target()
		self.target.position=self.pursuedTarget.position
		self.target.position += self.pursuedTarget.velocity * prediction
		
		# delegate to seek
		return super(Pursue,self).getSteering()

class Face(DynamicAlign):
	
	def __init__(self,char,target):
		super(Face,self).__init__(char,target)
		self.faceTarget=target
		
		def getSteering(self):
			# calculate the target to delegate to align
			# work out the direction to target
			direction = self.faceTarget.position - self.character.position
		
			# check for a zero direction ; make no change if so
			if direction.get_magnitude() == 0:
				return
			
			# put the target together
			self.target = Target()
			self.target.position=self.faceTarget.position
			self.target.orientation = math.atan2(-direction.y,direction.x)
		
			# delegate to align
			return super(Face,self).getSteering()
