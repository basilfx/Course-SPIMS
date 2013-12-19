import struct
import hashlib
import random
import binascii
import copy
import functools

aes_key = int("926E99A7AEF8C57456CAE8A99ABB6A9C58677CC6CE3E877E5CAE", 16)

def structurize(func=None, bytes=4, fmt_in="I", fmt_out="I"):
	# Next time we'll be decorating method
	if func is None:
		return functools.partial(structurize, bytes=bytes, fmt_in=fmt_in, fmt_out=fmt_out)

	# Register function property
	func.input_size = bytes

	# Wrap actual method
	@functools.wraps(func)
	def _inner(input):
		return struct.pack(fmt_out, func(struct.unpack(fmt_in, input)))

	# Done
	return _inner

@structurize(bytes=8, fmt_in="II", fmt_out="Q")
def test(input):
	"""
	Consume 8 bytes each time, convert to two integers and return a long
	"""
	return input[0] + input[1]

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