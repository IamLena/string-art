from PIL import Image, ImageTk, ImageDraw
from tkinter import Tk
from tkinter.ttk import Frame, Label
import sys
import numpy

PPLINE = 600
pic_path = 'pics/portrait.jpg'

def crop(photo):
	circlecrop = Image.new('L', [PPLINE, PPLINE], 255)
	circle = ImageDraw.Draw(circlecrop)
	circle.pieslice([0, 0, PPLINE, PPLINE], 0, 360, fill=0)
	npcrop = numpy.array(circlecrop).reshape(PPLINE * PPLINE)

	npimage = numpy.array(photo).reshape(PPLINE * PPLINE)
	for i in range(len(npcrop)):
		if (npcrop[i]):
			npimage[i] = 255
	return Image.fromarray(npimage.reshape((PPLINE, PPLINE)))

def photo_manipulating(filename):
	image = Image.open(filename)
	print("image loaded")
	if image.size[0] < image.size[1]: side = image.size[0]
	else: side = image.size[1]
	image.crop((0, 0, side, side))
	print("image cropped as a square from (0,0) to min side")
	image = image.convert('L')
	print("image converted to greyscale")
	image = image.resize((PPLINE, PPLINE), Image.ANTIALIAS)
	print("image's resolution downgraded")
	image = crop(image)
	print("image's cropped to circle")
	return image

def tk_showimage(image):
	root = Tk()
	frame = Frame()
	tkimage = ImageTk.PhotoImage(image)
	label = Label(frame, image=tkimage)
	label.image = tkimage
	label.pack()
	frame.pack()
	root.mainloop()

tk_showimage(photo_manipulating(pic_path))
