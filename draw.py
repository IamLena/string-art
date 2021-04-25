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
connections = numpy.random.choice([0, 1], size=NUM_OF_CONNECTIONS, p=[.97, .03])
print(connections.sum())
connections_compination = list(itertools.combinations(pin_coords, 2))

def draw_connection(myCanvas, connection_index):
	conn = connections_compination[connection_index]
	x0 = conn[0][0]
	y0 = conn[0][1]
	x1 = conn[1][0]
	y1 = conn[1][1]
	myCanvas.create_line(x0, y0, x1, y1,)

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


root = tkinter.Tk()
myCanvas = tkinter.Canvas(root, bg="white", height=RESOLUTION + 1, width=RESOLUTION + 1)
draw_all_connections(myCanvas, connections)
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
