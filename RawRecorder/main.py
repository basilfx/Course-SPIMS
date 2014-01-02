import serial
import sys
import random
import os

def main(argv):
    if len(argv) != 3:
        sys.stdout.write("Syntax: %s <input_dir> <output_dir>\n" % argv[0])
        return 1

    serial_device = os.path.abspath(argv[1])
    output_file = argv[2]

    sys.stdout.write("Reading from '%s' until CTRL+C received\n" % serial_device)

    gyro = []
    accelero = []

    # Read as much as possible
    device = serial.Serial(serial_device, baudrate=230400)

    try:
        while True:
            line = device.readline().strip()

            if not line[:1] == "#":
                parts = line.split(";")

                if len(parts) == 7:

                    try:
                        map(int, parts)
                    except ValueError:
                        # It were no integers
                        continue

                    accelero.append("%s;%s;%s;%s" % (parts[0], parts[1], parts[2], parts[3]))
                    gyro.append("%s;%s;%s;%s" % (parts[0], parts[4], parts[5], parts[6]))

                    # Stats
                    sys.stdout.write("\r%d recordings" % len(gyro))

    except KeyboardInterrupt:
        device.close()

    # Start saving
    sys.stdout.write("Saving...")

    with open(output_file, "w") as fp:
        fp.write("# Raw\n")
        fp.write("Raw device\n")
        fp.write("%d\n" % random.randrange(0, 2**32))


        fp.write("# ACCELEROMETER\n")
        fp.write("%d\n" % len(accelero))

        for x in accelero:
            fp.write("%s\n" % x)

        fp.write("# GYRO\n")
        fp.write("%d\n" % len(gyro))

        for x in gyro:
            fp.write("%s\n" % x)

    sys.stdout.write("done!\n")

    # Done
    return 0

# E.g. `python main.py /dev/usbdevice filename.txt'
if __name__ == "__main__":
    sys.exit(main(sys.argv))