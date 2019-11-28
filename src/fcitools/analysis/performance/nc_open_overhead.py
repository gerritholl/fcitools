"""Script to measure overhead of opening NetCDF files
"""

import netCDF4
import h5py
import xarray
import glob
import random
import functools
import dask.array

srcdir = "/data/gholl/cache/MTG"

filenames = glob.glob(srcdir + "/*BODY*.nc")

#n = 200
#n = 1000
#n = 5000
n = 10000
#opener = xarray.open_dataset
#opener = functools.partial(netCDF4.Dataset, mode="r")
#opener = functools.partial(open, mode="r")
opener = functools.partial(h5py.File, mode="r")
#opener = functools.partial(xarray.open_dataset,
#        engine="h5netcdf", group="/data/vis_08/measured",
#        chunks=4096)

def main():
    for _ in range(n):
        with opener(random.choice(filenames)) as ds:
            #pass
            dask.array.from_array(
                    ds["/data/vis_08/measured"],
                    chunks=(1000, 1000))
