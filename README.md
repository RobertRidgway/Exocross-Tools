# Exocross-Tools


## InpWrite.py 
InpWrite.py contains functions assisting in the creation of an input (.inp) file for use with Exocross. You can specify the species and (if any) broadeners.

## JobSubmit.py 

JobSubmit.py can create a list of input files to Exocross. It can also queue up the jobs for submission to a computing cluster. 


## Other files

The copy of **xcross.exe** that is include here is not the default version, as the length of acceptable filenames in the .inp files has been increased. **submit_job.pps** is the file that the computing cluster reads to compute the job. 
