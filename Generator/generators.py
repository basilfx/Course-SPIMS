from Crypto.Cipher import AES, SHA256

class SHA256Gen:
	index = 0
	name = "sha256"
	sha256 = SHA256.new()

	def __init__(self, input):
		self.input = input

	def get_rand(self):
		item = input[self.index % len(input)]
		processed = sha256.update(struct.pack('I', merged(input))
		input[self.index] = processed
		return processed
		

class AES128CtrGen:
	counter = 0
	name = "aes128ctr"
	aes = AES.new("xxx", AES.MODE_CTR, counter = lambda: self.counter, block_size = 8)

	def __init__(self, input):
		self.input = input

	def get_rand(self):
		item = input[counter % len(input)]
		processed = aes.encrypt(item)
		self.counter = self.counter + 1 % len(input)
		return processed

class OpenSSLPRNGen:
	prng = pyOpenSSL.rand()
	name = "openssl_prng"

	def __init__(self, input):
		self.input = input
		seed = reduce(lambda (s, item): s + struct.unpack('I', item), input)
		self.prng.seed(seed)

	def get_rand():
		return struct.pack('L', prng.bytes(8))