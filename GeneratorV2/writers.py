from utils import Chain

import os

class ByteWriter(Chain):

    def __init__(self, *path):
        self.path = path

    def start(self, base_dir, output_dir, filename):
        file_dir = os.path.dirname(filename)
        diff_dir = os.path.relpath(file_dir, base_dir)
        output_dir = os.path.join(output_dir, diff_dir, *self.path)

        output_file = os.path.join(output_dir, os.path.basename(filename))

        # Try to create directory
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                if e.errno == errno.EEXIST and os.path.isdir(output_dir):
                    pass
                else:
                    raise

        # Open file
        self.output_file = output_file
        self.file_handle = open(output_file, "w+b", 1024*1024)

    def stop(self):
        self.file_handle.close()

        return self.output_file

    def put(self, byte):
        self.file_handle.write(chr(byte))