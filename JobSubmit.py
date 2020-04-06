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
    line=['qsub submit_job.pbs -v param_file={0} -N AbsCoeff_{1}_{2}'.format(input_file,species,idx)]
    os.popen(line[0])
    return None


# Creates a list of .inp files for use with Exocross
def InpCreate(species, PTidx,PTPairs,npoints,range_,broadeners,offset=25,note=''):
    # Create .inp files
    for i in range(len(PTPairs[0])):
        pressure= PTPairs[0][i]
        temperature = PTPairs[1][i]
        print(PTidx[i],PTPairs[0][i],PTPairs[1][i])
        InpW.InpWrite(species,temperature,pressure,npoints,range_,peturbers=broadeners,offset=offset,note=note)
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


###### End of Functions, work area is below



# This assume we're looking at a Hot Jupiter
H2=InpW.Peturber()
H2.UpdateVars(species='H2',gamma=0.05,n=0.6,t0=296.0,p0=1.0, ratio=0.8379481147247214)
H2.StringCreate()

He=InpW.Peturber()
He.UpdateVars(species='He',gamma=0.05,n=0.4,t0=296.0,p0=1.0, ratio=0.16205188527527858)
He.StringCreate()


## Air is assuming nitrogen dominated
air=InpW.Peturber()
air.UpdateVars(species='air',t0=298.0, file='NewSpecies/LineWidths/H2O/1H2-16O__air_a0.broad',model='J', ratio = 1.0)
air.StringCreate()




TiO_46_16=InpW.Species()
folder='NewSpecies/LineLists/TiO/Toto/'
TiO_46_16.UpdateVars(mass=61.947543,molecule='46Ti-16O',source='Toto',states='NewSpecies/LineLists/TiO/Toto/46Ti-16O__Toto.states', pffile ='NewSpecies/PartitionFunctions/TiO/46Ti-16O__Toto.pf')
TiO_46_16.UpdateTransitions(folder)

TiO_47_16=InpW.Species()
folder='NewSpecies/LineLists/TiO/Toto/'
TiO_47_16.UpdateVars(mass=62.946663,molecule='47Ti-16O',source='Toto',states='NewSpecies/LineLists/TiO/Toto/47Ti-16O__Toto.states', pffile ='NewSpecies/PartitionFunctions/TiO/47Ti-16O__Toto.pf')
TiO_47_16.UpdateTransitions(folder)

TiO_48_16=InpW.Species()
folder='NewSpecies/LineLists/TiO/Toto/'
TiO_48_16.UpdateVars(mass=63.942857,molecule='48Ti-16O',source='Toto',states='NewSpecies/LineLists/TiO/Toto/48Ti-16O__Toto.states', pffile ='NewSpecies/PartitionFunctions/TiO/48Ti-16O__Toto.pf')
TiO_48_16.UpdateTransitions(folder)

TiO_49_16=InpW.Species()
folder='NewSpecies/LineLists/TiO/Toto/'
TiO_49_16.UpdateVars(mass=64.942780,molecule='49Ti-16O',source='Toto',states='NewSpecies/LineLists/TiO/Toto/49Ti-16O__Toto.states', pffile ='NewSpecies/PartitionFunctions/TiO/49Ti-16O__Toto.pf')
TiO_49_16.UpdateTransitions(folder)

TiO_50_16=InpW.Species()
folder='NewSpecies/LineLists/TiO/Toto/'
TiO_50_16.UpdateVars(mass=65.939702,molecule='50Ti-16O',source='Toto',states='NewSpecies/LineLists/TiO/Toto/50Ti-16O__Toto.states', pffile ='NewSpecies/PartitionFunctions/TiO/50Ti-16O__Toto.pf')
TiO_50_16.UpdateTransitions(folder)


# Range (cm-1)

offset=0.05
range_=[0.0005,29999.9995]
npoints=30000001 # 0.1 m-1 spacing

wavenumber=np.linspace(range_[0],range_[1],num=npoints)
print('The spacing is ',np.diff(wavenumber)[0]*100, 'm-1, is this correct?',flush=True)
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


InpCreate(TiO_46_16, PT_idx,PTPairs,npoints,range_,broadeners,offset=offset,note=note)
InpCreate(TiO_47_16, PT_idx,PTPairs,npoints,range_,broadeners,offset=offset,note=note)
InpCreate(TiO_48_16, PT_idx,PTPairs,npoints,range_,broadeners,offset=offset,note=note)
InpCreate(TiO_49_16, PT_idx,PTPairs,npoints,range_,broadeners,offset=offset,note=note)
InpCreate(TiO_50_16, PT_idx,PTPairs,npoints,range_,broadeners,offset=offset,note=note)

# Loop for submitting jobs

forceRec=False
JobSubmit(TiO_46_16,PTPairs,range_,maxJobs=300,forceRecreation=forceRec,note=note)
JobSubmit(TiO_47_16,PTPairs,range_,maxJobs=300,forceRecreation=forceRec,note=note)
JobSubmit(TiO_48_16,PTPairs,range_,maxJobs=300,forceRecreation=forceRec,note=note)
JobSubmit(TiO_49_16,PTPairs,range_,maxJobs=300,forceRecreation=forceRec,note=note)
JobSubmit(TiO_50_16,PTPairs,range_,maxJobs=300,forceRecreation=forceRec,note=note)


