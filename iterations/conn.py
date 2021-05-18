def find_index_by_pins(pin_1, pin_2, type, N, m, L_min):
	one_type_count = N / 4
	max_pins_in_line = m - 2 * L_min + 1

	if (pin_1 > pin_2):
		pin_1, pin_2 = pin_2, pin_1
		if (type == 0):
			type = 2
		elif (type == 2):
			type = 0
	if (pin_1 < L_min):
		if (pin_2 >= pin_1 + L_min and pin_2 <= N + pin_1 - L_min + 1):
			one_type_index = pin_1 * max_pins_in_line + pin_2 - L_min - pin_1
			return one_type_index + one_type_count * type
		else:
			return -1
	if (pin_2 >= pin_1 + L_min and pin_2 < N):
		index = max_pins_in_line * L_min
		max_pins_in_this_line = max_pins_in_line - 1
		found_pin = L_min
		while (found_pin != pin_1):
			found_pin += 1
			index += max_pins_in_this_line
			max_pins_in_this_line -= 1
		return (index + pin_2 - L_min - pin_1) + one_type_count * type
	else:
		return -1

def find_conn_by_index(index, N, m, L_min):
	one_type_count = N / 4
	max_pins_in_line = m - 2 * L_min + 1

	f_type = index // one_type_count
	part_index = index % one_type_count
	if part_index < max_pins_in_line * L_min:
		pin_1 = part_index // max_pins_in_line
		pin_2 = pin_1 + L_min + (part_index % max_pins_in_line)
	else:
		pin_1 = L_min
		part_index -= max_pins_in_line * L_min
		max_pins_in_this_line = max_pins_in_line - 1
		while (part_index >= max_pins_in_this_line):
			part_index -= max_pins_in_this_line
			max_pins_in_this_line -= 1
			pin_1 += 1
		pin_2 = pin_1 + L_min + (part_index % max_pins_in_this_line)
	return pin_1, pin_2, f_type

def find_conn_by_index_coords(index, N, m, L_min, pins):
	conn = find_conn_by_index(index, N, m, L_min)
	pin_coords_1 = pins[int(conn[0])]
	pin_coords_2 = pins[int(conn[1])]
	ftype = pins[int(conn[2])]
	return pin_coords_1, pin_coords_2, ftype
