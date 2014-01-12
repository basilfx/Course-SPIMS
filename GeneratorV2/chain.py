from writers import *
from readers import *
from processers import *
from outputters import *
from extractors import *
from generators import *

def chain_builder(readers, processors, outputters, extractors, generators, writers):
    result = []

    for a, reader in readers:
        aa = []

        for b, processor in processors:
            bb = []

            for c, outputter in outputters:
                cc = []

                for d, extractor in extractors:
                    dd = []

                    for e, generator in generators:
                        ee = []

                        for writer in writers:
                            ee.append(writer(a, b, c, d, e))

                        dd.append(generator(*ee))
                    cc.append(extractor(*dd))
                bb.append(outputter(*cc))
            aa.append(processor(*bb))
        result.append(reader(*aa))

    # Done
    return result

DEFAULT_CHAIN = chain_builder(
    readers=[
        ("gyro", GyroDefaultReader),
        #("nogyro", NoGyroDefaultReader)
    ],
    processors=[
        ("default", DefaultProcessor),
        ("diff", DiffProcessor),
        ("xor", XorProcessor),
        ("running_xor", RunningXorProcessor)
    ],
    outputters=[
        ("median", MedianOutputter),
        ("mean", MeanOutputter),
        ("raw", RawOutputter)
    ],
    extractors=[
        ("vonneumann", VonNeumannExtractor),
        ("raw", RawExtractor),
    ],
    generators=[
        ("dummy", DummyGenerator),
        ("sha1", SHA1Generator),
        #("crc32", CRC32Generator)
    ],
    writers=[
        ByteWriter
    ]
)