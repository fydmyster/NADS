
# Remember every script must know all vars its using for itself. Never rely on the vars coming in from imports
# I call 'this script self sufficiency'
# Scripts cant both import stuff from each other cyclically either. Avoid cyclic dependencies 

# this allows me to refer to anything from g_objects after I call import sgf in my main script
# as sgf.<anything from g_objects,vars,functions or classes>
from sgf.gameobjects.g_objects import*

# this allows me to refer to ButtonGrid after I call import sgf in my main script
# as sgf.<ButtonGrid>
from sgf.ui.widgets import ButtonGrid

# this allows me to refer to the module and the stuff in it after I call import sgf in my main script
# like sgf.collision.pixel_collision.<anthing in the module>
import sgf.collision.pixel_collision

# this allows me to refer to the module and the stuff in it after I call import sgf in my main script
# like sgf.gen.<anthing in the module>
import sgf.collision.gen_collision as gen


import sgf.ui.widgets