"""
This script imports a 'source' model, copies all its temperature results to its PyVista 'grid'
and then interpolates the results onto the PyVista grid of the target model. It then writes out
the interpoated temperature data to a 'loads' folder (under the current project's user_files folder)
in the form of APDL loads to be applied to the target model.

"""

import os
from ansys.mapdl import reader


#path to target model result file (.rst file. This is the Mechanical solution folder)
#rpath = r"C:\Users\alex.grishin\raytheon_officehours\baseline_files\dp0\SYS\MECH\file.rth"
#path to 'source' model (solved thermal model with temperatures to be mapped)
spath = r"C:\Users\alex.grishin\raytheon_officehours\2022R2_thermal_files\dp0\SYS\MECH\file.rth"
#path to 'target model (on which to map temperatures as structural loads)
tpath = r"C:\Users\alex.grishin\raytheon_officehours\2022R2_thermal_files\dp0\SYS-2\MECH\file.rst"
#path to store APDL commands for target model
loadpath = r"C:\Users\alex.grishin\raytheon_officehours\2022R2_thermal_files\user_files\load"

#get solution and mesh from source model
ssol = reader.read_binary(spath)
#get mesh from target model
tsol = reader.read_binary(tpath)

#insert solution arrays (one for each output time) into pyvista grid
for i in range(ssol.n_results):
	tstr = 'T'+str(i)
	nnum,ssol.grid[tstr] = ssol.nodal_temperature(i)
	
#Interpolate temperatures from ssol.grid onto tsolgrid (ANSYS volume data)
tmesh = tsol.grid.interpolate(ssol.grid,sharpness=2,radius=1.e-3,strategy='closest_point')
tmesh.plot(scalars='T47',cmap='rainbow')

#make sure there is a 'load' subdirectory in the user_files folder to write loads to
if not os.path.exists(loadpath):
	os.makedirs(loadpath)
	
#Now, apply the interpolated data as surface and body loads in MAPDL (and store macros in user_files)...
bfpath = f"{loadpath}\\mk_time.mac"
with open(bfpath,'w') as f:
	f.write(f"numtimes = {ssol.time_values.size}\n")
	f.write(f"*dim,ttime,,numtimes\n")
	for i,time in enumerate(ssol.time_values):
		f.write(f"ttime({i+1})={time}\n")
nodenums = tmesh['ansys_node_num']		
for tim in range(ssol.n_results):
	bfname = f"mk_BF{str(tim+1)}.mac"
	bfpath = f"{loadpath}\\{bfname}"
	tstr = f"T{str(tim)}"
	tvals = tmesh[tstr]
	with open (bfpath,'w') as f:
		for j in range(nodenums.size):
			anstr = f"bf,{str(int(nodenums[j]))},temp,{str(tvals[j])}\n"
			f.write(anstr)
	
	

	