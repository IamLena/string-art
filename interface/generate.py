import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from tkinter import filedialog
import numpy as np
import logging
from f_image import *
from draw_error import *
import math

after_id = -1

def update_clock(sec, root, timer):
	sec += 1
	timer.configure(text="Время генерации: " + str(sec) + " сек")
	global after_id
	after_id = root.after(1000, lambda: update_clock(sec, root, timer))

def create_command(data):
	app = data[0]
	app.output_label.configure(text = "")
	logging.info("start generation")
	# try:
	R = float(app.R_entry.get())
	t = float(app.t_entry.get())
	m = int(app.m_entry.get())
	if not app.stringart.pil_image:
		logging.info("image isn't loaded")
		app.warninig.configure(text = "Сначала загрузите изображение")
		return
	app.warninig.configure(text = "")
	app.create_btn.configure(state="disable")
	app.image_btn.configure(state="disable")
	update_clock(-1, app.root, app.timer)
	app.stringart.set_radius(R)
	app.stringart.set_thread(t)
	app.stringart.set_num_of_pins(m)
	app = prepare_for_generation(app)
	app = generate_scheme(app)
	# dir = filedialog.askdirectory(title="Chose directory to save results in")
	# print(dir)
	# move files there
	app.create_btn.configure(state="normal")
	app.image_btn.configure(state="normal")
	data[0] = app

	# except ValueError:
	# 	logging.info("input parameters are invalid")
	# 	app.warninig.configure(text = "Некорректный ввод (проверьте, что R > 0, t > 0, m > 1)")

def prepare_for_generation(app):
	app.stringart.set_resolution()
	app.stringart.set_num_of_all_conns()
	app.stringart.set_pins()
	app.stringart.set_result()
	app.stringart.parse_image()
	show_np_image(app.stringart.np_image, app.root, app.canvas)
	save_image("greyscaled.png", app.stringart.np_image)
	# app.stringart.log_data()
	return app

def save_data_scheme_close(app):
	str = app.stringart.get_data()
	app.output_label.configure(text = str)
	time = app.timer['text']
	app.root.after_cancel(after_id)
	save_image("result.png", app.stringart.res)
	app.stringart.log_data()
	logging.info(time)
	return

def generate_scheme(app):
	app.stringart.log_data()

	m = app.stringart.m
	Z = app.stringart.Z
	reserved_image = app.stringart.np_image.copy()
	skip = app.stringart.skip
	if_show = 1
	pins = app.stringart.pins
	max_con_flag = 0
	max_conns = app.stringart.N
	skip_error_check = 1
	skip_connections_check = 0

	scheme = open('scheme.txt', 'w')

	whole_error = get_whole_error(reserved_image, app.stringart.res)
	app.stringart.whole_error = whole_error

	if (whole_error == 0):
		logging.debug('white image, exiting')
		save_data_scheme_close(app)
		return app
	logging.info("starting whole_error " + str(whole_error))

	if (max_con_flag and max_conns == 0):
		logging.info('max number of connections are made')
		save_data_scheme_close(app)
		return app

	app.output_label.configure(text="происходит поиск начального соединения")
	logging.info("begin scheme generation")
	pin1, pin2 = find_best_conn_from_all(app.stringart.np_image, pins, skip)
	logging.info('first connection is found: ' + str(pin1) + " --- " + str(pin2))
	x0, y0 = get_coords(pins, pin1)
	x1, y1 = get_coords(pins, pin2)

	if (not max_con_flag):
		backup_res = app.stringart.res.copy()
	Wu(app.stringart.res, x0, y0, x1, y1)
	if (not max_con_flag):
		new_error = get_whole_error(reserved_image, app.stringart.res)
		if (new_error > whole_error):
			app.stringart.res = backup_res
			logging.info('adding this first connection makes whole error bigger')
			save_data_scheme_close(app)
			return app
		whole_error = new_error

	brezenhem(app.stringart.np_image, x0, y0, x1, y1, 1)
	app.stringart.update_stat(x0, y0, x1, y1)
	logging.info('first connection is drawn; whole error = ' + str(whole_error))

	app.output_label.configure(text="Определение направления плетения")
	pin3_v1, err_v1 = find_best_conn_from_pin(app.stringart.np_image, pins, pin1, skip)
	pin3_v2, err_v2 = find_best_conn_from_pin(app.stringart.np_image, pins, pin2, skip)

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
		backup_res = app.stringart.res.copy()
	Wu(app.stringart.res, x1, y1, x2, y2)
	new_error = get_whole_error(reserved_image, app.stringart.res)

	prev_pin = pin2
	xn, yn = x1, y1

	cur_pin = pin3
	xk, yk = x2, y2

	app.output_label.configure(text="Процесс поиска следующих соединений")
	while (max_con_flag and app.stringart.conns < max_conns) or (not max_con_flag and new_error <= whole_error):
		whole_error = new_error

		scheme.write(" " + str(cur_pin))
		brezenhem(app.stringart.np_image, xn, yn, xk, yk, 1)
		app.stringart.update_stat(xn, yn, xk, yk)
		app.stringart.conns += 1
		if (app.stringart.conns % 100 == 0):
			scheme.write("\n-------------"+str(app.stringart.conns)+" connections--------------\n")

		if (app.stringart.conns % 1 == 0):
			logging.info('connection #' + str(app.stringart.conns) + " : " + str(prev_pin) + " --- " + str(cur_pin) + " " + str(app.stringart.conns) + "/" + str(max_conns) + " whole error = " + str(whole_error))
			show_np_image(app.stringart.res, app.root, app.canvas)

		next_pin, err = find_best_conn_from_pin(app.stringart.np_image, pins, cur_pin, skip)

		xn, yn = xk, yk
		xk, yk = get_coords(pins, next_pin)
		if not max_con_flag:
			backup_res = app.stringart.res.copy()
		Wu(app.stringart.res, xn, yn, xk, yk)
		if (app.stringart.conns < skip_connections_check):
			new_error = whole_error - 0.0001
		elif (app.stringart.conns % skip_error_check == 0):
			new_error = get_whole_error(reserved_image, app.stringart.res)
		else:
			new_error = whole_error - 0.0001
		prev_pin = cur_pin
		cur_pin = next_pin

	if not max_con_flag:
		app.stringart.res = backup_res
	app.stringart.whole_error = whole_error
	logging.debug('adding connection making worse error, exiting')
	save_data_scheme_close(app)
	return app
