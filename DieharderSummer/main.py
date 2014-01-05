import sys
import os

def map_reduce(data, mapper, reducer=None):
    result = dict()

    # Map
    for item in data:
        key, value = mapper(item)

        # Add to list
        if key in result:
            result[key].append(value)
        else:
            result[key] = [value]

    # Reduce
    if reducer is not None:
        for key, group in result.iteritems():
            result[key] = reducer(group)

    # Done
    return result

def mapper_ext(item):
    base, device, generator, extractor, total, passed, failed, weak = item
    return ((base, device, extractor), (total, passed, failed, weak))

def mapper_gen(item):
    base, device, generator, extractor, total, passed, failed, weak = item
    return ((base, device, generator), (total, passed, failed, weak))

def mapper_ext_gen(item):
    base, device, generator, extractor, total, passed, failed, weak = item
    return ((base, device), (total, passed, failed, weak))

def mapper_ext_gen2(item):
    base, device, generator, extractor, total, passed, failed, weak = item
    return ((generator, extractor), (total, passed, failed, weak))

def reducer_sum(group):
    total = sum([ int(item[0]) for item in group ])
    passed = sum([ int(item[1]) for item in group ])
    failed = sum([ int(item[2]) for item in group ])
    weak = sum([ int(item[3]) for item in group ])

    return (total, passed, failed, weak)

MAPPERS = {
    "ext": (mapper_ext, reducer_sum, "base,filename,Extactor,TOTAL,PASSED,FAILED,WEAK", "%s,%s,%s,%d,%d,%d,%d\n"),
    "gen": (mapper_gen, reducer_sum, "base,filename,Generator,TOTAL,PASSED,FAILED,WEAK", "%s,%s,%s,%d,%d,%d,%d\n"),
    "extgen": (mapper_ext_gen, reducer_sum, "base,filename,TOTAL,PASSED,FAILED,WEAK", "%s,%s,%d,%d,%d,%d\n"),
    "extgen2": (mapper_ext_gen2, reducer_sum, "base,filename,TOTAL,PASSED,FAILED,WEAK", "%s,%s,%d,%d,%d,%d\n"),
}

def main(argv):
    if len(argv) != 3:
        sys.stdout.write("Syntax: %s <input_file> <grouper>\n" % argv[0])
        return 1

    input_file = os.path.abspath(argv[1])
    mapper = argv[2]

    data = []

    with open(input_file, "r") as fp:
        # Skip header
        fp.readline()

        # Read each line
        for line in fp:
            parts = line.strip().split("\t")
            parts2 = line.strip().split(",")

            if len(parts) == 8:
                data.append(parts)
            elif len(parts2) == 8:
                data.append(parts2)

    # Parse results
    mapper, reducer, header, formatting = MAPPERS[mapper]

    data = map_reduce(data, mapper, reducer)

    # Write to file
    sys.stdout.write(header + "\n")

    for k, v in data.iteritems():
        sys.stdout.write(formatting % (k + v))

    # Done
    return 0

# E.g. `python main.py input.csv ext_gen'
if __name__ == "__main__":
    sys.exit(main(sys.argv))