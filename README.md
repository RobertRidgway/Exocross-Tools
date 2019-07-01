# Exocross-Tools


## InpWrite.py 
InpWrite.py contains functions assisting in the creation of an input (.inp) file for use with Exocross. You can specify the species and (if any) broadeners.

## JobSubmit.py 

JobSubmit.py can create a list of input files to Exocross. It can also queue up the jobs for submission to a computing cluster. 

## NcGen.py

This script will convert the .xsec output files from Exocross into a .npy format, and then combine them into a netCDF file for later use.



## Other files

The copy of **xcross.exe** that is included here is not the default version, as the length of acceptable filenames in the .inp files has been increased. **submit_job.pbs** is the file that the computing cluster reads to compute the job. 

# How to use these files

After downloading the files that ExoCross needs for the molecule you wish to calculate absorption coefficients for (.states, .trans, etc), place **JobSubmit.py**, **InWrite.py**, **xcross.exe**, and **submit_job.pbs** in the folder where you want your output **.xsec** files to go. The input **.inp** files will be created here. Run **JobSubmit.py** and it will submit the jobs and create your files.

Edit **submit_job.pbs** for the estimated computation time required.
