import numpy
import sys
import os
import glob
import random
import struct
import collections
import itertools

class Shaker(object):
    def __init__(self):
        self.last_time = 0
        self.last_shake = 0
        self.last_force = 0

        self.last_x = 0
        self.last_y = 0
        self.last_z = 0

        self.shake_count = 0

        self.seeds = []

    def shake(self, timestamp, x, y, z):
        l1 = timestamp

        if (l1 - self.last_force) > 500:
            self.shake_count = 0

        if (l1 - self.last_time) > 100:
            l2 = float(l1 - self.last_time)

            if (10000.0 * abs(x + y + z - self.last_x - self.last_y - self.last_z) / l2) > 350.0:
                i = 1 + self.shake_count
                self.shake_count = i

                if (i >= 1) and (l1 - self.last_shake) > 100:
                    self.last_shake = l1
                    self.shake_count = 0
                    self.last_force = l1

                    # Pass on
                    self.on_shake(x, y, z)

            self.last_time = l1
            self.last_x = x
            self.last_y = y
            self.last_z = z

    def on_shake(self, x, y, z):
        sys.stdout.write("Hit: X=%.2f Y=%.2f Z=%.2f\n" % (x, y, z))

        seed = int(1000.0 * x + 700.0 * y + 800.0 * z)
        self.seeds.append(seed)

def shake_iterator():
    timestamp = 0
    time_step = 250
    steps = [-10.0000, 5.0000, 3.0000, 0]
    steps = [-10.0001, 5.0002, 3.0003, 0]

    for i in range(len(steps)):
        value = steps[i % len(steps)]
        yield timestamp, value, value, value

        timestamp += time_step * random.random()

def attempt():
    shaker = Shaker()

    # Shake
    for t, x, y, z in shake_iterator():
        shaker.shake(t, x, y, z)

    # Print stats
    print collections.Counter(shaker.seeds)

def main(argv):
    if len(argv) != 2:
        sys.stdout.write("Syntax: %s <input>\n" % argv[0])
        return 1

    input_file = argv[1]

    # Find files
    if os.path.isfile(input_file):
        global_stats = False
        input_files = [ os.path.abspath(input_file) ]
    else:
        global_stats = True
        input_files = glob.glob(os.path.join(input_file, "*.txt"))

    # Shake all files
    shakers = []

    for input_file in input_files:
        # Construct shaker
        shaker = Shaker()

        # Read file and feed it to the shaker
        with open(input_file, "r") as fp:
            # Parse file type
            file_type = fp.readline().strip()

            if file_type == "# General":
                mapper = float
                factor = 1000000
            if file_type == "# GeneralV2":
                mapper = lambda x: struct.unpack("f", struct.pack("i", int(x)))[0]
                factor = 1000000
            elif file_type == "# Raw":
                mapper = lambda x: int(x) / 2048 * 9.81
                factor = 1000

            for line in fp:
                line = line.strip()

                if ";" in line:
                    try:
                        parts = line.split(";")

                        timestamp = int(parts[0])
                        x, y, z = map(mapper, parts[1:])
                    except ValueError:
                        continue

                    # Timestamp to milliseconds
                    timestamp = timestamp / factor

                    # Feed the shaker
                    shaker.shake(timestamp, x, y, z)

        # Add to list
        if len(shaker.seeds) > 0:
            shakers.append(shaker)

    # Global stats
    seeds = list(itertools.chain(*map(lambda x: x.seeds, shakers)))

    import pylab
    figure = pylab.figure(figsize=(16, 6))
    axis = figure.add_subplot(1, 1, 1)
    axis.hist(seeds, 100)
    axis.set_ylabel("Frequency")
    axis.set_xlabel("Seed")

    pylab.grid(True)
    pylab.tight_layout()
    pylab.show()

    sys.stdout.write("Frequency distribution: %s" % collections.Counter(seeds))
    sys.stdout.write("Number of seeds: %s\n" % map(lambda x: len(x.seeds), shakers))
    sys.stdout.write("Average seed: %s\n" % map(lambda x: numpy.average(x.seeds), shakers))
    sys.stdout.write("Std seed: %s\n" % map(lambda x: numpy.std(x.seeds), shakers))

    # Done
    return 0

# E.g. `python main.py input.txt'
if __name__ == "__main__":
    sys.exit(main(sys.argv))