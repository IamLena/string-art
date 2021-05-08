import numpy as np
from PIL import Image, ImageDraw

image_path_in = 'pics/portrait.jpg'
image_path_out = 'pics/out_portrait.jpg'

Rc = 30			# canvas radius in cm
t = 0.1			# thread weight in cm
m = 200			# number of pins
d_m = 0.2		# pin diameter
n = 4000		# number of executed connections
L_min = 5		# min pin to be connected, conn min length = 1 if all connections needed

Rcp = int(Rc / t)					# canvas radius in pixels
Z = 2 * Rcp							# number of pixels in diameter (resolution)
a = 360 / m							# angle step for pins in degrees
N = 2 * m * (m - 2 * L_min + 1)		# number of all possible connections

assert(Rc > 0)
assert(t > 0)
assert (m > 0)
assert(d_m > 0)
assert(0 <= n <= N)
assert(0 <= L_min <= m/2)

pins = np.zeros((m, 2), dtype='int16')
conns = np.packbits(np.zeros((N), dtype='bool'))
img = np.zeros((Z, Z), dtype='int8')
# res[Z][Z]
# err[Z][Z]

def set_pin_coords(Z, m, a, pins):
	angle = 0
	for pin in range(m):
		pins[pin] = np.array([np.floor(Z/2 + Z/2 * np.cos(np.radians(angle))), np.floor(Z/2 + Z/2 * np.sin(np.radians(angle)))])
		angle += a

def image_parse(img, image_path_in, image_path_out, Z):
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

	# restore matching resolution
	image = image.resize((Z, Z), Image.ANTIALIAS)

	# circle crop
	circlecrop = Image.new('L', [Z, Z], 255)
	circle = ImageDraw.Draw(circlecrop)
	circle.pieslice([0, 0, Z, Z], 0, 360, fill=0)
	npcrop = np.array(circlecrop)
	img = np.asarray(image).copy()
	img[npcrop == 255] = 255

	#save
	gr_im = Image.fromarray(img).save(image_path_out)


set_pin_coords(Z, m, a, pins)
image_parse(img, image_path, Z)


print("pins: ", pins.nbytes, " bytes")
print("conns: ", conns.nbytes, " bytes")
print("img: ", img.nbytes, " bytes")

sum = pins.nbytes + conns.nbytes + img.nbytes
print("\nsum: ", sum, " bytes")
