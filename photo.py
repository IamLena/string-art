import numpy
import math
import tkinter
import itertools
from PIL import Image

NUM_OF_PINS = 180
DIAMETR = 60
DIAMETR_inch = DIAMETR / 2.54
RADIUS = DIAMETR / 2
ANGLE_STEP = 360 / NUM_OF_PINS
ANGLE_STEP_radians = 2 * math.pi / NUM_OF_PINS
NUM_OF_CONNECTIONS = int(2 * math.factorial(NUM_OF_PINS) / math.factorial(NUM_OF_PINS - 2))
STRING_WIDTH = 0.2
RESOLUTION = DIAMETR / STRING_WIDTH #number of pixels in diametr
CENTER_x = RESOLUTION / 2
CENTER_y = RESOLUTION / 2
RADIUS_pixels = RESOLUTION / 2
RESOLUTION_ppi = RESOLUTION / DIAMETR_inch

filepath = "IMG_20180617_202543.png"
img = Image.open(filepath).convert('LA')
size = 300, 300
new = img.resize(size, Image.ANTIALIAS)
filepath = 'grey' + filepath
new.save(filepath)

# dpi=(600,600)
