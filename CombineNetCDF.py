import numpy as np
import netCDF4 as nc


def CombineCDFs(output,files,ratios,absdir):
    
    ratios=np.array(ratios)
    norm=np.sum(ratios)
    print(ratios)
    ratios=ratios/norm
    print(ratios,norm,np.sum(ratios))
    for ratio in ratios:
        if ratio < 0:
            print('One of the fractions is negative!')
            return False

    # Assumes shape is identical over all files


    fnc=nc.Dataset(absdir+output,'w')

    # For dimensions and shapes
    file_=nc.Dataset(absdir+files[0],'r')
    nu_length=len(file_['nu'])
    pt_num=len(file_['t_calc'])
    scalar_dim=fnc.createDimension('scalar',1)
    nu_dim=fnc.createDimension('nu',nu_length)
    pt_pair_dim=fnc.createDimension('pt_pair',pt_num)
    nu_var=fnc.createVariable('nu','f8',('nu',))
    kabs=fnc.createVariable('kabs','f4',('pt_pair','nu',))
    t_calc= fnc.createVariable('t_calc','f8',('pt_pair',))
    p_calc= fnc.createVariable('p_calc','f8',('pt_pair',))

    nu_var[:]=file_['nu'][:]
    t_calc[:]=file_['t_calc'][:]
    p_calc[:]=file_['p_calc'][:]
    nu_var.step= abs(file_['nu'][1]-file_['nu'][0])
    print('Creating {0}!'.format(output))

    print(nu_var.step)
    file_.close()

    # Puts all ncs into memory to save time
    filesNC=[]
    for i in range(len(files)):
        filesNC.append(nc.Dataset(absdir+files[i],'r'))
        
    # Iterates over all PT points and weights them according 
    # to the supplied ratios
    for i in range(0,pt_num):
        print(i,pt_num,end='\r',flush=True)
        file_=filesNC[0]
        kabs_weighted=np.array(file_['kabs'][i,:])*ratios[0]
        for j in range(1,len(files)):
            file_=filesNC[j]
            kabs_weighted+=np.array(file_['kabs'][i,:])*ratios[j]
        kabs[i,:]=kabs_weighted
    # Closes all open ncs
    for file_ in filesNC:
        file_.close()
    del filesNC
    fnc.close()
    print('\n',output,'has been created!')
    return None

####### End of functions
####### Beginning of work area


HAbundances={ '1': 0.999885, '2': 0.000115}
SAbundances={ '32': 0.9499, '33':0.0075, '34': 0.0425,'36':0.0001}
SiAbundances={'28': 0.92223,'29':0.04685,'30':0.03092}
NaAbundances={'23': 1.0}
AlAbundances={'27': 1.0}
OAbundances={'16': 0.99757, '17': 0.00038,'18': 0.00205}
CaAbundances={'40': 0.96941}
TiAbundances={'46': 0.0825, '47': 0.0744, '48': 0.7372, '49': 0.0541, '50': 0.0518}
MgAbundances={'24': 0.7899, '25': 0.1000, '26':0.1101}


# NaH
ratios_NaH=[]
HCount=[1,2]
NaCount=[23,23]
files_NaH=[]
for i in range(len(HCount)):
    Na=NaCount[i]
    H=HCount[i]
    abund=NaAbundances[str(Na)]*HAbundances[str(H)]
    ratios_NaH.append(abund)
    filename='abs_coeff_{0}Na-{1}H_Rivlin_pt800.nc'.format(Na,H)
    files_NaH.append(filename)

absdir='/home/dc-ridg1/AbsCoeffs/'
filename_NaH='abs_coeff_NaH_Rivlin_TerrestrialAbund_pt800.nc'
CombineCDFs(filename_NaH,files_NaH,ratios_NaH,absdir)

# Source for abundances: 
# https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl


