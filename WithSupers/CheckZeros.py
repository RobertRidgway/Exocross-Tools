import os
import numpy as np

dirs=['24Mg-16O/','24Mg-17O/','24Mg-18O/','25Mg-16O/','26Mg-16O/']

empty_files=[]

for dir_ in dirs:
    files_all=os.listdir(dir_)
    for file_ in files_all:
        fname, ext=os.path.splitext(file_)
        wn=[]
        ab=[]
        if file_.endswith('.xsec'):
            fname=dir_+file_
            arr=[]
            with open(fname) as myfile:
                head = [next(myfile) for x in range(200)]
            for line in head:
                line=line.rstrip().lstrip()
                line=line.split('  ')
                arr.append(float(line[1]))
            if not np.any(np.array(arr) > 0):
                print(arr)
                empty_files.append(fname+'\n')
with open('output_empties.txt','w') as f:
    f.writelines(empty_files)

