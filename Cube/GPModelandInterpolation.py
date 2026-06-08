import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from urllib.error import HTTPError

from astropy import units as u
from astropy.coordinates import SkyCoord
import pickle
import CubeFunctions as cf

from scipy.interpolate import make_smoothing_spline

sys.path.append("/lustre/lrspec/users/4300/cube/gopreaux/src/caat/")
from SN import SN
from caat import SNCollection, GP, DataCube, GP3D, SNModel #,SN, GP3D, 
from caat.utils import WLE
import numpy as np
from sklearn.gaussian_process.kernels import Matern, RBF, WhiteKernel
import logging

logger = logging.getLogger()
logger.setLevel(logging.ERROR)


band_wl_dict = {"u":3600,
                "g":5000,
                "r":6400,
                "i":7800,
                "z":8600,
                "Y":9800
               }


models = []

kernel = RBF([np.log(10.0), np.log10(500.0)], (0.1, 3.0))
sn_to_normalize = SNCollection(sntype="Other", snsubtype = "SNIa")
filts = ['UVW2', 'UVM2', 'UVW1', 'U', 'B', 'g', 'c', 'V', 'r', 'o', 'i','z','y','J','H','K']
phasemin = -20
phasemax = 50
log_transform = 22
mangle_sed = True


SNeNames = os.listdir(f"/home/4300/miniconda3/envs/gopreaux/lib/python3.10/site-packages/caat/data/Other/SNIa/")


for name in SNeNames:
    sn_type = SNCollection([name])
    kernel = RBF([np.log(10.0), np.log10(500.0)], (0.1, 3.0))
    
    gp = GP3D(
        sn_type, 
        kernel, 
        filts,
        phasemin, 
        phasemax,
        set_to_normalize=sn_to_normalize,
        log_transform=log_transform,
        mangle_sed=mangle_sed
    )
    try:
        kernel_parameters = gp.optimize_hyperparams(subtract_polynomial=True)
    except ValueError:
        print(f'{name} has weird kernel')
    except IndexError:
        print(f'{name} returns error "list index out of range" during optimize parameters')
    # Let's look at the kernel hyperparameters
    optimized_kernel_hyperparams = np.asarray([np.median([k[i] for k in kernel_parameters]) for i in range(len(kernel_parameters[0]))])
    print(np.exp(optimized_kernel_hyperparams))
    if len(np.exp(optimized_kernel_hyperparams)) > 1:
        try:
            model = gp.predict(
                plot=False,
                subtract_polynomial=True,
            ) 
            print(f"{name} done!")
            models.append(model)
        except ValueError:
            print(f"{name} had error during modeling")
            continue
    else:
        print(f'{name} is weird')
        continue

ObjInterps = {'u': [], 'g': [], 'r': [], 'i': [], 'z': [], 'Y': []}
TimeRange = {'u': [], 'g': [], 'r': [], 'i': [], 'z': [], 'Y': []}
for i, model in enumerate(models):
    print(f'{model.collection.sne[0]}, {i+1} of {len(models)}')
    model.surface.iqr = np.abs(model.surface.iqr)
    try:
        for filt in list(band_wl_dict):
            wl = band_wl_dict[filt]
            times_wl = np.arange(-10,40,0.1)
            wls = np.full(len(times_wl),wl)
            phases, pred, dev = model.predict_photometry_points(wls,times_wl)
            interp = make_smoothing_spline(phases, pred)
            ObjInterps[filt].append(interp)
            TimeRange[filt].append([phases[0],phases[-1]])
            EventName = "SweetSpot_"+model.collection.sne[0].name
    except ValueError:
        print("Error",len(ObjInterps))
        continue
with open(f'/lustre/lrspec/users/4300/cube/Data/Interp/CAATSNIa_Interp.pkl', 'wb') as f:
    pickle.dump(ObjInterps, f)
    pickle.dump(TimeRange, f)
print("Done!")