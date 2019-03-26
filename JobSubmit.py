import os
import numpy as np
import InpWrite as InpW
import time
import subprocess

# Counts the number of active jobs
def JobCount(user='dc-ridg1'):
    var = os.popen('qstat -u {0} > test_count.txt ; grep -rnc "./test_count.txt" -e "{0}"'.format(user)).read()
    os.popen('rm test_count.txt')
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

# Submits jobs (assuming DiRaC)
def QSubmit(input_file,species,idx):
    line=['qsub submit_job.pbs -v param_file={0} -N AbsCoeff_{1}_{2}'.format(input_file,species,idx)]
    os.popen(line[0])
    return None


# Creates a list of .inp files for use with Exocross
def InpCreate(species, PTidx,PTPairs,npoints,range_,broadeners):
    # Create .inp files
    for i in range(len(PTPairs[0])):
        pressure= PTPairs[0][i]
        temperature = PTPairs[1][i]
        print(PTidx[i],PTPairs[0][i],PTPairs[1][i])
        InpW.InpWrite(species,temperature,pressure,npoints,range_,peturbers=broadeners)
    return None


# Submits jobs to the queue
def JobSubmit(species,PTPairs,range_,maxJobs=100,forceRecreation=False):
    for i in range(len(PTPairs[0]))[:1]:
        pressure= PTPairs[0][i]
        temperature = PTPairs[1][i]
    
        filenameInp='{0}_{1}_{2}_{3}_{4}_{5}.inp'.format(species.molecule,species.source,temperature,pressure,range_[0],range_[1])
        filenameXsec='{0}_{1}_{2}_{3}_{4}_{5}.xsec'.format(species.molecule,species.source,temperature,pressure,range_[0],range_[1])
        numJobs=JobCount()
        # Only submits job if file 
        if not os.path.isfile(filenameXsec) or forceRecreation:
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

    print('All jobs have been submitted!')
    return None


###### End of Functions, work area is below



# This assume we're looking at a Hot Jupiter
H2=InpW.Peturber()
H2.UpdateVars(species='H2',gamma=0.0207,n=0.44,t0=298.0,
               file='NewSpecies/LineWidths/H2O/1H2-16O__H2.broad', 
              model='JJ',ratio=0.8379481147247214)
H2.StringCreate()

He=InpW.Peturber()
He.UpdateVars(species='He',gamma=0.043,n=0.02,t0=298.0,
              file='NewSpecies/LineWidths/H2O/1H2-16O__He.broad', 
              model='JJ',ratio=0.16205188527527858)
He.StringCreate()


## Air is assuming nitrogen dominated
air=InpW.Peturber()
air.UpdateVars(species='air',t0=298.0, file='NewSpecies/LineWidths/H2O/1H2-16O__air_a0.broad',
               model='J', ratio = 1.0)
air.StringCreate()


H2O=InpW.Species()
folder='NewSpecies/LineLists/H2O/POKAZATEL/'
H2O.UpdateVars(mass=18.02,molecule='H2O',source='POKAZATEL',states='NewSpecies/LineLists/H2O/POKAZATEL/1H2-16O__POKAZATEL.states', pffile ='NewSpecies/PartitionFunctions/H2O/1H2-16O__POKAZATEL.pf')
H2O.UpdateTransitions(folder)


# Range (cm-1)
range_=[0,41200]

# Number of Pressure, Temperature points
num_P=40
num_T=40

# Pressure Limits (Bar)
Pmin=1e-6
Pmax=1e3

# Temperature Limits (K)
Tmin=70
Tmax=6000

P=[Pmin,Pmax]
T=[Tmin,Tmax]

PT_idx,PTPairs=PTGen(num_P,num_T,P,T)

npoints=412001
broadeners=[H2.String,He.String]

InpCreate(H2O, PT_idx,PTPairs,npoints,range_,broadeners)

# Loop for submitting jobs

JobSubmit(H2O,PTPairs,range_)


