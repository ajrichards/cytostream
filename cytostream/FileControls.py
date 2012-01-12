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

    if os.path.exists(homeDir) == False:
        return []

    if os.path.exists(os.path.join(homeDir,"data")) == False:
        return []

    if type(excludedFiles) != type([]):
        print "INPUT ERROR: bad type for excluded files in get_fcs_file_names"
        return None

    fileList = []
    for fileName in os.listdir(os.path.join(homeDir,"data")):
        if not re.search("data",fileName):
            continue
        if not re.search("\.array",fileName):
            continue
        if not re.search("data",fileName):
            continue

        if fileName not in excludedFiles:
            fileList.append(fileName)

    fileList = [re.sub("\_data.array","", fi) for fi in fileList]
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

def get_models_run_list(log):
    """
    returns a list of the models run for a given project 
    """

    maxModelRun = int(log['models_run_count'])

    if maxModelRun == 0:
        return []

    modelsRunList = ['run'+str(i+1) for i in range(maxModelRun)]

    return modelsRunList
