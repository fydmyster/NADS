##############################################################################
# 2exe.py
##############################################################################
# Script for invoking py2exe to turn a game into an exe
##############################################################################

##############################################################################
# IMPORTS
##############################################################################
from distutils.core import setup
import py2exe
import sys
import os,os.path
import glob
import shutil
import pygame
from modulefinder import Module

fullpath = os.path.abspath(__file__)
#fullpath = os.getcwd()
maindir = os.path.split(fullpath)[0]

# change directory to lib and import the code
libdir = os.path.join(maindir,"lib")
#os.chdir(libdir)

# add a module search path	cause im importing from a different folder
sys.path.append(libdir)		# even in this mofo I have to do this so my includes of user scripts is detected


##############################################################################
# GLOBAL DATA
##############################################################################

VERSION = '1.0.1'
AUTHOR_NAME = 'Fyeidale Edmond'
AUTHOR_EMAIL = 'fienixgdev@gmail.com'
AUTHOR_URL = "www.fydmysterdev.tumblr.com"
PRODUCT_NAME = "Not Another Dungeon Shooter"
SCRIPT_MAIN = 'NADS.py'
VERSIONSTRING = PRODUCT_NAME + " ALPHA " + VERSION

PYGAMEDIR = os.path.split(pygame.base.__file__)[0]

ICONFILE = None

#all .dlls from the pygame directory will be copied to the dist dir
SDL_DLLS = glob.glob(os.path.join(PYGAMEDIR,'*.dll'))

#if true, the build directory will be deleted at the end of the build
REMOVE_BUILD_ON_EXIT = True

fullpath = os.path.abspath(__file__)
maindir = os.path.split(fullpath)[0] 


sfxdir = os.path.join(maindir,"sounds")
fontsdir = os.path.join(maindir,"fonts")
imagesdir = os.path.join(maindir,"images")

# list files I'm including
sfxdirfiles = os.listdir(sfxdir)
fontsdirfiles = os.listdir(fontsdir)
imagesdirfiles = os.listdir(imagesdir)

# make the paths fully qualified
newsfxfiles=[]
for thing in sfxdirfiles:
	nthing = os.path.join(sfxdir,thing)
	newsfxfiles.append(nthing)

newfontsfiles=[]
for thing in fontsdirfiles:
	nthing = os.path.join(fontsdir,thing)
	newfontsfiles.append(nthing)

newimagesfiles=[]
for thing in imagesdirfiles:
	nthing = os.path.join(imagesdir,thing)
	newimagesfiles.append(nthing)

# Notice that I supply fully qualified paths to extra_files
		
#Extra files to be included in the dist directory  
                  #directory #files 
extra_files = [ 		(".",["getpath.py"]),
						("sounds", newsfxfiles),
						("images", newimagesfiles),
						("fonts", newfontsfiles)
              ]
               
#list of modules to be excluded from the .exe
MODULE_EXCLUDES =[
'email',
'AppKit',
'Foundation',
'bdb',
'difflib',
'tcl',
'Tkinter',
'Tkconstants',
'curses',
'distutils',
'setuptools',
'urllib',
'urllib2',
'urlparse',
'BaseHTTPServer',
'_LWPCookieJar',
'_MozillaCookieJar',
'ftplib',
'gopherlib',
'_ssl',
'htmllib',
'httplib',
'mimetools',
'mimetypes',
'rfc822',
'tty',
'webbrowser',
'socket',
'base64',
'compiler',
'pydoc']



#print libdirfiles

# if you need to handpick module scripts uncomment the next bit then concat it to <stuff>		
'''
lib_imports = []
for i in range(len(libdirfiles)):
	if libdirfiles[i].endswith("py"):
		module = libdirfiles[i][:-3]
		lib_imports.append(module)
'''
		
# these are the modules your main script imports
# earlier I appended their location to sys.path so py2exe knows where to find them		
stuff = ['encodings',"encodings.latin_1","lib"]				# you don't have to write ".py" after the module name
INCLUDE_STUFF = stuff

##############################################################################
# OVERRIDE OF BUILDEXE
##############################################################################

#override is used to ensure the default font is included
class BuildExe(py2exe.build_exe.py2exe):
   def copy_extensions(self,extensions):
      defaultFont = os.path.join(PYGAMEDIR,pygame.font.get_default_font())
     
      extensions.append(Module("pygame.font",defaultFont))
      py2exe.build_exe.py2exe.copy_extensions(self,extensions)

##############################################################################
# EXECUTION
##############################################################################

#append 'py2exe' to the arguments to invoke py2exe
sys.argv.append("py2exe")

#if the dist directory already exists, delete it
if os.path.exists('dist/'): shutil.rmtree('dist/')

#call setup with the correct parameters
setup(
   cmdclass = {'py2exe':BuildExe},
   windows=[
             {'script': SCRIPT_MAIN,
               'other_resources': [(u"VERSIONTAG",1,VERSIONSTRING)],
               'icon_resources': [(1,"nad_ico.ico")]}],
   options = {"py2exe": {
                         "optimize": 2,
                         "includes": INCLUDE_STUFF,
                         "compressed": 1,
                         "ascii": 1,
                         "bundle_files": 2,
                         "ignores": ['tcl','AppKit','Numeric','Foundation'],
                        "excludes": MODULE_EXCLUDES} },
   name = PRODUCT_NAME,
   version = VERSION,
   data_files = extra_files,
   zipfile = None,
   author = AUTHOR_NAME,
   author_email = AUTHOR_EMAIL,
   url = AUTHOR_URL)


#clean up
if os.path.exists('dist/tcl'): shutil.rmtree('dist/tcl')

# Remove the build tree
if REMOVE_BUILD_ON_EXIT:
     shutil.rmtree('build/')

if os.path.exists('dist/tcl84.dll'): os.unlink('dist/tcl84.dll')
if os.path.exists('dist/tk84.dll'): os.unlink('dist/tk84.dll')

for f in SDL_DLLS:
    fname = os.path.basename(f)
    try:
        shutil.copyfile(f,os.path.join('dist',fname))
    except: pass