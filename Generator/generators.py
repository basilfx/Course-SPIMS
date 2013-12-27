from Crypto.Cipher import AES
from Crypto.Hash import SHA256

class SHA256Gen:
	name = "sha256"

	def __init__(self, input):
		self.input = input
		self.sha256 = SHA256.new()

	def get_rand(self):
		item = input[self.index % len(input)]
		processed = self.sha256.update(struct.pack('I', merged(input)))
		input[self.index] = processed
		return processed
		

class AES128CtrGen:
	name = "aes128ctr"
	
	def __init__(self, input):
		self.input = input
		self.counter = 0
		self.aes = AES.new("xxx", AES.MODE_CTR, counter = lambda: self.counter, block_size = 8)

	def get_rand(self):
		item = input[self.counter % len(self.input)]
		processed = self.aes.encrypt(item)
		self.counter = self.counter + 1 % len(self.input)
		return processed

class OpenSSLPRNGen:
	name = "openssl_prng"

	def __init__(self, input):
		seed = reduce(lambda (s, item): s + struct.unpack('I', item), input)
		self.prng = pyOpenSSL.rand()
		self.prng.seed(seed)

	def get_rand():
		return struct.pack('L', self.prng.bytes(8))