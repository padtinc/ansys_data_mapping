"""
This script imports a 'source' model temperature data in the same ascii text format as the External
Data tool. It then interpolates the results onto the PyVista grid of the target model. It then writes out
the interpoated temperature data to a 'loads' folder (under the current project's user_files folder)
in the form of APDL loads to be applied to the target model.

Note that this script uses DPF Post on the same database (the rst file of the target model) that will
need to be updated with a new Ansys run. This means that the DPF connection to the rst file must be
severed before the rst file can be updated. The last two lines of this script intend to do that (but don't
always work. We haven't figured out why)

"""

import os
import glob
import numpy as np
import pyvista as pv
import ansys.dpf.core as dpf
from ansys.dpf import post

dlimiter = ','
#dlimiter = '\t'
fext = 'xls'
#path to source data. This is the Project user_files folder. Change as necessary
spath = r"C:\Users\alex.grishin\raytheon_officehours\2022R2_thermal_files\user_files"
#path to target model rst file. This is in the solver files directory of the target system.
#Change as necessary
tpath = r"C:\Users\alex.grishin\raytheon_officehours\2022R2_thermal_files\dp0\SYS-2\MECH\file.rst"
#path to APDL commands to apply temperature loading. This is under the Project user_files folder
#change as necessary
loadpath = r"C:\Users\alex.grishin\raytheon_officehours\2022R2_thermal_files\user_files\load"

#get source data locations one time (don't need to keep reading them from each temperature file)
slocs = np.loadtxt(spath+'\\tresult1.'+fext,delimiter=dlimiter,skiprows=1,usecols=(1,2,3))
spts = pv.PolyData(slocs)
resultfiles = glob.glob1(spath,"*."+fext)
numtimes = len(resultfiles)

#get base file name
fname = resultfiles[0].split('.')[0]
fname = ''.join(filter(str.isalpha,fname))

#Now, loop over numtimes and fill spts with temperature data...
for i in range(numtimes):
    dmodelpath = f"{spath}\{fname}{str(i+1)}.{fext}"
    tvals = np.loadtxt(dmodelpath,delimiter=dlimiter,skiprows=1,usecols=4)
    tstr = 'T'+str(i)
    spts[tstr] = tvals

#get the target mesh using dpf post...	
tsolution = post.load_solution(tpath)
tsimulation = post.load_simulation(tpath)
nmap = tsolution.mesh.nodes.mapping_id_to_index
tnids = tsimulation.mesh.node_ids
tgrid = tsolution.mesh.grid

#Interpolate temperatures from source points onto tgrid (ANSYS volume data)
tmesh = tgrid.interpolate(spts,sharpness=2,radius=1.e-3,strategy='closest_point')

tmesh.plot(scalars='T47',cmap='rainbow')

#get the sequential time data output in rimtes.txt...
timepath = f"{spath}\RTIMES.txt"
timevals = np.loadtxt(timepath)

#make sure there is a 'load' subdirectory in the user_files folder to write loads to
if not os.path.exists(loadpath):
	os.makedirs(loadpath)

#Now, apply the interpolated data as surface and body loads in MAPDL (and store macros in user_files)...
bfpath = f"{loadpath}\\mk_time.mac"
with open(bfpath,'w') as f:
	f.write(f"numtimes = {numtimes}\n")
	f.write(f"*dim,ttime,,numtimes\n")
	for i,time in enumerate(timevals):
		f.write(f"ttime({i+1})={time}\n")
		
mindex = np.array([nmap[item] for item in tnids])
for tim in range(numtimes):
	bfname = f"mk_BF{str(tim+1)}.mac"
	bfpath = f"{loadpath}\\{bfname}"
	tstr = f"T{str(tim)}"
	with open (bfpath,'w') as f:
		mtvals = tmesh[tstr][mindex]
		for j in range(len(tnids)):
			#mtval = tmesh[tstr][mindex[j]]
			anstr = f"bf,{str(int(tnids[j]))},temp,{str(mtvals[j])}\n"
			f.write(anstr)
			
#shut down grpc server (if you don't do this, the result file won't get updated)
#The dpf server can always be restarted wtih dpf.server.connect_to_server()
tsimulation.release_streams()
dpf.server.shutdown_global_server()
	