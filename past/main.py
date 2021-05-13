import numpy as np
from PIL import Image, ImageDraw, ImageTk
import math
from tkinter import Tk
from tkinter.ttk import Frame, Label

# for printing whole nparrays
import sys
np.set_printoptions(threshold=sys.maxsize)

image_path_in = 'pics/portrait.jpg'
image_path_out = 'pics/portrait_out.jpg'

Rc = 30			# canvas radius in cm
t = 0.1			# thread weight in cm
m = 200			# number of pins
d_m = 0.2		# pin diameter
n = 40		# number of executed connections
L_min = 1		# min pin to be connected, conn min length = 1 if all connections needed

Rcp = int(Rc / t)					# canvas radius in pixels
Z = 2 * Rcp							# number of pixels in diameter (resolution)
a = 360 / m							# angle step for pins in degrees
N = 2 * m * (m - 2 * L_min + 1)		# number of all possible connections

n = int(N * 0.005)

assert(Rc > 0)
assert(t > 0)
assert (m > 0)
assert(d_m > 0)
assert(0 <= n <= N)
assert(0 <= L_min <= m/2)

def set_pin_coords(Z, m, a, pins):
	angle = 0
	for pin in range(m):
		pins[pin] = np.array([np.floor(Z/2 + (Z - 2)/2 * np.cos(np.radians(angle))), np.floor(Z/2 + (Z - 2)/2 * np.sin(np.radians(angle)))])
		angle += a

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

def find_conn_by_index(index):
	one_type_count = N / 4
	max_pins_in_line = m - 2 * L_min + 1

	f_type = index // one_type_count
	part_index = index % one_type_count
	if part_index < max_pins_in_line * L_min:
		pin_1 = part_index // max_pins_in_line
		pin_2 = pin_1 + L_min + (part_index % max_pins_in_line)
	else:
		pin_1 = L_min
		part_index -= max_pins_in_line * L_min
		max_pins_in_this_line = max_pins_in_line - 1
		while (part_index >= max_pins_in_this_line):
			part_index -= max_pins_in_this_line
			max_pins_in_this_line -= 1
			pin_1 += 1
		pin_2 = pin_1 + L_min + (part_index % max_pins_in_this_line)
	return([pin_1, pin_2, f_type])

def find_index_by_pins(pin_1, pin_2, type):
	one_type_count = N / 4
	max_pins_in_line = m - 2 * L_min + 1

	if (pin_1 > pin_2):
		pin_1, pin_2 = pin_2, pin_1
		if (type == 0):
			type = 2
		elif (type == 2):
			type = 0
	if (pin_1 < L_min):
		if (pin_2 >= pin_1 + L_min and pin_2 <= N + pin_1 - L_min + 1):
			one_type_index = pin_1 * max_pins_in_line + pin_2 - L_min - pin_1
			return one_type_index + one_type_count * type
		else:
			return -1
	if (pin_2 >= pin_1 + L_min and pin_2 < N):
		index = max_pins_in_line * L_min
		max_pins_in_this_line = max_pins_in_line - 1
		found_pin = L_min
		while (found_pin != pin_1):
			found_pin += 1
			index += max_pins_in_this_line
			max_pins_in_this_line -= 1
		return (index + pin_2 - L_min - pin_1) + one_type_count * type
	else:
		return -1

def draw(pin_1, pin_2, f_type, res):
	xk = pin_1[0]
	xn = pin_2[0]
	yk = pin_1[1]
	yn = pin_2[1]
	intensity = 255 #levels of intensity
	# intensity = 255
	dx = xk - xn
	dy = yk - yn

	# color pin_coords black
	res[yk][xk] = 0
	res[yn][xn] = 0

	curInt = intensity

	# vertical line
	if (dx == 0):
		sy = np.sign(yk - yn)
		y = yn
		while (y != yk):
			if (res[y][xn] <= curInt):
				res[y][xn] = 0
			else:
				res[y][xn] -= curInt
			y += sy

	# horizontal line
	elif (dy == 0):
		sx = np.sign(xk - xn)
		x = xn
		while (x != xk):
			if (res[yn][x] <= curInt):
				res[yn][x] = 0
			else:
				res[yn][x] -= curInt
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
			if res[math.floor(yi)][x] <= curInt:
				res[math.floor(yi)][x] = 0
			else:
				res[math.floor(yi)][x] -= curInt
			if (curInt != intensity):
				curInt = intensity - curInt
				if res[math.floor(yi)+1][x] <= curInt:
					res[math.floor(yi)+1][x] = 0
				else:
					res[math.floor(yi)+1][x] -= curInt
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
			if res[y][math.floor(xi)] <= curInt:
				res[y][math.floor(xi)] = 0
			else:
				res[y][math.floor(xi)] -= curInt
			if (curInt != intensity):
				curInt = intensity - curInt
				if (res[y][math.floor(xi)+1] <= curInt):
					res[y][math.floor(xi)+1] = 0
				else:
					res[y][math.floor(xi)+1] -= curInt
			xi = xi + m

# init
pins = np.zeros((m, 2), dtype='int16')
set_pin_coords(Z, m, a, pins)
print("pins: shape: ", pins.shape, " : ", pins.nbytes, " bytes")
# print(pins)

conns = np.zeros((N), dtype='bool')
# conns = np.packbits(np.zeros((N), dtype='bool'))		print(N, len(conns))
# conns = np.random.choice(a=[False, True], size=(N), p=[0.99, 0.01])
print("conns: shape: ", conns.shape, " : ", conns.nbytes, " bytes")
# print(conns)

# img = np.zeros((Z, Z), dtype=np.uint8)
img = image_parse(image_path_in, image_path_out, Z)
print("img: shape: ", img.shape, " : ", img.nbytes, " bytes")
# print(img)
Image.fromarray(img).show(title="img")

res = np.full((Z, Z), 255, dtype=np.uint8)
print("res: shape: ", res.shape, " : ", res.nbytes, " bytes")
# print(res)

err = np.subtract(img, res, dtype='int16')
print("err: shape: ", err.shape, " : ", err.nbytes, " bytes")
# print(err)
minerror = np.sum(np.abs(err))
print(minerror)

sum = pins.nbytes + conns.nbytes + img.nbytes + res.nbytes + err.nbytes
print("\nsum: ", sum, " bytes")

print ("connection will be made: ", n)

def draw_image(img, res, n, N, minerror):
	for j in range(N):
		conn_index = -1
		# print("----iter: ", j, "-----")
		oldminerror = minerror
		for i in range(N):
			copy_canvas = np.copy(res)
			f_con = find_conn_by_index(i)
			pin_1 = pins[int(f_con[0])]
			pin_2 = pins[int(f_con[1])]
			draw(pin_1, pin_2, 0, copy_canvas)
			err = np.subtract(img, copy_canvas, dtype='int16')
			new_error = np.sum(np.abs(err))
			if (new_error < minerror):
				# print("		new err: ", new_error, end="")
				# print("			MIN")
				minerror = new_error
				res_pin_1 = pin_1
				res_pin_2 = pin_2
				conn_index = i
		if conns[conn_index]:
			break
		conns[conn_index] = True
		draw(res_pin_1, res_pin_2, 0, res)
		# Image.fromarray(res).show()
		if (j > n):
			break
	print(j, "connections")
	Image.fromarray(res).save("pics/res.png")


draw_image(img, res, n, N, minerror)
