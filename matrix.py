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

Z = 2 * int(Rc / t)							# number of pixels in diameter (resolution)
a = 360 / m							# angle step for pins in degrees

assert(Rc > 0)
assert(t > 0)
assert (m > 0)

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
	Image.fromarray(img).show(title="img")
	return np.reshape(img, (Z**2,))

def connect(xk, yk, xn, yn, Z):
	i_connection = np.zeros((Z, Z), dtype=np.uint8)
	intensity = 255
	curInt = intensity

	dx = xk - xn
	dy = yk - yn

	i_connection[yk][xk] = curInt
	i_connection[yn][xn] = curInt

	# vertical line
	if (dx == 0):
		sy = np.sign(yk - yn)
		y = yn
		while (y != yk):
			i_connection[y][xn] = curInt
			y += sy

	# horizontal line
	elif (dy == 0):
		sx = np.sign(xk - xn)
		x = xn
		while (x != xk):
			i_connection[yn][x] = curInt
			x += sx

	# m < 1
	elif (abs(dy) <= abs(dx)):
		if (dx < 0):
			xk, xn = xn, xk
			yk, yn = yn, yk
			dx = -dx
			dy = -dy
		m = dy / dx

		yi = yn + m
		for x in range (xn + 1, xk, 1):
			curInt = intensity - (yi % 1) * intensity
			i_connection[math.floor(yi)][x] = curInt
			if (curInt != intensity):
				curInt = intensity - curInt
				i_connection[math.floor(yi)+1][x] = curInt
			yi = yi + m

	else:
		if (dy < 0):
			xn, xk = xk, xn
			yn, yk = yk, yn
			dy = -dy
			dx = -dx
		m = dx / dy

		xi = xn + m
		for y in range (yn + 1, yk, 1):
			curInt =  intensity - (xi % 1) * intensity
			i_connection[y][math.floor(xi)] = curInt
			if (curInt != intensity):
				curInt = intensity - curInt
				i_connection[y][math.floor(xi)+1] = curInt
			xi = xi + m

	i_connection = i_connection.reshape((Z**2, ))
	return (i_connection)


def set_conns(Z, m, a):
	N = int(m * (m - 1) / 2)
	conns = np.zeros((N, Z**2), dtype=np.uint8)
	conn_index = 0
	pins_to_connect_with = m -  1
	for pin_1 in range(m - 1):
		angle1 = pin_1 * a
		ends = pin_1 + 1 + pins_to_connect_with
		if (ends >= m):
			ends = m
		for pin_2 in range (pin_1 + 1, ends):
			angle2 = pin_2 * a
			x1 = int(np.floor(Z/2 + (Z - 2)/2 * np.cos(np.radians(angle1))))
			y1 = int(np.floor(Z/2 + (Z - 2)/2 * np.sin(np.radians(angle1))))
			x2 = int(np.floor(Z/2 + (Z - 2)/2 * np.cos(np.radians(angle2))))
			y2 = int(np.floor(Z/2 + (Z - 2)/2 * np.sin(np.radians(angle2))))
			print("connection #", conn_index)
			conns[conn_index] = connect(x1, y1, x2, y2, Z)
			conn_index += 1
	return conns

# try:
conns = np.load("connections.npy")
# except:
# 	conns = set_conns(Z, m, a)
# 	np.save("connections", conns)

print("conns: shape: ", conns.shape, " : ", conns.nbytes, " bytes")

img = image_parse(image_path_in, image_path_out, Z)
print("img: shape: ", img.shape, " : ", img.nbytes, " bytes")

res = np.full((Z**2, ), 255, dtype=np.uint8)
print("res: shape: ", res.shape, " : ", res.nbytes, " bytes")

conn_status = np.zeros((len(conns), ), dtype=np.uint8)

sum = conns.nbytes + img.nbytes + res.nbytes + conn_status.nbytes
print("\nsum: ", sum, "B = ", sum / 1024 / 1024, "MB = ", sum / 1024 / 1024 / 1024, "GB")

def draw_connection(connection, res):
	res = np.clip(res - connection, 0, 255)
	Image.fromarray(res.reshape((Z, Z))).show(title="img")

draw_connection(conns[100], res)

