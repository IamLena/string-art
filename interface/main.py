import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from tkinter import filedialog
import time
import numpy as np
import math
import logging
from f_image import *
from generate import *

class String_art:
	def __init__ (self):
		self.R = -1
		self.t = -1
		self.m = -1
		self.pil_image = None
		self.np_image = None
		self.res = None
		self.pins = None
		self.N = -1
		self.Z = -1
		self.length = 0
		self.conns = 0
		self.skip = 1
		self.whole_error = -1

	def set_radius(self, R):
		if (R <= 0):
			raise ValueError
		self.R = R

	def set_thread(self, t):
		if (t <= 0):
			raise ValueError
		self.t = t

	def set_num_of_pins(self, m):
		if (m < 2):
			raise ValueError
		self.m = m

	def set_resolution(self):
		logging.info("calculation resolution")
		if (self.R != -1 and self.t != -1):
			self.Z = int(2 * self.R / self.t)

	def set_num_of_all_conns(self):
		logging.info("calculation number of all possible connections")
		if (self.m != -1):
			self.N = int(self.m * (self.m - 2 * self.skip + 1) / 2)

	def parse_image(self):
		logging.info("parsing input image")
		self.np_image = parse_pil_image(self.pil_image, self.Z)

	def set_result(self):
		logging.info("filling result matrix")
		self.res = np.full((self.Z, self.Z), 255, dtype=np.uint8)

	def set_pins(self):
		logging.info("filling pins coordinates")
		if (self.m != -1 and self.Z != -1):
			angles = np.linspace(0, 2*np.pi, self.m)
			center = self.Z / 2
			xs = center + (self.Z - 2)/2 * np.cos(angles)
			ys = center + (self.Z - 2)/2 * np.sin(angles)
			self.pins = list(map(lambda x,y: (int(x),int(y)), xs,ys))

	def update_stat(self, x0, y0, x1, y1):
		logging.info("updates length and number of conns")
		self.length += math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2) * self.t
		self.conns += 1

	def log_data(self):
		logging.info(
			"Радиус холста: " + str(self.R) + "\n" +
			"Толщина нити: " + str(self.t) + "\n" +
			"Количество гвоздей" + str(self.m) + "\n" +
			"Количество всех возможных соединений: " + str(self.N) + "\n" +
			"Разрешение: " + str(self.Z) + "\n" +
			"Длина нити: " + str(self.length) + "\n" +
			"Количество проведенных соединений: " + str(self.conns) + "\n" +
			"Количество гвоздей пропускаемое при минимальной хорде" + str(self.skip) + "\n" +
			"Общая ошибка: " + str(self.whole_error) + " " + str(100 - self.whole_error / 255 * 100) + " %"
		)

	def get_data(self):
		return ("Результат\nРадиус холста: " + str(self.R) + "\n" +
			"Толщина нити: " + str(self.t) + "\n" +
			"Количество гвоздей" + str(self.m) + "\n" +
			"Количество всех возможных соединений: " + str(self.N) + "\n" +
			"Разрешение: " + str(self.Z) + "\n" +
			"Длина нити: " + str(round(self.length / 100, 2)) + "m\n" +
			"Количество проведенных соединений: " + str(self.conns) + "\n" +
			"Количество гвоздей пропускаемое при минимальном соединении: " + str(self.skip) + "\n" +
			"Общая ошибка: " + str(round(self.whole_error, 2)) + " " + str(round(100 - self.whole_error / 255 * 100, 2)) + " %")


class App:
	def __init__ (self):
		self.stringart = String_art()

		self.root = tk.Tk()
		self.root.title("string art")

		# init widgets
		self.label = tk.Label(self.root, text = "Генерация схемы стринг-арта", font='Helvetica 18 bold')
		self.space = tk.Label(self.root, text = "   ")
		self.R_label = tk.Label(self.root, text = "Радиус холста (см) - R: ")
		self.R_entry = tk.Entry()
		self.t_label = tk.Label(self.root, text = "Толщина нити (см) - t: ")
		self.t_entry = tk.Entry()
		self.m_label = tk.Label(self.root, text = "Количество гвоздей - m: ")
		self.m_entry = tk.Entry()
		self.output_label = tk.Label(self.root, text = "")
		CANVAS_SIZE = 300
		self.canvas = tk.Canvas(self.root,width=CANVAS_SIZE,height=CANVAS_SIZE, bd=1, relief='ridge')
		self.warninig = tk.Label(self.root, text = "")
		self.timer = tk.Label(self.root, text = "Время генерации: 0 cек")

		self.image_btn = tk.Button(self.root, text="Загрузить изображение", command = lambda: load_image([app]))
		self.create_btn = tk.Button(self.root, text="Начать расчет", command= lambda: create_command([app]))

		# show widgets
		self.label.grid(row=0, column=0, columnspan=3)
		self.R_label.grid(row=1, column=0)
		self.R_entry.grid(row=1, column=1)
		self.t_label.grid(row=2, column=0)
		self.t_entry.grid(row=2, column=1)
		self.m_label.grid(row=3, column=0)
		self.m_entry.grid(row=3, column=1)
		self.image_btn.grid(row=4, column=0, columnspan=3)
		self.create_btn.grid(row=5, column=0, columnspan=3)
		self.output_label.grid(row=6, column=0, columnspan=3)
		self.canvas.grid(row = 1, rowspan = 10, column = 3)
		self.timer.grid(row = 11, rowspan = 1, column = 3)
		self.warninig.grid(row = 12, rowspan = 1, column =3)
		self.space.grid(row=1, column = 2, rowspan = 20)

	def set_test_fields(self):
		self.R_entry.insert(0, "30")
		self.t_entry.insert(0, "0.1")
		self.m_entry.insert(0, "200")


def init_log(log_file, level_code):
	logging.basicConfig(
		level=level_code,
		format='%(asctime)s : %(levelname)s : %(message)s',
		handlers=[logging.FileHandler(log_file, "w"),
		logging.StreamHandler()])

init_log("log.txt", logging.DEBUG)
app = App()

app.set_test_fields()
app.root.mainloop()
