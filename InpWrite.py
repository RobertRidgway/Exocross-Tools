import os
import glob

folder_base='/data/dp015/dc-ridg1/'

class Peturber(object):

    def __init__(self):
        self.gamma=None
        self.n=None
        self.t0=None
        self.p0=None
        self.species=None
        self.model=None
        self.file=None
        self.ratio=None

    def UpdateVars(self,**kwargs):
        for key, value in kwargs.items():
            if key == 'gamma':
                self.gamma=value
            elif key == 'n':
                self.n = value
            elif key == 't0':
                self.t0 = value
            elif key == 'p0':
                self.p0 = value
            elif key == 'species':
                self.species = value
            elif key == 'model':
                self.model = value
            elif key == 'file':
                self.file = folder_base+value
            elif key == 'ratio':
                self.ratio = value
            else:
                print('{0} is not recognized as a variable'.format(key))
        return None


    def StringCreate(self):
        if self.species is None:
            print('The peturbing species is not defined!')
            return False
        #elif self.model is None:
        #    print('The peturbing model is not defined!')
        #    return False
        #elif self.file is None:
        #    print('The file containing the broadening terms is not defined!')
        #    return False
        elif self.ratio is None:
            print('The abundance ratio for the peturber is not defined!')
            return False
        self.String='{0} '.format(self.species)
        if self.gamma is not None:
            self.String += 'gamma {0} '.format(self.gamma)
        if self.n is not None:
            self.String += 'n {0} '.format(self.n)
        if self.t0 is not None:
            self.String += 't0 {0} '.format(self.t0)
        if self.p0 is not None:
            self.String += 'p0 {0} '.format(self.p0)
        if self.file is not None:
            self.String += 'file {0} '.format(self.file)
        if self.model is not None:
            self.String += 'model {0} '.format(self.model)
        if self.ratio is not None:
            self.String += 'ratio {0}'.format(self.ratio)
        return True

# Class for the species we want to create absorption coefficients for 
class Species(object):
    def __init__(self):
        self.states=None
        self.pffile=None
        self.mass=None
        self.molecule=None
        self.source=None
        self.transitions=None
    # Updates Species,states,partition function file, and mass
    def UpdateVars(self,**kwargs):
        for key, value in kwargs.items():
            if key == 'molecule':
                self.molecule=value
            elif key =='source':
                self.source=value
            elif key == 'states':
                self.states=folder_base+value
            elif key == 'mass':
                self.mass=value
            elif key == 'pffile':
                self.pffile=folder_base+value
            else:
                print('{0} is not recognized as a variable'.format(key))
        return None

    # Creates list of transition files used in the .inp file, needs range (in cm-1)
    # and containing folder

    def UpdateTransitions(self, folder):
        # List of files
        files=glob.glob(folder_base+folder+'*.trans')
        files.sort()
        self.transitions=files
        return True

# Rounds up to the next multiple of 100
# This is used assuming 100 cm-1 spacing is used for .trans files
def roundup(x):
    if x % 100 ==0:
        return x
    else:
        return x +100 - x % 100

# Rounds down to the next multiple of 100
def rounddown(x):
    if x %100 ==0:
        return max(x,0)
    else:
        x= x-x % 100
        return max(0,x)

# Takes pressure in Bar, temperature in K
def InpWrite(speciesInfo,temperature,pressure,npoints,range_,note='',offset=25, peturbers=None,homedir=os.getcwd()):
    
    if homedir[-1] != '/':
        homedir=homedir+'/'

    filename=homedir+'{0}_{1}_{2:8.7e}_{3:8.7e}_{4}_{5}{6}.inp'.format(speciesInfo.molecule,speciesInfo.source,temperature,pressure,range_[0],range_[1],note)
    #print(filename)
    fileInp=open(filename,'w')

    fileInp.write('temperature {0:8.7e} (K)\n'.format(float(temperature)))
    fileInp.write('pressure {0:8.7e} (bar)\n\n'.format(float(pressure)))
    fileInp.write('range {0},{1} (cm-1)\n'.format(range_[0],range_[1]))
    fileInp.write('npoints {0}\n'.format(npoints))

    #fileInp.write('offset {0}\n'.format(offset))
    fileInp.write('mem 12 GB\n')
    fileInp.write('Ncache 10000000\n')
    fileInp.write('absorption\nthreshold 0\nVoi-Fnorm\n')
    fileInp.write('output {0}_{1}_{2:8.7e}_{3:8.7e}_{4}_{5}{6}\n'.format(speciesInfo.molecule,speciesInfo.source,temperature,pressure,range_[0],range_[1],note))

    fileInp.write('nprocs 36\n')

    ####### Species info and lists of files for States, Partition Function
    ####### and Transitions

    fileInp.write('States {0}\n'.format(speciesInfo.states))
    fileInp.write('pffile {0}\n'.format(speciesInfo.pffile))
    fileInp.write('mass {0} (amu)\n'.format(speciesInfo.mass))

    ## Writes Transitions
    ## Finds all fies within a certain window around the range
    ## Takes into account offset
    rangemin=range_[0]
    rangemax=range_[1]
    
    rangemin=rounddown(range_[0])
    rangemax=roundup(range_[1])
    files=[]
    for file_ in speciesInfo.transitions:
        line=os.path.splitext(os.path.basename(file_))[0]
        if speciesInfo.molecule != line[:len(speciesInfo.molecule)]:
           
            continue
        line=line.split('__')
        # Presumably in form of species__source__rangemin-rangmax.trans
        if len(line) > 2:
            line=line[2]
            line=line.split('-')
            rmin=int(line[0])
            rmax=int(line[1])
            if (rmin >= rangemax or rmax <= rangemin):
                pass
            else:
                files.append(file_)
        else: # Files without mins or maxes
            files.append(file_)
            
        
    if len(files)==1:
        fileInp.write('Transitions {0}\n'.format(files[0]))
    else:
        fileInp.write('Transitions\n')
        for transfile in files:
            fileInp.write('  {0}\n'.format(transfile))
        fileInp.write('end\n\n')
    # Puts in the terms controlling broadening species, if they exist
    if peturbers is not None:
        
        if isinstance(peturbers,str):
            peturbers=[peturbers]
        
        if len(peturbers) ==1:
            fileInp.write('Species {0}\n'.format(peturbers[0]))
        elif len(peturbers) >1:
            fileInp.write('Species\n')
            for species in peturbers:
                fileInp.write('  {0}\n'.format(species))
            fileInp.write('end\n')
    fileInp.close()



