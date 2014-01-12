from utils import flatten
from chain import DEFAULT_CHAIN

import os
import sys
import formic
import multiprocessing
import subprocess
import pipes
#import yappi

def main(argv):
    if len(argv) not in [3, 4]:
        sys.stdout.write("Syntax: %s <input_dir> <output_dir> [<cpus>]\n" % argv[0])
        return 1

    # Parse arguments
    input_dir = os.path.abspath(argv[1])
    output_dir = os.path.abspath(argv[2])

    try:
        cpus = int(argv[3])
    except (LookupError, ValueError):
        cpus = multiprocessing.cpu_count()

    # Find files
    file_set = formic.FileSet(include="**/*.txt", directory=input_dir)
    filenames = list(file_set)
    sys.stdout.write("Found %d files\n" % len(filenames))

    jobs = [ (input_dir, output_dir, filename) for filename in filenames ]
    #yappi.start()
    #result = map(run_job, jobs)
    #yappi.get_func_stats().print_all()
    #return 0

    # Create a pool
    pool = multiprocessing.Pool(processes=cpus)

    # Wait for completion
    result = flatten(pool.imap_unordered(run_job, jobs))

    # Output stats
    result = sorted(result, key=lambda x: x[0])

    for row in result:
        sys.stdout.write("%8s %10s %s\n" % (str(row[0]), str(row[1]), row[2]))

    # Done
    sys.stdout.write("Done!\n")
    return 0

def run_job(job):
    base_dir, output_dir, filename = job
    output_files = []
    result = []

    sys.stdout.write("Starting job for input '%s'\n" % filename)

    # Run the chain
    for item in DEFAULT_CHAIN:
        # Initialize chain
        item.start(base_dir, output_dir, filename)

        # Start chain
        item.put(filename)

        # Stop chain
        output_files = output_files + list(flatten(item.stop()))

    # Collect information about the entropy
    for output_file in output_files:
        # Execute program
        command = ["ent", "-t", pipes.quote(output_file)]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        lines = proc.stdout.read().split("\n")

        # Read stats
        stats = lines[1].split(",")

        result.append((float(stats[2]), int(stats[1]), output_file))

    # Done
    sys.stdout.write("Finished job\n")
    return result

# E.g. `python main.py ../Results/upload output'
if __name__ == "__main__":
    sys.exit(main(sys.argv))