from datetime import datetime

import sys
import os
import pipes
import multiprocessing
import subprocess
import formic
import os

def main(argv):
    if len(argv) not in [2, 3]:
        sys.stdout.write("Syntax: %s <input_dir> [<cpus>]\n" % argv[0])
        return 1

    # Parse arguments
    input_dir = os.path.abspath(argv[1])

    try:
        cpus = int(argv[2])
    except (LookupError, ValueError):
        cpus = multiprocessing.cpu_count()

    # Find files
    file_set = formic.FileSet(include="**/*.txt", directory=input_dir)
    file_names = list(file_set)
    sys.stdout.write("Found %d files\n" % len(file_names))

    # Create a pool
    pool = multiprocessing.Pool(processes=cpus)

    # Wait for completion
    r = pool.map_async(run_job, file_names)
    r.wait()
    sys.stdout.write("Done!\n")

    # Done
    return 0


def run_job(file_name):
    output_file = file_name.rsplit(".", 1)[0] + ".diehard"

    # Remove old file since we concatenate
    if os.path.exists(output_file):
        os.remove(output_file)

    tests = [0, 1, 2, 3, 4, 8, 9, 10, 11, 12, 13, 15, 16, 17, 100, 101, 102, 201, 204, 205]
    pre_cmd = ["dieharder", "-f", pipes.quote(file_name), "-g", "201"]
    post_cmd = ["-D", "default", "-D", "histogram", ">>", pipes.quote(output_file)]

    # Run command
    sys.stdout.write("Job starting for file: %s\n" % file_name)

    start = datetime.now()

    for test in tests:
        command = pre_cmd + ["-d", str(test)] + post_cmd
        subprocess.call(" ".join(command), shell=True)

    end = datetime.now()

    sys.stdout.write("Job time: %s\n" % (end - start))

# E.g. `python main.py ../Results/upload 4'
if __name__ == "__main__":
    sys.exit(main(sys.argv))