import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from tkinter import filedialog
import numpy as np
import logging

def square_crop(pil_image):
	logging.info("square crop")
	if pil_image.size[0] != pil_image.size[1]:
		if pil_image.size[0] < pil_image.size[1]:
			side = pil_image.size[0]
		else:
			side = pil_image.size[1]
		left = (pil_image.size[0] - side) / 2
		top = (pil_image.size[1] - side) / 2
		right = (pil_image.size[0] + side) / 2
		bottom = (pil_image.size[1] + side) / 2
		pil_image = pil_image.crop((left, top, right, bottom))
	return pil_image

def change_resolution(pil_image, size):
	# logging.info("resized")
	return pil_image.resize((size, size), Image.ANTIALIAS)

def circle_crop(pil_image):
	logging.info("circle crop")
	# new white canvas
	Z = pil_image.size[0]
	circlecrop = Image.new('L', [Z, Z], 255)
	circle = ImageDraw.Draw(circlecrop)
	# set fields of 1 pixel, draw black circle
	circle.pieslice([1, 1, Z - 1, Z - 1], 0, 360, fill=0)
	np_circle = np.array(circlecrop)
	np_image = np.asarray(pil_image).copy()
	# set pixels of image where circle_image is white to 255
	np_image[np_circle == 255] = 255
	return Image.fromarray(np_image)

def greyscale(pil_image):
	logging.info("greyscale")
	return pil_image.convert('L')

def save_image(filename, np_img):
	logging.info("saving image into " + filename)
	Image.fromarray(np_img).save(filename)

image = None # global tk canvas image
loaded_pil_image = None

def show_np_image(np_arr, root, canvas):
	show_pil_image(Image.fromarray(np_arr), root, canvas)

def show_pil_image(pil_image, root, canvas):
	global image
	pil_image = change_resolution(pil_image, canvas.winfo_width())
	image = ImageTk.PhotoImage(pil_image)
	imagesprite = canvas.create_image(0, 0, image=image, anchor='nw')
	root.update()

def load_image(data):
	app = data[0]
	logging.info("loading image")
	image_path = filedialog.askopenfilename(filetypes=[('.png', '.jpg')])
	if (image_path == ""):
		logging.info("no file was chosen")
		return
	logging.info("loaded path " + image_path)
	pil_image = Image.open(image_path)
	pil_image = square_crop(pil_image)
	show_pil_image(pil_image, app.root, app.canvas)
	global loaded_pil_image
	app.stringart.pil_image = pil_image
	data[0] = app

def parse_pil_image(pil_image, resolution):
	logging.info("greyscale, update resolution, circle crop")
	pil_image = greyscale(pil_image)
	pil_image = change_resolution(pil_image, resolution)
	pil_image = circle_crop(pil_image)
	return np.asarray(pil_image).copy()
