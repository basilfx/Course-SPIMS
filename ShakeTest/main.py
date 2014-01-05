import numpy
import sys
import os
import glob

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
            l2 = l1 - self.last_time

            if (10000.0 * abs(x + y + z - self.last_x - self.last_y - self.last_z) / 12.0) > 350.0:
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

        seed = 1000.0 * x + 700.0 * y + 800.0 * z
        self.seeds.append(seed)

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
            for line in fp:
                line = line.strip()

                if ";" in line:
                    try:
                        parts = line.split(";")

                        timestamp = int(parts[0])
                        x, y, z = map(float, parts[1:])
                    except ValueError:
                        continue

                    # Timestamp to milliseconds
                    timestamp = timestamp / 1000000

                    # Feed the shaker
                    shaker.shake(timestamp, x, y, z)

        # Add to list
        if len(shaker.seeds) > 0:
            shakers.append(shaker)

    # Global stats
    sys.stdout.write("Number of seeds: %s\n" % map(lambda x: len(x.seeds), shakers))
    sys.stdout.write("Average seed: %s\n" % map(lambda x: numpy.average(x.seeds), shakers))
    sys.stdout.write("Std seed: %s\n" % map(lambda x: numpy.std(x.seeds), shakers))

    # Done
    return 0

# E.g. `python main.py input.txt'
if __name__ == "__main__":
    sys.exit(main(sys.argv))