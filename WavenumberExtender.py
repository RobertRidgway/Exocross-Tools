


import netCDF4 as nc
import numpy as np
import os


def RangeExtender(filename,directory):
    
    fileNC=nc.Dataset(directory+filename,'r')
    nu=fileNC['nu'][:]
    filename,ext=os.path.splitext(filename)
    fileOut=nc.Dataset(directory+filename+"_50000cm-1.nc",'w')
    nu_orig_length=len(nu)
    step=abs(nu[1]-nu[0])
    print(nu,step,len(nu))
    nu=[nu[i] for i in range(len(nu))]
    count=0
    while nu[-1] < 50000*100:
        count+=1
        if count % 2.5e4 ==0:
            print("{0}, {1:6.5e}".format(len(nu),50000*100-nu[-1]),end='\r',flush=True)
        nu.append(nu[-1]+step)
    print('\n',len(nu))
    nu_length=len(nu)
    pt_num=len(fileNC['t_calc'])
    nu_dim=fileOut.createDimension('nu',nu_length)
    pt_pair_dim=fileOut.createDimension('pt_pair',pt_num)
    scalar_dim=fileOut.createDimension('scalar',1)

    nu_var=fileOut.createVariable('nu','f8',('nu',))
    kabs=fileOut.createVariable('kabs','f4',('pt_pair','nu',))
    t_calc= fileOut.createVariable('t_calc','f8',('pt_pair',))
    p_calc= fileOut.createVariable('p_calc','f8',('pt_pair',))
    nu=np.array(nu)
    nu_var[:]=nu[:]
    nu_var.step=step

    t_calc[:]=fileNC['t_calc'][:]
    p_calc[:]=fileNC['p_calc'][:]
    k_zero=np.zeros(nu_length)

    for i in range(pt_num):
        print(i,pt_num,end='\r',flush=True)
        k_zero_used=np.copy(k_zero)
        kabs[i,:]=k_zero_used[:]
        kabs[i,:nu_orig_length]=fileNC['kabs'][i,:]
    print('')
    fileNC.close()
    fileOut.close()
filename='abs_coeff_TiO_Toto_TerrestrialAbund_pt800.nc'
directory='/home/dc-ridg1/AbsCoeffs/'
RangeExtender(filename,directory)
