# Work log
## Format
Mon XX, XXXX
| File | What changed | 
|---|---|
| File1 | Blah blah blah |
| File2 | Blah blah blah | 

Next steps:
* step
* step
* step

---
Jan 21, 2026

| File | What changed | 
|---|---|
| CheckingICanUsePresto2D.ipynb | Ran code to open data file and plot light curves from SNIa_SALT2 data. |

Next steps:
- ask about interpolation function to use
- plot data cube slices of PrestoColor 2 data
- use code to get SweetSpot data and plot LCs
- plot data cube slices of SweetSpot 2 data
- figure out how I want to save data
  - check pickle out
  - check HDF5 out
  - figure out what structure makes sense to me
  - pre or post interpolation?
- write a first edition more general script for doing the above
---
Feb 6, 2026

| File | What changed | 
|---|---|
| CheckingICanUsePresto2D.ipynb | Ran this notebook on DARWIN, made sure all needed packages were installed in cube-env | 
| HDF5_file_for_SNIa-SALT2.ipynb | Tried to save interpolation functions as HDF5 file, not possible, should just focus on saving data cube instead | 
| log.md | Created the log | 

Next steps:
* test code for data cube
* try making data cube but as .hdf5 instead of .pkl
* ask if doing it this way even makes sense lol (aka I think something is confusing me but I'm not even sure what.)
* delete/rm HDF5_file_for_SNIa-SALT2.ipynb
---
Feb 7, 2026

| File | What changed | 
|---|---|
| HDF5_file_for_SNIa-SALT2.ipynb | Removed from staging/repository. Also accessed Darwin on my Windows laptop which will make things very convenient going forward | 

Next steps:
* test code for data cube
* try saving data cube but as .hdf5 instead of .pkl
---
Feb 20, 2026
| File | What changed | 
|---|---|
| ProbabilityCube.py | Uploaded file from PrestoColor2, used to make data cube for SNIa-SALT2 |
| Data | Made directory for data cube | 
| PlottingDataCubeSlice_test.ipynb | was in fact able to plot a data cube slice. There are comments on things to update in there.|

Next steps:
* no real reason to save as .hdf5
* make more plots of data cubes to make sure I understand how to load data in
* change dT1s and dT2s for the data cube and also add more bands
* change enquiry function in PlottingDataCubeSlice_test.ipynb so it properly pulls 4 indices for the HashTable
* set up VSCode SSH

---
Mar 18, 2026
| File | What changed | 
|---|---|
| Data/Phot | Made another directory for data because the one I made a month ago doesn't exist in GitHub |
| SweetSpotLCs.txt | Added SweetSpot LCs to Data/Phot. These are the LCs from DR1. Photometry was done in JHKs bands.| 
* load SweetSpot data in
* test interpolating on SweetSpot, knowing I'm going to change the method of interpolation later
