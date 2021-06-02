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

	def set_radius(R):
		if (R <= 0):
			raise ValueError
		self.R = R

	def set_thread(t):
		if (t <= 0):
			raise ValueError
		self.t = t

	def set_num_of_pins(m):
		if (m < 2):
			raise ValueError
		self.m = m

	def set_resolution():
		if (self.R != -1 and self.t != -1):
			self.Z = int(2 * R / t)

	def set_num_of_all_conns():
		if (m != -1):
			N = int(self.m * (self.m - 2 * self.skip + 1) / 2)

	def parse_image():
		self.np_image = parse_pil_image(self.pil_image, self.Z)

	def set_result():
		self.res = np.full((Z, Z), 255, dtype=np.uint8)

	def set_pins():
		if (self.m != -1 and self.Z != -1):
			angles = np.linspace(0, 2*np.pi, self.m)
			center = self.Z / 2
			xs = center + (self.Z - 2)/2 * np.cos(angles)
			ys = center + (self.Z - 2)/2 * np.sin(angles)
			self.pins = list(map(lambda x,y: (int(x),int(y)), xs,ys))

	def update_stat(x0, y0, x1, y1):
		self.length += math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2) * self.t
		self.conns += 1
