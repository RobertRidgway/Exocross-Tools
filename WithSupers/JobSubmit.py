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


###### End of Functions, work area is below



# This assume we're looking at a Hot Jupiter
H2=InpW.Peturber()
H2.UpdateVars(species='H2',gamma=0.07,n=0.50,t0=298.0,p0=1.0, ratio=0.8379481147247214)
H2.StringCreate()

He=InpW.Peturber()
He.UpdateVars(species='He',gamma=0.07,n=0.50,t0=298.0,p0=1.0, ratio=0.16205188527527858)
He.StringCreate()


### Air is assuming nitrogen dominated
#air=InpW.Peturber()
#air.UpdateVars(species='air',t0=298.0, file='NewSpecies/LineWidths/H2O/1H2-16O_#_air_a0.broad',model='J', ratio = 1.0)
#air.StringCreate()


#### SiO2 Isotopologues

# 28Si-16O2

OCount=[16]
SiCount=[28]


Masses=[59.96675578]   # 28Si-16O2

SiO2Isotopologue=[]
source='OYT3'
molecule='SiO2'
for i in range(len(OCount)):
    if isinstance(source,list):
        source_used=source[i]
    else: # Assume it is only a string or list of strings
        source_used=source
    O=OCount[i]
    Si=SiCount[i]
    Mass=Masses[i]
    Iso=InpW.Species()
    folder='NewSpecies/LineLists/{1}/{0}/'.format(source_used,molecule)
    moleculestr='{0}Si-{1}O2'.format(Si,O)
    Iso.UpdateVars(mass=Mass,molecule=moleculestr,source=source_used,states='NewSpecies/LineLists/{2}/{1}/{0}__{1}.states'.format(moleculestr,source_used,molecule), pffile ='NewSpecies/PartitionFunctions/{2}/{0}__{1}.pf'.format(moleculestr,source_used,molecule))
    Iso.UpdateTransitions(folder)
    SiO2Isotopologue.append(Iso)
# Range (cm-1)

offset=0.05
range_=[0.0005,5999.9995]
npoints=6000001 # 0.1 m-1 spacing

wavenumber=np.linspace(range_[0],range_[1],num=npoints)
print('The spacing is ',np.diff(wavenumber)[0]*100, 'm-1, is this correct?',flush=True)
print('The spacing is 0.1 m-1 ideally.')
import time
time.sleep(5)
broadeners=[H2.String,He.String]
note='_HotJupiter'

# Number of Pressure, Temperature points
num_P=40
num_T=20

# Pressure Limits (Bar)
Pmin=1e-11
Pmax=1e3

# 1 Bar = 10^5 Pa
# 1 Pa = 10^-5 Bar
# Matches Davids PT800 file
Pmin = 7.8804628e-05*1e-5 
Pmax = 1e3 # 10^8 Pa


# Temperature Limits (K)
Tmin=70
Tmax=6000


# Matches Davids PT800 file
Tmin=70
Tmax=3000 

P=[Pmin,Pmax]
T=[Tmin,Tmax]

offset=1e-06
PT_idx,PTPairs=PTGen(num_P,num_T,P,T)
ts=PTPairs[1]
print(np.unique(ts),len(np.unique(ts)))

UseSupers=True
if UseSupers:#
    #Extract T points to make Super-lines
    Ts=[]
    for i in range(len(PTPairs[0])):
        Ts.append(PTPairs[1][i])
    Ts=np.array(Ts)
    Ts=np.unique(Ts)

    # Make Super-line making .inp files and submit them for creation
    for i in range(len(SiO2Isotopologue)):
        IsoT=SiO2Isotopologue[i]
        print(IsoT)
        SuperLineInpCreate(IsoT,Ts,npoints,range_,broadeners,offset=offset,note=note)
        forceRec=False
        SuperLineJobSubmit(IsoT,Ts,range_,maxJobs=200,forceRecreation=forceRec,note=note)
    
    numJobs=JobCount()
    #Holds loop while waiting for jobs to finish
    while (numJobs > 0):
        print('Waiting for jobs to finish...',end='\r')
        time.sleep(100)
        numJobs=JobCount()
        if numJobs < 1:
            print('')


for i in range(len(SiO2Isotopologue)):
    IsoT=SiO2Isotopologue[i]

    InpCreate(IsoT, PT_idx,PTPairs,npoints,range_,broadeners,offset=offset,note=note,UseSupers=UseSupers)
    # Loop for submitting jobs
    forceRec=False
    JobSubmit(IsoT,PTPairs,range_,maxJobs=200,forceRecreation=forceRec,note=note)


