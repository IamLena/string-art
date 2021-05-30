from PIL import Image, ImageDraw, ImageTk
from tkinter import Tk, Canvas
import numpy as numpy
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
	# logging.debug("this is debug msg")
	# logging.info("this is info msg")
	# logging.warning("this is warning msg")
	# logging.error("this is error msg")
	# logging.critical("this is critical msg")

def load_data():
	params = {'R':-1, 't':-1, 'm':-1, 'skip':-1, 'if_log':-1, 'if_show':-1, 'max_conns':-1}
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
					if (float(pair[1]) <= 0):
						raise Exception('Canvas radius should be positive number')
					params['R'] = float(pair[1])
				elif (pair[0].strip().lower() == 'thread weight'):
					if (float(pair[1]) <= 0):
						raise Exception('Thread weight should be positive number')
					params['t'] = float(pair[1])
				elif (pair[0].strip().lower() == 'number of pins'):
					if (int(pair[1]) <= 0):
						raise Exception('Number of pins should be positive integer')
					params['m'] = int(pair[1])
				elif (pair[0].strip().lower() == 'number of pins to skip in minimum chord'):
					if (int(pair[1]) <= 0):
						raise Exception('Number of pins to skip in minimum chord should be positive integer')
					params['skip'] = int(pair[1])
				elif (pair[0].strip().lower() == 'logging'):
					if int(pair[1]) == 0 or int(pair[1]) == 1:
						params['if_log'] = int(pair[1])
					else:
						raise Exception('logging should be 0 or 1')
				elif (pair[0].strip().lower() == 'show process'):
					if int(pair[1]) == 0 or int(pair[1]) == 1:
						params['if_show'] = int(pair[1])
					else:
						raise Exception('show process should be 0 or 1')
				elif (pair[0].strip().lower() == 'maximum connections to make'):
					if (int(pair[1]) <= 0):
						raise Exception('Maximum connections to make should be positive integer')
					params['max_conns'] = int(pair[1])
			return params
	except FileNotFoundError:
		logging.critical("config.txt file wasn't found")
		exit(1)
	except ValueError:
		logging.critical("types or values of paramenters are invalid")
		exit(1)
	except Exception as error:
		logging.critical(str(error))
		exit(1)

init_log("log.txt", logging.DEBUG)
conf_dic = load_data()
print(conf_dic)
