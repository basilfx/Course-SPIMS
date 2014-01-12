from utils import Chain

import numpy

median = lambda x: sorted(x)[len(x) / 2]

class FuncOutputter(Chain):
    def __init__(self, *chain, **kwargs):
        super(FuncOutputter, self).__init__(*chain, **kwargs)

        self.samples = kwargs.pop("samples", 1000)
        self.func = kwargs.pop("func")

    def start(self, *data):
        super(FuncOutputter, self).start(*data)

        self.input = []
        self.output_bits = bytearray()
        self.func_val = 0
        self.count = 0

    def put(self, size, data):
        if self.count < self.samples:
            self.input.append(data)
            self.count += 1
        else:
            if self.count == self.samples:
                self.func_val = self.func(self.input)
                self.count += 1

            # Output a bit
            if data > self.func_val:
                self.output_bits.append(1 << len(self.output_bits))
            elif data < self.func_val:
                self.output_bits.append(0)

            # Construct a byte
            if len(self.output_bits) == 8:
                byte = sum(self.output_bits)

                for x in self.chain:
                    x.put(byte)

                self.output_bits[:] = bytearray()

def MedianOutputter(*args, **kwargs):
    kwargs["func"] = median
    return FuncOutputter(*args, **kwargs)

def MeanOutputter(*args, **kwargs):
    kwargs["func"] = numpy.mean
    return FuncOutputter(*args, **kwargs)

class RawOutputter(Chain):
    def put(self, size, data):
        for x in self.chain:
            for s in reversed(range(size)):
                x.put((data >> (s * 8)) & 0xFF)

class NoopOutputter(Chain):
    def put(self, size, data):
        for x in self.chain:
            x.put(0xAA)