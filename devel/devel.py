import logging
import glob

from adcpreader import rdi_reader, rdi_writer, rdi_info

logging.basicConfig(level=logging.ERROR)
logging.getLogger("adcpreader.rdi_reader").setLevel(logging.WARNING)

# look for many files 
filenames = glob.glob("*.pd0")
filenames.sort()

valid_files = []
for i, fn in enumerate(filenames):
    try:
        print(i, *rdi_reader.get_info(fn))
    except ValueError:
        print(f"File {i} could not be read.")
    else:
        valid_files.append(fn)


reader = rdi_reader.PD0()
info = rdi_info.FileInfo()
data = rdi_writer.DataStructure(has_bottom_track=False)


pipeline = reader | info


pipeline.process(valid_files)






