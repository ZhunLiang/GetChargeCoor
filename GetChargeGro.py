#!/home/lz/lz/Software/anaconda3/bin/python
#run like:  GetChargeGro.py -i end.gro -p output1.dat -o gro_charge.dat

import re
import os
import numpy as np
import sys
from optparse import OptionParser

#----Set input parameter----#
parser = OptionParser()
parser.add_option("-i",dest="gro_file",default="start.gro",help="Input gro file")
parser.add_option("-p",dest="ecpm_file",default="output.dat",help="Input ecpm output.dat file")
parser.add_option("-o",dest="output_file",default="ChargeCoor.dat",help="Output file with coor and charge")
(options,args)=parser.parse_args()

#----Iinitial input parameter----#
gro_file = options.gro_file
ecpm_file = options.ecpm_file
output_file = options.output_file

#----Read ecpm output.dat----#
#------ele_num: electrode atom numer------#
#------mean_charge: electrode atom mean charge, ele_num*1 matrix------#

if os.path.exists(ecpm_file):
    ecpm = open(ecpm_file,"r")
else:
    print("%s do not exit." %(ecpm_file))
    sys.exit()
ecpm_line = ecpm.readlines()
temp_file = "Charge.dat"
temp_output = open(temp_file,"w+")
end_string = "= On-fly processing: # density ="
ele_atom_string = "NUserSelectGrid"

begin_line = 0
for i in range(len(ecpm_line)):
    if ele_atom_string in ecpm_line[i]:
        num_line = ecpm_line[i].rstrip("\n").split("=")
        ele_num = int(num_line[1])
    if end_string in ecpm_line[i]:
        begin_line = i+1
        break
end_line = len(ecpm_line)
for i in range(begin_line,end_line):
    temp_output.write(ecpm_line[i])
ecpm.close()
temp_output.close()
charge_data = np.loadtxt(temp_file)
mean_charge = np.mean(charge_data,0).reshape([-1,1])
os.remove(temp_file)

#----Read gro file and get coordinate----#
#------gro_coor: electrode coordinate and box size: (ele_num+1)*3 matrix------#
if os.path.exists(gro_file):
    gro = open(gro_file,"r")
else:
    print("%S do not exit." %(gro_file))
    sys.exit()
coor_match = r"-?\d+\.\d+"
re_match = re.compile(coor_match)
gro_line = gro.readlines()
gro_temp = "electrode.dat"
temp_gro = open(gro_temp,"w+")
for i in range(ele_num):
    temp = re_match.findall(gro_line[i + 2])[0:3]
    temp_str = '\t'.join(temp)
    temp_gro.write(temp_str + "\n")
Box_size = gro_line[-1].split()
Box_size_str = '\t'.join(Box_size)
temp_gro.write(Box_size_str + "\n")
gro.close()
temp_gro.close()
gro_coor = np.loadtxt(gro_temp)
os.remove(gro_temp)

#----Combine gro_coor and mean_charge as gro_charge: (ele_num + 1)*4----#
mean_charge = np.vstack((mean_charge,np.array([[-1]])))
assert (mean_charge.shape[0] == gro_coor.shape[0])
gro_charge = np.c_[gro_coor,mean_charge]
np.savetxt(output_file,gro_charge)
