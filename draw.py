from conn import *
from tkinter import Tk, Canvas
from tkinter.ttk import Frame, Label
import concurrent.futures
import math
import numpy as np
from PIL import Image, ImageDraw, ImageTk

def show_any_img(root, canvas, nparr):
	w = len(nparr) / 2
	image = ImageTk.PhotoImage(Image.fromarray(nparr))
	imagesprite = canvas.create_image(w, w, image=image)
	canvas.pack()
	root.update()

def get_error(pin_1, pin_2, f_type, res, img):
	error = 0
	len_p = 0

	xk = pin_1[0]
	xn = pin_2[0]
	yk = pin_1[1]
	yn = pin_2[1]
	intensity = 255 #levels of intensity
	curInt = intensity

	dx = xk - xn
	dy = yk - yn

	# color pin_coords black
	error += int(img[yk][xk])	# res[yk][xk] -> 0
	error += int(img[yn][xn])	# res[yn][xn] -> 0
	len_p += 2

	# vertical line
	if (dx == 0):
		sy = np.sign(yk - yn)
		y = yn
		while (y != yk):
			error += int(img[y][xn])	# res[y][xn] -> 0; curInt - max
			len_p += 1
			y += sy

	# horizontal line
	elif (dy == 0):
		sx = np.sign(xk - xn)
		x = xn
		while (x != xk):
			error += int(img[yn][x])	# res[yn][x] -> 0; curInt - max
			len_p += 1
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
				error += int(img[math.floor(yi)][x])	# res -> 0
			else:
				error += np.abs(int(img[math.floor(yi)][x]) - (int(res[math.floor(yi)][x]) - curInt))
			len_p += 1

			if (curInt != intensity):
				curInt = intensity - curInt
				if res[math.floor(yi)+1][x] <= curInt:
					error += int(img[math.floor(yi)+1][x])	# res -> 0
				else:
					error += np.abs(int(img[math.floor(yi)+1][x]) - (int(res[math.floor(yi)+1][x]) - curInt))
				len_p += 1
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
				error += int(img[y][math.floor(xi)]) 	# res -> 0
			else:
				error += np.abs(int(img[y][math.floor(xi)]) - (int(res[y][math.floor(xi)]) - curInt))
			len_p += 1

			if (curInt != intensity):
				curInt = intensity - curInt
				if (res[y][math.floor(xi)+1] <= curInt):
					error += int(img[y][math.floor(xi)+1])	# res -> 0
				else:
					error += np.abs(int(img[y][math.floor(xi)+1]) - (int(res[y][math.floor(xi)+1]) - curInt))
				len_p += 1
			xi = xi + m

	error /= len_p
	return error

def try_connection(listofargs):
	conn_index = listofargs[0]
	pins = listofargs[1]
	res = listofargs[2]
	img = listofargs[3]
	N = listofargs[4]
	m = listofargs[5]
	L_min = listofargs[6]

	pin_1, pin_2, ftype = find_conn_by_index_coords(conn_index, N, m, L_min, pins)

	new_error = get_error(pin_1, pin_2, ftype, res, img)
	if (0 <= conn_index % 3000 <= 10):
		print(new_error, conn_index)
	return new_error, conn_index

def draw(pin_1, pin_2, f_type, res):
	xk = pin_1[0]
	xn = pin_2[0]
	yk = pin_1[1]
	yn = pin_2[1]
	intensity = 255 #levels of intensity
	# intensity = 255
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

def draw_connection(conn_index, img, res,  N, m, L_min, pins):
	pin_1, pin_2, ftype = find_conn_by_index_coords(conn_index, N, m, L_min, pins)
	draw(pin_1, pin_2, ftype, res)

def draw_image(img, res, conns, pins, N, n, m, L_min):
	try:
		root = Tk()
		w = len(img)
		canvas = Canvas(root,width=w,height=w)
		canvas.pack()
		count = 0

		for j in range(n):
			conn_index = -1
			minerr = -1
			errors = []

			with concurrent.futures.ProcessPoolExecutor() as executor:
				filter = []
				for i in range(N):
					if (conns[i] == 0):
						filter.append([i, pins, res, img, N, m, L_min])
				errors = executor.map(try_connection, filter)
				errors = list(errors)
				errors.sort()
				print("errorlen = ", len(errors))

				if (len(errors) != 0):
					minerr = errors[0][0]
					conn_index = errors[0][1]
					# for er in errors:
					# 	if er[0] < minerr:
					# 		minerr = er[0]
					# 		conn_index = er[1]

					# print('min', minerr, conn_index)
					# exit(0)
					# nperr = np.array(errors, shape=())
					# conn_index = errors.index(min(errors))
					print(f'conn #{conn_index}\t: error = {minerr}')

			if len(errors) == 0:
				break

			conns[conn_index] = 1
			print("drawing ", j, " conn # ", conn_index, " err = ", minerr)
			draw_connection(conn_index, img, res, N, m, L_min, pins)
			show_any_img(root, canvas, res)
			for i in range (len(errors)):
				if (len(errors) - i < 100 or errors[i][0] > 100):
					conns[errors[i][1]] = 2
					print("throwing ", errors[i])

			# conns[conn_index] = 1
			# print("drawing ", conn_index)
			# draw_connection(conn_index, img, res, N, m, L_min, pins)
			# show_any_img(root, canvas, res)

		print(j, "connections are made")
		print("conns\n", conns)
		Image.fromarray(res).save("pics/res_portrait.png")
		count += 1

	except(e):
		print(e)
		Image.fromarray(res).save("pics/res_portrait.png")
		print(count, "connections are made")
		print("conns\n", conns)
