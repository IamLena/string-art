from PIL import Image, ImageDraw, ImageTk
from tkinter import Tk, Canvas
import numpy as np
import math
from time import time
import logging
from funcs import *

Rc = 10			# canvas radius in cm
t = 0.1			# thread weight in cm
m = 100			# number of pins
skip = 20		# min pin to be connected

if_log = 1		# 1 - logs, 0 - don't
if_show = 1		# 1 - show process, 0 - don't. set to 0 if display problems

Z = 2 * int(Rc / t)						# number of pixels in diameter (resolution)
N = int(m * (m - 2 * skip + 1) / 2)		# number of all possible connections

schema = ""					# schema buff
max_conn = N				# max connections number to be made
length = 0					# length of neede thread

res = np.full((Z, Z), 255,  dtype=np.uint8)		# white canvas
img = None										# will be loaded
err = None										# inits as img - res as soon as img loaded
# set pins
angles = np.linspace(0, 2*np.pi, m)
center = Z / 2
xs = center + (Z - 2)/2 * np.cos(angles)
ys = center + (Z - 2)/2 * np.sin(angles)
pins = list(map(lambda x,y: (int(x),int(y)), xs,ys))

img_path = "image.png"						# define input image path

gr_img_path = "gr_" + img_path
result_path = "res_" + img_path
prefix = img_path.split('.')[0]
schema_path = "sch_" + prefix + ".txt"
conf_path = "cnf_" + prefix + ".txt"
if if_log:
	log_path = "log_" + prefix + ".txt"

# set display process environment
root = None
canvas = None
if if_show:
	root = Tk()
	canvas = Canvas(root,width=Z,height=Z)
	canvas.pack()

if if_log:
	logging.basicConfig(level=logging.DEBUG,
		format='%(asctime)s %(message)s',
		handlers=[logging.FileHandler(log_path),
		logging.StreamHandler()])

###############
#### START ####
###############
if if_log:
	log_data(img_path, Rc, m, t, skip, if_log, if_show, Z, N)
	log_msg("loading image")
try:
	img = parse_image(img_path, Z)
except Exception as e:
	error("ERR: occured while processing input image\n" + str(e) + "\n", 1)
if if_log:
	log_msg("image loaded")
whole_err = get_whole_error(img, res)
if (err == 0):
	# the image is white
	savedata()
	exit(0)
if if_log:
	log_msg("start error is " + str(err))

cur_pin, schema = find_1st_2nd_conn(img, pins, schema, skip, if_log)
print(schema)
conn_count = 2 # two connections are made
error_check = 10
if if_log:
	log_msg("start loop; error check every " + str(error_check) + "; connections limit is " + str(max_conn))
while conn_count < max_conn:
	xk, yk = get_coords(pins, cur_pin)
	next_pin, err = find_best_conn_from_pin(img, pins, cur_pin, skip)
	schema += str(next_pin) + " "
	xn, yn = get_coords(pins, next_pin)
	brezenhem(img, xn, yn, xk, yk, 1)
	cur_pin = next_pin

	if (conn_count % error_check == 0):
		new_res = draw_connections(np.copy(res), schema, pins)
		new_err = get_whole_error(img, new_res)
		if (new_err < whole_err):
			whole_err = new_err
			res = new_res
			schema = ""
			if if_log:
				log_msg(str(conn_count) + " connections made; error is " + str(whole_err))
			if if_show:
				show_image(new_res)
				# show_image(res, root, canvas)
		else:
			# error is getting bigger, res is getting worse, saving previous good result
			log_msg(str(conn_count) + " connections made; minimum error is " + str(whole_err))
			savedata()
			exit(0)

	if (conn_count % 100 == 0):
		schema += "\n" + str(conn_count) + " connections made\n"

	conn_count += 1

if if_show:
	root.mainloop()

