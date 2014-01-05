from fnmatch import fnmatch

import sys
import os
import formic

# Select which tests to disable
DISABLED_TESTS = [
    "dab_bytedistrib",
    "marsaglia_tsang_gcd",
    "rgb_minimum_distance",
    "rgb_kstest_test"
]

def main(argv):
    if len(argv) != 2:
        sys.stdout.write("Syntax: %s <input_dir>\n" % argv[0])
        return 1

    input_dir = os.path.abspath(argv[1])

    # Find files
    file_set = formic.FileSet(include="**/*.diehard", directory=input_dir)
    filenames = list(file_set)

    # Print header
    sys.stdout.write("base,filename,Generator,Extactor,TOTAL,PASSED,FAILED,WEAK\n")

    for filename in filenames:
        # Strip extractor and generator name from path
        try:
            base, extractor, generator, device = filename.rsplit("/", 3)
            base = base.replace(input_dir, "")
            device = device.rsplit(".", 1)[0]
        except ValueError:
            continue

        # Initialize counters
        total = 0
        weak = 0
        failed = 0
        passed = 0
        state = 0

        # Read file and scan for test results
        with open(filename, "r") as fp:
            for line in fp:
                # Search for 'test_name'
                if state == 0:
                    # Unpack line
                    parts = map(lambda x: x.strip(), line.split("|"))

                    if parts[0] == "test_name":
                        state = 1

                # Next line is comment
                elif state == 1:
                    state = 2

                # Read all test results
                elif state == 2:
                    # Test for test end
                    if line[:3] == "#==":
                        state = 0
                        continue

                    # Split results
                    parts = map(lambda x: x.strip(), line.split("|"))

                    # Unpack line
                    try:
                        test_name, ntup, tsamples, psamples, p_value, assessment = parts
                    except ValueError:
                        continue

                    # Count results
                    if test_name not in DISABLED_TESTS:
                        total += 1

                        if assessment == "FAILED":
                            failed += 1
                        elif assessment == "PASSED":
                            passed += 1
                        elif assessment == "WEAK":
                            weak += 1

            # Print result
            sys.stdout.write("%s,%s,%s,%s,%d,%d,%d,%d\n" % (base, device, generator, extractor, total, passed, failed, weak))

    # Done
    return 0

# E.g. `python main.py input'
if __name__ == "__main__":
    sys.exit(main(sys.argv))