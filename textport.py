'''
This is a Python script used to export scalar results to N 
text files (where N is the number of load steps in the result) 
from a Workbench thermal or structural model from the Mechanical 
application (either from the Automation->Scripting editor
or withe use of a custom button). The script first writes all the files
to the Solver Files Directory, and then copies them to the Project's
user_files directory. 
To make the data interpolatable (using the External Data tool, for example), 
users should first modify the Export settings to include location information.
This can be done by going to File->Options->Export and setting 
"Include Node Locations" to "yes".

The text data should be in the following format:
column 1	column 2	column 3	column 4	Column5
--------    --------	--------	--------	-------
Node Id		X-coord.	Y-coord.	Z-coord.	Temperature

'''
# Script:
import os
import shutil

fpath = ExtAPI.DataModel.Project.Model.Analyses[0].AnalysisSettings.SolverFilesDirectory
reader = ExtAPI.DataModel.Project.Model.Analyses[0].GetResultsData()

userpath = os.path.dirname(fpath)
for i in range(3):
    userpath = os.path.dirname(userpath)
userpath = os.path.join(userpath,'user_files')

times = list(reader.ListTimeFreq)
result = Tree.ActiveObjects[0]
result.By = SetDriverStyle.ResultSet

tpath = fpath + "rtimes.txt"
with open(tpath,'w') as f:
    for i in range(reader.ResultSetCount):
        fname = 'tresult' + str(i+1) + '.xls'
        wpath = fpath + fname
        result.SetNumber = int(i+1)
        result.EvaluateAllResults()
        result.ExportToTextFile(wpath)
        print >> f,times[i]
        targetpath = os.path.join(userpath,fname)
        shutil.move(wpath,targetpath)

targetpath = os.path.join(userpath,'rtimes.txt')
shutil.move(tpath,targetpath)
