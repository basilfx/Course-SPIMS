from utils import Chain, chunks

class VonNeumannExtractor(Chain):
    def start(self, *data):
        super(VonNeumannExtractor, self).start(*data)

        self.output_bits = bytearray()
        self.extra_bits = bytearray()

    def put(self, byte):
        for i in range(4):
            scope = (byte >> (i * 2)) & 0b11

            if scope == 0b01:
                self.output_bits.append(0)
                self.extra_bits.append(1)
            elif scope == 0b10:
                self.output_bits.append(1 << len(self.output_bits))
                self.extra_bits.append(0)
            elif scope == 0b00:
                self.extra_bits.append(0)
            elif scope == 0b11:
                self.extra_bits.append(1)

            # Output full bytes
            if len(self.output_bits) == 8:
                byte = sum(self.output_bits)

                for x in self.chain:
                    x.put(byte)

                self.output_bits[:] = bytearray()


    def stop(self):
        # Handle the saved bits
        for chunk in chunks(self.extra_bits, 8):
            if len(chunk) == 8:
                byte = sum([ x << i for i, x in enumerate(chunk) ])

                for x in self.chain:
                    x.put(byte)

        # Continue
        return super(VonNeumannExtractor, self).stop()

class RawExtractor(Chain):
    pass