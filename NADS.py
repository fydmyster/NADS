import os.path,sys
#import getpath			# have to use wildcard or else fullpath doesnt import into namespace
from getpath import*

#abs_dir = os.path.abspath(__file__)
abs_dir = fullpath

cur_dir = os.path.split(abs_dir)[0]
libdir = os.path.join(cur_dir,"lib")

#print libdir
sys.path.append(libdir)

import main

