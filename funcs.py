from PIL import Image, ImageDraw, ImageTk
import numpy as np
import math

def log_msg(log_stream, msg):
	msg += '\n'
	log_stream.write(msg)

def log_data(log_stream, img_path, Rc, m, t, skip, if_log, if_show, Z, N):
	log_msg(log_stream, "image path: " + img_path)

	log_msg(log_stream, "canvas radius (cm): " + str(Rc))
	log_msg(log_stream, "numer of pins: " + str(m))
	log_msg(log_stream, "thread thickness (cm): " + str(t))
	log_msg(log_stream, "pins to skip in minimum connection: " + str(skip))

	log_msg(log_stream, "logging: " + str(if_log))
	log_msg(log_stream, "showing process: " + str(if_show))

	log_msg(log_stream, "resolution: " + str(Z))
	log_msg(log_stream, "number of all possible connections: " + str(N))


def show_image(img):
	Image.fromarray(img).show()

def show_tk_img(root, canvas, nparr):
	w = len(nparr) / 2
	image = ImageTk.PhotoImage(Image.fromarray(nparr))
	imagesprite = canvas.create_image(w, w, image=image)
	canvas.pack()
	root.update()

def save_image(filename, img):
	Image.fromarray(img).save(filename)

def parse_image(image_path_in, Z):
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
	img = np.asarray(image).copy().astype(np.uint8)
	img[npcrop == 255] = 255
	return img

def get_coords(pins, index):
	x = pins[index][0]
	y = pins[index][1]
	return (x, y)

def get_conn_length(x0, y0, x1, y1):
	return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

def get_whole_error(img, res):
	Z = len(img)
	return np.sum(np.abs(np.subtract(img.astype("int16"), res.astype("int16")))) / Z / Z

def brezenhem(img, xn, yn, xk, yk, draw):
	error = 0
	count = 0
	dx = xk - xn
	dy = yk - yn
	sx = np.sign(dx)
	sy = np.sign(dy)
	dx = abs(dx)
	dy = abs(dy)
	swapFlag = 0
	if (dy > dx):
		dx, dy = dy, dx
		swapFlag = 1
	er = 2 * dy - dx

	x = xn
	y = yn
	for i in range (1, dx):
		if (draw):
			img[y][x] = 255
		else:
			error += img[y][x]
			count += 1
		if (er >= 0):
			if not swapFlag:
				y += sy
			else:
				x += sx
			er -= 2 * dx
		if swapFlag:
			y += sy
		else:
			x += sx
		er += 2 * dy
	if (count):
		return error / count
	return count # trace it - happens when? if connection is real small

def set_cur_int(res_pixel, curInt):
	if (res_pixel <= curInt):
		return 0
	return res_pixel - curInt

def Wu(res, xn, yn, xk, yk):
	# levels of intensity
	intensity = 255
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
			res[y][xn] = set_cur_int(res[y][xn], curInt)
			y += sy
	# horizontal line
	elif (dy == 0):
		sx = np.sign(xk - xn)
		x = xn
		while (x != xk):
			res[yn][x] = set_cur_int(res[yn][x], curInt)
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
			res[math.floor(yi)][x] = set_cur_int(res[math.floor(yi)][x], curInt)
			if (curInt != intensity):
				curInt = intensity - curInt
				res[math.floor(yi)+1][x] = set_cur_int(res[math.floor(yi)+1][x], curInt)
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
			res[y][math.floor(xi)] = set_cur_int(res[y][math.floor(xi)], curInt)
			if (curInt != intensity):
				curInt = intensity - curInt
				res[y][math.floor(xi)+1] = set_cur_int(res[y][math.floor(xi)+1], curInt)
			xi = xi + m

def draw_connections(res, schema, pins):
	# cutting out conns info
	pins_to_connect = ""
	lines = schema.split("\n")
	for line in lines:
		if "connections made" not in line:
			pins_to_connect += line
	pins_to_connect = pins_to_connect.split(" ")
	xn, yn = get_coords(pins, int(pins_to_connect[0]))
	for pin_index in pins_to_connect[1:]:
		if pin_index != "":
			xk, yk = get_coords(pins, int(pin_index))
			Wu(res, xn, yn, xk, yk)
			xn, yn = xk, yk
	return res

def find_best_conn_from_pin(img, pins, cur_pin, skip):
	m = len(pins)
	best_pin = -1
	min_err = 255
	xk, yk = get_coords(pins, cur_pin)

	for pin in range(cur_pin + skip, cur_pin + m - skip):
		pin = pin % m
		xn, yn = get_coords(pins, pin)
		tmp_err = brezenhem(img, xn, yn, xk, yk, 0)
		if (tmp_err < min_err):
			best_pin = pin
			min_err = tmp_err
	return best_pin, min_err

def find_best_conn_from_all(img, pins, skip, if_log, log_stream):
	best_pin_1 = -1
	best_pin_2 = -1
	min_err = 255

	pin_1_index = 0
	xk, yk = get_coords(pins, pin_1_index)
	pin_2_index = pin_1_index + skip
	xn, yn = get_coords(pins, pin_2_index)

	m = len(pins)
	N = int(m * (m - 2 * skip + 1) / 2)
	for conn_index in range(N):
		if if_log:
			if (conn_index % 500 == 0):
				log_msg(log_stream, str(conn_index) + " connections passed")

		xn, yn = get_coords(pins, pin_2_index)
		tmp_err = brezenhem(img, xn, yn, xk, yk, 0)

		if (tmp_err < min_err):
			best_pin_1 = pin_1_index
			best_pin_2 = pin_2_index
			min_err = tmp_err

		ends = pin_1_index + m - skip
		if (ends >= m):
			ends = m - 1
		if (pin_2_index == ends):
			pin_1_index += 1
			xk, yk = get_coords(pins, pin_1_index)
			pin_2_index = pin_1_index + skip
		else:
			pin_2_index += 1
	brezenhem(img, xn, yn, xk, yk, 1)
	return best_pin_1, best_pin_2

def find_1st_2nd_conn(img, pins, schema, skip, if_log, log_stream):
	# find and draw best conn 1 --- 2
	best_pin_1, best_pin_2 = find_best_conn_from_all(img, pins, skip, if_log, log_stream)
	# choose 1 -> 2 -> 3 or 2 -> 1 -> 3
	next_pin_12, err_12 = find_best_conn_from_pin(img, pins, best_pin_1, skip)
	next_pin_21, err_21 = find_best_conn_from_pin(img, pins, best_pin_2, skip)

	if (err_12 < err_21):
		# 1 -> 2 -> 3
		first_pin = best_pin_1
		second_pin = best_pin_2
		third_pin = next_pin_12
	else:
		# 2 -> 1 -> 3
		first_pin = best_pin_2
		second_pin = best_pin_1
		third_pin = next_pin_21

	schema += str(first_pin) + " " + str(second_pin) + " " + str(third_pin) + " "
	x1, y1 = get_coords(pins, first_pin)
	x2, y2 = get_coords(pins, second_pin)
	x3, y3 = get_coords(pins, third_pin)
	brezenhem(img, x2, y2, x3, y3, 1)
	if if_log:
		log_msg(log_stream, "best connection is " + str(first_pin) + " --- " + str(second_pin))
		log_msg(log_stream, "next connection is " + str(second_pin) + " --- " + str(third_pin))
	add_length = get_conn_length(x1, y1, x2, y2)
	add_length += get_conn_length(x2, y2, x3, y3)
	return third_pin, schema, add_length
