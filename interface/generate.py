import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from tkinter import filedialog
import numpy as np
import logging
from f_image import *

def update_clock(sec, root, timer):
	sec += 1
	timer.configure(text="Время генерации: " + str(sec) + " сек")
	root.after(1000, lambda: update_clock(sec, root, timer))

def create_command(data):
	app = data[0]
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
	app = generate(app)
	# dir = filedialog.askdirectory(title="Chose directory to save results in")
	# print(dir)
	# move files there
	# create_btn.configure(state="normal")
	# image_btn.configure(state="normal")
	data[0] = app

	# except ValueError:
	# 	logging.info("input parameters are invalid")
	# 	app.warninig.configure(text = "Некорректный ввод (проверьте, что R > 0, t > 0, m > 1)")

def generate(app):
	app.stringart.log_data()
	app.stringart.set_resolution()
	app.stringart.parse_image()
	show_np_image(app.stringart.np_image, app.root, app.canvas)
	return app
