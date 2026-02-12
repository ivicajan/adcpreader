import arrow

import logging
import pathlib

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates

import adcpreader
import dbdreader

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


mounted_pitch = 0
mounted_heading = 45*np.pi/180
mounted_roll = 0

reader = adcpreader.rdi_reader.PD0()
t0 = adcpreader.rdi_transforms.TransformBEAM_XYZ()
t1 = adcpreader.rdi_transforms.TransformXYZ_SFU(mounted_heading, mounted_pitch, mounted_roll)

rotation = t1 * t0

data = adcpreader.rdi_writer.DataStructure()

pipeline = reader | rotation | data

pipeline.process(filenames[30:80])

date_fmt = "%d %m %Y %H %M"
t_start = arrow.get(data.Time[0]).strftime(date_fmt)
t_end = arrow.get(data.Time[-1]).strftime(date_fmt)

ps = dbdreader.DBDPatternSelect(date_format= date_fmt)
filenames = ps.select("/home/lucas/gliderdata/foxstorm0825/hd/echo*.dbd",
                      from_date = t_start,
                      until_date = t_end)

dbd = dbdreader.MultiDBD(filenames)

tm, pitch, roll, heading = dbd.get_sync("m_pitch", "m_roll", "m_heading")



# Figuring out the how the ADCP is mounted.

index = slice(1,3)
u = data.velocity_forward[:, index].mean(axis=1)
v = data.velocity_starboard[:, index].mean(axis=1)
w = data.velocity_up[:,index].mean(axis=1)

# angle between forward and starboard velocity
angle = (np.arctan2(v, u))%(2*np.pi)
# remove spikes
condition = np.logical_and(angle<angle.mean()+angle.std(), angle>angle.mean()-angle.std())
angle = angle.compress(condition)
U_angle = float(angle.mean())
U_angle_degrees = U_angle * 180/np.pi
# if properly corrected for, then the U_angle should be 180 degrees
print(f"U angle: {U_angle_degrees}.")

if 0:
    f, ax = plt.subplots(1,1)
    ax.hlines(180, 0, len(angle), color='black', linestyle='--', linewidth=2, label='Expected flow angle', zorder=1000)
    ax.plot(angle*180/np.pi, 'C3', alpha=0.2, label='Incident flow angle')
    ax.hlines(U_angle_degrees, 0, len(angle), 'C0', linewidth=2, label='Averaged flow angle')
    ax.legend(loc='lower left')


aoa = (np.atan(w/u)) * 180/np.pi
