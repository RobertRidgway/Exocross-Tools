import numpy as np
import netCDF4 as nc
import os
import XsecConvert as XC





# Converts .xsec files into .npy files, and then creates a .nc 
# for use in corr-k and SOCRATES/ATMO
def NcCreate(filename,mass,homedir,absdir,datadir,xsecfolder,npyfolder,npoints_P=40,npoints_T=20):
    files_all=os.listdir(xsecfolder)
    files=[]
    count=0
    for file_ in files_all:
        fname, ext=os.path.splitext(file_)
        if file_.endswith('.xsec'):
            fnamenpy=fname+'.npy'
            count+=1
            if not os.path.isfile(npyfolder+fnamenpy):
                print(count,'Converting {0} to .npy format.'.format(file_))
                XC.Convert(xsecfolder,file_,mass,savedir=npyfolder)
    # File format is wavenumber (cm-1) and absorption coeff (m^2/kg)        
    print('Getting list of .npy files')
    files_npy=os.listdir(npyfolder)

    temp_list=[]
    pressure_list=[]
    abscoeff_list=[]
    fname_list=[]
    count=0
    for file_ in files_npy:
        count+=1
        print(count, 'Loading ',file_)
        fname,ext=os.path.splitext(file_)
        fname=fname.split('_')
        temp=float(fname[2])
        pressure=float(fname[3])
        temp_list.append(temp)
        pressure_list.append(pressure)
        fname_list.append(file_)
        
        #abscoeff_list.append(absc)

    temp_list=np.array(temp_list)
    pressure_list=np.array(pressure_list)
    fname_list=np.array(fname_list)
    abscoeff_list=np.array(abscoeff_list)
    idx_P=np.argsort(pressure_list)

    temp_list=temp_list[idx_P]
    pressure_list=pressure_list[idx_P]
    #abscoeff_list=abscoeff_list[idx_P]
    fname_list=fname_list[idx_P]
    temp_ss=[]
    pressure_ss=[]
    fname_ss=[]

    filenp=np.load(npyfolder+fname_list[0])
    nu, absc = filenp[0]*100,filenp[1] # m^{-1}, m^2/kg
    proper_nu_length=len(nu)
    del filenp
    del nu
    del absc
    for pressure in np.unique(pressure_list):
        # List of pressure indices 
        idx=np.where(pressure_list == pressure)
        #print(idx)
        temp_slice=temp_list[idx]
        if (npoints_T - len(temp_slice)) > 1: 
            print('{0:.3e} Bar is missing {1} points, skipping.'.format(pressure,40-len(temp_slice)))
            continue
        elif (npoints_T - len(temp_slice)) ==1:
            print('{0:.3e} Bar is missing {1} point, skipping.'.format(pressure,40-len(temp_slice)))
            continue
        #print('{0:.3e} Bar has all {1} points, adding to the .nc.'.format(pressure,len(temp_slice)))
        fname_slice=fname_list[idx]
    
        idx_t=np.argsort(temp_slice)
        temp_slice=temp_slice[idx_t]
        fname_slice=fname_slice[idx_t]
        #print(pressure,len(temp_slice),len(abs_slice),len(abs_slice[0]))
        for i in range(len(temp_slice)):
            pressure_ss.append(pressure)
            temp_ss.append(temp_slice[i])
            
            fname_ss.append(fname_slice[i])
    
    pressure_ss=np.array(pressure_ss)
    temp_ss=np.array(temp_ss)
    fname_ss=np.array(fname_ss)
        
        #Okay, so they're all in .npy format for easy access, now what?

    # Let's make a .nc file for them!
    fnc=nc.Dataset(absdir+filename,'w')

    scalar_dim=fnc.createDimension('scalar',1)
    nu_dim=fnc.createDimension('nu',proper_nu_length)
    pt_pair_dim=fnc.createDimension('pt_pair',len(temp_ss))


    nu_var=fnc.createVariable('nu','f8',('nu',))
    kabs=fnc.createVariable('kabs','f4',('pt_pair','nu',))
    t_calc= fnc.createVariable('t_calc','f8',('pt_pair',))
    p_calc= fnc.createVariable('p_calc','f8',('pt_pair',))


    filenp=np.load(npyfolder+fname_ss[0])
    nu, absc = filenp[0]*100,filenp[1] # m^{-1}, m^2/kg
    del filenp
    nu_var[:]=nu
    nu_var.step=abs(nu[1]-nu[0])
    print(nu_var.step)
    #nu_var.step=0.1
    #nu_var.step=10.0 # Equivalent to 0.1 in cm-1

    # Number of PT points

    PTnum=npoints_P*npoints_T
    print('Loading .npy files and placing into .nc file.')
    for i in range(0,len(pressure_ss)):
        print(i,PTnum,fname_ss[i])
        filenp=np.load(npyfolder+fname_ss[i])
        nu, absc = filenp[0]*100,filenp[1] # m^{-1}, m^2/kg
        t_calc[i]=temp_ss[i]
        p_calc[i]=pressure_ss[i]*1e5 # Bar to Pa
        #for j in range(1,len(abs_ss[i])):
        #    kabs[i,j]=abs_ss[i][j]
        #print(i,pressure_ss[i])
        kabs[i,:] = absc


    fnc.close()
    print('File written to: {0}'.format(absdir+filename))
    return None


################ End of Functions
################ Beginning of work area
import shutil
homedir='/home/dc-ridg1/data/Exocross/'
absdir='/home/dc-ridg1/AbsCoeffs/'
datadir='/data/dp015/dc-ridg1/NewSpecies/AbsCoeffs/TiO/'


# https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl
Omass=15.99491461956
masses= [45.9526316,
         46.9517631,
         47.9479463,
         48.9478700,
         49.9447912]
masses=(np.array(masses)+Omass)*1.6726e-27
for i in range(0,len(masses)):
    xsecfolder=homedir+'Results/TiO_Toto/{0}Ti-16O/'.format(i+46)
    npyfolder=homedir+'npys/TiO_Toto/{0}Ti-16O/'.format(i+46)
    filename='abs_coeff_{0}Ti-16O_Toto_pt800.nc'.format(i+46)
    NcCreate(filename,masses[i],homedir,absdir,datadir,xsecfolder,npyfolder,npoints_P=40,npoints_T=20)
    shutil.copy(absdir+filename,datadir+filename)

    
    




