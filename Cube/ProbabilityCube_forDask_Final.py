import os
import numpy as np
import time
from scipy import interpolate
import pickle
import sys

#import dask
# from dask.distributed import Client

# scheduler_file = os.path.join(os.environ["SCRATCH"], "scheduler.json")

# print("here is our scheduler file")
# print(scheduler_file)

#dask.config.config["distributed"]["dashboard"]["link"] = "{JUPYTERHUB_SERVICE_PREFIX}proxy/{host}:{port}/status"

# client = Client(scheduler_file=scheduler_file)

# print('###############\nStart!\n###############')
# print("hello form dask, here is our client")
# print(client)

# WorkerNo = len(client.processing())
# print('{} workers created'.format( WorkerNo ) )

#########################################################
#Parameter setting

# RootPath = '/global/cscratch1/sd/lianming/'
Path1 = '/lustre/lrspec/prestocolor/Test_Interp1'
# Path2 = '/global/homes/l/lianming/Presto-Color-2/data/2Day_Interp'

TargetFolder = '/lustre/lrspec/users/4300/cube/Data/Datacube/KNe_updated'

PathInterp = Path1

# EventNames = np.load(os.path.join(PathInterp, 'EventName.npy'))
# EventNames = ['AGN', 'CART', 'EB', 'ILOT', 'MIRA', 'Mdwarf',
              # 'PISN', 'RRL', 'SLSN-I', 'SNII-NMF', 'SNII-Templates', 'SNIIn',
              # 'SNIa-91bg', 'SNIa-SALT2', 'SNIax', 'SNIbc-MOSFIT',
              # 'SNIbc-Templates', 'TDE', 'V19_CC+HostXT', 'uLens-Binary',
              # 'uLens-Single-GenLens', 'uLens-Single_PyLIMA']

# EventNames = [ 'SNIa-SALT2']
# EventNames = EventNames[0:11]
EventNames = ["KN_B19"]

PointsPerDay = 1
Objects = np.arange(0, 4000, 4)

Bands = ['u', 'g', 'r', 'i', 'z', 'Y']
#Bands = ['g', 'i']

dT1s = np.arange(-480, 481, 15)
dT2s = np.hstack(( np.arange(-1920, -1439, 30), np.arange(-480, 481, 30), np.arange(1440, 1921, 30) )) 

# dT1s = np.arange(-480, 481, 120) #for test
# dT2s = np.hstack(( np.arange(-1920, -1439, 240), np.arange(-480, 481, 240), np.arange(1440, 1921, 240) )) #for test
# dT1s = np.arange(60, 76, 15)
# dT2s = np.arange(450, 466, 15)

BinMag = np.arange(-5.05, 6.0, 0.1)
BinColor = np.arange(-9.25, 9.8, 0.5)
# BinMag = np.arange(-5.05, 6.0, 1)
# BinColor = np.arange(-9.25, 9.8, 2)

#print(dT1s)
#print(dT2s)
#print(BinMag)
#print(BinColor)

#sys.exit()

Thrs = {'u': 23.9, 'g': 25.0, 'r': 24.7, 'i': 24.0, 'z': 23.3, 'Y': 22.1}

###
time1 = time.time()

#########################################################
#Generating filter pairs, time pairs, see if worker No is enough for the job. 

BandPairs = [B1+B2 for B1 in Bands for B2 in Bands if B1!=B2 and B1+B2!='uY' and B1+B2!='Yu']
TimePairs = [ [ii, jj] for ii in dT1s for jj in dT2s if abs(ii) <= abs(ii-jj) ]

#if WorkerNo < len(EventNames) * len(BandPairs):
#    raise ValueError('Worker Not Enough! No. of worker is {}.'.format(WorkerNo) )

HashTableDim = [ len(BandPairs), len(TimePairs), len(BinMag)-1, len(BinColor)-1 ]

print(HashTableDim)
#sys.exit()

#########################################################
#Functions

def GeneratePath(EventName, PathInterp=PathInterp):
    return os.path.join(PathInterp, EventName+'_Interp.pkl')

def CalculateMap(BandPair, FilePath,
                 TimePairs=TimePairs,  
                 BinMag=BinMag, BinColor=BinColor,
                 HashTableDim=HashTableDim, 
                 Objects=Objects, PointsPerDay=PointsPerDay, Thrs=Thrs):
    
    Band1 = BandPair[0]
    Band2 = BandPair[1]   

    with open(FilePath, 'rb') as f:
        Interp_load = pickle.load(f)
        TimeRange_load = pickle.load(f)    
        
    TotalObjNo = len(Interp_load[Band1])
        
    if TotalObjNo <= Objects[-1]:
        Objects = Objects[Objects<TotalObjNo]
        
    HashTable = np.zeros(HashTableDim[1:], dtype=np.uint32)
    
    for kk, TimePair in enumerate(TimePairs):
        
        dT1 = TimePair[0]
        dT2 = TimePair[1]

        dMag = []
        Color = []

        dMagMin = []
        dMagMax = []
        ColorMin = []
        ColorMax = []

        for II in Objects:

            if Interp_load[Band1][II]==[] or Interp_load[Band2][II]==[]:
                continue

            #Decide the range and the length of XX.
            TimeRangeStart = max( TimeRange_load[Band1][II][0], TimeRange_load[Band2][II][0] - dT1/1440, TimeRange_load[Band1][II][0] - dT2/1440 )
            TimeRangeEnd = min( TimeRange_load[Band1][II][1], TimeRange_load[Band1][II][1] - dT2/1440, TimeRange_load[Band2][II][1] - dT1/1440 )

            TimeRange = TimeRangeEnd - TimeRangeStart
            if TimeRange<=0:
                continue
                
            SampleNo = int(PointsPerDay*TimeRange)

            XX = np.random.rand(SampleNo)*TimeRange + TimeRangeStart

            #Calculate the values of the functions with selected x values.  
            Mag1 = Interp_load[Band1][II](XX)
            Mag2 = Interp_load[Band2][II](XX+dT1/1440)
            Mag12 = Interp_load[Band1][II](XX+dT2/1440)

            #Add a threshold for the results and output.
            Mask = (Mag1<Thrs[Band1]) * (Mag2<Thrs[Band2]) * (Mag12<Thrs[Band1])

            dMag.extend(  (Mag1[Mask] - Mag12[Mask])*np.sign(dT2) )
            Color.extend(Mag1[Mask] - Mag2[Mask])

            
        # data = np.array([dMag, Color])
        histdata,_,_ = np.histogram2d(dMag, Color, bins=[BinMag, BinColor])

        dMagMin.append(min(dMag))
        dMagMax.append(max(dMag))
        ColorMin.append(min(Color))
        ColorMax.append(max(Color))

        outliersNo = len(dMag) - int(histdata.sum())

        HashTable[kk] = histdata
        if kk == 1000 or kk == len(TimePairs)-1:
            print("Step 3")
    return  [len(Objects), BandPair, outliersNo, min(dMagMin), max(dMagMax), min(ColorMin), max(ColorMax)], HashTable

def reduceAndSave(results, EventName, HashTableDim=HashTableDim, 
                  BandPairs=BandPairs, dT1s=dT1s, dT2s=dT2s, TimePairs=TimePairs, 
                  BinMag=BinMag, BinColor=BinColor, PointsPerDay=PointsPerDay, TargetFolder=TargetFolder):
    
    HashTableTotal = np.zeros(HashTableDim, dtype=np.uint32)
    
    outliersNo = 0
    dMagMin = []
    dMagMax = []
    ColorMin = []
    ColorMax = []
    
    for info, HashTable in results:
        
        HashTableTotal[BandPairs.index(info[1])] = HashTable
        outliersNo += info[2]
        dMagMin.append(info[3])
        dMagMax.append(info[4])
        ColorMin.append(info[5])
        ColorMax.append(info[6])
        
    InfoDict = {}
    InfoDict['EventName'] = EventName
    InfoDict['PointsPerDay'] = PointsPerDay
    InfoDict['ObjectNo'] = results[0][0][0]

    InfoDict['BandPairs'] = [ii.lower() for ii in BandPairs]

    InfoDict['dT1s'] = dT1s
    InfoDict['dT2s'] = dT2s

    InfoDict['BinMag'] = BinMag
    InfoDict['BinColor'] = BinColor

    InfoDict['dMagRange'] = [ min(dMagMin), max(dMagMax) ]
    InfoDict['ColorRange'] = [ min(ColorMin), max(ColorMax) ]
    InfoDict['TimePairs'] = np.array(TimePairs)
    
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

#########################################################
#Delayed

# lazy_results_Total = []

# for EventName in EventNames:
    
#     lazy_results = []
    
#     Path = GeneratePath(EventName)
    
#     for BandPair in BandPairs:
#         lazy_results.append(dask.delayed(CalculateMap)(BandPair, Path))
        
#     lazy_results_Total.append( dask.delayed(reduceAndSave)(lazy_results, EventName) )
    
# dask.compute(*lazy_results_Total);

#########################
for EventName in EventNames:
    results = []
    Path = GeneratePath(EventName)
    for BandPair in BandPairs:
        results.append(CalculateMap(BandPair, Path))
    reduceAndSave(results, EventName)
    
    

print( '{} min spent.'.format( (time.time() - time1)/60 ))

print('###############\nFinish!\n###############')
