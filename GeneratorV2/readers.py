from utils import intfloat_to_raw, float_to_raw, float_to_int, Chain

class DefaultReader(Chain):
    def __init__(self, *chain, **kwargs):
        super(DefaultReader, self).__init__(*chain)

        self.gyro = kwargs.pop("gyro")

    def put(self, filename):
        # Read the file
        with open(filename, "r") as fp:
            # Parse file type
            file_type = next(fp).strip()

            if file_type == "# General":
                size = 4
                #mapper = float_to_raw
                mapper = float_to_int
            elif file_type == "# GeneralV2":
                size = 4
                mapper = int
            elif file_type == "# Raw":
                size = 2
                mapper = int

            # Parse device string from line 2
            next(fp)

            # Parse generated unique id for device
            next(fp)

            # Skip comment line
            next(fp)

            # Read data lines
            for line in fp:
                line = line.strip()

                # Stop at gyro data if it is configured to not be included
                if self.gyro == False and line == "# GYRO":
                    break

                if ";" in line:
                    result = map(mapper, line.split(";")[1:])

                    if result:
                        for x in self.chain:
                            x.put(size, *result)

def GyroDefaultReader(*args, **kwargs):
    kwargs["gyro"] = True
    return DefaultReader(*args, **kwargs)

def NoGyroDefaultReader(*args, **kwargs):
    kwargs["gyro"] = False
    return DefaultReader(*args, **kwargs)