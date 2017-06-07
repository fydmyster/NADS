import pygame,math
from pygame.locals import*

# constants for ease of use

LMOUSE_DOWN = 0
RMOUSE_DOWN = 2
LMOUSE_UP = 1
RMOUSE_UP = 3
LDOUBLE_CLICK = 4

# this is hacky but it allows me to use both my kind of events along with the pygame ones seamlessly
PYGAME_EVENT_TYPE = type(pygame.event.Event(USEREVENT))

MOD_KEYS = []
DEG2RAD = math.pi/180