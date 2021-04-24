import numpy
import math
import tkinter
import itertools

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
	myCanvas.create_line(x0, y0, x1, y1)

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
	from PIL import Image
	img = Image.open("file_name.ps")
	img.save("file.png", "png")

root = tkinter.Tk()
myCanvas = tkinter.Canvas(root, bg="white", height=RESOLUTION + 1, width=RESOLUTION + 1)
draw_all_connections(myCanvas, connections)
root.mainloop()
