from PIL import Image, ImageDraw, ImageTk
from tkinter import Tk, Canvas
import numpy as np
import math
from time import time
from funcs import *

start_time = time()

''' You can change this parameters '''

Rc = 20			# canvas radius in cm
t = 0.1			# thread weight in cm
m = 200			# number of pins
skip = 20		# min pin to be connected

if_log = 1		# 1 - logs, 0 - don't
if_show = 0		# 1 - show process, 0 - don't. set to 0 if display problems

img_path = "spiral.png"						# define input image path

'''-----------------------------------------'''

Z = 2 * int(Rc / t)						# number of pixels in diameter (resolution)
N = int(m * (m - 2 * skip + 1) / 2)		# number of all possible connections

assert(Rc > 0)
assert(t > 0)
assert (m > 0)
assert(1 <= skip <= m/2)

schema = ""					# schema buff
max_conn = N				# max connections number to be made
whole_length = 0					# length of neede thread

res = np.full((Z, Z), 255,  dtype=np.uint8)		# white canvas
img = None										# will be loaded
err = None										# inits as img - res as soon as img loaded
# set pins
angles = np.linspace(0, 2*np.pi, m)
center = Z / 2
xs = center + (Z - 2)/2 * np.cos(angles)
ys = center + (Z - 2)/2 * np.sin(angles)
pins = list(map(lambda x,y: (int(x),int(y)), xs,ys))

gr_img_path = "gr_" + img_path
result_path = "res_" + img_path
prefix = img_path.split('.')[0]
schema_path = "sch_" + prefix + ".txt"
conf_path = "cnf_" + prefix + ".txt"

if if_log:
	log_path = "log_" + prefix + ".txt"
	log_stream = open(log_path, "w")

# set display process environment
root = None
canvas = None
if if_show:
	root = Tk()
	canvas = Canvas(root,width=Z,height=Z)
	canvas.pack()

if if_log:
	log_data(log_stream, img_path, Rc, m, t, skip, if_log, if_show, Z, N)

img = parse_image(img_path, Z)
origin_img = np.copy(img)
if if_show:
	show_image(img)
save_image(gr_img_path, img)

if if_log:
	log_msg(log_stream, "\nimage loaded")

whole_err = get_whole_error(img, res)
if if_log:
	log_msg(log_stream, "start error is " + str(whole_err))

schema_stream = open(schema_path, "w")
cur_pin, schema, add_length = find_1st_2nd_conn(img, pins, schema, skip, if_log, log_stream)
length = add_length
conn_count = 2 # two connections are made
error_check = 50
if if_log:
	log_msg(log_stream, "start loop\nerror check every " + str(error_check) + "\nconnections limit is " + str(max_conn))
while conn_count < max_conn:
	xk, yk = get_coords(pins, cur_pin)
	next_pin, err = find_best_conn_from_pin(img, pins, cur_pin, skip)
	schema += str(next_pin) + " "
	xn, yn = get_coords(pins, next_pin)
	brezenhem(img, xn, yn, xk, yk, 1)
	length += get_conn_length(xn, yn, xk, yk)
	cur_pin = next_pin

	if (conn_count % error_check == 0):
		new_res = draw_connections(np.copy(res), schema, pins)
		new_err = get_whole_error(origin_img, new_res)
		if (new_err < whole_err):
			whole_err = new_err
			res = new_res
			if if_log:
				log_msg(log_stream, str(conn_count) + " connections made; error is " + str(whole_err))
			if if_show:
				show_tk_img(root, canvas, res)
			schema_stream.write(schema)
			schema = ""
			whole_length = length
		else:
			if if_log:
				log_msg(log_stream, str(conn_count) + " connections made; minimum error is " + str(whole_err))
			break

	if (conn_count % 100 == 0):
		schema += "\n" + str(conn_count) + " connections made\n"

	conn_count += 1


gen_time = time() - start_time
save_image(result_path, res)
schema_stream.write(schema)

# cnf and analysis in the begining
schema_stream.write("\n\n")
log_data(schema_stream, img_path, Rc, m, t, skip, if_log, if_show, Z, N)
log_msg(schema_stream, str(conn_count) + " connections made out of " + str(N))
log_msg(schema_stream, str(whole_length * t /100) + " m of thread needed")
log_msg(schema_stream, "error is " + str(whole_err))
log_msg(schema_stream, "time: " + str(gen_time) + "\n")
schema_stream.close()

if if_log:
	log_msg(log_stream, str(whole_length * t /100) + " m of thread needed")
	log_msg(log_stream, "time: " + str(gen_time))
	log_stream.close()

if if_show:
	show_tk_img(root, canvas, res)
	root.mainloop()
