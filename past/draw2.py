import numpy
import math
import tkinter
import itertools
from PIL import Image, ImageTk

scale = 1
NUM_OF_PINS = 180
PIN_RADIUS = 0.2
DIAMETR = 60
DIAMETR_inch = DIAMETR / 2.54
RADIUS = DIAMETR / 2
ANGLE_STEP = 360 / NUM_OF_PINS
ANGLE_STEP_radians = 2 * math.pi / NUM_OF_PINS
NUM_OF_CONNECTIONS = int(2 * NUM_OF_PINS * (NUM_OF_PINS - 1) / 4)
STRING_WIDTH = 0.2
RESOLUTION = int (DIAMETR / STRING_WIDTH) #number of pixels in diametr
CENTER = RESOLUTION / 2
RADIUS_pixels = RESOLUTION / 2
PIN_RADIUS_pixel = PIN_RADIUS / STRING_WIDTH

pin_coords = []
angle = 0
for i in range(NUM_OF_PINS):
	center = CENTER * scale
	radius = RADIUS_pixels * scale
	pin_coords.append([math.floor(center + radius * math.cos(angle)), math.floor(center + radius * math.sin(angle))])
	angle += ANGLE_STEP_radians

# connections = numpy.zeros(NUM_OF_CONNECTIONS, dtype=numpy.bool8) # is there a way to use bits not bytes
connections = numpy.random.choice([0, 1], size=NUM_OF_CONNECTIONS, p=[.99, .01])
print("number of applyed connections = ", connections.sum())

###############
## VARIANT 1 ##
###############

connections_compination = list(itertools.combinations(pin_coords, 2))

def draw_connection(myCanvas, connection_index):
	conn = connections_compination[connection_index]
	x0 = conn[0][0]
	y0 = conn[0][1]
	x1 = conn[1][0]
	y1 = conn[1][1]
	myCanvas.create_line(x0, y0, x1, y1, fill="#000", width=scale)

###############
## VARIANT 2 ##
###############

# def draw_connection(myCanvas, connection_index):
# 	conn = cgen(connection_index, NUM_OF_PINS, 2)
# 	x0 = pin_coords[conn[0]-1][0]
# 	y0 = pin_coords[conn[0]-1][1]
# 	x1 = pin_coords[conn[1]-1][0]
# 	y1 = pin_coords[conn[1]-1][1]
# 	myCanvas.create_line(x0, y0, scale * x1, scale * y1, fill="#000", width=scale)

###############
## VARIANT 3 ##
###############

def sign(x):
	if x >= 0:
		return 1
	return -1

def anti_alizing_draw_connection(npimage, conn_index):
	conn = connections_compination[conn_index]
	xn = conn[0][0]
	yn = conn[0][1]
	xk = conn[1][0]
	yk = conn[1][1]

	# ввод: xn, yn, xk, yk
	# пиксель - как площадь
	# закрашивается с интенсивностью пропорциональной площади под отрезком

	print(xn, yn, xk, yk)
	intencity = 100
	x = xn
	y = yn
	dx = xk - xn
	dy = yk - yn
	sx = sign(dx)
	sy = sign(dy)
	dx = abs(dx)
	dy = abs(dy)
	swap_flag = False

	if (dx < dy):
		dx, dy = dy, dx
		swap_flag = True

	m = dy / dx * intencity
	w = intencity - m
	er = intencity / 2

	for i in range(1, dx + 1):
		# or [x][y] ?
		print(round(-(er - 100) * 2.55))
		print(x, y)
		npimage[y][x] = round(-(er - 100) * 2.55)
		if er < w:
			if swap_flag:
				y += sy
			else:
				x += sx
			er += m
		else:
			y += sy
			x += sx
			er -= w

	image = Image.fromarray(npimage)
	frame = tkinter.Frame()
	tkimage = ImageTk.PhotoImage(image)
	label = tkinter.Label(frame, image=tkimage)
	label.image = tkimage
	label.pack()
	frame.pack()


def draw_pins(myCanvas, pin_coords):
	r = PIN_RADIUS_pixel * scale
	for pin in pin_coords:
		myCanvas.create_oval(pin[0]-r, pin[1]-r, pin[0]+r, pin[1]+r, fill='#000000')

def draw_all_connections(myCanvas, connections):
	# height = int ((RESOLUTION + 1 + 2 * PIN_RADIUS_pixel) * scale)
	# width = int ((RESOLUTION + 1 + 2 * PIN_RADIUS_pixel) * scale)
	height = RESOLUTION
	width = RESOLUTION
	threading = numpy.zeros((height, width))

	for i in range(len(connections)):
		if connections[i]:
			anti_alizing_draw_connection(threading, i)
			# draw_connection(myCanvas, i)
	# myCanvas.pack()
	# myCanvas.update()

def saveimage(myCanvas, fileprefix):
	psfile = fileprefix + ".ps"
	myCanvas.postscript(file=psfile, colormode='color')
	img = Image.open(psfile)
	pngfile = fileprefix + ".png"
	img.save(pngfile, "png")

def C(n, k):
	result = n
	stop = n - k + 1
	while n > stop:
		n -= 1
		result *= n
	while k > 1:
		result /= k
		k -= 1
	return int(result)

def cgen(i,n,k):
	c = []
	r = i
	j = 0
	for s in range(1,k+1):
		cs = j+1
		while r-C(n-cs,k-s)>0:
			r -= C(n-cs,k-s)
			cs += 1
		if (s == k):
			cs += r
		c.append(cs)
		j = cs
	return c

def tk_showthread():
	root = tkinter.Tk()
	myCanvas = tkinter.Canvas(root, bg="white", height=(RESOLUTION + 1 + 2 * PIN_RADIUS_pixel) * scale, width=(RESOLUTION + 1 + 2 * PIN_RADIUS_pixel) * scale)
	# draw_pins(myCanvas, pin_coords)
	draw_all_connections(myCanvas, connections)
	myCanvas.pack()
	myCanvas.update()
	root.mainloop()

tk_showthread()
