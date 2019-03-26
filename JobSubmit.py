

import os
import numpy as np
import ExocrossINPWrite as InpW
import time
import subprocess

def JobCount(user='dc-ridg1'):
    var = os.popen('qstat -u {0} > test_count.txt ; grep -rnc "./test_count.txt" -e "{0}"'.format(user)).read()
    return int(var)


num_P=40
num_T=40

Pmin=1e-6
Pmax=1e3

Tmin=70
Tmax=6000

P=np.logspace(np.log10(Pmin),np.log10(Pmax),num=num_P)  # in Bar
T=np.logspace(np.log10(Tmin),np.log10(Tmax),num=num_T)  # in Kelvin


PT_idx=[]
PTPairs=[[],[]]
count=0
for pressure in P:
    for temp in T:
        PT_idx.append(count)
        count+=1
        PTPairs[0].append(pressure)
        PTPairs[1].append(temp)


def QSubmit(input_file):
    line=['qsub submit_job.pbs -v param_file={0} -N AbsCoeff_H2O'.format(input_file)]
    os.popen(line[0]) 
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

selfPressure=InpW.Peturber()

H2O=InpW.Species()
range_=[0,41200]
folder='NewSpecies/LineLists/H2O/POKAZATEL/'
H2O.UpdateVars(mass=18.02,molecule='H2O',states='NewSpecies/LineLists/H2O/POKAZATEL/1H2-16O__POKAZATEL.states', pffile ='NewSpecies/PartitionFunctions/H2O/1H2-16O__POKAZATEL.pf')
H2O.UpdateTransitions(folder)
listpeturbers=[H2.String,He.String]


InpDir='Inps/'

# Create .inp files
for i in range(len(PT_idx)):
    pressure= PTPairs[0][i]
    temperature = PTPairs[1][i]
    print(PT_idx[i],PTPairs[0][i],PTPairs[1][i])
    InpW.InpWrite(H2O,temperature,pressure,412001,range_,peturbers=listpeturbers)

maxJobs=101

for i in range(len(PT_idx))[194:]:
    pressure= PTPairs[0][i]
    temperature = PTPairs[1][i]
    
    filenameInp='{0}_{1}_{2}_{3}_{4}.inp'.format(H2O.molecule,temperature,pressure,range_[0],range_[1])
    filenameXsec='{0}_{1}_{2}_{3}_{4}.xsec'.format(H2O.molecule,temperature,pressure,range_[0],range_[1])
    numJobs=JobCount()
    while (numJobs >= maxJobs):
        print('Waiting for jobs to finish...',end='\r')
        time.sleep(100)
        numJobs=JobCount()
        if numJobs < maxJobs:
            print('')
    if os.path.isfile(filenameXsec):
        QSubmit(filename)
        time.sleep(5)
        numJobs=JobCount()
        print('{0:6.3f} Bar {1:6.3f} Kelvin Job submitted! {2} Jobs currently running.'.format(pressure,temperature,numJobs))
