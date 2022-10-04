import os
import numpy as np
import InpWrite as InpW
import time
import subprocess


# Counts the number of active jobs
def JobCount(user='dc-ridg1'):
    var = os.popen('qstat -u {0} > test_count.txt ; grep -rnc "./test_count.txt" -e "{0}"'.format(user)).read()
    #os.popen('rm test_count.txt')
    return int(var)

# Generates a list of PT points
def PTGen(numP,numT,Ps,Ts):
    P=np.logspace(np.log10(Ps[0]),np.log10(Ps[1]),num=numP)  # in Bar
    T=np.logspace(np.log10(Ts[0]),np.log10(Ts[1]),num=numT)  # in Kelvin
    PT_idx=[]
    PTPairs=[[],[]]
    count=0
    for pressure in P:
        for temp in T:
            PT_idx.append(count)
            count+=1
            PTPairs[0].append(pressure)
            PTPairs[1].append(temp)
    return PT_idx,PTPairs

def ptRead(filename):
    f=open(filename,'r')
    lines=f.readlines()
    f.close()
    count=0
    pressure=[]
    temperature=[]
    for line in lines:
        line=line.rstrip()
        line=line.split(' ')
        for i in range(0,len(line)):
            p=float(line[0].replace("D","E"))
            
            pressure.append(np.float64(line[0]))
            temperature.append(np.float64(line[i]))

# Submits jobs (assuming DiRaC)
def QSubmit(input_file,species,idx):
    line=['qsub submit_job.pbs -v param_file={0} -N Abs_{1}_{2}'.format(input_file,species,idx)]
    os.popen(line[0])
    return None


# Creates a list of .inp files for use with Exocross
def InpCreate(species, PTidx,PTPairs,npoints,range_,broadeners,offset=25,note='',UseSupers=False):
    # Create .inp files
    for i in range(len(PTPairs[0])):
        pressure= PTPairs[0][i]
        temperature = PTPairs[1][i]
        #print(PTidx[i],PTPairs[0][i],PTPairs[1][i])
        InpW.InpWrite(species,temperature,pressure,npoints,range_,peturbers=broadeners,offset=offset,note=note,UseSupers=UseSupers)
    return None

# Creates a list of .inp files for use with Exocross
def SuperLineInpCreate(species,Ts,npoints,range_,broadeners,offset=25,note=''):
    # Create .inp files
    for i in range(len(Ts)):
        temperature = Ts[i]
        InpW.SuperLineInpWrite(species,temperature,npoints,range_,peturbers=broadeners,offset=offset,note=note)
    return None


# Submits jobs to the queue
def JobSubmit(species,PTPairs,range_,maxJobs=100,forceRecreation=False,note=''):
    for i in range(len(PTPairs[0])):
        pressure= PTPairs[0][i]
        temperature = PTPairs[1][i]
    
        filenameInp='{0}_{1}_{2:8.7e}_{3:8.7e}_{4}_{5}{6}.inp'.format(species.molecule,species.source,temperature,pressure,range_[0],range_[1],note)
        filenameXsec='{0}_{1}_{2:8.7e}_{3:8.7e}_{4}_{5}{6}.xsec'.format(species.molecule,species.source,temperature,pressure,range_[0],range_[1],note)
        numJobs=JobCount()
        # Only submits job if file doesn't exist or recreation asked
        # Just for TiO
        xsecfolder=os.getcwd()+'/{0}/'.format(species.molecule)
        if not os.path.isfile(xsecfolder+filenameXsec) or forceRecreation:
            #print(filenameInp,species.molecule,i)
            QSubmit(filenameInp,species.molecule,i)
            time.sleep(5)
            numJobs=JobCount()
            if numJobs == 1:
                print('The {0:6.3e} Bar {1:6.3e} Kelvin Job has been submitted! {2} Job is currently submitted.'.format(pressure,temperature,numJobs))
            else:
                print('The {0:6.3e} Bar {1:6.3e} Kelvin Job has been submitted! {2} Jobs are currently submitted.'.format(pressure,temperature,numJobs))

        #Holds loop while waiting for jobs to finish
        while (numJobs >= maxJobs):
            print('Waiting for jobs to finish...',end='\r')
            time.sleep(100)
            numJobs=JobCount()
            if numJobs < maxJobs:
                print('')

    print('All jobs have been submitted for {0}!'.format(species.molecule))
    return None

# Submits jobs to the queue
def SuperLineJobSubmit(species,Ts,range_,maxJobs=100,forceRecreation=False,note=''):
    for i in range(len(Ts)):
        temperature = Ts[i]
    
        filenameInp='SuperLine_{0}_{1}_{2:8.7e}_{3}_{4}{5}.inp'.format(species.molecule,species.source,temperature,range_[0],range_[1],note)
        filenameXsec='super{0}_{1}_{2:8.7e}_{3}_{4}{5}.xsec'.format(species.molecule,species.source,temperature,range_[0],range_[1],note)
        numJobs=JobCount()
        # Only submits job if file doesn't exist or recreation asked
        # Just for TiO
        xsecfolder=os.getcwd()+'/{0}/'.format(species.molecule)
        if not os.path.isfile(filenameXsec) or forceRecreation:
            #print(filenameInp,species.molecule,i)
            QSubmit(filenameInp,species.molecule+'_Sup',i)
            time.sleep(5)
            numJobs=JobCount()
            if numJobs == 1:
                print('The {0:6.3e} Kelvin Super-line Job has been submitted! {1} Job is currently submitted.'.format(temperature,numJobs))
            else:
                print('The {0:6.3e} Kelvin Super-line Job has been submitted! {1} Jobs are currently submitted.'.format(temperature,numJobs))

        #Holds loop while waiting for jobs to finish
        while (numJobs >= maxJobs):
            print('Waiting for jobs to finish...',end='\r')
            time.sleep(100)
            numJobs=JobCount()
            if numJobs < maxJobs:
                print('')

    print('All super-line jobs have been submitted for {0}!'.format(species.molecule))
    return None
