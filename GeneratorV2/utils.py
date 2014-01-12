import struct
import collections

struct_int = struct.Struct("i")
struct_float = struct.Struct("f")

CRC32_POLYNOMIAL = 0x11EDC6F41
CRC32_INITIAL = 0x00000000L

def crc32(buf):
    result = CRC32_INITIAL

    def crc32_value(c):
        ulTemp1 = (result >> 8) & 0x00FFFFFFl
        ulCRC = (result ^ c) & 0xff

        for i in range(8):
            if ulCRC & 0x01:
                ulCRC = (ulCRC >> 1) ^ CRC32_POLYNOMIAL
            else:
                ulCRC = ulCRC >> 1

        return ulTemp1 ^ ulCRC

    # Execute above function for each byte
    for b in buf:
        result = crc32_value(b)

    # Done
    return result

def flatten(l):
    for el in l:
        if isinstance(el, list):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def float_to_raw(value):
    return int(float(value) / 9.81)

def intfloat_to_raw(value):
    return int(struct_float.unpack(struct_int.pack(int(value)))[0] / 9.81)

def float_to_int(value):
    return struct_int.unpack(struct_float.pack(float(value)))[0]

class Chain(object):
    def __init__(self, *chain, **kwargs):
        self.chain = chain

    def start(self, *data):
        for x in self.chain:
            x.start(*data)

    def stop(self):
        return [ x.stop() for x in self.chain ]

    def put(self, *data):
        for x in self.chain:
            x.put(*data)