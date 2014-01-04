import sys
import os
from fnmatch import fnmatch

def main(argv):
    print "File,PASSED,FAILED,WEAK"
    pattern = "*.diehard"
    for path, subdirs, files in os.walk("results"):
        for name in files:
            if fnmatch(name, pattern):
                file = open(os.path.join(path, name))
                contents = file.read()

                failed = search(contents, "FAILED")
                passed = search(contents, "PASSED")
                weak = search(contents, "WEAK")

                print os.path.join(path, name) + "," + str(passed) + "," + str(failed) + "," + str(weak)


    # Done
    return 0

def search(contents, string):
    index = 0
    result = 0
    while(index != -1):
        index = contents.find(string, index + 1)
        if(index != -1):
            result+= 1
    return result


if __name__ == "__main__":
    sys.exit(main(sys.argv))