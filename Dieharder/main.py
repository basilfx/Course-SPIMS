from datetime import datetime

import sys
import glob
import os
import multiprocessing
import subprocess

def main(argv):
    if len(argv) not in [3, 4]:
        sys.stdout.write("Syntax: %s <input_dir> <output_dir> [<cpus>]\n" % argv[0])
        return 1

    # Parse arguments
    input_dir = os.path.abspath(argv[1])
    output_dir = os.path.abspath(argv[2])

    try:
        cpus = int(argv[3])
    except (LookupError, ValueError)
        cpus = multiprocessing.cpu_count()

    # Find files
    file_names = glob.glob(os.path.join(input_dir, "*"))
    sys.stdout.write("Found %d files\n" % len(file_names))

    # Create a pool
    pool = multiprocessing.Pool(processes=cpus)
    r = pool.map_async(lambda x: run_job(x, output_dir), file_names)

    # Wait for completion
    r.wait()
    sys.stdout.write("Done!\n")

    # Done
    return 0


def run_job(file_name, output_dir):
    output_file = os.path.join(output_dir, os.path.basename(file_name))
    command = ["dieharder", "-a", "-f", file_name, "-g", "201", ">", output_file]
    sys.stdout.write("Executing command: %s\n" % (" ".join(command)))

    # Run command
    start = datetime.now()
    subprocess.call(" ".join(command), shell=True)
    end = datetime.now()

    sys.stdout.write("Job time: %s\n" % (start - end))

# E.g. `python main.py ../Results/upload output 4'
if __name__ == "__main__":
    sys.exit(main(sys.argv))