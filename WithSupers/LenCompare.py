import os
import numpy as np
import subprocess


cwd=os.getcwd()
npyfolder='/data/dp015/dc-ridg1/Exocross/npys/TiO_Toto/'

def filesize(file_):
    var = os.popen('wc -l {0}'.format(file_))
    print(var)
    return int(var)

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


numTarget=30000001
count=0

files_npy_all=[]
files_xsec_all=[]
for i in [46,47,48,49,50]:
    npyf=npyfolder+'{0}Ti-16O/'.format(i)
    xsecf=cwd+'/{0}Ti-16O/'.format(i)
    files=os.listdir(xsecf)
    for file_ in files:
        fname,ext=os.path.splitext(file_)
        files_npy_all.append(npyf+fname+'.npy')
        files_xsec_all.append(xsecf+fname+'.xsec')
for i in range(len(files_npy_all))[150:]:
    xsecfile=files_xsec_all[i]
    npyfile=files_npy_all[i]
    numLines=file_len(xsecfile)
    print(i,xsecfile,numLines)
    if numLines != numTarget:

        os.remove(npyfile)
        os.remove(xsecfile)
        print('File Deleted!')
