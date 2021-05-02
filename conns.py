NUM_OF_PINS = 16
MIN_CONN_LEN = 4
ONE_TYPE_COUNT = NUM_OF_PINS * (NUM_OF_PINS - 1 - 2 * (MIN_CONN_LEN - 1)) / 2
MAX_PINS_IN_LINE = NUM_OF_PINS - 2 * MIN_CONN_LEN + 1
NUM_OF_CONNS = 2 * NUM_OF_PINS * (NUM_OF_PINS - 1 - 2 * (MIN_CONN_LEN - 1))

connections = []
index = 0
for type in range(4):
	for pin_1 in range(NUM_OF_PINS - MIN_CONN_LEN):
		ends = NUM_OF_PINS + pin_1 - 2 * (MIN_CONN_LEN - 1) + 2 + 1
		if (ends >= NUM_OF_PINS):
			ends = NUM_OF_PINS
		# print("ends", ends)
		for pin_2 in range (pin_1 + MIN_CONN_LEN, ends):
			# print(index, ":", pin_1, pin_2, type)
			connections.append([pin_1, pin_2, type])
			index += 1

assert(NUM_OF_CONNS == len(connections))

# index = 44
# print("target", connections[index])
# print("ONE_TYPE_COUNT", ONE_TYPE_COUNT, "MAX_PINS_IN_LINE", MAX_PINS_IN_LINE)
# print("MAX_PINS_IN_LINE * MIN_CONN_LEN", MAX_PINS_IN_LINE * MIN_CONN_LEN)

def find_conn_by_index(index, log = 0):

	f_type = index // ONE_TYPE_COUNT
	part_index = index % ONE_TYPE_COUNT
	if (log):
		print("part_index", part_index)
	if part_index < MAX_PINS_IN_LINE * MIN_CONN_LEN:
		pin_1 = part_index // MAX_PINS_IN_LINE
		pin_2 = pin_1 + MIN_CONN_LEN + (part_index % MAX_PINS_IN_LINE)
	else:
		pin_1 = MIN_CONN_LEN
		part_index -= MAX_PINS_IN_LINE * MIN_CONN_LEN
		max_pins_in_this_line = MAX_PINS_IN_LINE - 1
		if (log):
			print("pin_1", pin_1, "part_index", part_index, "max_pins_in_this_line", max_pins_in_this_line)
		while (part_index >= max_pins_in_this_line):
			part_index -= max_pins_in_this_line
			max_pins_in_this_line -= 1
			pin_1 += 1
			if (log):
				print("pin_1", pin_1, "part_index", part_index, "max_pins_in_this_line", max_pins_in_this_line)
		pin_2 = pin_1 + MIN_CONN_LEN + (part_index % max_pins_in_this_line)
	return([pin_1, pin_2, f_type])

def test():
	for index in range (NUM_OF_CONNS):
		my_res = find_conn_by_index(index)
		if connections[index] != my_res:
			print(index)
			print("target: ", connections[index])
			print("my: ", my_res)


