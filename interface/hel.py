import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from tkinter import filedialog
import time

root = tk.Tk()
root.title("string art")

# init widgets
label = tk.Label(root, text = "Генерация схемы стринг-арта", font='Helvetica 18 bold')
space = tk.Label(root, text = "   ")
R_label = tk.Label(root, text = "Радиус холста (см) - R: ")
R_entry = tk.Entry()
t_label = tk.Label(root, text = "Толщина нити (см) - t: ")
t_entry = tk.Entry()
m_label = tk.Label(root, text = "Количество гвоздей - m: ")
m_entry = tk.Entry()
canvas_size = 300
canvas = tk.Canvas(root,width=canvas_size,height=canvas_size, bd=1, relief='ridge')
warninig = tk.Label(root, text = "")
timer = tk.Label(root, text = "Время генерации: 0 cек")

image = None

#for test
R_entry.insert(0, "1")
t_entry.insert(0, "2")
m_entry.insert(0, "3")

def update_clock(sec):
	sec += 1
	timer.configure(text="Время генерации: " + str(sec) + " сек")
	root.after(1000, lambda: update_clock(sec))

def load_image():
	print("loading image")
	global image
	image_path = filedialog.askopenfilename(filetypes=[('.png', '.jpg')])
	print(image_path)
	if (image_path == ""):
		return
	image = Image.open(image_path)

	# square crop
	if image.size[0] != image.size[1]:
		if image.size[0] < image.size[1]:
			side = image.size[0]
		else:
			side = image.size[1]
		left = (image.size[0] - side) / 2
		top = (image.size[1] - side) / 2
		right = (image.size[0] + side) / 2
		bottom = (image.size[1] + side) / 2
		image = image.crop((left, top, right, bottom))

	resized_img = image.resize((canvas_size, canvas_size), Image.ANTIALIAS)
	image = ImageTk.PhotoImage(resized_img)
	imagesprite = canvas.create_image(0, 0, image=image, anchor='nw')
	root.update()

	print(filename)

def generate(R, t, m):
	print("generate", R, t, m)
	# time.sleep(20)
	return

def create_comamnd(create_btn, image_btn):
	try:
		R = float(R_entry.get())
		t = float(t_entry.get())
		m = int(m_entry.get())
		if (m < 2):
			raise ValueError
		if not image:
			warninig.configure(text = "Сначала загрузите изображение")
			return
		warninig.configure(text = "")
		create_btn.configure(state="disable")
		image_btn.configure(state="disable")
		update_clock(-1)
		generate(R, t, m)
		dir = filedialog.askdirectory(title="Chose directory to save results in")
		print(dir)
		create_btn.configure(state="normal")
		image_btn.configure(state="normal")

	except ValueError:
		warninig.configure(text = "Некорректный ввод (проверьте, что R > 0, t > 0, m > 1)")


image_btn = tk.Button(root, text="Загрузить изображение", command = load_image)
create_btn = tk.Button(root, text="Начать расчет", command=lambda : create_comamnd(create_btn, image_btn))

# show widgets
label.grid(row=0, column=0, columnspan=3)
R_label.grid(row=1, column=0)
R_entry.grid(row=1, column=1)
t_label.grid(row=2, column=0)
t_entry.grid(row=2, column=1)
m_label.grid(row=3, column=0)
m_entry.grid(row=3, column=1)
image_btn.grid(row=4, column=0, columnspan=3)
create_btn.grid(row=5, column=0, columnspan=3)
canvas.grid(row = 1, rowspan = 10, column = 3)
timer.grid(row = 11, rowspan = 1, column = 3)
warninig.grid(row = 12, rowspan = 1, column =3)
space.grid(row=1, column = 2, rowspan = 20)

root.mainloop()
