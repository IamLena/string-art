import numpy
import math
import tkinter
import itertools
from PIL import Image

NUM_OF_PINS = 180
DIAMETR = 60
DIAMETR_inch = DIAMETR / 2.54
RADIUS = DIAMETR / 2
ANGLE_STEP = 360 / NUM_OF_PINS
ANGLE_STEP_radians = 2 * math.pi / NUM_OF_PINS
NUM_OF_CONNECTIONS = int(2 * math.factorial(NUM_OF_PINS) / math.factorial(NUM_OF_PINS - 2))
STRING_WIDTH = 0.2
RESOLUTION = DIAMETR / STRING_WIDTH #number of pixels in diametr
CENTER_x = RESOLUTION / 2
CENTER_y = RESOLUTION / 2
RADIUS_pixels = RESOLUTION / 2
RESOLUTION_ppi = RESOLUTION / DIAMETR_inch

pin_coords = []
angle = 0
for i in range(NUM_OF_PINS):
	pin_coords.append([math.floor(CENTER_x + RADIUS_pixels * math.cos(angle)), math.floor(CENTER_y + RADIUS_pixels * math.sin(angle))])
	angle += ANGLE_STEP_radians

# connections = numpy.zeros(NUM_OF_CONNECTIONS, dtype=numpy.bool8)
NUM_OF_CONNECTIONS = int(NUM_OF_CONNECTIONS / 4)
# connections = numpy.random.randint(0, 2, NUM_OF_CONNECTIONS)
connections = numpy.random.choice([0, 1], size=NUM_OF_CONNECTIONS, p=[.99, .01])
print(connections.sum())
connections_compination = list(itertools.combinations(pin_coords, 2))

def draw_connection(myCanvas, connection_index):
	conn = connections_compination[connection_index]
	x0 = conn[0][0]
	y0 = conn[0][1]
	x1 = conn[1][0]
	y1 = conn[1][1]
	myCanvas.create_line(x0, y0, x1, y1, fill="#000", width=1)

def draw_all_connections(myCanvas, connections):
	for i in range(len(connections)):
	# for i in range (30):
		if connections[i]:
			# print(i)
			draw_connection(myCanvas, i)
	myCanvas.create_oval(1, 1, RESOLUTION, RESOLUTION, dash=(1,5))
	myCanvas.pack()

	myCanvas.update()
	myCanvas.postscript(file="file_name.ps", colormode='color')
	img = Image.open("file_name.ps")
	img.save("file.png", "png")

	# black or white!
	# print("colors")
	# for i in range(100):
	# 	colors = img.getpixel((i,40))
	# 	print(colors)

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
	# result = n * (n - 1) / 2

def cgen(i,n,k):
	"""
	returns the i-th combination of k numbers chosen from 1,2,...,n
	"""
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

def color_pixel(x, y, myCanvas, color)
	myCanvas.create_line(x, y, x + 1, y, fill=color)
	myCanvas.pack()
	myCanvas.update()

root = tkinter.Tk()
myCanvas = tkinter.Canvas(root, bg="white", height=RESOLUTION + 1, width=RESOLUTION + 1)
# draw_all_connections(myCanvas, connections)
myCanvas.create_line(pin_coords[100][0] - 2, pin_coords[100][1], pin_coords[30][0], pin_coords[30][1], fill="#000", width=1)
myCanvas.create_line(pin_coords[100][0] + 2, pin_coords[100][1], pin_coords[30][0], pin_coords[30][1], fill="#000", width=1)
myCanvas.create_oval(1, 1, RESOLUTION, RESOLUTION, dash=(1,5))
myCanvas.pack()
myCanvas.update()

root.mainloop()

print(C(NUM_OF_PINS, 2))
index = 13000
print(cgen(index, NUM_OF_PINS, 2))
print(pin_coords[101-1])
print(pin_coords[102-1])
print("-----------------")
res = connections_compination[index]
print(res)
print(pin_coords.index(res[0]))
print(pin_coords.index(res[1]))


def sign(x):
	if (sign > 0):
		return 1
	if (signa < 0):
		return -1
	return 0

def By(xn, yn, xk, yk):
	# m, xi, yi
	intensity = 100 #levels of intensity
	dx = (xk - xn)
	dy = (yk - yn)
	color = "#000000"

	color_pixel(xn, yn, myCanvas, color)
	color_pixel(xk, yk, myCanvas, color)

	if (dx == 0) {
		sy = sign(yk - yn)
		y = yn
		while (y != yk) {
			color_pixel(xn, yn, myCanvas, color)
			y += sy
		}
	}
	else if (dy == 0) {
		sx = sign(xk - xn)
		x = xn
		while (x != xk) {
			color_pixel(xn, yn, myCanvas, color)
			x += sx
		}
	}
	else if (abs(dy) <= abs(dx)) { #m < 1
		if (dx < 0) {
			t = xk
			xk = xn
			xn = t

			t = yk
			yk = yn
			yn = t
			dx = -dx
			dy = -dy
		}

		m = dy / dx

		yi = yn + m
		for x in range(xn + 1, x < xk)
		for (let x = xn + 1; x < xk; x += 1) {
			let curInt = intensity - (yi % 1) * 100
			let newColor = changeColor(color, curInt)
			ctx.fillStyle = newColor
			ctx.fillRect(x, Math.floor(yi), 1, 1)
			if (curInt != 100) {
				curInt = intensity - curInt
				newColor = changeColor(color, curInt)
				ctx.fillStyle = newColor
				ctx.fillRect(x, Math.ceil(yi), 1, 1)
			}
			yi = yi + m
		}
	}
	else {
		if (dy < 0) {
			let t = xn
			xn = xk
			xk = t

			t = yn
			yn = yk
			yk = t
			dy = -dy
			dx = -dx
		}
		m = dx / dy
		console.log(`m = ${m}, dx = ${dx}, dy = ${dy}, xn = ${xn}`)

		xi = xn + m
		for (let y = yn + 1; y < yk; y += 1) {
			let curInt =  intensity - (xi % 1) * 100
			let newColor = changeColor(color, curInt)
			ctx.fillStyle = newColor
			ctx.fillRect(Math.floor(xi), y, 1, 1)
			if (curInt != 100) {
				curInt = intensity - curInt
				newColor = changeColor(color, curInt)
				ctx.fillStyle = newColor
				ctx.fillRect(Math.ceil(xi), y, 1, 1)
			}
			xi = xi + m
		}
	}
}
