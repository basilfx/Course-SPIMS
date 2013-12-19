import struct
import glob
import os
import hashlib
import random
import binascii
import copy

from parse import parse

aes_key = int("926E99A7AEF8C57456CAE8A99ABB6A9C58677CC6CE3E877E5CAE", 16)

def raw(input):
	result_str = ""
	for i in input:
		result_str += str(i)
	return int(result_str)


def merged(input):
	return reduce(lambda x,y: x ^ y, input)

def sha256(input):
	return int(hashlib.sha256(struct.pack('I', merged(input))).hexdigest(), 16)

def von_neumann(input):
	bitstr = bin(merged(input))[2:]
	cp = copy.deepcopy(bitstr)
	output = ""
	while len(bitstr) > 1:
		current_scope = bitstr[0:2]
		
		if current_scope == "01":
			output += "0"
			bitstr += "1"
		elif current_scope == "10":
			output += "1"
			bitstr += "0"
		elif current_scope == "00":
			bitstr += "0"
		elif current_scope == "11":
			bitstr += "1"

		bitstr = bitstr[2:]

	return int(output, 2)


def von_neumann_sha256(input):
	return int(hashlib.sha256(struct.pack('i', von_neumann(input))).hexdigest(), 16)

def sha256_mersenne(input):
	# We use python's built-in mersenne twister
	random.seed(sha256(input))
	result_str = ""
	for i in range(0, 8):
		result_str += str(random.randint(0, 2**32-1))

	return int(result_str)

def aes128_cbc_mac(input):
	return input

def aes128_cbc_mac_mersenne(input):
	return input

extractors = [ raw, merged, sha256, von_neumann, von_neumann_sha256,
				sha256_mersenne, aes128_cbc_mac, aes128_cbc_mac_mersenne ] 

os.chdir(os.path.dirname(os.path.realpath(__file__)))

for file_name in glob.glob("*.txt"):
	with open(file_name, "r") as input_file:
		next(input_file)
		# Parse device string from line 2
		device_string = next(input_file).strip()
		# Parse generated unique id for device
		device_id = next(input_file).strip()
		# Skip comment line
		next(input_file)

		device_data_dict = dict()

		for line in input_file:
			if ";" in line:
				result = parse("{:d};{:f};{:f};{:f}", line)

				if result:
					timestamp, first, second, third = result
					existing_data = device_data_dict.get((device_string + "_" + device_id), [])
					data = struct.pack('fff', first, second, third)
					existing_data.append(struct.unpack('III', data))
					device_data_dict[(device_string + "_" + device_id)] = existing_data

		for extractor in extractors:
			for device, data in device_data_dict.items():
				name = extractor.__name__

				if not os.path.exists(name):
					os.makedirs(name)

				with open("%s/%s.txt" % (name, device), "w+") as output_file:
					for item in data:
						extractor.cache = 0
						processed = extractor(item)
						print>>output_file, processed