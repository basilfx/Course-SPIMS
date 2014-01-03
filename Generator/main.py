from extractors import *
from generators import *

import sys
import glob
import os
import collections
import struct

# Extractors are transformations that attempt to extract
# randomness from non-randomness in entropy sources
EXTRACTORS = [
    raw,
    merged,
#    von_neumann,
    aes128_cbc_mac
]

# Generators take entropy and generate random numbers
GENERATORS = [
    SHA256Gen,
    AES128CtrGen,
    OpenSSLPRNGen
]

# Defines the number of random numbers that must be generated
NUMBERS_OUTPUT_SIZE = 2500000

# Include gyro data or not
INCLUDE_GYRO = False

def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def main(argv):
    if len(argv) != 3:
        sys.stdout.write("Syntax: %s <input_dir> <output_dir>\n" % argv[0])
        return 1

    input_dir = os.path.abspath(argv[1])
    output_dir = os.path.abspath(argv[2])
    file_names = glob.glob(os.path.join(input_dir, "*.txt"))

    sys.stdout.write("Found %d result files\n" % len(file_names))

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

            device_data_dict = collections.defaultdict(list)
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
            sys.stdout.write("Read %d lines of data for '%s'\n" % (lines, device_key))

            # Apply generators and extractors
            for extractor in EXTRACTORS:
                for generator in GENERATORS:
                    ext_name = extractor.__name__
                    gen_name = generator.name

                    # Create output directory
                    current_output_dir = os.path.join(output_dir, ext_name, gen_name)

                    if not os.path.exists(current_output_dir):
                        os.makedirs(current_output_dir)

                    # Iterate over each device
                    for device, data in device_data_dict.iteritems():
                        sys.stdout.write("Generating for '%s' with extractor '%s' and generator '%s'\n" % (device, ext_name, gen_name))

                        current_device_file = os.path.join(current_output_dir, "%s.txt" % device)
                        #data = zip(*[iter(data)]*3)

                        with open(current_device_file, "wb+") as output_file:
                            # Call extractor then generator
                            gen = generator(extractor(data))

                            for i in range(NUMBERS_OUTPUT_SIZE):
                                # Write output to file
                                output_file.write(str(gen.get_rand()))

    # Done
    return 0

# E.g. `python main.py ../Results/upload output'
if __name__ == "__main__":
    sys.exit(main(sys.argv))