import datetime
from satpy.scene import Scene
from satpy.utils import debug_on
from glob import glob
from dask.diagnostics import (ResourceProfiler, Profiler, CacheProfiler,
                              visualize)

srcdir = "/data/gholl/cache/MTG"
#debug_on()

# MTG Test data from EUMETSAT
with Profiler() as prof, ResourceProfiler() as rprof, CacheProfiler() as cprof:
    fciscene = Scene(sensor="fci",
                     filenames=glob(srcdir + "/*BODY*.nc"),
                     reader=['fci_l1c_fdhsi'])

    dn_all = fciscene.available_dataset_names()
    fciscene.load(dn_all)

visualize([prof, rprof, cprof],
        file_path=datetime.datetime.now().strftime("/tmp/fci_profile_%Y%m%d_%H%M%S.html"),
        show=False)
