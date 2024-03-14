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


# Running Exocross Tools

Please note that this tool set assumes you're running on a system which uses PBS for job submission.

1. Identify which species you want to calculate opacity coefficients for.
2. From the species page on Exomol, identify the Linelist you wish to use
3. Identify any isotopologues you wish to include.
4. For each isotopologue, look at the .def files for:
    1. Molecule mass
    2. Maximum wavenumber
    3. Default Lorentztian HWHM
    4. Default Temperature Exponent
    5. Maximum temperature in the Partition Function file (.pf)
5. Between the isotopologues, determine the maximum wavenumber you wish to use. If you want to combine them together, the maximum wavenumber needs to be the same for all isotopologues. 
6. Download and unzip all .states and .trans files to a folder of your choice.
7. Download the .pf file. 
    1. If the file does not exist or the maximum temperature is insufficient, you will need to create one.
8. Modify JobSubmit.py by:
   1. Making a list of isotopologue input classes with the isotopologue masses and isotope numbers for each isotopologue, specifiying the appropriate folder location.
   2. Define the wavenumber range (in cm^-1) and number of points
   4. Define the range of Pressure/Temperature points and the number of each unique pressure and temperature points required.
   5. Modify the control flow at the bottom of the script to specify the number of jobs or if Super-lines are being used.
9. Run JobSubmit.py. You can use screen to ensure that the job submission occurs automatically in the background.
