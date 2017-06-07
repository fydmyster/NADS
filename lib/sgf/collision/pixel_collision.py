import pygame
import sgf.utils.Vector2d

def PixelPerfectCollision(obj1, obj2):
	"""Returns True if collision found ; False otherwise ; None if one of the objects is invalid type"""
	
	try:
		# create attributes
		rect1, mask1 = obj1.rect, obj1.hitmask
		rect2, mask2 = obj2.rect, obj2.hitmask
		
		# initial examination
		if rect1.colliderect(rect2) is False:
			return False
	
	except AttributeError:
		return None
		
	# get the overlapping area
	clip = rect1.clip(rect2)
	
	# find where the clip's topleft point is in both rectangles
	x1 = clip.left - rect1.left
	y1 = clip.top - rect1.top
	x2 = clip.left - rect2.left
	y2 = clip.top - rect2.top
	
	# cycle through the clip's area of hitmasks
	for x in range(clip.width):
		for y in range(clip.height):
			# returns True if neither pixel is blank
			if mask1[x1+x][y1+y] is not 0 and\
			mask2[x2+x][y2+y] is not 0:
				return True
	
	# if there was neither collision nor error 
	return False
	
def checkMaskCollision(obj1, obj2):
	"""check if two objects have collided using masks"""
	
	try:
		rect1, rect2, hm1, hm2 = obj1.rect, obj2.rect, obj1.hitmask, obj2.hitmask
		
		if rect1.colliderect(rect2) is False:
			return False
		
	except AttributeError:
		return False
		
	rect = rect1.clip(rect2)
	
	if rect.width == 0  or rect.height == 0:
		return False
		
	x1, y1 = rect.x - rect1.x, rect.y - rect1.y
	x2, y2 = rect.x - rect2.x, rect.y - rect2.y
	
	for x in xrange(rect.width):
		for y in xrange(rect.height):
			if hm1[x1+x][y1+y] and hm2[x2+x][y2+y]:
				return True
			else:
				continue
				
	return False
	
def getColorkeyHitmask(image, rect, key=None):
	"""Returns a hitmask using the image's colorkey"""
	if key == None:
		colorkey = image.get_colorkey()
	else:
		colorkey = key
		
	mask = []
	
	for x in range(rect.width):
		mask.append([])
		for y in range(rect.height):
			mask[x].append(not image.get_at((x,y)) == colorkey)
			
	return mask
	
def getAlphaHitmask(image, rect, alpha = 0):
	"""Returns a hitmask using the image's alpha"""
	
	mask = []
	
	for x in range(rect.width):
		mask.append([])
		for y in range(rect.height):
			mask[x].append(not image.get_at((x,y))[3] == alpha)
			
	return mask
	
def getFullHitmask(image, rect, alpha = 0):
	"""Returns a completely full hitmask of the entire image"""
	
	mask = []
	
	for x in range(rect.width):
		mask.append([])
		for y in range(rect.height):
			mask[x].append(True)
			
	return mask

# The pygame mask implementation functions	

def vadd(x,y):
    return [x[0]+y[0],x[1]+y[1]]

def vsub(x,y):
    return [x[0]-y[0],x[1]-y[1]]

def vdot(x,y):
    return x[0]*y[0]+x[1]*y[1]

	
def maskFromSurface_p(surface, threshold = 127):
    #return pygame.mask.from_surface(surface, threshold)

    mask = pygame.mask.Mask(surface.get_size())
    key = surface.get_colorkey()
    if key:
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                if surface.get_at((x+0.1,y+0.1)) != key:
                    mask.set_at((x,y),1)
    else:
        for y in range(surface.get_height()):
            for x in range (surface.get_width()):
                if surface.get_at((x,y))[3] > threshold:
                    mask.set_at((x,y),1)
    return mask

def collideMask_p(obj1,obj2):
		"""Test if the sprites are colliding and
		return the collision normal."""
		
		if not obj1.rect.colliderect(obj2.rect):
			return False
		
		offset = [int(x) for x in vsub(obj2.rect.topleft,obj1.rect.topleft)]
		overlap = obj1.hitmask_p.overlap_area(obj2.hitmask_p,offset)
		if overlap == 0:
			return False
		# Calculate collision normal
		nx = (obj1.hitmask_p.overlap_area(obj2.hitmask_p,(offset[0]+1,offset[1])) -
			obj1.hitmask_p.overlap_area(obj2.hitmask_p,(offset[0]-1,offset[1])))
		ny = (obj1.hitmask_p.overlap_area(obj2.hitmask_p,(offset[0],offset[1]+1)) -
			obj1.hitmask_p.overlap_area(obj2.hitmask_p,(offset[0],offset[1]-1)))
		
		#normal = Vector2d.Vector2(nx,ny)
		#normal.normalize()
		
		#return (normal.x,normal.y)
		return (nx,ny)
		
