#!/usr/bin/env python

import os,re

# returns a list of file names associated with the project
#
#
def get_fcs_file_names(homeDir,getPickles=False):
    fileList = []
    for fileName in os.listdir(os.path.join(homeDir,"data")):
        if re.search("\.fcs",fileName) and getPickles == False:
            fileList.append(fileName)
        if re.search("\.pickle",fileName) and getPickles == True:
            fileList.append(fileName)

    return fileList

# return the file names for images 
#
#
def get_img_file_names(homeDir):
    fileList = []
    for fileName in os.listdir(os.path.join(homeDir,"figs")):
        if re.search("\.png",fileName):
            fileList.append(fileName)
            
    return fileList

# returns the models run
#
#
def get_models_run(homeDir):
    modelList = []

    for fileName in os.listdir(os.path.join(homeDir,"models")):
        # ignore classifications
        if re.search("classify\.pickle",fileName):
            continue
        
        if re.search("\.pickle",fileName):
            modelList.append(fileName)

    return modelList

# returnss all the different projects on computer
#
#
def get_project_names():    
    projectNamesList = []
    for dirName in os.listdir(os.path.join(".","projects")):  
        if os.path.isdir(os.path.join(".","projects",dirName)) == True:
            projectNamesList.append(dirName)
    return projectNamesList
