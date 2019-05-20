import numpy as np
import netCDF4 as nc


def CombineCDFs(output,files,ratios,absdir):
    
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

    t_calc[:]=file_['t_calc'][:]
    p_calc[:]=file_['p_calc'][:]
    file_.close()

    # Puts all ncs into memory to save time
    filesNC=[]
    for i in range(len(files)):
        filesNC.append(nc.Dataset(absdir+files[i],'r'))
        
    # Iterates over all PT points and weights them according 
    # to the supplied ratios
    for i in range(0,pt_num):
        print(i,pt_num)
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
    print(output,'has been created!')
    return None

####### End of functions
####### Beginning of work area



absdir='/home/dc-ridg1/AbsCoeffs/'
files=[]
for i in [46,47,48,49,50]:
    filename='abs_coeff_{0}Ti-16O_Toto_pt800.nc'.format(i)
    files.append(filename)
ratios=[0.0825,
        0.0744,
        0.7372,
        0.0541,
        0.0518]

filename='abs_coeff_TiO_Toto_EarthIsotopicComposition_pt800.nc'

CombineCDFs(filename,files,ratios,absdir)
