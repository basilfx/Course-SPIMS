from extractors import *
from generators import *

import sys
import glob
import os
import collections

# Extractors are transformations that attempt to extract
# randomness from non-randomness in entropy sources
EXTRACTORS = [
    raw,
    merged,
    von_neumann,
    aes128_cbc_mac
]

# Generators take entropy and generate random numbers
GENERATORS = [
    SHA256Gen,
    AES128CtrGen,
    OpenSSLPRNGen
]

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
            next(input_file)
            # Parse device string from line 2
            device_string = next(input_file).strip()
            # Parse generated unique id for device
            device_id = next(input_file).strip()
            # Skip comment line
            next(input_file)

            device_data_dict = collections.defaultdict(str)

            for line in input_file:
                if ";" in line:
                    result = map(float, line.split(";")[1:])

                    if result:
                        # Unpack a line
                        first, second, third = result

                        # Float to ints
                        data = struct.pack("fff", first, second, third)
                        #data = struct.unpack("III", data)

                        # Store it
                        device_data_dict["%s_%s" % (device_string, device_id)] += data

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
                        current_device_file = os.path.join(current_output_dir, "%s.txt" % device)

                        with open(current_device_file, "w+") as output_file:
                            # Grab extractor properties
                            input_size = getattr(extractor, "input_size", 4)

                            # Iterate over each N bytes
                            for bytes in chunks(data, input_size):
                                if len(bytes) == input_size:
                                    # Call extractor then generator
                                    gen = generator.__init__(extractor(bytes))

                                    for i in range(5000000):
                                        # Write output to file
                                        output_file.write(gen.get_rand())

    # Done
    return 0

# E.g. `python main.py ../Results/upload output'
if __name__ == "__main__":
    sys.exit(main(sys.argv))