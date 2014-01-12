from utils import Chain, crc32

import hashlib

class DummyGenerator(Chain):
    pass

class SHA1Generator(Chain):
    def start(self, *data):
        super(SHA1Generator, self).start(*data)

        self.bytes = bytearray()
        self.last_hash = None

    def put(self, byte):
        if len(self.bytes) < 20:
            if self.last_hash is None:
                self.bytes.append(byte)
            else:
                self.bytes.append(byte ^ self.last_hash[len(self.bytes)])

        if len(self.bytes) == 20:
            self.last_hash = bytearray(hashlib.sha1(self.bytes).digest())
            self.bytes[:] = bytearray()

            for byte in self.last_hash:
                for x in self.chain:
                    x.put(byte)

class CRC32Generator(Chain):
    def start(self, *data):
        super(CRC32Generator, self).start(*data)

        self.bytes = bytearray()

    def put(self, byte):
        if len(self.bytes) < 8:
            self.bytes.append(byte)

        if len(self.bytes) == 8:
            hash = crc32(self.bytes)

            for x in self.chain:
                for i in range(4):
                    x.put((byte >> (i * 8)) & 0xFF)

            self.bytes[:] = bytearray()

