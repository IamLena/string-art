import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from tkinter import filedialog
import numpy as np
import logging
import math

def get_whole_error(img, res):
	Z = len(img)
	return np.sum(np.abs(np.subtract(img.astype("int16"), res.astype("int16")))) / Z / Z

def get_coords(pins, index):
	x = pins[index][0]
	y = pins[index][1]
	return (x, y)

def brezenhem(img, xn, yn, xk, yk, draw):
	error = 0
	count = 0
	dx = xk - xn
	dy = yk - yn
	sx = np.sign(dx)
	sy = np.sign(dy)
	dx = abs(dx)
	dy = abs(dy)
	swapFlag = 0
	if (dy > dx):
		dx, dy = dy, dx
		swapFlag = 1
	er = 2 * dy - dx

	x = xn
	y = yn
	for i in range (1, dx):
		if (draw):
			img[y][x] = 255
		else:
			error += img[y][x]
			count += 1
		if (er >= 0):
			if not swapFlag:
				y += sy
			else:
				x += sx
			er -= 2 * dx
		if swapFlag:
			y += sy
		else:
			x += sx
		er += 2 * dy
	if (count):
		return error / count
	return count

def set_cur_int(res_pixel, curInt):
	if (res_pixel <= curInt):
		return 0
	return res_pixel - curInt

def Wu(res, xn, yn, xk, yk):
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

def find_best_conn_from_all(img, pins, skip):
	best_pin_1 = -1
	best_pin_2 = -1
	min_err = 255

	pin_1_index = 0
	xk, yk = get_coords(pins, pin_1_index)
	pin_2_index = pin_1_index + skip
	xn, yn = get_coords(pins, pin_2_index)

	m = len(pins)
	N = int(m * (m - 2 * skip + 1) / 2)
	for conn_index in range(N):
		xn, yn = get_coords(pins, pin_2_index)
		tmp_err = brezenhem(img, xn, yn, xk, yk, 0)

		if (conn_index % 1000 == 0):
			logging.info(str(conn_index) + " : " + str(pin_1_index) + " --- " + str(pin_2_index) + " min conn err " + str(min_err))

		if (tmp_err < min_err):
			best_pin_1 = pin_1_index
			best_pin_2 = pin_2_index
			min_err = tmp_err

		ends = pin_1_index + m - skip
		if (ends >= m):
			ends = m - 1
		if (pin_2_index == ends):
			pin_1_index += 1
			xk, yk = get_coords(pins, pin_1_index)
			pin_2_index = pin_1_index + skip
		else:
			pin_2_index += 1
	return best_pin_1, best_pin_2

def find_best_conn_from_pin(img, pins, cur_pin, skip):
	m = len(pins)
	best_pin = -1
	min_err = 255
	xk, yk = get_coords(pins, cur_pin)

	for pin in range(cur_pin + skip, cur_pin + m - skip):
		pin = pin % m
		xn, yn = get_coords(pins, pin)
		tmp_err = brezenhem(img, xn, yn, xk, yk, 0)
		if (tmp_err < min_err):
			best_pin = pin
			min_err = tmp_err
	if best_pin == -1:
		logging.debug("going to the neighbour")
		best_pin = cur_pin + 1
		if (best_pin == len(pins)):
			best_pin = 0
	return best_pin, min_err
