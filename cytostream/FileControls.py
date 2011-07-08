#!/usr/bin/env python

import os,re,csv,time

def add_project_to_log(baseDir,homeDir,status):
    logFile = os.path.join(baseDir,'projects', 'projects.log')
    if os.path.exists(logFile) == False:
        writeHeader = True
    else:
        writeHeader = False
   
    fid = csv.writer(open(logFile,'a'))
    
    if writeHeader == True:
        fid.writerow(['project','time','status'])
    fid.writerow([homeDir,time.asctime(),status])

def read_project_log(baseDir):
    logFile = os.path.join(baseDir,'projects', 'projects.log')
    fid = csv.reader(open(logFile,'r'))
    header = fid.next()
    
    projectsList = []

    for linja in fid:
        projectsList.append(linja)
    
    return projectsList

def get_fcs_file_names(homeDir,excludedFiles=[]):
    '''
    returns a sorted list of file names associated with the project
    
    '''

    if homeDir == None:
        return []

    if type(excludedFiles) != type([]):
        print "INPUT ERROR: bad type for excluded files in get_fcs_file_names"
        return None

    fileList = []
    for fileName in os.listdir(os.path.join(homeDir,"data")):
        if not re.search("data",fileName):
            continue
        if not re.search("\.pickle",fileName):
            continue
        if not re.search("original",fileName):
            continue

        if fileName not in excludedFiles:
            fileList.append(fileName)

    fileList = [re.sub("\_data_original.pickle","", fi) for fi in fileList]
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

    print "WARNING: FileControls -- get_models_run deprec. use tools.get_model_run_list"


    #if re.search("\.pickle",fileName):
    #    modelList.append(fileName)

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
