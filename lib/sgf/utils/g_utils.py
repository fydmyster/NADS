import math,pygame,random,cPickle
from pygame.locals import*

class DataObject(object):
	"""Hold a single value ;Doesn't type cast,just returns as is;
	Behaves just like tk special vars without the type checking"""
	def __init__(self,val):
		self.val = val
		
	def getVal(self):
		return self.val
		
	def setVal(self,val):
		self.val = val

class StrObject(object):
	"""Hold a single value ; Behaves just like tk special vars without the type checking"""
	def __init__(self,val=""):
		self.val = str(val)
		
	def getVal(self):
		return str(self.val)
		
	def setVal(self,val=""):
		self.val = str(val)

class IntObject(object):
	"""Hold a single value ; Behaves just like tk special vars without the type checking"""
	def __init__(self,val=""):
		self.val = val
		
	def getVal(self):
		return int(self.val)
		
	def setVal(self,val):
		self.val = val

class FloatObject(object):
	"""Hold a single value ; Behaves just like tk special vars without the type checking"""
	def __init__(self,val=""):
		self.val = val
		
	def getVal(self):
		return float(self.val)
		
	def setVal(self,val):
		self.val = val

		
def sliceSheetAlpha(w,h,filename):
	imageList=[]
	master_image=pygame.image.load(filename).convert_alpha()
	master_w,master_h=master_image.get_size()
	
	for i in xrange(int(master_w/w)):
		imageList.append(master_image.subsurface(i*w,0,w,h))
	return imageList

def sliceSheetNorm(w,h,filename):
	imageList=[]
	master_image=pygame.image.load(filename).convert()
	master_w,master_h=master_image.get_size()
	
	for i in xrange(int(master_w/w)):
		imageList.append(master_image.subsurface(i*w,0,w,h))
	return imageList
	
def sliceSheetColKey(w,h,filename):
	imageList=[]
	master_image=pygame.image.load(filename).convert()
	master_image.set_colorkey((255,0,255))
	master_w,master_h=master_image.get_size()
	
	for i in xrange(int(master_w/w)):
		imageList.append(master_image.subsurface(i*w,0,w,h))
	return imageList

def colorLerp(color1,color2,factor):
	r1,g1,b1=color1
	r2,g2,b2=color2
	
	newR= int(r1 + (r2-r1) * factor)
	newG= int(g1 + (g2-g1) * factor)
	newB= int(b1 + (b2-b1) * factor)
	
	newColor=(newR,newG,newB)
	return newColor

def getRandColor():
	r = random.randint(0,255) 
	g = random.randint(0,255)
	b = random.randint(0,255)
	
	return (r,g,b)

def saturateColor(color,factor):
	
	max_sat = 255
	new_color = []
	
	for c in color:
		temp_c = c
		c *= factor
		c += temp_c
		if c > max_sat:
			new_color.append(int(max_sat))
		else:
			new_color.append(int(c))
	
	new_color = tuple(new_color)
	return new_color

def desaturateColor(color,factor):
	
	min_sat = 0
	new_color = []
	
	for c in color:
		temp_c = c
		c *= factor
		temp_c -= c
		if temp_c < min_sat:
			new_color.append(int(min_sat))
		else:
			new_color.append(int(temp_c))
	
	new_color = tuple(new_color)
	return new_color

	
def getTime(self,mils):
		secs=int((mils/1000)%60)
		mins=int((mils/(1000*60))%60)
		hours=int((mils/(1000*60*60))%24)
		return (hours,mins,secs)

def rotateImage(image,rect,angle):
	"""Rotate an image while keeping its center"""
	
	rot_image = pygame.transform.rotate(image,angle)
	rot_rect = rot_image.get_rect(center = rect.center)
	
	return (rot_image,rot_rect)
	
def fillGradient(surface, color, gradient, rect=None, vertical=True, forward=True):
	"""Fills a surface with a gradient pattern"""
	
	# param : color - starting color
	# param : gradient - final color
	# param : vertical - True=vertical; False=horizontal
	
	if rect is None:
		rect = surface.get_rect()
		
	x1, x2 = rect.left, rect.right
	y1, y2 = rect.top, rect.bottom
	
	if vertical:
		h = y2 - y1
	else:
		h = x2 - x1
		
	if forward:
		a,b = color,gradient
	else:
		b,a = color,gradient
		
	rate = (
			float(b[0]-a[0])/h,
			float(b[1]-a[1])/h,
			float(b[2]-a[2])/h
			)
	
	fn_line = pygame.draw.line
	
	if vertical:
		for line in range(y1,y2):
			color = (
				min(max(a[0]+(rate[0]*(line-y1)),0),255),
				min(max(a[1]+(rate[1]*(line-y1)),0),255),
				min(max(a[2]+(rate[2]*(line-y1)),0),255)
			)
			fn_line(surface,color,(x1,line),(x2,line))
			
	else:
		for col in range(x1,x2):
			color = (
				min(max(a[0]+(rate[0]*(col-x1)),0),255),
				min(max(a[1]+(rate[1]*(col-x1)),0),255),
				min(max(a[2]+(rate[2]*(col-x1)),0),255)
			)
			fn_line(surface,color,(col,y1),(col,y2))
		