import os
import numpy as np
import InpWrite as InpW
import time
import subprocess
import JobSubmitLib as JSL


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
PT_idx,PTPairs=JSL.PTGen(num_P,num_T,P,T)
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
        JSL.SuperLineInpCreate(IsoT,Ts,npoints,range_,broadeners,offset=offset,note=note)
        forceRec=False
        JSL.SuperLineJobSubmit(IsoT,Ts,range_,maxJobs=200,forceRecreation=forceRec,note=note)
    
    numJobs=JSL.JobCount()
    #Holds loop while waiting for jobs to finish
    while (numJobs > 0):
        print('Waiting for jobs to finish...',end='\r')
        time.sleep(100)
        numJobs=JSL.JobCount()
        if numJobs < 1:
            print('')


for i in range(len(SiO2Isotopologue)):
    IsoT=SiO2Isotopologue[i]

    JSL.InpCreate(IsoT, PT_idx,PTPairs,npoints,range_,broadeners,offset=offset,note=note,UseSupers=UseSupers)
    # Loop for submitting jobs
    forceRec=False
    JSL.JobSubmit(IsoT,PTPairs,range_,maxJobs=200,forceRecreation=forceRec,note=note)


