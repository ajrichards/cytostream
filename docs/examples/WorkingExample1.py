#!/usr/bin/env python

import os
from cytostream import NoGuiAnalysis

## basic variables
projectID = 'tutorial'
currentWorkingDir = os.getcwd()
homeDir =  os.path.join(currentWorkingDir,projectID)

## specify the file path list
fileNameList = ["G69019FF_Costim_CD4.fcs", "G69019FF_SEB_CD4.fcs","G69019FF_CMVpp65_CD4.fcs"]
filePathList = [os.path.join(currentWorkingDir, fn) for fn in fileNameList]

## load the project
if os.path.isdir(homeDir) == False:
    nga = NoGuiAnalysis(homeDir,filePathList,autoComp=False)
else:
    nga = NoGuiAnalysis(homeDir,loadExisting=True)

## determine if all channels could be identified automatically
print nga.is_valid()
