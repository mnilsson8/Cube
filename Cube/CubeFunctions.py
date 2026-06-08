import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from astropy import units as u
from astropy.coordinates import SkyCoord
import pickle

#allowed passbands
allowed_b = ["UVW2","UVM2", "UVW1", "U", "V", "g", "c", "B", "R", "r", "r'", "o", "I","i","i'","z","z'","y","y'","J","H","K"]
#allowed_b = ["UVW2","UVM2", "UVW1", "U", "V", "g", "c", "B", "r", "o", "i","z","y","J","H","K"]

band_wl_dict = {"u":3600,
                "g":5000,
                "r":6400,
                "i":7800,
                "z":8600,
                "y":9800
               }

#catch functions for pulling from OSC
def catch(func, arg):
    try:
        return func(arg)
    except TypeError:
        return np.nan

def catch2(ph, arg):
    try:
        return ph[arg]
    except KeyError:
        return np.nan

def catch22(ph, arg1, arg2):
    try:
        return float(ph[arg1])
    except KeyError:
        try: 
            return float((ph[arg2]))/2
        except KeyError:
            return np.nan

def PullFromOSC(SN):
    """ Pulls photometric data from Open Supernova Catalog from 2010-2014, given a supernova name.
    Args:
        SN: supernovae name as a string
    Returns:
        Right ascension, declination, times, bands, magnitudes, magnitude errors
    """
    path = "https://raw.githubusercontent.com/astrocatalogs/sne-2010-2014/refs/heads/master/"
    ext = "json"
#    print(path + "/" + SN + "." + ext)
    sn = pd.read_json(path + "/" + SN + "." + ext)
    sn_nice = []
    for ph in sn.loc["photometry"].loc[SN]:
      try:
        ph["upperlimit"]
      except KeyError:
        sn_nice.append(ph)
          
    c1 = sn.loc["ra"].loc[SN][0]["value"]
    c2 = sn.loc["dec"].loc[SN][0]["value"]
    c = SkyCoord(c1,c2,unit=(u.hourangle, u.deg))
    RA = c.ra.deg
    Dec = c.dec.deg

    z = float(sn.loc["redshift"].loc[SN][0]["value"])
    
    t = np.array([catch(float, ph["time"] ) for ph in sn_nice])
    b = np.array([catch2(ph, "band") for ph in sn_nice])
    m = np.array([catch(float, catch2(ph, "magnitude")) for ph in sn_nice])
    source = np.array([catch2(ph, "source") for ph in sn_nice])
    elow = np.array([catch22(ph,"e_lower_magnitude","e_magnitude") for ph in sn_nice])
    eup = np.array([catch22(ph,"e_upper_magnitude","e_magnitude") for ph in sn_nice])
    e = np.mean([elow, eup], axis=0)

    return RA, Dec, z, t, b, m, e, source 

def FilterOSCDataforTable(SN, RA, Dec, z, t, b, m, e, source, allowed_b):
    names = [SN]
    RAs = [RA]
    Decs = [Dec]
    zs = [z]
    LCs = []
    LC0s = []
    for band in np.unique(b):
        if band in allowed_b:
            LC_holder = []
            LC0 = []
            mags = []
            mag_errs = []
            mjd = []
            indx = b == band
            indx2 = source[indx] == (source[indx][0])
            for mag in m[indx][indx2]:
                mags.append(mag)
            for magerr in e[indx][indx2]:
                mag_errs.append(magerr)
            for date in t[indx][indx2]:
                if date > 55000:
                    mjd.append(date)
            LC_holder.append(mjd)
            LC_holder.append(mags)
            LC_holder.append(mag_errs)
            LC0.append(band)
            LC0.append(LC_holder)
            LC0s.append(LC0)
    #need to check that there are any allowed bands and kill it/return message if not
        
    LCs.append(LC0s)
    return names, RAs, Decs, zs, LCs

def FormatSNDict(SN, RA, Dec, z, t, b, m, e, source, allowed_b):
    """Takes name, coordinates, photometry of a supernova, formats it into a dictionary to be used to create a CAAT file.
    """
    names, RAs, Decs, zs, LCs = FilterOSCDataforTable(SN, RA, Dec, z, t, b, m, e, source, allowed_b)
    LCs_dict = []
    names_dict = []
    RAs_dict = []
    Decs_dict = []
    zs_dict = []
    for i in range(len(LCs)):
        points = []
        for j in range(len(LCs[i])):
            points_bool = (len(LCs[i][j][1][0]) > 4) #selects for SN w/ more than 4 points in at least one filter  
            points.append(points_bool)
        if sum(points) != 0:
            LCs_dict.append(LCs[i])
            names_dict.append(names[i])
            RAs_dict.append(RAs[i])
            Decs_dict.append(Decs[i])
            zs_dict.append(zs[i])
            
    infos = []
    for i in range(len(LCs_dict)):
        infos.append(dict(ra = RAs_dict[i], dec = Decs_dict[i], z = zs_dict[i])) 

    datas = []
    for i in range(len(LCs_dict)):
        bands_used = []
        list_of_dicts = []
        for j in range(len(LCs_dict[i])):
            bands_used.append(LCs_dict[i][j][0])
            datapoints = []
            for k in range(len(LCs_dict[i][j][1][0])):
                datapoints.append(dict(mjd=LCs_dict[i][j][1][0][k],mag = LCs_dict[i][j][1][1][k],err = LCs_dict[i][j][1][2][k]))
            list_of_dicts.append(datapoints)
#        print(bands_used)
        datas.append(dict(zip(bands_used,list_of_dicts)))
    return infos, datas, names_dict

def SaveTables(path, infos, datas, names_dict):
    with open(path+"/"+names_dict[0]+"dict.pkl", 'wb') as f:
        pickle.dump(infos, f)
        pickle.dump(datas, f)
        pickle.dump(names_dict,f)

def OSCtoCAATTables(SN, save = False, path = None):
    """ Takes SN name, returns dictionaries for CAAT
        args:
        SN = supernova name
        save = if True, will save .pkl file with table
        path = folder to save dictionary in
        
        returns: infos, datas, names_dict
    """
    RA, Dec, z, t, b, m, e, source = PullFromOSC(SN)
    infos, datas, names_dict = FormatSNDict(SN, RA, Dec, z, t, b, m, e, source, allowed_b)
    if save == True:
        SaveTables(path, infos, datas, names_dict)
    return infos, datas, names_dict
    
