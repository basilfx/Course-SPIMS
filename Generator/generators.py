from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import struct

# Generates a random number by making a number of the SHA-256
# hash for each of the extracted inputs
class SHA256Gen:
	name = "sha256"

	def __init__(self, input):
		self.input = input
		self.sha256 = SHA256.new()
		self.index = 0

	def get_rand(self):
		item = self.input[self.index]
		hx = '%x' % item
		bytes = ('0'*(len(hx) % 2) + hx).decode('hex')
		self.sha256.update(bytes)
		processed = int(self.sha256.hexdigest(), 16)
		self.input[self.index] = processed
		self.index = (self.index + 1) % len(self.input)
		return processed
		
# Generates a random number by applying the AES counter cipher to the
# sequence of extracted inputs
class AES128CtrGen:
	name = "aes128_ctr"
	
	def __init__(self, input):
		self.input = input
		self.counter = 0
		self.aes = AES.new("xxx", AES.MODE_CTR, counter = lambda: self.counter, block_size = 8)

	def get_rand(self):
		item = input[self.counter % len(self.input)]
		processed = self.aes.encrypt(item)
		self.counter = self.counter + 1 % len(self.input)
		return processed

# Generates random numbers by using the OpenSSL pseudorandom number
# generator with the entropy coming from the extracted randomness
class OpenSSLPRNGen:
	name = "openssl_prng"

	def __init__(self, input):
		seed = reduce(lambda (s, item): s + struct.unpack('I', item), input)
		self.prng = pyOpenSSL.rand()
		self.prng.seed(seed)

	def get_rand():
		return struct.pack('L', self.prng.bytes(8))