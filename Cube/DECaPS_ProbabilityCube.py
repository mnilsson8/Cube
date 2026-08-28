import os
import numpy as np
import time
from scipy import interpolate
import pickle
import sys

SourceFolder = '/lustre/lrspec/users/4300/cube/Data/Phot/Decaps_LCs'
TargetFolder = '/lustre/lrspec/users/4300/cube/Data/Datacube/DECaPS_VS'

""" things I need to do to get this python script in shape
    Make function to get the dmags, colors, timepairs, bandpairs
    Put function in correct place in script
    Check that the logic of the script is correct
"""


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

EventNames = my_types.keys()


Bands = ['g', 'r', 'i', 'z']

#dT1s = np.arange(-480, 481, 15)
#dT2s = np.hstack(( np.arange(-1920, -1439, 30), np.arange(-480, 481, 30), np.arange(1440, 1921, 30) )) 

BinMag = np.arange(-5.05, 6.0, 0.1)
BinColor = np.arange(-9.25, 9.8, 0.5)

Thrs = {'u': 23.9, 'g': 25.0, 'r': 24.7, 'i': 24.0, 'z': 23.3, 'Y': 22.1}


def GeneratePath(EventName, PathInterp=PathInterp):
    return os.path.join(PathInterp, EventName+'_DECaPS.parquet.gzip')


def GetdMagsandColors(data):
    

def CalculateMap(BandPair, to_be_cubed,
                 TimePairs=TimePairs,  
                 BinMag=BinMag, BinColor=BinColor,
                 HashTableDim=HashTableDim, 
                 Objects=Objects, PointsPerDay=PointsPerDay, Thrs=Thrs):

    
    Band1 = BandPair[0]
    Band2 = BandPair[1]   
    
    
    to_be_cubed2 = to_be_cubed[to_be_cubed["Bandpairs"] == BandPair]
    
        
    Objects = np.unique(to_be_cubed2["Object Name"])
    
    HashTable = np.zeros(HashTableDim[1:], dtype=np.uint32)

    dMagMin = []
    dMagMax = []
    ColorMin = []
    ColorMax = []
    
    for kk, TimePair in enumerate(TimePairs):
        # print(kk+1,"of",len(TimePairs), TimePair)
        dT1 = TimePair[0]
        dT2 = TimePair[1]
    
        dMag = []
        Color = []
    
        #Calculate the values of the functions with selected x values.  
        dMag = to_be_cubed2["dMags"][to_be_cubed2["Timepairs"]==TimePair]
        if len(dMag) == 0:
            continue
        Color = to_be_cubed2["Colors"][to_be_cubed2["Timepairs"]==TimePair]
            
        # data = np.array([dMag, Color])
        histdata,_,_ = np.histogram2d(dMag, Color, bins=[BinMag, BinColor])
    
        dMagMin.append(min(dMag))
        dMagMax.append(max(dMag))
        ColorMin.append(min(Color))
        ColorMax.append(max(Color))
    
        outliersNo = len(dMag) - int(histdata.sum())
    
        HashTable[kk] = histdata

return  [len(Objects), BandPair, outliersNo, min(dMagMin), max(dMagMax), min(ColorMin), max(ColorMax)], HashTable


def reduceAndSave(results, EventName, HashTableDim=HashTableDim, 
                  BandPairs=BandPairs, dT1s=dT1s, dT2s=dT2s, TimePairs=TimePairs, 
                  BinMag=BinMag, BinColor=BinColor, PointsPerDay="N/A", TargetFolder=TargetFolder):
    
    
    HashTableTotal = np.zeros(HashTableDim, dtype=np.uint32)
    
    outliersNo = 0
    dMagMin = []
    dMagMax = []
    ColorMin = []
    ColorMax = []
    
    for info, HashTable in results:
        
        HashTableTotal[list(BandPairs).index(info[1])] = HashTable
        outliersNo += info[2]
        dMagMin.append(info[3])
        dMagMax.append(info[4])
        ColorMin.append(info[5])
        ColorMax.append(info[6])
        
    InfoDict = {}
    InfoDict['EventName'] = EventName
    InfoDict['PointsPerDay'] = PointsPerDay
    InfoDict['ObjectNo'] = results[0][0][0]

    InfoDict['BandPairs'] = [ii.lower() for ii in list(BandPairs)]

    InfoDict['dT1s'] = dT1s
    InfoDict['dT2s'] = dT2s

    InfoDict['BinMag'] = BinMag
    InfoDict['BinColor'] = BinColor

    InfoDict['dMagRange'] = [ min(dMagMin), max(dMagMax) ]
    InfoDict['ColorRange'] = [ min(ColorMin), max(ColorMax) ]

    infdict_tps = []
    for pair in np.unique(to_be_cubed["Timepairs"]):
        infdict_tps.append(list(pair))
    InfoDict['TimePairs'] = infdict_tps

    
    if outliersNo>0:
        InfoDict['Outliers'] = outliersNo
        InfoDict['OutliersRatio'] = outliersNo / HashTableTotal.max()        
    
    if HashTableTotal.min()<0:
        InfoDict['Overflow'] = HashTableTotal.min()
        
    #Save results

    FileName = 'ProbCube_' + time.strftime('%m%d_%H%M') + '__' + EventName + '.pkl'

    FilePath = os.path.join(TargetFolder, FileName)
    FilePath0 = FilePath

    ii = 1
    while os.path.exists(FilePath):
        FilePath = FilePath0[:-4] + '('+str(ii)+')' + '.pkl'
        ii += 1

    with open(FilePath, 'wb') as f:
        pickle.dump(InfoDict, f)
        pickle.dump(HashTableTotal, f ) 




for EventName in EventNames:
    BandPairs = np.unique(to_be_cubed["Bandpairs"])
    TimePairs = np.unique(to_be_cubed["Timepairs"])


    HashTableDim = [ len(BandPairs), len(TimePairs), len(BinMag)-1, len(BinColor)-1 ]
    results = []
    Path = GeneratePath(EventName)
    data = pd.read_parquet("/lustre/lrspec/users/4300/cube/Data/Phot/Decaps_LCs/Cep_DECaPS.parquet.gzip")
    data = 
    for z, BandPair in enumerate(BandPairs):
        print(f'{z+1} of {len(BandPairs)}, {BandPair}')

        results.append(CalculateMap(BandPair, Data))
    reduceAndSave(results, EventName)


print('###############\nFinish!\n###############')