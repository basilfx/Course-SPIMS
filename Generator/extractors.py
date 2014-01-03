from Crypto.Cipher import AES
import struct
from bitstring import BitArray

# Randomly generated by random.org
aes_key = "ea8df4d0b45a757ca65f7e2d80fc9c37".decode("hex")
aes_iv ="e25cac42e472c1a6bc8143959d9cb014".decode("hex")

# Formats the raw input values by concatenating the number strings
def raw(inp):
	return inp

# XORs the raw input value dimensions together
def merged(inp):
	res = list()
	for xs, ys, zs in zip(*[iter(inp)]*3):
		res += "".join(map(lambda (x,y,z): chr(ord(x) ^ ord(y) ^ ord(z)), zip(xs,ys,zs)))

	return res

# Applies an iterated Von Neumann extractor to the input values' dimensions
def von_neumann(inp):
	bitstr = reduce(lambda s, i: s +  "".join([bin(ord(j))[2:] for j in i]), inp)

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

	bytes = [output[x:x+8] for x in range(0, len(output), 8)]
	del bytes[-1]
	return map(lambda b: BitArray(bin=b).bytes, bytes)

def von_neumann2(inp):
	pass

# Applies AES-CBC to each of the inputs in sequence
def aes128_cbc_mac(input):
	aes = AES.new(aes_key, AES.MODE_CBC, aes_iv)
	items = ["".join(input[x:x+16]) for x in range(0, len(input), 16)]
	del items[-1] # Remove last, not aligned block
	enc_items = map(lambda bl: aes.encrypt(bl), items)
	return [byte for byte in "".join(enc_items)]
