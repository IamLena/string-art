import numpy as np
from PIL import Image, ImageDraw, ImageTk
from tkinter import Tk, Canvas
from tkinter.ttk import Frame, Label
import concurrent.futures
import time
import math

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
	left = (image.size[0] - side) / 2
	top = (image.size[1] - side) / 2
	right = (image.size[0] + side) / 2
	bottom = (image.size[1] + side) / 2
	image = image.crop((left, top, right, bottom))
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

def find_index_by_pins(pin_1, pin_2, N, m, L_min):
	max_pins_in_line = m - 2 * L_min + 1

	if (pin_1 > pin_2):
		pin_1, pin_2 = pin_2, pin_1
	if (pin_1 < L_min):
		if (pin_2 >= pin_1 + L_min and pin_2 <= N + pin_1 - L_min + 1):
			return pin_1 * max_pins_in_line + pin_2 - L_min - pin_1
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
		return index + pin_2 - L_min - pin_1
	else:
		return -1

def find_conn_by_index(index, N, m, L_min):
	max_pins_in_line = m - 2 * L_min + 1

	if index < max_pins_in_line * L_min:
		pin_1 = index // max_pins_in_line
		pin_2 = pin_1 + L_min + (index % max_pins_in_line)
	else:
		pin_1 = L_min
		index -= max_pins_in_line * L_min
		max_pins_in_this_line = max_pins_in_line - 1
		while (index >= max_pins_in_this_line):
			index -= max_pins_in_this_line
			max_pins_in_this_line -= 1
			pin_1 += 1
		pin_2 = pin_1 + L_min + (index % max_pins_in_this_line)
	return pin_1, pin_2

def find_conn_by_index_coords(index, N, m, L_min, pins):
	conn = find_conn_by_index(index, N, m, L_min)
	pin_coords_1 = pins[int(conn[0])]
	pin_coords_2 = pins[int(conn[1])]
	return pin_coords_1, pin_coords_2

def show_any_img(root, canvas, nparr):
	w = len(nparr) / 2
	image = ImageTk.PhotoImage(Image.fromarray(nparr))
	imagesprite = canvas.create_image(w, w, image=image)
	canvas.pack()
	root.update()

def get_error(pin_1, pin_2, res, img):
	error = 0
	len_p = 0

	xk = pin_1[0]
	xn = pin_2[0]
	yk = pin_1[1]
	yn = pin_2[1]
	intensity = 255 #levels of intensity
	curInt = intensity

	dx = xk - xn
	dy = yk - yn

	# color pin_coords black
	error += int(img[yk][xk])	# res[yk][xk] -> 0
	error += int(img[yn][xn])	# res[yn][xn] -> 0
	len_p += 2

	# vertical line
	if (dx == 0):
		sy = np.sign(yk - yn)
		y = yn
		while (y != yk):
			error += int(img[y][xn])	# res[y][xn] -> 0; curInt - max
			len_p += 1
			y += sy

	# horizontal line
	elif (dy == 0):
		sx = np.sign(xk - xn)
		x = xn
		while (x != xk):
			error += int(img[yn][x])	# res[yn][x] -> 0; curInt - max
			len_p += 1
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
				error += int(img[math.floor(yi)][x])	# res -> 0
			else:
				error += np.abs(int(img[math.floor(yi)][x]) - (int(res[math.floor(yi)][x]) - curInt))
			len_p += 1

			if (curInt != intensity):
				curInt = intensity - curInt
				if res[math.floor(yi)+1][x] <= curInt:
					error += int(img[math.floor(yi)+1][x])	# res -> 0
				else:
					error += np.abs(int(img[math.floor(yi)+1][x]) - (int(res[math.floor(yi)+1][x]) - curInt))
				len_p += 1
			yi = yi + m
	# m > 1
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
				error += int(img[y][math.floor(xi)]) 	# res -> 0
			else:
				error += np.abs(int(img[y][math.floor(xi)]) - (int(res[y][math.floor(xi)]) - curInt))
			len_p += 1

			if (curInt != intensity):
				curInt = intensity - curInt
				if (res[y][math.floor(xi)+1] <= curInt):
					error += int(img[y][math.floor(xi)+1])	# res -> 0
				else:
					error += np.abs(int(img[y][math.floor(xi)+1]) - (int(res[y][math.floor(xi)+1]) - curInt))
				len_p += 1
			xi = xi + m

	error /= len_p
	return error

def try_connection(listofargs):
	conn_index = listofargs[0]
	pins = listofargs[1]
	res = listofargs[2]
	img = listofargs[3]
	N = listofargs[4]
	m = listofargs[5]
	L_min = listofargs[6]

	pin_1, pin_2 = find_conn_by_index_coords(conn_index, N, m, L_min, pins)

	new_error = get_error(pin_1, pin_2, res, img)
	return new_error, conn_index

def draw(pin_1, pin_2, res):
	xk = pin_1[0]
	xn = pin_2[0]
	yk = pin_1[1]
	yn = pin_2[1]
	intensity = 255 #levels of intensity

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

def draw_connection(conn_index, img, res,  N, m, L_min, pins):
	pins_f = find_conn_by_index(conn_index, N, m, 1)
	draw(pins[int(pins_f[0])], pins[int(pins_f[1])], res)

def draw_image(img, res, conns, pins, N, m, L_min, filename):
	root = Tk()
	w = len(img)
	canvas = Canvas(root,width=w,height=w)
	canvas.pack()

	valid_error = 127


# breaking doesn't work for some reason ???
	# j = 0
	# error_len = 1
	# while (error_len > 0):
	n = int(0.2 * N)
	for j in range(n):
		conn_index = -1
		errors = []

		filter = []
		for i in range(N):
			if (conns[i] == 0):
				filter.append([i, pins, res, img, N, m, L_min])

		filter = []
		for i in range(N):
			if (conns[i] == 0):
				filter.append([i, pins, res, img, N, m, L_min])
		if (len(filter) == 0):
			print("filter break")
			break

		with concurrent.futures.ProcessPoolExecutor() as executor:
			errors = executor.map(try_connection, filter)
			errors = list(errors)
			errors.sort()
			print("errorlen = ", len(errors))

		error_len = len(errors)

		if (error_len!= 0):
			conn_index = errors[0][1]

		if (error_len == 0):
			print('break')
			break

		if (j == 0):
			throw_count = 0
			for i in range (len(errors) - 1, 0, -1):
				if (errors[i][0] > valid_error):
					conns[errors[i][1]] = 2
					throw_count += 1
				else:
					break
			print("throwing ", throw_count)

		conns[conn_index] = 1
		print("drawing ", j, " conn # ", conn_index, " err = ", errors[0][0])
		# j += 1
		draw_connection(conn_index, img, res, N, m, L_min, pins)
		show_any_img(root, canvas, res)

	print(j, "connections are made")
	Image.fromarray(res).save(filename)

	return conns

# по удаленным можно пройтись еще раз
def remove_neigbours_count_degree(degree, conns):
	removed_conn_indexes = []
	for conn_index in range(N):
		if (conns[conn_index] == 1):
			pins = find_conn_by_index(conn_index, len(conns), len(degree), 1)
			if (pins[0] + 1 == pins[1]):
				conns[conn_index] = 0
				removed_conn_indexes.append(conn_index)
			else:
				degree[pins[0]] += 1
				degree[pins[1]] += 1
	return removed_conn_indexes

def make_circuit(degree, conns):
	odd_pins = np.where(degree % 2 == 1)[0]
	while (len(odd_pins) > 0):
		pin_start, odd_pins = odd_pins[0], odd_pins[1:]
		pin_end, odd_pins = odd_pins[0], odd_pins[1:]
		for pin in range(pin_start, pin_end):
			# connect pin to pin + 1
			# now it is in min -> max index direction
			conn_index = find_index_by_pins(pin, pin + 1, 0, len(conns), len(degree), 1)
			conns[conn_index] = 1
	return conns

def form_path(degree, conns):
	path = []
	stack = [0]
	N = len(conns)
	m = len(degree)

	while (len(stack) > 0):
		pin = stack.pop()
		while (degree[pin] > 0):
			degree[pin] -= 1
			for conn_index in range(len(conns)):
				if (conn_index == 1):
					pins = find_conn_by_index(conn_index, N, m, 1)
					if (pins[0] == pin):
						conns[conn_index] = 0
						stack.insert(0, pins[1])
					elif (pins[1] == pin):
						conns[conn_index] = 0
						stack.insert(0, pins[0])
		else:
			path.insert(0, pin)
	return path


filename_in = 'pics/Blackline.png'
filname_gr = 'pics/Blackline_gr.png'
filename_res = 'pics/Blackline_res.png'
filename_sch = 'pics/Blackline_sch.txt'


Rc = 15			# canvas radius in cm
t = 0.1			# thread weight in cm
m = 100			# number of pins
L_min = 1		# min pin to be connected, conn min length = 1 if all connections needed

Rcp = int(Rc / t)						# canvas radius in pixels
Z = 2 * Rcp								# number of pixels in diameter (resolution)
a = 360 / m								# angle step for pins in degrees
N = int(m * (m - 2 * L_min + 1) / 2)	# number of all possible connections

assert(Rc > 0)
assert(t > 0)
assert (m > 0)
assert(0 <= L_min <= m/2)

pins = np.array([get_coords(a * i, Z) for i in range(m)])
print("pins: shape: ", pins.shape, " : ", pins.nbytes, " bytes")
# print(pins)

conns = np.zeros((N), dtype=np.uint8)		# 0 - not drawn, 1 - drawn, 2 - thrown away
print("conns: shape: ", conns.shape, " : ", conns.nbytes, " bytes")
# print(conns)

img = image_parse(filename_in, filname_gr, Z)
print("img: shape: ", img.shape, " : ", img.nbytes, " bytes")
# print(img)
Image.fromarray(img).show(title="img")

res = np.full((Z, Z), 255, dtype=np.uint8)
print("res: shape: ", res.shape, " : ", res.nbytes, " bytes")
# print(res)

sum = pins.nbytes + conns.nbytes + img.nbytes + res.nbytes
print("\nsum: ", sum, " bytes")

t1 = time.perf_counter()
# root = Tk()
# w = len(img)
# canvas = Canvas(root,width=w,height=w)
# canvas.pack()

for i in range(len(conns)):
	# draw_connection(i, img, res, N, m, 1, pins)
	# show_any_img(root, canvas, res)
	# Image.fromarray(res).save(filename_res)

	res_conn = draw_image(img, res, conns, pins, N, m, L_min, filename_res)
t2 = time.perf_counter()

print(f'Finished in {t2-t1} seconds')

degree = np.zeros(m)
remove_neigbours_count_degree(degree, conns)
make_circuit(degree, conns)
path = form_path(degree, conns)

with open(filename_sch, 'w') as writer:
	for pin in path:
		writer.write(str(pin) + " ")
