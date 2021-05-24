from PIL import Image, ImageDraw
import numpy as np
import math
import time

filename_in = 'lada.jpg'
filename_gr = 'lada_gr.png'
filename_res = 'lada_res.png'
filename_sch = 'lada_sch.txt'

Rc = 30			# canvas radius in cm
t = 0.1			# thread weight in cm
m = 300			# number of pins
skip = 10		# min pin to be connected
Z = 2 * int(Rc / t)				# number of pixels in diameter (resolution)
N = int(m * (m - 2 * skip + 1) / 2)		# number of all possible connections
schema = ""				# updates in generate loop
# pins - list of pins coords
# img - input image of Z resolution
# res - output image

assert(Rc > 0)
assert(t > 0)
assert (m > 0)
assert(0 <= skip <= m/2)

def parse_image(image_path_in):
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

def show_image(img):
	Image.fromarray(img).show()

def save_image(filename, img):
	Image.fromarray(img).save(filename)

def set_cur_int(res_pixel, curInt):
	if (res_pixel <= curInt):
		return 0
	return res_pixel - curInt

def draw(res, xk, yk, xn, yn):
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

def draw_image(pins, conns):
	res = np.full((Z, Z), 255, dtype=np.uint8)
	for pin_1 in range(m):
		for pin_2 in range(pin_1 + 1, m):
			if conns[pin_1][pin_2]:
				xk = pins[pin_1][0]
				yk = pins[pin_1][1]
				xn = pins[pin_2][0]
				yn = pins[pin_2][1]
				draw(res, xk, yk, xn, yn)
	return res

def whole_error(res, img):
	diff = np.subtract(img.astype(np.int16), res.astype(np.int16))
	error = np.sum(np.abs(diff))
	return error / Z / Z

def gen_draw(res, img, xk, yk, xn, yn):
	dx = xk - xn
	dy = yk - yn
	sx = np.sign(dx)
	sy = np.sign(dy)
	dx = abs(dx)
	dy = abs(dy)
	swapFlag = 0
	if (dy > dx):
		t = dx
		dx = dy
		dy = t
		swapFlag = 1
	er = 2 * dy - dx

	x = xn
	y = yn
	for i in range (1, dx, 1):
		res[y][x] = 0
		img[y][x] = 255
		if (er >= 0):
			if not swapFlag:
				y += sy
			else:
				x += sx
			er -= 2 * dx
		if swapFlag == 1:
			y += sy
		else:
			x += sx

		er += 2 * dy

def get_error(img, res, xk, yk, xn, yn):
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
	for i in range (1, dx, 1):
		error += img[y][x]
		count += 1
		if (er >= 0):
			if not swapFlag:
				y += sy
			else:
				x += sx
			er -= 2 * dx
		if swapFlag == 1:
			y += sy
		else:
			x += sx

		er += 2 * dy
	return error / count

# best connection out of all to start with
def find_first_conn(img, res, pins):
	best_pin_1 = -1
	min_err = 255

	pin_1_index = 0
	xk = pins[pin_1_index][0]
	yk = pins[pin_1_index][1]
	pin_2_index = pin_1_index + skip
	for conn_index in range(N):
		if (conn_index % 300 == 0):
			print(conn_index, "connection passed")
		ends = m + pin_1_index - skip + 1
		if (ends >= m):
			ends = m
		if (pin_2_index == ends):
			pin_1_index += 1
			xk = pins[pin_1_index][0]
			yk = pins[pin_1_index][1]
			pin_2_index = pin_1_index + skip

		xn = pins[pin_2_index][0]
		yn = pins[pin_2_index][1]
		tmp_err = get_error(img, res, xk, yk, xn, yn)

		if (tmp_err < min_err):
			best_pin_1 = pin_1_index
			min_err = tmp_err
		pin_2_index += 1
	return best_pin_1

def find_and_draw_best_conn(img, res, pins, cur_pin, conns):
	best_pin = -1
	min_err = 255
	xk = pins[cur_pin][0]
	yk = pins[cur_pin][1]

	for pin in range(cur_pin + skip, cur_pin + m - skip):
		pin = pin % m
		xn = pins[pin][0]
		yn = pins[pin][1]
		if not conns[cur_pin][pin]:
			tmp_err = get_error(img, res, xk, yk, xn, yn)
			if (tmp_err < min_err):
				best_pin = pin
				min_err = tmp_err

	xn = pins[best_pin][0]
	yn = pins[best_pin][1]
	gen_draw(res, img, xk, yk, xn, yn)
	conns[cur_pin][best_pin] = 1
	conns[best_pin][cur_pin] = 1

	return best_pin

def generate(img, res, pins):
	global schema
	conns = np.zeros((m, m), dtype="bool")
	MAX_ITER = 4000
	print("look for best first pin")
	cur_pin = find_first_conn(img, res, pins)
	# cur_pin = 5
	print("first pin index is ", cur_pin)
	schema += str(cur_pin) + " "
	img_copy = np.copy(img)
	min_err = whole_error(draw_image(pins, conns), img_copy)

	for i in range(MAX_ITER):
		cur_pin = find_and_draw_best_conn(img, res, pins, cur_pin, conns)
		schema += str(cur_pin) + " "
		if (i % 25 == 0):
			wh_err = whole_error(draw_image(pins, conns), img_copy)
			print("conn #", i, ": error = ", wh_err)
			if wh_err < min_err:
				min_err = wh_err
			else:
				result = draw_image(pins, conns)
				print(i, " connections made")
				print("error is not getting less any more ", wh_err)
				return result
		if (i % 100 == 0):
			schema += "\n" + str(i) + " pins connected\n"
			# show_image(res)
			# show_image(img)
	result = draw_image(pins, conns)
	return result

def save_schema(filename_sch):
	results = open(filename_sch, "w")
	results.write(schema)
	results.close()

t_start = time.time()

# set pins
angles = np.linspace(0, 2*np.pi, m)
center = Z / 2
xs = center + (Z - 2)/2 * np.cos(angles)
ys = center + (Z - 2)/2 * np.sin(angles)
pins = list(map(lambda x,y: (int(x),int(y)), xs,ys))

# load input image
img = parse_image(filename_in)
show_image(img)
save_image(filename_gr, img)

# initialize res
res = np.full((Z, Z), 255, dtype=np.uint8)

# #draws just pins
# for pin in pins:
# 	x = pin[0]
# 	y = pin[1]
# 	res[y][x] = 0
# show_image(res)
# exit(0)

result = generate(img, res, pins)
show_image(result)
save_image(filename_res, result)
save_schema(filename_sch)

t_end = time.time()
print(t_end - t_start)
