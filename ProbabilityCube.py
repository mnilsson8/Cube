import os
import numpy as np
import math
import time
from scipy import interpolate
import pickle

import Functions

Path0 = '/global/homes/l/lianming/Presto-Color-2/data'
Path1 = '/global/homes/l/lianming/Presto-Color-2/data/Test_Interp'
Path2 = '/global/homes/l/lianming/Presto-Color-2/data/2Day_Interp'

PathInterp = Path2

####### Parameter setting

# EventNames = np.load(os.path.join(PathInterp, 'EventName.npy'))
EventNames = [ 'SNIa-SALT2']

PointsPerDay = 0.1
ObjNo = 1000

#Coordinates

InfoDict = {}
InfoDict['EventNames'] = EventNames
# InfoDict['Bands'] = ['u', 'g', 'r', 'i', 'z', 'Y']
InfoDict['Bands'] = ['g', 'i']
# InfoDict['dT1s'] = np.arange(0, 241, 15)
# InfoDict['dT2s'] =  np.arange(120, 481, 15)
InfoDict['dT1s'] = np.arange(0, 31, 15)
InfoDict['dT2s'] =  np.arange(30, 61, 15)

InfoDict['BinMag'] = np.arange(-1.25, 3.84, 0.1)
InfoDict['BinColor'] = np.arange(-9.25, 9.8, 0.5)

HashTable = np.zeros([len(InfoDict['Bands']), len(InfoDict['Bands']), len(InfoDict['dT1s']), len(InfoDict['dT2s']), len(InfoDict['BinMag'])-1, len(InfoDict['BinColor'])-1], dtype='int32')

########
time1 = time.time()

dMagRange = [[], []]
ColorRange = [[], []]

for EventName in EventNames:
    
    FilePath = os.path.join(PathInterp, EventName+'_Interp.pkl')
    with open(FilePath, 'rb') as f:
        Interp_load = pickle.load(f)
        TimeRange_load = pickle.load(f)  

    for ii, Band1 in enumerate(InfoDict['Bands']):
        for jj, Band2 in enumerate(InfoDict['Bands']):
            if jj==ii:
                continue
            else:
                for kk, dT1 in enumerate(InfoDict['dT1s']):
                    for ll, dT2 in enumerate(InfoDict['dT2s']):

                        data = Functions.CalculateMap(Interp_load, TimeRange_load, 
                                     Band1, Band2, dT1, dT2, PointsPDay=PointsPerDay, ObjNo=ObjNo);

                        histdata,_,_ = np.histogram2d(data[0], data[1], bins=[InfoDict['BinMag'], InfoDict['BinColor']])

                        dMagRange[0].append(data[0].min())
                        dMagRange[1].append(data[0].max())
                        ColorRange[0].append(data[1].min())
                        ColorRange[1].append(data[1].max())

                        outliersNo = len(data[0]) - np.sum(histdata)
                        if outliersNo != 0:
                            print('{:.0f} outliers found!'.format(outliersNo), end='')

#                         HashTable[ii, jj, kk, ll] = histdata*RateDict[EventName] + HashTable[ii, jj, kk, ll]
                        HashTable[ii, jj, kk, ll] = histdata + HashTable[ii, jj, kk, ll]

                        print('|', end='')
                    
        print('')
            
print('Finish!')

print( 'The range of dMag is [{}, {}].'.format( min(dMagRange[0]), max(dMagRange[1])) ) 
print( 'The range of Color is [{}, {}].'.format( min(ColorRange[0]), max(ColorRange[1])) )

print( '{} min spent.'.format( (time.time() - time1)/60 ))

############
# FolderPath = '/global/cscratch1/sd/lianming/Results'
FolderPath = '/global/homes/l/lianming/Presto-Color-2/data'

timestring = time.ctime()
Len = len(EventNames)
FileName = '_'.join(['ProbabilityCube', timestring[4:7]+timestring[8:10], timestring[11:16],
                     ','.join( [ EventNames[ii] for ii in range(Len) if ii <3 ] + ['and_{}_more'.format(Len-3) for _ in range(1) if Len>3]  ) ] )

FilePath = os.path.join(FolderPath, FileName+'.pkl')
FilePath0 = FilePath

ii = 1
while os.path.exists(FilePath):
    FilePath = FilePath0[:-4] + '('+str(ii)+')' + '.pkl'
    ii += 1

with open(FilePath, 'wb') as f:
    pickle.dump(EventNames, f)
    pickle.dump(InfoDict, f)
    pickle.dump(HashTable, f ) 
