#!/usr/bin/env python

import os,re

def get_fcs_file_names(homeDir,getPickles=False):
    '''
    returns a sorted list of file names associated with the project
    
    '''

    fileList = []
    for fileName in os.listdir(os.path.join(homeDir,"data")):
        if re.search("\.fcs",fileName) and getPickles == False:
            fileList.append(fileName)
        if re.search("\.pickle",fileName) and getPickles == True:
            fileList.append(fileName)

    fileList.sort()

    return fileList

def get_img_file_names(homeDir):
    '''
    return the file names for images 

    '''

    fileList = []
    for fileName in os.listdir(os.path.join(homeDir,"figs")):
        if re.search("\.png",fileName):
            fileList.append(fileName)
            
    return fileList

def get_models_run(homeDir, possibleModels):
    '''
    returns the models run
    
    '''
    modelList = []
    for fileName in os.listdir(os.path.join(homeDir,"models")):
        # ignore classifications
        if re.search("classify|\.log",fileName):
            continue
        
        modelFound = None
        for possibleModelUsed in possibleModels:
            if modelFound != None:
                continue

            if re.search(possibleModelUsed,fileName):
                modelList.append(re.sub("\_components\.pickle|\_modes\.pickle","",possibleModelUsed))
        
    modelList = list(set(modelList))

    #if re.search("\.pickle",fileName):
    #    modelList.append(fileName)

    print "returning model list", modelList

    return modelList

def get_project_names(baseDir):    
    '''
    returns all the projects on local computer
    
    '''
    if os.path.isdir(baseDir) == False:
        print "ERROR: bad base dir specified in get_project_names"

    projectNamesList = []
    projectDir = os.path.join(baseDir,"projects")
    if os.path.isdir(projectDir) == False:
        print "INFO: making project dir"
        os.mkdir(projectDir)

    for dirName in os.listdir(os.path.join(baseDir,"projects")):  
        if os.path.isdir(os.path.join(baseDir,"projects",dirName)) == True:
            if dirName != 'utest':
                projectNamesList.append(dirName)
    return projectNamesList
