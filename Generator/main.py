from extractors import *
from generators import *

import sys
import glob
import os
import collections
import struct
import multiprocessing
import errno
import time
import random

# Extractors are transformations that attempt to extract
# randomness from non-randomness in entropy sources
EXTRACTORS = [
    raw,
    merged,
    von_neumann2,
    aes128_cbc_mac
]

# Generators take entropy and generate random numbers
GENERATORS = [
#    SHA256GenV2,
#    AES128CtrGen,
#    OpenSSLPRNGen,
    DummyGen
]

# Defines the number of random numbers that must be generated. Only applies to
# infinite generators.
NUMBERS_OUTPUT_SIZE = 5000000 * 5

# Include gyro data or not
INCLUDE_GYRO = True

def spawn(f):
    def fun(q_in,q_out):
        while True:
            i,x = q_in.get()
            if i is None:
                break
            q_out.put((i,f(x)))
    return fun

def parmap(f, X, nprocs = multiprocessing.cpu_count()):
    q_in   = multiprocessing.Queue(1)
    q_out  = multiprocessing.Queue()

    proc = [multiprocessing.Process(target=spawn(f),args=(q_in,q_out)) for _ in range(nprocs)]
    for p in proc:
        p.daemon = True
        p.start()

    sent = [q_in.put((i,x)) for i,x in enumerate(X)]
    [q_in.put((None,None)) for _ in range(nprocs)]
    res = [q_out.get() for _ in range(len(sent))]

    [p.join() for p in proc]

    return [x for i,x in sorted(res)]

def main(argv):
    if len(argv) not in [3, 4]:
        sys.stdout.write("Syntax: %s <input_dir> <output_dir> [<cpus>]\n" % argv[0])
        return 1

    # Parse arguments
    input_dir = os.path.abspath(argv[1])
    output_dir = os.path.abspath(argv[2])

    try:
        cpus = int(argv[2])
    except (LookupError, ValueError):
        cpus = multiprocessing.cpu_count()

    file_names = glob.glob(os.path.join(input_dir, "*.txt"))
    device_data_dict = collections.defaultdict(list)

    sys.stdout.write("Found %d result files in %d directories\n" % (len(file_names), len(argv[2:])))

    # Load each file in memory
    for file_name in file_names:
        with open(file_name, "r") as input_file:
            # Parse file type
            file_type = next(input_file).strip()

            if file_type == "# General":
                mapper = float
                formatting = "fff"
            if file_type == "# GeneralV2":
                mapper = int
                formatting = "iii"
            elif file_type == "# Raw":
                mapper = int
                formatting = "hhh"

            # Parse device string from line 2
            device_string = next(input_file).strip()
            # Parse generated unique id for device
            device_id = next(input_file).strip()
            # Skip comment line
            next(input_file)

            device_key = "%s_%s" % (device_string, device_id)
            lines = 0

            # Read data lines
            for line in input_file:
                line = line.strip()

                # Stop at gyro data if it is configured to not be included
                if INCLUDE_GYRO == False and line == "# GYRO":
                    break

                if ";" in line:
                    result = map(mapper, line.split(";")[1:])

                    if result:
                        lines += 1

                        # Unpack a line
                        first, second, third = result
                        # Convert to bytes
                        data = struct.pack(formatting, first, second, third)

                        # Store it
                        device_data_dict[device_key] += data

        # Stats
        sys.stdout.write("Read %d lines of data for '%s' in memory\n" % (lines, device_key))

    # Iterate over each device
    #for device, data in device_data_dict.iteritems():
    def _run(device):
        time.sleep(random.random())
        data = device_data_dict[device]

        # Apply generators and extractors
        for extractor in EXTRACTORS:
            ext_name = extractor.__name__

            # Apply extractor
            data = extractor(data)

            for generator in GENERATORS:
                gen_name = generator.name

                sys.stdout.write("Generating for '%s' with extractor '%s' and generator '%s'\n" % (device, ext_name, gen_name))

                # Create output directory and output file
                current_output_dir = os.path.join(output_dir, ext_name, gen_name)
                current_device_file = os.path.join(current_output_dir, "%s.txt" % device)

                # Try to create directory
                if not os.path.exists(current_output_dir):
                    try:
                        os.makedirs(current_output_dir)
                    except OSError as e:
                        if e.errno == errno.EEXIST and os.path.isdir(current_output_dir):
                            pass
                        else:
                            raise

                with open(current_device_file, "a+b", 1024*1024*1024) as output_file:
                    # Call generator
                    gen = generator(data)

                    try:
                        # Write to file
                        for i in xrange(NUMBERS_OUTPUT_SIZE):
                            output_file.write(gen.get_rand())
                    except StopIteration:
                        pass

    # Spawn several processes
    parmap(_run, device_data_dict.keys(), min(cpus, len(device_data_dict)))

    # Done
    return 0

# E.g. `python main.py ../Results/upload output'
if __name__ == "__main__":
    sys.exit(main(sys.argv))