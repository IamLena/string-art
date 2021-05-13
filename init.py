import numpy as np
from PIL import Image, ImageDraw, ImageTk
import math

# for printing whole nparrays
import sys
np.set_printoptions(threshold=sys.maxsize)

image_path_in = 'pics/portrait.jpg'
image_path_out = 'pics/portrait_gr.jpg'

Rc = 25			# canvas radius in cm
t = 0.1			# thread weight in cm
m = 200			# number of pins
d_m = 0.2		# pin diameter
L_min = 1		# min pin to be connected, conn min length = 1 if all connections needed

Rcp = int(Rc / t)					# canvas radius in pixels
Z = 2 * Rcp							# number of pixels in diameter (resolution)
a = 360 / m							# angle step for pins in degrees
# N = 2 * m * (m - 2 * L_min + 1)		# number of all possible connections
N = int(m * (m - 2 * L_min + 1) / 2)

n = int(N * 0.1)					# number of executed connections

assert(Rc > 0)
assert(t > 0)
assert (m > 0)
assert(d_m > 0)
assert(0 <= n <= N)
assert(0 <= L_min <= m/2)

def get_coords(angle, Z):
	x = np.floor(Z/2 + (Z - 2)/2 * np.cos(np.radians(angle)))
	y = np.floor(Z/2 + (Z - 2)/2 * np.sin(np.radians(angle)))
	return np.array([x, y], dtype='int16')

def image_parse(image_path_in, image_path_out, Z):
	# load
	image = Image.open(image_path_in)
	# square crop
	if image.size[0] < image.size[1]:
		side = image.size[0]
	else:
		side = image.size[1]
	image.crop((image.size[0] / 2, image.size[1] / 2, side, side))
	# greyscale
	image = image.convert('L')
	nparr = np.array(image)
	min = np.amin(nparr)
	max = np.amax(nparr)
	nparr = np.rint((nparr - min) / (max - min) * 255).astype(np.uint8)
	image = Image.fromarray(nparr)
	# restore matching resolution
	image = image.resize((Z, Z), Image.ANTIALIAS)
	# circle crop
	circlecrop = Image.new('L', [Z, Z], 255)
	circle = ImageDraw.Draw(circlecrop)
	circle.pieslice([1, 1, Z - 1, Z - 1], 0, 360, fill=0)
	npcrop = np.array(circlecrop)
	img = np.asarray(image).copy()
	img[npcrop == 255] = 255
	#save
	Image.fromarray(img).save(image_path_out)
	return img


pins = np.array([get_coords(a * i, Z) for i in range(m)])
print("pins: shape: ", pins.shape, " : ", pins.nbytes, " bytes")
# print(pins)

conns = np.zeros((N), dtype=np.uint8)		# 0 - not drawn, 1 - drawn, 2 - thrown away
# conns = np.random.choice(a=[0, 1, 2], size=(N), p=[0.99, 0.01])
print("conns: shape: ", conns.shape, " : ", conns.nbytes, " bytes")
# print(conns)

img = image_parse(image_path_in, image_path_out, Z)
print("img: shape: ", img.shape, " : ", img.nbytes, " bytes")
# print(img)
Image.fromarray(img).show(title="img")

res = np.full((Z, Z), 255, dtype=np.uint8)
print("res: shape: ", res.shape, " : ", res.nbytes, " bytes")
# print(res)

minerror = 255

sum = pins.nbytes + conns.nbytes + img.nbytes + res.nbytes
print("\nsum: ", sum, " bytes")

print ("maximum connection will be made: ", n)
