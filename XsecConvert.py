# Converts cm^2/molecule to m^2/kg

import astropy.units as units
import numpy as np
import os
# Mass of water in AMU

waterMass=18.02*1.6726e-27

def Convert(Xsecfolder,fileXsec,savedir=os.getcwd()):
    if savedir[-1] != '/':
        savedir=savedir+'/'
    filename,extension=os.path.splitext(fileXsec)
    f=open(Xsecfolder+fileXsec,'r')
    lines=f.readlines()
    f.close()
    wavenumber=[]
    crosssection=[]
   ### print(len(lines))
    for line in lines:
       # print(line)
        line=line.lstrip().rstrip()
        line=line.replace('    ',' ')
        line=line.replace('   ',' ')
        line=line.replace('  ',' ')

        line=line.split(' ')
       # print(line)
        line = [float(line[i]) for i in range(len(line))]
       # print(line)
        line[1]= line[1]/(1e4*waterMass)
        #print(line)
        wavenumber.append(line[0])
        crosssection.append(line[1])

    wavenumber=np.array(wavenumber)
    crosssection=np.array(crosssection)
    arr=np.array([wavenumber,crosssection])
    np.save(savedir+'{0}.npy'.format(filename),arr)
    return None

