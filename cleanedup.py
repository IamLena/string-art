from PIL import Image, ImageDraw, ImageTk
from tkinter import Tk, Canvas
import numpy as np
import logging
import math
from time import time

def init_log(log_file, level_code):
	logging.basicConfig(
		level=level_code,
		format='%(asctime)s : %(levelname)s : %(message)s',
		handlers=[logging.FileHandler(log_file, "w"),
		logging.StreamHandler()])

	# init_log("log.txt")
	# logging.info("this is debug msg")
	# logging.info("this is info msg")
	# logging.warning("this is warning msg")
	# logging.error("this is error msg")
	# logging.critical("this is critical msg")

def set_defaults(params):
	logging.info('setting default parameters')
	if params['R'] == -1:
		raise Exception('Canvas radius must be defined')
	if params['t'] == -1:
		raise Exception('Thread weight must be defined')
	if params['m'] == -1:
		raise Exception('Number of pins must be defined')
	if params['name'] == -1:
		raise Exception('Image path must be defined')
	if params['skip'] == -1:
		params['skip'] = 1
	if params['if_log'] == -1:
		params['if_log'] = 1
	if params['if_show'] == -1:
		params['if_show'] = 1

def check_validation(params):
	logging.info('checking validation of parameters')
	if (params['skip'] > params['m'] / 2):
		raise Exception('To much pins to skip, redefine "number of pins to skip in minimum chord" parameter')
	angle_step = 2 * np.pi / params['m']
	dist_b_pins = math.sqrt(params['R']**2 + params['R']**2 - 2 * params['R'] * params['R']  * math.cos(angle_step))
	logging.info("angle between pins equal to " + str(360 / params['m']) + " degrees; distination between pins equals to " + str(dist_b_pins) + " cm")
	if (dist_b_pins / params['t'] < 3):
		logging.warning("with this resolution, pins are too close to each other")

def load_data():
	logging.info('loading input data')
	params = {'R':-1, 't':-1, 'm':-1, 'skip':-1, 'if_log':-1, 'if_show':-1, 'max_conns':-1, "image":-1, "name":-1}
	try:
		with open("config.txt") as f:
			while True:
				line = f.readline()
				if not line:
					break
				if line[0] == '#' or line.strip() == "":
					continue
				pair = line.split('=')
				if (len(pair) != 2):
					raise Exception('Invalid line in config.txt - ' + line)
				if (pair[0].strip().lower() == 'canvas radius'):
					if (params['R'] != -1):
						logging.warning('canvas radius is defined several times, the last will be procesed')
					if (float(pair[1]) <= 0):
						raise Exception('Canvas radius should be positive number')
					params['R'] = float(pair[1])
				elif (pair[0].strip().lower() == 'thread weight'):
					if (params['t'] != -1):
						logging.warning('thread weight is defined several times, the last will be procesed')
					if (float(pair[1]) <= 0):
						raise Exception('Thread weight should be positive number')
					params['t'] = float(pair[1])
				elif (pair[0].strip().lower() == 'number of pins'):
					if (params['m'] != -1):
						logging.warning('number of pins is defined several times, the last will be procesed')
					if (int(pair[1]) <= 0):
						raise Exception('Number of pins should be positive integer')
					params['m'] = int(pair[1])
				elif (pair[0].strip().lower() == 'image'):
					params['image'] = 1
					name = pair[1].strip()
					params['image'] = Image.open(name)
					params['name'] = pair[1].strip().split('.')[0][name.rfind('/') + 1:]


				elif (pair[0].strip().lower() == 'number of pins to skip in minimum chord'):
					if (params['skip'] != -1):
						logging.warning('number of pins to skip in minimum chord is defined several times, the last will be procesed')
					if (int(pair[1]) <= 0):
						raise Exception('Number of pins to skip in minimum chord should be positive integer')
					params['skip'] = int(pair[1])
				elif (pair[0].strip().lower() == 'logging'):
					if (params['if_log'] != -1):
						logging.warning('logging is defined several times, the last will be procesed')
					if int(pair[1]) == 0 or int(pair[1]) == 1:
						params['if_log'] = int(pair[1])
					else:
						raise Exception('logging should be 0 or 1')
					if params['if_log'] == 0:
						logging.getLogger().setLevel(logging.CRITICAL)
				elif (pair[0].strip().lower() == 'show process'):
					if (params['if_show'] != -1):
						logging.warning('show process is defined several times, the last will be procesed')
					if int(pair[1]) == 0 or int(pair[1]) == 1:
						params['if_show'] = int(pair[1])
					else:
						raise Exception('show process should be 0 or 1')
				elif (pair[0].strip().lower() == 'maximum connections to make'):
					if (params['max_conns'] != -1):
						logging.warning('maximum connections to make is defined several times, the last will be procesed')
					if (int(pair[1]) <= 0):
						raise Exception('Maximum connections to make should be positive integer')
					params['max_conns'] = int(pair[1])
			set_defaults(params)
			check_validation(params)
			logging.info('loading complete')
			return params
	except FileNotFoundError:
		if params['image'] == 1:
			logging.critical("image file wasn't found")
		else:
			logging.critical("config.txt file wasn't found")
		exit(1)
	except ValueError:
		logging.critical("types or values of paramenters are invalid")
		exit(1)
	except Exception as error:
		logging.critical(str(error))
		exit(1)

def main():
	init_log("log.txt", logging.INFO)
	conf_dic = load_data()
	print(conf_dic)

main()
