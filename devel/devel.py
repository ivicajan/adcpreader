import logging
import pathlib

import numpy as np
import matplotlib.pyplot as plt

import adcpreader

logging.basicConfig(level=logging.ERROR)
logging.getLogger("adcpreader.rdi_reader").setLevel(logging.WARNING)

mounted_pitch=11*np.pi/180


# look for many files
path = pathlib.Path("/home/lucas/gliderdata/foxstorm0825/dvl/echo")
filenames = list(path.glob("YH*.pd0"))
filenames.sort()

valid_files = []
for i, fn in enumerate(filenames):
    try:
        print(i, fn, *adcpreader.rdi_reader.get_info(fn))
    except ValueError:
        print(f"File {i} could not be read.")
    else:
        valid_files.append(fn)

valid_files = ["/home/lucas/gliderdata/foxstorm0825/dvl/echo/YH291723.pd0"]



# Data are recoreded in beam coordinates. Transform to ENUcoordinates

t1 = adcpreader.rdi_transforms.TransformBEAM_XYZ()
t2 = adcpreader.rdi_transforms.TransformXYZ_SFU(0, mounted_pitch, 0)
t3 = adcpreader.rdi_transforms.TransformSFU_ENU()
transform_beam_to_enu = t3 * t2 * t1

# some data filtering:
max_velocity = 0.75
qc_u_limit = adcpreader.rdi_qc.ValueLimit(drop_masked_ensembles=False)
qc_u_limit.mask_parameter('velocity','Velocity1','||>',max_velocity)
qc_u_limit.mask_parameter('velocity','Velocity2','||>',max_velocity)
qc_u_limit.mask_parameter('velocity','Velocity3','||>',max_velocity)
qc_u_limit.mask_parameter('velocity','Velocity4','||>',max_velocity)


qc_snr_limit = adcpreader.rdi_qc.SNRLimit(SNR_limit=5, noise_floor_db=51, use_AVG=True)

qc_amplitude_limit = adcpreader.rdi_qc.AcousticAmplitudeLimit(75)

# and a writer (sink)
writer = adcpreader.rdi_writer.NetCDFWriter('output.nc')

data = adcpreader.rdi_writer.DataStructure()
data.add_parameter_list("echo", "SNR1", "SNR2", "SNR3", "SNR4", "SNR_AVG") # <= these data are added by qc_snr_limit()

# and reader (source)
reader = adcpreader.rdi_reader.PD0()

pipeline = reader | transform_beam_to_enu
#pipeline |= qc_u_limit
pipeline |= qc_snr_limit 
#pipeline |= qc_amplitude_limit # alternatively
branch_writer = pipeline | writer
branch_data   = pipeline | data


with writer:
    reader.process(valid_files[:30])

ncells = data.r.shape[0]
ntimes = data.Time.shape[0]


r = data.r.reshape(ncells,1) @ np.ones((1, ntimes), float)
tm = data.Time.reshape(ntimes, 1) @ np.ones((1, ncells), float)
depth = data.Depth.reshape(ntimes, 1) @ np.ones((1, ncells), float)
depth *= 10
z = (depth.T + r).T

f, ax = plt.subplots(2,1, sharex=True)
for _t, _z, _u in zip(tm, z, data.velocity_north):
    ax[0].scatter(_t, _z, 5, _u)


