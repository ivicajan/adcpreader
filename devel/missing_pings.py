import logging
import pathlib

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates

import adcpreader

logging.basicConfig(level=logging.ERROR)
logging.getLogger("adcpreader.rdi_reader").setLevel(logging.WARNING)


def epoch2num(t):
    # seconds: 1D numpy array of dtype float or int (POSIX seconds)
    mdates = t / 86400.0 + 719163.0
    return mdates


# look for many files
path = pathlib.Path("/home/lucas/gliderdata/foxstorm0825/dvl/echo")
filenames = list(path.glob("YH*.pd0"))
filenames.sort()

valid_files = []
invalid_files = []
incomplete_files = {}
complete_files = {}

for i, fn in enumerate(filenames):
    try:
        info = adcpreader.rdi_reader.get_info(fn)
    except ValueError:
        print(f"File {i} could not be read.")
        invalid_files.append(fn)
    else:
        valid_files.append(fn)
        t_start, t_end, n_profiles, max_profiles = info
        if n_profiles != max_profiles:
            incomplete_files[fn] = (t_start, t_end, n_profiles, max_profiles-n_profiles)
        else:
            complete_files[fn] = (t_start, t_end, n_profiles, max_profiles-n_profiles)

print("Invalid profiles:")
for fn in invalid_files:
    print(f"   {fn}")
print()
print("Incomplete profiles:")
for fn, (_, _,  n, m) in incomplete_files.items():
    print(f"   {fn} has {n:4d} profiles, and {m:3d} missing profiles")



