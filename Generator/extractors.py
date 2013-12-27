from Crypto.Cipher import AES

# Formats the raw input values by concatenating the number strings
def raw(input):
	return map(lambda x: int(str(x[0]) + str(x[1]) + str(x[2])), input)

# XORs the raw input value dimensions together
def merged(input):
	return map(lambda x: x[0] ^ x[1] ^ x[2], input)

# Applies an iterated Von Neumann extractor to the input values' dimensions
def von_neumann(input):
	def von_neumann_single(x):
		bitstr = bin(x[0]) + bin(x[1]) + bin(x[2])
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

	return map(von_neumann_single, input)

# Applies AES-CBC to each of the inputs in sequence
def aes128_cbc_mac(input):
	aes = AES.new("xxx", AES.MODE_CBC, block_size = 8)
	items = []
	for item in input:
		input_str = bin(input)
		items += struct.pack("I", aes.encrypt(input_str))

	return items