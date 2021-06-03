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
		self.angle_step = -1
		self.c = -1
		self.n = -1
		self.N = -1
		self.Z = -1

		self.length = 0
		self.conns = 0
		self.whole_error = -1

		self.pin_skip = 1
		self.error_check_skip = 0
		self.error_check_step = 1
		self.max_conns = -1
		self.max_conns_flag = 0
		self.if_log = 1
		self.if_show = 1

	def clean(self):
		self.R = -1
		self.t = -1
		self.m = -1

		self.pil_image = None
		self.np_image = None

		self.res = None
		self.pins = None
		self.angle_step = -1
		self.c = -1
		self.n = -1
		self.N = -1
		self.Z = -1

		self.length = 0
		self.conns = 0
		self.whole_error = -1

		self.pin_skip = 1
		self.error_check_skip = 0
		self.error_check_step = 1
		self.max_conns = -1
		self.max_conns_flag = 0
		self.if_log = 1
		self.if_show = 1

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
			self.N = int(self.m * (self.m - 1) / 2)

	def set_num_of_conns_to_check(self):
		logging.info("calculation number of all connections that will be checked (taking into concideration pin_skip parameter")
		if (self.m != -1):
			self.n = int(self.m * (self.m - 2 * self.pin_skip + 1) / 2)

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
			ys = center - (self.Z - 2)/2 * np.sin(angles)
			self.pins = list(map(lambda x,y: (int(x),int(y)), xs,ys))
		self.angle_step = 2 * np.pi / self.m
		self.c = self.R * math.sqrt(2 - 2 * np.cos(self.angle_step))

	def update_stat(self, x0, y0, x1, y1):
		self.length += math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2) * self.t
		self.conns += 1
		logging.info("updates length:" + str(round(self.length / 100, 2)) + " and number of conns: " + str(self.conns))

	def set_max_conns(self, max_conns):
		if max_conns == -1:
			return
		if max_conns < 0 or max_conns > self.N:
			raise ValueError
		self.max_conns = max_conns
		self.max_conns_flag = 1

	def set_pin_skip(self, pin_skip):
		if (pin_skip < 1 or pin_skip > self.m / 2):
			raise ValueError
		self.pin_skip = pin_skip

	def set_error_check_skip(self, error_check_skip):
		if (error_check_skip < 0 or error_check_skip > self.N):
			raise ValueError
		self.error_check_skip = error_check_skip

	def set_error_check_step(self, error_check_step):
		if (error_check_step < 1 or error_check_step > self.N):
			raise ValueError
		self.error_check_step = error_check_step

	def set_if_log(self, if_log):
		self.if_log = if_log

	def set_if_show(self, if_show):
		self.if_show = if_show

	def get_data(self):
		data = ("РЕЗУЛЬТАТ\nРадиус холста: " + str(self.R) + "\n" +
			"Толщина нити: " + str(self.t) + "\n" +
			"Количество гвоздей: " + str(self.m) + "\n\n" +
			"Количество всех возможных соединений: " + str(self.N) + "\n" +
			"Количество рассмотренных соединений: " + str(self.n) + "\n" +
			"Количество проведенных соединений: " + str(self.conns) + "\n\n" +
			"Разрешение изображения: " + str(self.Z) + " x " + str(self.Z) + "пикселей\n\n" +
			"Требуемая длина нити: " + str(round(self.length / 100, 2)) + " m\n" +
			"Расстрояние между гвоздями: " + str(round(self.c, 3)) + "; угловой шаг: " + str(round(self.angle_step, 3)) + "\n\n"
			"Общая ошибка: " + str(round(self.whole_error, 2)) + " (" + str(round(100 - self.whole_error / 255 * 100, 2)) + ") %\n")
		if self.if_log:
			data += "Логгирование включено\n"
		else:
			data += "Логгирование отключено\n"
		if self.if_show:
			data += "Отображение процесса генерации включено\n"
		else:
			data += "Отображение процесса генерации отключено\n"
		if (self.max_conns_flag):
			data += ("Было отрисовано " + str(self.max_conns) + " соединений без проверки ошибки в процессе\n")
		else:
			if (self.pin_skip != 1):
				data += "Количество гвоздей, пропускаемое при кротчайшей хорде: " + str(self.pin_skip) + "\n"
			if (self.error_check_skip != 0):
				data += "Количество соединений, отрисованное без проверки: " + str(self.error_check_skip) + "\n"
			if (self.error_check_step != 1):
				"Общая ошибка проверялась каждые " + str(self.error_check_step) + " соединений\n"

		return data

	def log_data(self):
		data = self.get_data()
		logging.info(data)

class App:
	def __init__ (self):
		self.stringart = String_art()

		self.root = tk.Tk()
		self.root.title("string art")

		# init widgets
		self.label = tk.Label(self.root, text = "Генерация схемы стринг-арта", font='Helvetica 18 bold')
		self.space = tk.Label(self.root, justify="left", anchor="w", text = "   ")

		self.R_label = tk.Label(self.root, justify="left", anchor="w", text = "Радиус холста (см): ")
		self.R_entry = tk.Entry()

		self.t_label = tk.Label(self.root, justify="left", anchor="w", text = "Толщина нити (см): ")
		self.t_entry = tk.Entry()

		self.m_label = tk.Label(self.root, justify="left", anchor="w", text = "Количество гвоздей: ")
		self.m_entry = tk.Entry()

		self.param_label = tk.Label(self.root, justify="left", anchor="w", text = "Дополнительные параметры:", font='Helvetica 12 bold')

		self.log_checkbox_var = tk.IntVar(value=1)
		self.log_checkbox = tk.Checkbutton(self.root, text='Включить логирование',variable=self.log_checkbox_var, onvalue=1, offvalue=0)

		self.show_checkbox_var = tk.IntVar(value=1)
		self.show_checkbox = tk.Checkbutton(self.root, text='Показывать процесс генерации',variable=self.show_checkbox_var, onvalue=1, offvalue=0)

		self.pin_skip_label = tk.Label(self.root, justify="left", anchor="w", text = "Количество гвоздей, пропускаемое при кротчайшей хорде: ")
		self.pin_skip_entry = tk.Entry()
		self.pin_skip_entry.insert(0, "1")

		self.error_check_skip_label = tk.Label(self.root, justify="left", anchor="w", text = "Количество соединений, отрисованное без проверки: ")
		self.error_check_skip_entry = tk.Entry()
		self.error_check_skip_entry.insert(0, "0")

		self.error_check_step_label = tk.Label(self.root, justify="left", anchor="w", text = "Шаг проверки ошибки: ")
		self.error_check_step_entry = tk.Entry()
		self.error_check_step_entry.insert(0, "1")

		self.max_conns_label = tk.Label(self.root, justify="left", anchor="w", text = "Максимальное количество соединений: ")
		self.max_conns_entry = tk.Entry()
		self.max_conns_entry.insert(0, "не учитывается")

		self.output_label = tk.Label(self.root, justify="left", anchor="w", text = "")

		CANVAS_SIZE = 400
		self.canvas = tk.Canvas(self.root,width=CANVAS_SIZE,height=CANVAS_SIZE, bd=1, relief='ridge')

		self.warninig = tk.Label(self.root, justify="left", anchor="w", text = "")

		self.timer = tk.Label(self.root, justify="left", anchor="w", text = "Время генерации: 0 cек")

		self.image_btn = tk.Button(self.root, text="Загрузить изображение", command = lambda: load_image([app]))
		self.create_btn = tk.Button(self.root, text="Начать расчет", command= lambda: create_command([app]))


		# show widgets
		self.label.grid(row=0, column=0, columnspan=3)
		self.space.grid(row=1, column = 2, rowspan = 20)

		self.R_label.grid(sticky = "W", row=1, column=0)
		self.R_entry.grid(row=1, column=1)

		self.t_label.grid(sticky = "W", row=2, column=0)
		self.t_entry.grid(row=2, column=1)

		self.m_label.grid(sticky = "W", row=3, column=0)
		self.m_entry.grid(row=3, column=1)

		self.param_label.grid(row = 4, column = 0, columnspan = 2)

		self.pin_skip_label.grid(sticky = "W", row = 5, column = 0)
		self.pin_skip_entry.grid(row = 5, column = 1)

		self.error_check_skip_label.grid(sticky = "W", row = 6, column = 0)
		self.error_check_skip_entry.grid(row = 6, column = 1)

		self.error_check_step_label.grid(sticky = "W", row = 7, column = 0)
		self.error_check_step_entry.grid(row = 7, column = 1)

		self.max_conns_label.grid(sticky = "W", row = 8, column = 0)
		self.max_conns_entry.grid(row = 8, column = 1)

		self.log_checkbox.grid(sticky = "W", row = 9, column = 0)
		self.show_checkbox.grid(sticky = "W", row = 10, column = 0)

		self.image_btn.grid(row=9, column=1)
		self.create_btn.grid(row=10, column=1)
		self.output_label.grid(sticky = "W", row=11, column=0, columnspan=3)
		self.canvas.grid(row = 1, rowspan = 15, column = 3)
		self.timer.grid(row = 16, rowspan = 1, column = 3)
		self.warninig.grid(row = 17, rowspan = 1, column =3)

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
