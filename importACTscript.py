"""
This is a Python ACT script which gets the source files and solution times used in an Imported Load
object (External Data in the Project Schematic). It then configures the data and tranfers it in the
last line (importedTemperature.ImportLoad()).

This script is identical to the script found on lines 88 - 117 of the journal script 'loadfiledata.wbjn'
except that the parameters filepath, timepath, and ext are hard-coded here (lines 13 - 16).
It is provided here has a convenience to uses
"""
import glob
import os

#path to temperature data files: the Project users_files directory. Change this as necessary
datapath = r"C:\Users\alex.grishin\raytheon_officehours\2022R2_thermal_files\user_files"
#path to load step times text file: The Project user_files directory. Change as necessary
timepath = r"C:\Users\alex.grishin\raytheon_officehours\2022R2_thermal_files\user_files\RTIMES.txt"
fext = "prn"
namedSelStr = "mapbodies"
resultfiles = glob.glob1(datapath,"*."+fext)
resultfiles.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
analysis = ExtAPI.DataModel.Project.Model.Analyses[0]
with open(timepath,"r") as r:
    data = r.read().strip()
    datalist = data.split('\n')
times = map(float,datalist)
numfilestoload = len(resultfiles)
importedloadobjects = [child for child in analysis.Children if child.DataModelObjectCategory.ToString() == "ImportedLoadGroup"]
lastimportedloadobj = importedloadobjects[-1]
importedTemperature = lastimportedloadobj.AddImportedBodyTemperature()
named_selection = ExtAPI.DataModel.GetObjectsByName(namedSelStr)[0]
importedTemperature.Location = named_selection
table = importedTemperature.GetTableByName("")
for i in range(numfilestoload-1):
    table.Add(None)
for i in range(numfilestoload):
    table[i][0]="File"+str(i+1)+":"+str(resultfiles[i])
    table[i][1]=times[i]
importedTemperature.ImportLoad()