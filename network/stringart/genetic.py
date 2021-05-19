from random import choices
from PIL import Image, ImageDraw, ImageTk
from tkinter import Tk, Canvas
import numpy as np
import math
import time

Rc = 15									# canvas radius in cm
t = 0.1									# thread weight in cm
Z = int(2 * (Rc / t))					# number of pixels in diameter (resolution)
m = 10									# number of pins
angle_step = 360 / m								# angle step for pins in degrees
L_min = 2								# min pin to be connected, conn min length = 1 if all connections needed
N = int(m * (m - 2 * L_min + 1) / 2)	# number of all possible connections

# genome is a random connections
genome_length = N
polpulation_size = 5

def generate_genome(genome_length: int):
	return choices([0, 1], k=genome_length)

def generate_population(size: int, genome_length: int):
	return [generate_genome(genome_length) for _ in range(size)]

def draw_connection(pin_1, pin_2, res):
	xk = math.floor(Z/2 + (Z - 2)/2 * np.cos(np.radians(pin_1 * angle_step)))
	yk = math.floor(Z/2 + (Z - 2)/2 * np.sin(np.radians(pin_1 * angle_step)))

	xn = math.floor(Z/2 + (Z - 2)/2 * np.cos(np.radians(pin_2 * angle_step)))
	yn = math.floor(Z/2 + (Z - 2)/2 * np.sin(np.radians(pin_2 * angle_step)))

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

def show_any_img(nparr, root, canvas):
	w = len(nparr) / 2
	image = ImageTk.PhotoImage(Image.fromarray(nparr))
	imagesprite = canvas.create_image(w, w, image=image)
	canvas.pack()
	root.update()


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
	# Image.fromarray(img).show()
	return img

def fitness(genome, N, m, img):
	assert(len(genome) == N)
	res = np.full_like(img, 255)
	error = 0

	pin_1 = 0
	pin_2 = 2
	for conn_index in range(N):
		pin_2 += 1
		if (pin_2 == m - 1):
			pin_1 += 1
			pin_2 = pin_1 + 2
		if (genome[conn_index]):
			draw_connection(pin_1, pin_2, res)
	error = np.sum(np.subtract(img, res))
	return error, res




filename_in = '/mnt/c/diplom/myrepo/pics/Blackline.png'
filname_gr = '/mnt/c/diplom/myrepo/pics/Blackline_gr.png'

# root = Tk()
# canvas = Canvas(root,width=Z,height=Z)
# canvas.pack()

img = image_parse(filename_in, filname_gr, Z)
for i in range(5):
	g1 = generate_genome(genome_length)
	start = time.time()
	fit, res = fitness(g1, N, m, img)
	end = time.time()
	print(fit)
	print(f'{i}: time = {end - start}')
	# show_any_img(res, root, canvas)
	# time.sleep(3)

# root.mainloop()
