import os
import tarfile
import io
import numpy as np
import time
import pandas as pd
from scipy import interpolate
import pickle
import sys
from astropy.io import ascii
from astropy.table import Table
from astropy import units as u
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, ListedColormap
    
decaps_cat_path = "/lustre/lrspec/users/4300/cube/Data/Phot/decaps_east.variable.parquet"
decaps_lc_path =  "/lustre/lrspec/users/4300/cube/Data/Phot/Decaps_LCs/var_curves_csv.tar.gz" #don't touch this please

my_types = {
    "Delta_sct": ["DSCT-multimode", "DSCT-singlemode", "HADS", "DSCT|GDOR|SXPHE"],
    "Ecl_ell": ["ELL", "ECL-ELL", "Ell","HB-RG","HB-MS"],
    "RRLyr": ["RRcd", "RRab", "RRLyr-RRd", "RR", "RRLyr-RRab", "RRLyr-RRc"],
    "Cep": ["Cep-1","CEP", "Cep-F", "T2Cep-WVir", "T2Cep-RVTau", "T2CEP", "T2Cep-BLHer"],
    "LPV" : ["M", "LPV", "LPV-Mira", "LPV-SRV", "LPV-OSARG"],
    "Mira" : ["M", "LPV-Mira"],
    "Type2_Cep" : ["T2Cep-WVir", "T2Cep-RVTau", "T2CEP", "T2Cep-BLHer"],
    "Ecl" : ["EA/EB","EW","EA","ECL-NC","ECL-C","ECL"]
}

for VS_type in my_types:
    u = pd.read_parquet(decaps_cat_path)
    
    u = u[u["gdr3_class"] != "WD"]
    
    u_type = u[u[["gdr3_class", "ogle_class","asassn_class","vivace_class"]].isin(my_types[VS_type]).any(axis=1)]
    
    files = []
    for ID in u_type["varID"]:
        files.append(str(ID)+".csv")
    
    with tarfile.open(decaps_lc_path,"r|gz") as tar:
        dfs = []
        keys = []
        for member in tar:
            if member.name in files:
                csv_file = io.StringIO(tar.extractfile(member).read().decode('ascii'))
                df = pd.read_csv(csv_file)
                df["varID"] = member.name.removesuffix(".csv")
                dfs.append(df)
        
    df_type = pd.concat(dfs, ignore_index = True)
    
    df_type.to_parquet(f"/lustre/lrspec/users/4300/cube/Data/Phot/Decaps_LCs/{VS_type}_DECaPS.parquet.gzip", compression="gzip")
    
    print("Done! :D")