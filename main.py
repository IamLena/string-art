import random
import logging
from keras.models import Sequential
from keras.layers import Dense
from PIL import Image, ImageDraw, ImageTk
import time
import math
import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

logging.basicConfig(level=logging.DEBUG,
format='%(asctime)s %(message)s',
handlers=[logging.FileHandler("test.log"),
logging.StreamHandler()])

# string art params
Rc = 10
t = 0.1
IMG_SIZE = int (2 * Rc / t)
PINS_NUM = 100
ANGLE_STEP = 360 / PINS_NUM
image_path_in = "image.png"

# network params
IMG_IN_ROW = IMG_SIZE ** 2
HIDDEN_LAYER_Q = 500
HIDDEN_LAYER_Q_2 = 500
HIDDEN_LAYER_Q_3 = 500
CONNECTION_NUM = int (PINS_NUM * (PINS_NUM - 1) / 2)

# GA params
epochs = 200
population = 10
optimal_weights = None
mutation_probability = 0.5

def log_data():
	logging.debug("\n\n...STARTING...")
	logging.debug("image " + image_path_in)
	logging.debug("pins: " + str(PINS_NUM) + " resulting in "+ str(CONNECTION_NUM) + " of connections = output neurons\r\n")
	logging.debug("image size: " + str(IMG_SIZE) + "x" + str(IMG_SIZE) + " = " + str(IMG_IN_ROW) + " input neurons\r\n")
	logging.debug("has 1st hidden layer of: " + str(HIDDEN_LAYER_Q) + " neurons\r\n")
	logging.debug("has 2nd hidden layer of: " + str(HIDDEN_LAYER_Q_2) + " neurons\r\n")
	logging.debug("has 3rd hidden layer of: " + str(HIDDEN_LAYER_Q_3) + " neurons\r\n")
	logging.debug("population " + str(population) + "\r\n")
	logging.debug("max generations " + str(epochs) + "\r\n")
	logging.debug("mutation probability " + str(mutation_probability) + "\r\n")


log_data()

# artificial neural network class
# has input layer, 3 hidden layers and output layer
# sigmoid activation function
# init and forward propagation methods
class ANN(Sequential):
	def __init__(self, child_weights=None):
		super().__init__()
		if child_weights is None:
			# random weights
			layer1 = Dense(HIDDEN_LAYER_Q, input_shape=(IMG_IN_ROW,), activation='sigmoid')
			layer2 = Dense(HIDDEN_LAYER_Q_2, activation='sigmoid')
			layer3 = Dense(HIDDEN_LAYER_Q_3, activation='sigmoid')
			output_layer = Dense(CONNECTION_NUM, activation='sigmoid')
		else:
			layer1 = Dense(
					HIDDEN_LAYER_Q,
					input_shape=(IMG_IN_ROW,),
					activation='sigmoid',
					weights=[child_weights[0], np.zeros(HIDDEN_LAYER_Q)]) # i guess than np.zeros is biases
			layer2 = Dense(
					HIDDEN_LAYER_Q_2,
					activation='sigmoid',
					weights=[child_weights[1], np.zeros(HIDDEN_LAYER_Q_2)])
			layer3 = Dense(
					HIDDEN_LAYER_Q_3,
					activation='sigmoid',
					weights=[child_weights[2], np.zeros(HIDDEN_LAYER_Q_3)])
			output_layer = Dense(
					CONNECTION_NUM,
					activation='sigmoid',
					weights=[child_weights[3], np.zeros(CONNECTION_NUM)])
		self.add(layer1)
		self.add(layer2)
		self.add(layer3)
		self.add(output_layer)

	# input = image.reshape(-1, IMG_IN_ROW, ) / 255
	# input is an nparray of IMG_IN_ROW float values from 0 to 1
	# image is a matrix IMG_SIZE x IMG_SIZE to calculate error
	# pass both so not convertting types
	def forward_propagation(self, input, image):
		predict_conns = self.predict(input)
		self.fitness = get_error(predict_conns, image)

# loading input image data
def image_parse(image_path_in, Z):
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
	if (min != 0 or max != 255):
		nparr = np.rint((nparr - min) / (max - min) * 255).astype(np.uint8)
		image = Image.fromarray(nparr)
	# restore matching resolution
	image = image.resize((Z, Z), Image.ANTIALIAS)
	# circle crop
	# new white canvas
	circlecrop = Image.new('L', [Z, Z], 255)
	circle = ImageDraw.Draw(circlecrop)
	# set fields of 1 pixel, draw black circle
	circle.pieslice([1, 1, Z - 1, Z - 1], 0, 360, fill=0)
	npcrop = np.array(circlecrop)
	img = np.asarray(image).copy()
	# set pixels of image where circle_image is white to 255
	img[npcrop == 255] = 255
	return img

# drawing and getting error as sum (abs (diff image and res) / 255)
def set_cur_int(res_pixel, curInt):
	if (res_pixel <= curInt):
		return 0
	return res_pixel - curInt

def draw(res, xk, yk, xn, yn):
	# levels of intensity
	intensity = 255
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
			res[y][xn] = set_cur_int(res[y][xn], curInt)
			y += sy
	# horizontal line
	elif (dy == 0):
		sx = np.sign(xk - xn)
		x = xn
		while (x != xk):
			res[yn][x] = set_cur_int(res[yn][x], curInt)
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
			res[math.floor(yi)][x] = set_cur_int(res[math.floor(yi)][x], curInt)
			if (curInt != intensity):
				curInt = intensity - curInt
				res[math.floor(yi)+1][x] = set_cur_int(res[math.floor(yi)+1][x], curInt)
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
			res[y][math.floor(xi)] = set_cur_int(res[y][math.floor(xi)], curInt)
			if (curInt != intensity):
				curInt = intensity - curInt
				res[y][math.floor(xi)+1] = set_cur_int(res[y][math.floor(xi)+1], curInt)
			xi = xi + m

def draw_image(predict_conns):
	res = np.full((IMG_SIZE, IMG_SIZE), 255)
	pin_1_index = 0
	pin_2_index = 1
	# predict_conns[0] because there is a batch of outputs for diffrerent input images
	for conn in predict_conns[0]:
		pin_2_index += 1
		if (pin_2_index == PINS_NUM - 1):
			pin_1_index += 1
			pin_2_index = pin_1_index + 1
		# output is in range (0, 1)
		# 0.5 gets pretty simmilar results as error values
		if (conn > 0.6):
			pin_1_x = math.floor(IMG_SIZE/2 + (IMG_SIZE - 2)/2 * np.cos(np.radians(pin_1_index * ANGLE_STEP)))
			pin_1_y = math.floor(IMG_SIZE/2 + (IMG_SIZE - 2)/2 * np.sin(np.radians(pin_1_index * ANGLE_STEP)))

			pin_2_x = math.floor(IMG_SIZE/2 + (IMG_SIZE - 2)/2 * np.cos(np.radians(pin_2_index * ANGLE_STEP)))
			pin_2_y = math.floor(IMG_SIZE/2 + (IMG_SIZE - 2)/2 * np.sin(np.radians(pin_2_index * ANGLE_STEP)))

			draw(res, pin_1_x, pin_1_y, pin_2_x, pin_2_y)
	return res

def get_error(predict_conns, image):
	res = draw_image(predict_conns)
	diff = np.subtract(image.astype(np.int16), res.astype(np.int16))
	error = np.sum(np.abs(diff) / IMG_IN_ROW)
	return error

# GA crossover and mutation functions
def crossover(nn1, nn2):
	nn1_weights = []
	nn2_weights = []
	child_weights = []

	# get_weights returns matrix of weights (weights_neuron_1, weights_neuron_2, ...) and array of biases
	# crossovers only for weights
	for layer in nn1.layers:
		nn1_weights.append(layer.get_weights()[0])

	for layer in nn2.layers:
		nn2_weights.append(layer.get_weights()[0])

	# (len(nn1_weights) is equal to len(nn2_weights))
	weights_length = len(nn1_weights)
	# iteration through neurons
	for i in range(weights_length):
		# Get single point to split the matrix in parents based on # of cols
		# np.shape(nn1_weights[i])[1]-1 last index of connection from previous layer to a single neuron
		last_index = np.shape(nn1_weights[i])[1]-1
		split = random.randint(0, last_index)
		# Iterate through after a single point and set the remaing cols to nn_2
		for j in range(split, last_index):
			nn1_weights[i][:, j] = nn2_weights[i][:, j]

		child_weights.append(nn1_weights[i])

	mutation(child_weights)

	child = ANN(child_weights)
	return child

def mutation(child_weights):
	# sekect neuron connections to which will probably mutate
	selection = random.randint(0, len(child_weights)-1)
	mut = random.uniform(0, 1)
	if mut <= mutation_probability:
		# mult float number -5 to 5 with step of 0.1
		child_weights[selection] *= random.randint(-50, 50) * 0.1

# GA loop

# wont put new ann to pull if its error value is already there
# overflows min values, decrease diversity in breading
def if_includes(pool, fitness_value):
	for nn in pool:
		if (nn.fitness == fitness_value):
			return True
	return False

def log_pool(pool):
	min_fit = 255
	max_fit = 0
	avg = 0
	for ann in pool:
		avg += ann.fitness
		if (ann.fitness < min_fit):
			min_fit = ann.fitness
		if (ann.fitness > max_fit):
			max_fit = ann.fitness
	avg /= len(pool)
	logging.debug("\nmin " + str(min_fit) + " max " + str(max_fit) + "avg " + str(avg) + " len " + str(len(pool)))

def run_evolution(train_input, train_image):
	networks = []
	pool = []
	max_fitness = 255
	generation = 0
	for i in range(population):
		networks.append(ANN())

	for i in range(epochs):
		generation += 1
		logging.debug("Generation: " + str(generation) + "\r\n")

		for ann in networks:
			# Propagate to calculate fitness score
			ann.forward_propagation(train_input, train_image)
			# Add to pool after calculating fitness
			if not if_includes(pool, ann.fitness):
				pool.append(ann)
		# Clear for propagation of next children
		networks.clear()

		# Sort anns by fitness
		pool = sorted(pool, key=lambda x: x.fitness)
		# # perhapse delete worst species from pool
		# not good idea bcs lose diversity, falls into local minimum i guess
		# if (len(pool) > population * 5):
		# 	pool = pool[:population * 5]
		log_pool(pool)

		if pool[0].fitness < max_fitness:
			max_fitness = pool[0].fitness
			logging.debug("Max Fitness updated: " + str(max_fitness) + "\r\n")

			# Iterate through layers, get weights, and update optimal
			optimal_weights = []
			for layer in pool[0].layers:
				optimal_weights.append(layer.get_weights()[0])

		# Crossover: top 5 randomly select 2 partners
		for i in range(5):
			for j in range(population // 5):
				# Create a child and add to networks
				temp = crossover(pool[i], random.choice(pool))
				# Add to networks to calculate fitness score next iteration
				networks.append(temp)

def main():
	# loading train data
	image = image_parse(image_path_in, IMG_SIZE)
	input = image.reshape((-1, IMG_IN_ROW,)) / 255
	Image.fromarray(image).show()

	# run evolution, result id in optimal_weights
	run_evolution(input, image)

	#saving model
	ann = ANN(optimal_weights)
	ann.save('model' + str(error))
	ann.summary()

	# load test data
	# for now it is the same image to see the result

	# test neural network
	predict_conns = ann.predict(image.reshape((-1, IMG_IN_ROW,)) / 255)
	error = get_error(predict_conns, image)
	print('Test Error (must be close to zero): %.2f' % error)
	res = draw_image(predict_conns)
	Image.fromarray(res).show()
	Image.fromarray(res).save("result")

main()
