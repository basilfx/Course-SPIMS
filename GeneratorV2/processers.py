
from utils import Chain

import collections

class DefaultProcessor(Chain):
    def put(self, size, a, b, c):
        for x in self.chain:
            x.put(size, a)
            x.put(size, b)
            x.put(size, c)

class DiffProcessor(Chain):
    def start(self, *data):
        super(DiffProcessor, self).start(*data)

        self.first = True

    def put(self, size, a, b, c):
        if self.first:
            self.first = False
        else:
            for x in self.chain:
                x.put(size, abs(self.a - a))
                x.put(size, abs(self.b - b))
                x.put(size, abs(self.c - c))

        self.a = a
        self.b = b
        self.c = c

class XorProcessor(Chain):
    def put(self, size, a, b, c):
        for x in self.chain:
            x.put(size, a ^ b ^ c)

class RunningXorProcessor(Chain):
    def start(self, *data):
        super(RunningXorProcessor, self).start(*data)

        self.previous = 0

    def put(self, size, a, b, c):
        self.previous = self.previous ^ a ^ b ^ c

        for x in self.chain:
            x.put(size, self.previous)