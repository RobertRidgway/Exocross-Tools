# Exocross-Tools


## Example #1: Downloading a line-list and computing absorption coefficients

Please read the Exocross users manual. The scripts which interact with Exocross use similar terminology to the users manual. In this example we will be using the VBATHY line-list for 40Ca-16O supplied by ExoMol.

1. Create a working directory, or use this directory.
2. Copy JobSubmit-Clean.py to the working directory.
3. Copy InpWrite.py to the working directory.
4. Copy xcross.exe (or your compiled version of Exocross) to the working directory.
5. If your computer supports the **qsub** job submission system, copy submit_job.pbs to the working directory. If it does not, you will need to modify the **QSubmit** function in JobSubmit-Clean.py to the method you use to submit your own jobs.
6. Download the .trans, .states, .pf, and .def files from the ExoMol website. Unzip the .states and .trans file. To save time, you can run the Download bash file in this directory to do this step for you.
7. From the .def file, find the following:
   1. The molecular mass (in Da)
   2. The maximum wavenumber (in cm-1)
   3. The maximum temperature of the partition function
   4. The default Lorentzian Half-width
   5. The default Temperature exponent
8. Modify the species object by completing the empty fields
   1. folder_trans = '$working directory' (In practice, this is the folder where the .trans files are located, use the absolute path and not the relative path)
   2. mass = the mass you obtained earlier (I have been using the mass supplied from ExoMol)
   3. molecule = '40Ca-16O' (I typically match the name of the molecule from the line-list, but this does not need to be followed)
   4. source= 'VBATHY' (I typically attach the name of the list-list for quick idenfication in case of updated line-lists being released in the future)
   5. states='$working directory+40Ca-16O__VBATHY.states'
   6. pffile = '$working directory+40Ca-16O__VBATHY.pf'

9. Now we need to supply information about pressure broadening species. As of May 2020, the VBATHY line-list does not have any pressure broadening data. We will need to supply the following information into **broadener1**.
   1. The broadening species. In practice this is likely to be H2, He, air, self (The molecule itself), or CO2. Let us assume this is data being used for a Hot Jupiter and use H2 for the species.
   2. The temperature exponent, gamma. This value is used if the supplied broadening data does not exist for some wavenumber range. Since we do not have any supplied data, this value will be used everywhere. It is possible for a broadening species to have its own default Half-width and temperature exponent, and those values should be used for each species instead of default values. For an example of this data, see the H2O BT2 linelist's .def file, and compare the values for H2 and He broadening. 
   3. The Lorentzian Half-width, n. Similarly to gamma, this is used if there is no supplied data that can be used.
   4. The reference temperature (K), typically 298 K
   5. The reference pressure (bar), typically 1.0
   6. The abundance ratio of the broadening species. This is usually 1 unless multiple broadening species are being included, in which case the abundance ratios of the broadening species should be used.
   7. We do not have supplied data, so **file** and **model** should be left untouched. If they are left untouched, they will not be included in the string containing the broadening information which will be put into the .inp file.
10. Add a second element to **range_** to determine the maximum wavenumber. Supply a value in cm-1. We can use 24999.97 here. Note that Exocross will provide points for each endpoints, which is why our minimum bound is not 0.
11. Provide an odd number of points, and vary the number of points until the wavenumber spacing is what you want. (I have been using a spacing of 0.1 m-1, but any number will suffice).
12. Uncomment **broadeners** to create a list of the strings containing the information from the broadeners that will be supplied to the .inp files.
13. Add a note (this can be anything, but could be used to denote any assumptions about the pressure broadeners, such as being an Earth-like atmosphere or a Hot Jupiter atmosphere).
14. Determine the number of Pressure and Temperature points you want absorption coefficients to be calculated for. The number of points that are calculated for, will be **num_P** **num_T**.
15. Determine the limits (in bar) for the pressure.
16. Determine the limits (in Kevlin) for the temperature.
17. PTGen will generate a list of P-T points (in log-space) that ranges between the limits of pressure and temperature)
18. InpCreate will create a list of .inp files in your working directory. These will be used for JobSubmit as it will assume they exist.
19. JobSubmit will (over time) submit each of the Exocross jobs to your job submission queue. It will periodically check on the number of submitted jobs and will not submit more jobs if there are **maxJobs** being submitted (running and queued). If your computer does not use the **qsub** job submission system this may not work as intended and may require signification modification of the job submission and job checking functions.
20. JobSubmit-Clean.py can now be run, and now create the input files and will submit each of the exocross jobs.
21. As part of the **qsub** submission system, the computation time in **submit_job.pbs** may need to be increased.

### Inp Format

To understand the information supplied in the .inp files in more detail, please refer to the Exocross user's manual. You can see how Exocross-Tools creates the .inp files by looking at the InpWrite function in InpWrite.py. Note: if **nprocs** is changed, make sure that **ppn** in **submit_job.pbs** is changed to the same value.

### Next Steps

Now that you have a list of .xsec files containing absorption coefficients (in cm^2/molecule) over a range of pressures and temperatures, you're essentially done. You can take the data and use it however you wish. If you want to turn the data into a netCDF, please move on to Example 2.

