import sys
import glob
import os
import multiprocessing

import subprocess

def main(argv):
    if len(argv) != 3:
        sys.stdout.write("Syntax: %s <input_dir> <output_dir>\n" % argv[0])
        return 1

    global input_dir
    input_dir = os.path.abspath(argv[1])
    global output_dir
    output_dir = os.path.abspath(argv[2])
    file_names = glob.glob(os.path.join(input_dir, "*"))

    sys.stdout.write("Found %d files\n" % len(file_names))

    
    count = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=count)

    r = pool.map_async(run_job, file_names)
    r.wait()

    print "done"
    # Done
    return 0


def run_job(file_name):
    output_file = os.path.join(output_dir, os.path.basename(file_name))
    command = ["dieharder", "-a", "-f", file_name, "-g", "201", ">", output_file]
    print "Executing: " + " ".join(command)
    subprocess.call(" ".join(command), shell=True)

# E.g. `python main.py ../Results/upload output'
if __name__ == "__main__":
    sys.exit(main(sys.argv))