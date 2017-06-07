from OpenGL.GL import*
import math
from sgf.const import*

def drawQuad(x=0,y=0,w=32,h=32,color1=(0.0,0.0,1.0,1.0),color2=(1.0,0.0,0.0,1.0),vert=True):
	""""Draws a quad to the display. Supports gradient by defining color1 and color2"""

	hx = w/2
	hy = h/2
	
	glDisable(GL_TEXTURE_2D)
	glPushMatrix()
	glTranslatef(hx+x,+hy+y,0.0)
	
	glBegin(GL_QUADS)
	
	if vert:
		glColor4f(*color1)		# sets the alpha 
	
	if not vert:
		glColor4f(*color1)		# sets the alpha 
	
	glVertex2f(-hx,-hy)
	
	if not vert:
		glColor4f(*color2)		# sets the alpha 
	
	glVertex2f(hx,-hy)
	
	if vert:
		glColor4f(*color2)		# sets the alpha 
		
	glVertex2f(hx,hy)
	
	if not vert:
		glColor4f(*color1)		# sets the alpha 
	
	glVertex(-hx,hy)
	
	glEnd()
	glPopMatrix()
	glEnable(GL_TEXTURE_2D)

def drawCircleFill(xpos,ypos,radius,color=(1.0,1.0,0.5)):

	glDisable(GL_TEXTURE_2D)
	glPushMatrix()
	
	glTranslatef(xpos,ypos,0.0)
	glColor4f(color[0],color[1],color[2],1.0)		# sets the alpha 
	
	glBegin(GL_TRIANGLE_FAN)
	for i in range(180):
		
		x = radius * math.cos(i)
		y = radius * math.sin(i)
		
		glVertex2f(x, y)
		
		x = radius * math.cos(i+0.1)
		y = radius * math.sin(i+0.1) 
		glVertex2f(x, y)
		
		#print x+k,y-h
	glEnd()
	glEnable(GL_TEXTURE_2D)
	glPopMatrix()

def drawCircle(xpos,ypos,radius,color=(1.0,1.0,0.5)):

	glDisable(GL_TEXTURE_2D)
	glPushMatrix()
	
	glTranslatef(xpos,ypos,0.0)
	glColor4f(color[0],color[1],color[2],1.0)		# sets the alpha 
	
	glBegin(GL_LINE_LOOP)
	for i in range(360):
		
		angle =  i * DEG2RAD
		
		x = radius * math.cos(angle)
		y = radius * math.sin(angle)
		
		glVertex2f(x, y)
		
	glEnd()
	glEnable(GL_TEXTURE_2D)
	glPopMatrix()

	
def drawTexture(tex_id,x=0,y=0,w=32,h=32,alpha=1.0,size=1.0,style="both"):
	"""Draws a texture onto the display"""
	
	hx = w/2.0
	hy = h/2.0
	
	glBindTexture(GL_TEXTURE_2D,tex_id)
	glPushMatrix()
	glTranslatef(hx+x,+hy+y,0.0)
	
	if style=="hor":
		glScalef(size,1.0,1.0)
	elif style=="ver":
		glScalef(1.0,size,1.0)
	else:
		glScalef(size,size,1.0)
		
	glBegin(GL_QUADS)
	glColor4f(1.0,1.0,1.0,alpha)		# sets the alpha 
	
	glTexCoord2f(0,1)
	glVertex2f(-hx,-hy)
	glTexCoord2f(1,1)
	glVertex2f(hx,-hy)
	glTexCoord2f(1,0)
	glVertex2f(hx,hy)
	glTexCoord2f(0,0)
	glVertex(-hx,hy)
	glEnd()
	glPopMatrix()
	
def drawBlur(tex_id,x,y,w,h,
			strength=0.19,
			passes = 8,
			softness = 3,				# softness should not exceed passes
			x_displacement=0,
			y_displacement=0,
			base_scale = 1.0,
			alpha = 1.0,
			style = "hor",
			blend = 0):
	fx = x
	fy = y
	fw = w
	fh = h
	falpha = alpha
	
	(GL_ONE_MINUS_DST_ALPHA,GL_ONE_MINUS_DST_ALPHA)	
	(GL_ONE_MINUS_DST_ALPHA,GL_ONE)		
	(GL_ONE_MINUS_DST_ALPHA,GL_ONE_MINUS_SRC_ALPHA)		
	(GL_ONE,GL_ONE_MINUS_SRC_ALPHA)		 
	(GL_ONE,GL_ONE_MINUS_DST_ALPHA)		
	(GL_ONE,GL_DST_COLOR)		
	(GL_SRC_COLOR,GL_ONE)		
	
	blend_modes =[(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA),
					(GL_ONE_MINUS_DST_ALPHA,GL_ONE_MINUS_DST_ALPHA),	
					(GL_ONE_MINUS_DST_ALPHA,GL_ONE),		
					(GL_ONE_MINUS_DST_ALPHA,GL_ONE_MINUS_SRC_ALPHA),
					(GL_ONE,GL_ONE_MINUS_SRC_ALPHA),
					(GL_ONE,GL_ONE_MINUS_DST_ALPHA),
					(GL_ONE,GL_DST_COLOR),
					(GL_SRC_COLOR,GL_ONE)		
						]
	max_modes = len(blend_modes)
	
	if blend > max_modes - 1:
		blend = 0
			
	# set the specified blending function
	glBlendFunc(*blend_modes[blend])
	
	for i in range(softness,passes): 
		
		drawTexture(tex_id,fx,fy,fw,fh,(falpha/i),base_scale+(strength*i),style)
		fx += x_displacement
		fy += y_displacement
	
	glBlendFunc(*blend_modes[0])		# set default blend mode

