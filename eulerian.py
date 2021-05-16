import numpy as np
import math
import time
import sys
np.set_printoptions(threshold=sys.maxsize)

def form_pin_conns(m):
	pin_conns = []
	for pin_1 in range(m - 1):
		for pin_2 in range(pin_1 + 1, m):
			pin_conns.append((pin_1, pin_2))
	return np.array(pin_conns)

def set_connections(m):
	N = int(m * (m - 1) / 2)
	connections = np.random.choice(a=[0, 1], size=(N), p=[0.6, 0.4])
	for pin_conn_index in range(len(pin_conns)):
		if (pin_conns[pin_conn_index][0] + 1 == pin_conns[pin_conn_index][1] or (pin_conns[pin_conn_index][0] == 0 and pin_conns[pin_conn_index][1] == m - 1)):
			connections[pin_conn_index] = 0
	return connections

def count_degree(m, pin_conns, connections):
	deg = np.zeros(m, dtype=np.uint8)
	for conn_index in range(len(connections)):
		if (connections[conn_index] == 1):
			pins = pin_conns[conn_index]
			pin_1 = pins[0]
			pin_2 = pins[1]
			deg[pin_1] += 1
			deg[pin_2] += 1
	return deg

def make_circuit(pin_conns, deg, connections):
	odd_pins = np.where(deg % 2 == 1)[0]
	while (len(odd_pins) > 0):
		pin_start, odd_pins = odd_pins[0], odd_pins[1:]
		pin_end, odd_pins = odd_pins[0], odd_pins[1:]
		for pin in range(pin_start, pin_end):
			# connect pin to pin + 1
			for index in range(len(pin_conns)):
				if pin_conns[index][0] == pin and pin_conns[index][1] == pin + 1:
					connections[index] = 1
	return connections


m = 10
pin_conns = form_pin_conns(m)

connections = set_connections(m)
deg = count_degree(m, pin_conns, connections)

###
print(deg)
odd_pins_indexes = np.where(deg % 2 == 1)[0]
print(odd_pins_indexes)
###

connections = make_circuit(pin_conns, deg, connections)

###
print(connections)
print(m, " pins ", len(connections), " possible connections ", np.sum(connections), " connnections made")
deg = count_degree(m, pin_conns, connections)
print(deg)
odd_pins_indexes = np.where(deg % 2 == 1)[0]
print(odd_pins_indexes)
###

