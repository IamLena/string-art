from PIL import Image, ImageDraw, ImageTk
from tkinter import Tk, Canvas
import numpy as np
import logging
import math
from time import time
import os
import shutil

def init_log(log_file, level_code):
	logging.basicConfig(
		level=level_code,
		format='%(asctime)s : %(levelname)s : %(message)s',
		handlers=[logging.FileHandler(log_file, "w"),
		logging.StreamHandler()])

	# init_log("log.txt")
	# logging.info("this is debug msg")
	# logging.info("this is info msg")
	# logging.warning("this is warning msg")
	# logging.error("this is error msg")
	# logging.critical("this is critical msg")

def set_defaults(params):
	logging.info('setting default parameters')
	if params['R'] == -1:
		raise Exception('Canvas radius must be defined')
	if params['t'] == -1:
		raise Exception('Thread weight must be defined')
	if params['m'] == -1:
		raise Exception('Number of pins must be defined')
	if params['name'] == -1:
		raise Exception('Image path must be defined')
	if params['skip'] == -1:
		params['skip'] = 1
	if params['if_log'] == -1:
		params['if_log'] = 1
	if params['if_show'] == -1:
		params['if_show'] = 1

def check_validation(params):
	logging.info('checking validation of parameters')
	if (params['skip'] > params['m'] / 2):
		raise Exception('To much pins to skip, redefine "number of pins to skip in minimum chord" parameter')
	angle_step = 2 * np.pi / params['m']
	dist_b_pins = math.sqrt(params['R']**2 + params['R']**2 - 2 * params['R'] * params['R']  * math.cos(angle_step))
	logging.info("angle between pins equal to " + str(360 / params['m']) + " degrees; distination between pins equals to " + str(dist_b_pins) + " cm")
	if (dist_b_pins / params['t'] < 3):
		logging.warning("with this resolution, pins are too close to each other")

def load_data():
	logging.info('loading input data')
	params = {'R':-1, 't':-1, 'm':-1, 'skip':-1, 'if_log':-1, 'if_show':-1, 'max_conns':-1, "image":-1, "name":-1}
	try:
		with open("config.txt") as f:
			while True:
				line = f.readline()
				if not line:
					break
				if line[0] == '#' or line.strip() == "":
					continue
				pair = line.split('=')
				if (len(pair) != 2):
					raise Exception('Invalid line in config.txt - ' + line)
				if (pair[0].strip().lower() == 'canvas radius'):
					if (params['R'] != -1):
						logging.warning('canvas radius is defined several times, the last will be procesed')
					if (float(pair[1]) <= 0):
						raise Exception('Canvas radius should be positive number')
					params['R'] = float(pair[1])
				elif (pair[0].strip().lower() == 'thread weight'):
					if (params['t'] != -1):
						logging.warning('thread weight is defined several times, the last will be procesed')
					if (float(pair[1]) <= 0):
						raise Exception('Thread weight should be positive number')
					params['t'] = float(pair[1])
				elif (pair[0].strip().lower() == 'number of pins'):
					if (params['m'] != -1):
						logging.warning('number of pins is defined several times, the last will be procesed')
					if (int(pair[1]) <= 0):
						raise Exception('Number of pins should be positive integer')
					params['m'] = int(pair[1])
				elif (pair[0].strip().lower() == 'image'):
					params['image'] = 1
					name = pair[1].strip()
					params['image'] = Image.open(name)
					params['name'] = pair[1].strip().split('.')[0][name.rfind('/') + 1:]


				elif (pair[0].strip().lower() == 'number of pins to skip in minimum chord'):
					if (params['skip'] != -1):
						logging.warning('number of pins to skip in minimum chord is defined several times, the last will be procesed')
					if (int(pair[1]) <= 0):
						raise Exception('Number of pins to skip in minimum chord should be positive integer')
					params['skip'] = int(pair[1])
				elif (pair[0].strip().lower() == 'logging'):
					if (params['if_log'] != -1):
						logging.warning('logging is defined several times, the last will be procesed')
					if int(pair[1]) == 0 or int(pair[1]) == 1:
						params['if_log'] = int(pair[1])
					else:
						raise Exception('logging should be 0 or 1')
					if params['if_log'] == 0:
						logging.info('switching off logging')
						logging.getLogger().setLevel(logging.CRITICAL)
				elif (pair[0].strip().lower() == 'show process'):
					if (params['if_show'] != -1):
						logging.warning('show process is defined several times, the last will be procesed')
					if int(pair[1]) == 0 or int(pair[1]) == 1:
						params['if_show'] = int(pair[1])
					else:
						raise Exception('show process should be 0 or 1')
				elif (pair[0].strip().lower() == 'maximum connections to make'):
					if (params['max_conns'] != -1):
						logging.warning('maximum connections to make is defined several times, the last will be procesed')
					if (int(pair[1]) < 0):
						raise Exception('Maximum connections to make should not be be negative')
					params['max_conns'] = int(pair[1])
			set_defaults(params)
			check_validation(params)
			logging.info('loading complete')
			return params
	except FileNotFoundError:
		if params['image'] == 1:
			logging.critical("image file wasn't found")
		else:
			logging.critical("config.txt file wasn't found")
		exit(1)
	except ValueError:
		logging.critical("types or values of paramenters are invalid")
		exit(1)
	except Exception as error:
		logging.critical(str(error))
		exit(1)

def parse_image(conf_dic):
	# load
	image = conf_dic['image']
	image.save(conf_dic['name'] + "/" + conf_dic['name'] + ".png")
	Z = conf_dic['Z']
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
	# restore matching resolution
	image = image.resize((Z, Z), Image.ANTIALIAS)
	# circle crop
	# new white canvas
	circlecrop = Image.new('L', [Z, Z], 255)
	circle = ImageDraw.Draw(circlecrop)
	# set fields of 1 pixel, draw black circle
	circle.pieslice([1, 1, Z - 1, Z - 1], 0, 360, fill=0)
	npcrop = np.array(circlecrop)
	img = np.asarray(image).copy()
	# set pixels of image where circle_image is white to 255
	img[npcrop == 255] = 255
	save_image(conf_dic['name'] + "/greyscale.png", img)
	conf_dic['image'] = img

def get_whole_error(img, res):
	Z = len(img)
	return np.sum(np.abs(np.subtract(img.astype("int16"), res.astype("int16")))) / Z / Z

def get_coords(pins, index):
	x = pins[index][0]
	y = pins[index][1]
	return (x, y)

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
	return count

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

def find_best_conn_from_all(img, pins, skip):
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
		xn, yn = get_coords(pins, pin_2_index)
		tmp_err = brezenhem(img, xn, yn, xk, yk, 0)

		if (tmp_err < min_err):
			best_pin_1 = pin_1_index
			best_pin_2 = pin_2_index
			min_err = tmp_err
			logging.debug(str(conn_index) + " : " + str(best_pin_1) + " --- " + str(best_pin_2) + " conn err " + str(min_err))

		ends = pin_1_index + m - skip
		if (ends >= m):
			ends = m - 1
		if (pin_2_index == ends):
			pin_1_index += 1
			xk, yk = get_coords(pins, pin_1_index)
			pin_2_index = pin_1_index + skip
		else:
			pin_2_index += 1
	return best_pin_1, best_pin_2

def get_conn_length(x0, y0, x1, y1):
	return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

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
	if best_pin == -1:
		logging.debug("going to the neighbour")
		best_pin = cur_pin + 1
		if (best_pin == len(pins)):
			best_pin = 0
	return best_pin, min_err

def show_image(img):
	Image.fromarray(img).show()

def save_image(filename, img):
	Image.fromarray(img).save(filename)

def save_data_scheme_close(conf_dic, scheme):
	scheme.write("\n--------------------------------\n")
	scheme.write("\nresolution: " + str(conf_dic['Z']) + " pixels in diameter")
	scheme.write("\nthread length: " + str(math.ceil(conf_dic['length'] * conf_dic['t'] / 100)) + " m")
	scheme.write("\nconnections: " + str(conf_dic['conns']) + " / " + str(conf_dic['N']))
	scheme.write("\nwhole error: " + str(conf_dic['whole_error']) + "; " + str(round(100 - (conf_dic['whole_error'] / 255 * 100), 2)) + "% acccuracy")
	scheme.close()

def generate(conf_dic):
	m = conf_dic['m']
	skip = conf_dic['skip']
	Z = conf_dic['Z']

	conf_dic['length'] = 0
	conf_dic['conns'] = 0

	image = conf_dic['image'].copy()
	result = np.full((Z, Z), 255,  dtype=np.uint8)
	whole_error = get_whole_error(image, result)
	if (whole_error == 0):
		logging.debug('white image, exiting')
		save_data_scheme_close(conf_dic, scheme)
		return result
	logging.info("starting whole_error " + str(whole_error))

	logging.info("filling pins coordinates")
	angles = np.linspace(0, 2*np.pi, m)
	center = Z / 2
	xs = center + (Z - 2)/2 * np.cos(angles)
	ys = center + (Z - 2)/2 * np.sin(angles)
	pins = list(map(lambda x,y: (int(x),int(y)), xs,ys))

	length = 0
	scheme = open(conf_dic['name'] + '/scheme.txt', 'w')
	conn_count = 0
	max_con_flag = 0
	max_conns = conf_dic['N']

	if (conf_dic['max_conns'] != -1):
		logging.debug('priority to max conns, not error')
		max_con_flag = 1
		max_conns = conf_dic['max_conns']

	if (max_con_flag and max_conns == 0):
		logging.info('max number of connections are made')
		save_data_scheme_close(conf_dic, scheme)
		return

	logging.info("begin scheme generation")
	pin1, pin2 = find_best_conn_from_all(conf_dic['image'], pins, skip)
	logging.info('first connection is found: ' + str(pin1) + " --- " + str(pin2))
	x0, y0 = get_coords(pins, pin1)
	x1, y1 = get_coords(pins, pin2)

	if (not max_con_flag):
		backup_res = result.copy()
	Wu(result, x0, y0, x1, y1)
	show_image(result)
	if (not max_con_flag):
		new_error = get_whole_error(image, result)
		if (new_error > whole_error):
			result = backup_res
			logging.info('adding this first connection makes whole error bigger')
			save_data_scheme_close(conf_dic, scheme)
			return result
		whole_error = new_error

	brezenhem(conf_dic['image'], x0, y0, x1, y1, 1)
	conn_count += 1
	length += get_conn_length(x0, y0, x1, y1)
	logging.info('first connection is drawn; whole error = ' + str(whole_error))

	pin3_v1, err_v1 = find_best_conn_from_pin(conf_dic['image'], pins, pin1, skip)
	pin3_v2, err_v2 = find_best_conn_from_pin(conf_dic['image'], pins, pin2, skip)

	if (err_v1 < err_v2):
		# pin2 - pin1 - pin3
		x1, y1 = x0, y0
		x2, y2 = get_coords(pins, pin3_v1)
		pin1, pin2 = pin2, pin1
		pin3 = pin3_v1
	else:
		# pin1 - pin2 - pin3
		x2, y2 = get_coords(pins, pin3_v2)
		pin3 = pin3_v2

	scheme.write(str(pin1) + " " + str(pin2))
	logging.info('next connection: ' + str(pin2) + " --- " + str(pin3))
	if not max_con_flag:
		backup_res = result.copy()
	Wu(result, x1, y1, x2, y2)
	new_error = get_whole_error(image, result)

	prev_pin = pin2
	xn, yn = x1, y1

	cur_pin = pin3
	xk, yk = x2, y2

	while (max_con_flag and conn_count < max_conns) or (not max_con_flag and new_error < whole_error):
		whole_error = new_error

		scheme.write(" " + str(cur_pin))
		brezenhem(conf_dic['image'], xn, yn, xk, yk, 1)
		length += get_conn_length(xn, yn, xk, yk)
		conn_count += 1
		logging.info('connection ' + str(prev_pin) + " --- " + str(cur_pin) + " " + str(conn_count) + "/" + str(max_conns) + " whole error = " + str(whole_error))
		if (conn_count % 100 == 0):
			scheme.write("\n-------------"+str(conn_count)+" connections--------------\n")

		next_pin, err = find_best_conn_from_pin(conf_dic['image'], pins, cur_pin, skip)
		logging.debug("next pin " + str(next_pin))

		xn, yn = xk, yk
		xk, yk = get_coords(pins, next_pin)
		if not max_con_flag:
			backup_res = result.copy()
		Wu(result, xn, yn, xk, yk)
		new_error = get_whole_error(image, result)
		prev_pin = cur_pin
		cur_pin = next_pin

	if not max_con_flag:
		result = backup_res
	conf_dic['length'] = length
	conf_dic['conns'] = conn_count
	conf_dic['whole_error'] = whole_error
	logging.debug('adding connection making worse error, exiting')
	save_data_scheme_close(conf_dic, scheme)
	return result

def main():
	init_log("log.txt", logging.DEBUG)
	conf_dic = load_data()
	try:
		os.mkdir(conf_dic['name'])
	except OSError as error:
		if error.errno == 17:
			logging.warning('files in ' + conf_dic['name'] + ' folder will be overwrite')
		else:
			logging.warning('cannot create ' + conf_dic['name'] + ' folder to save results, saving to root')
			conf_dic['name'] = '.'
	shutil.copy("config.txt", conf_dic['name'] + "/config.txt")
	conf_dic['Z'] = int(2 * conf_dic['R'] / conf_dic['t'])
	conf_dic['N'] = int(conf_dic['m'] * (conf_dic['m'] - 2 * conf_dic['skip'] + 1) / 2)
	logging.debug(repr(conf_dic))
	parse_image(conf_dic)
	result = generate(conf_dic)
	save_image(conf_dic['name'] + "/result.png", result)
	save_image(conf_dic['name'] + "/error.png", conf_dic['image'])
	show_image(result)
	shutil.move("log.txt", conf_dic['name'] + "/log.txt")
main()
