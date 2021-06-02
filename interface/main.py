import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from tkinter import filedialog
import time
import numpy as np
import math
# from functions import *
from f_image import *

def init_log(log_file, level_code):
	logging.basicConfig(
		level=level_code,
		format='%(asctime)s : %(levelname)s : %(message)s',
		handlers=[logging.FileHandler(log_file, "w"),
		logging.StreamHandler()])

class App:
	def __init__ (self):
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
		CANVAS_SIZE = 300
		self.canvas = tk.Canvas(self.root,width=CANVAS_SIZE,height=CANVAS_SIZE, bd=1, relief='ridge')
		self.warninig = tk.Label(self.root, text = "")
		self.timer = tk.Label(self.root, text = "Время генерации: 0 cек")

		self.image_btn = tk.Button(self.root, text="Загрузить изображение", command = lambda: load_image(self))
		self.create_btn = tk.Button(self.root, text="Начать расчет", command=lambda: create_command(self))

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
		self.canvas.grid(row = 1, rowspan = 10, column = 3)
		self.timer.grid(row = 11, rowspan = 1, column = 3)
		self.warninig.grid(row = 12, rowspan = 1, column =3)
		self.space.grid(row=1, column = 2, rowspan = 20)

	def set_test_fields(self):
		self.R_entry.insert(0, "30")
		self.t_entry.insert(0, "0.1")
		self.m_entry.insert(0, "200")


init_log("log.txt", logging.DEBUG)
app = App()
app.set_test_fields()
app.root.mainloop()
