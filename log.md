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
---