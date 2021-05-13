NUM_OF_PINS = 20
MIN_CONN_LEN = 6
ONE_TYPE_COUNT = NUM_OF_PINS * (NUM_OF_PINS - 1 - 2 * (MIN_CONN_LEN - 1)) / 2
MAX_PINS_IN_LINE = NUM_OF_PINS - 2 * MIN_CONN_LEN + 1
NUM_OF_CONNS = 2 * NUM_OF_PINS * (NUM_OF_PINS - 1 - 2 * (MIN_CONN_LEN - 1))

connections = []
index = 0
for type in range(4):
	for pin_1 in range(NUM_OF_PINS - MIN_CONN_LEN):
		ends = pin_1 + MIN_CONN_LEN + MAX_PINS_IN_LINE
		if (ends >= NUM_OF_PINS):
			ends = NUM_OF_PINS
		for pin_2 in range (pin_1 + MIN_CONN_LEN, ends):
			# print(index, ":", pin_1, pin_2, type)
			connections.append([pin_1, pin_2, type])
			index += 1


assert(NUM_OF_CONNS == len(connections))

def find_conn_by_index(index):
	f_type = index // ONE_TYPE_COUNT
	part_index = index % ONE_TYPE_COUNT
	if part_index < MAX_PINS_IN_LINE * MIN_CONN_LEN:
		pin_1 = part_index // MAX_PINS_IN_LINE
		pin_2 = pin_1 + MIN_CONN_LEN + (part_index % MAX_PINS_IN_LINE)
	else:
		pin_1 = MIN_CONN_LEN
		part_index -= MAX_PINS_IN_LINE * MIN_CONN_LEN
		max_pins_in_this_line = MAX_PINS_IN_LINE - 1
		while (part_index >= max_pins_in_this_line):
			part_index -= max_pins_in_this_line
			max_pins_in_this_line -= 1
			pin_1 += 1
		pin_2 = pin_1 + MIN_CONN_LEN + (part_index % max_pins_in_this_line)
	return([pin_1, pin_2, f_type])

def find_index_by_pins(pin_1, pin_2, type, log = 0):
	if (pin_1 > pin_2):
		pin_1, pin_2 = pin_2, pin_1
		# types switch, changing direction!
	if (pin_1 < MIN_CONN_LEN):
		if (pin_2 >= pin_1 + MIN_CONN_LEN and pin_2 <= NUM_OF_PINS + pin_1 - MIN_CONN_LEN + 1):
			one_type_index = pin_1 * MAX_PINS_IN_LINE + pin_2 - MIN_CONN_LEN - pin_1
			return one_type_index + ONE_TYPE_COUNT * type
		else:
			return -1
	if (pin_2 >= pin_1 + MIN_CONN_LEN and pin_2 < NUM_OF_PINS):
		index = MAX_PINS_IN_LINE * MIN_CONN_LEN
		max_pins_in_this_line = MAX_PINS_IN_LINE - 1
		found_pin = MIN_CONN_LEN
		while (found_pin != pin_1):
			found_pin += 1
			index += max_pins_in_this_line
			max_pins_in_this_line -= 1
		return (index + pin_2 - MIN_CONN_LEN - pin_1) + ONE_TYPE_COUNT * type
	else:
		return -1


def test_1():
	for index in range (NUM_OF_CONNS):
		my_res = find_conn_by_index(index)
		if connections[index] != my_res:
			print(index)
			print("target: ", connections[index])
			print("my: ", my_res)

def test_2():
	for index in range (NUM_OF_CONNS):
		conn = connections[index]
		res = find_index_by_pins(conn[0], conn[1], conn[2])
		if (index != res):
			print(conn)
			print("target: ", index)
			print("my: ", res)

test_1()
test_2()
