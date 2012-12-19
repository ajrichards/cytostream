#!/usr/bin/python

'''
Cytostream
Logger
Logger class used to document the steps involved in the analysis pipeline

'''

__author__ = "A Richards"

import os,csv,re,ast
from cytostream import configDictDefault


class Logger():
    '''
    Logger class to handle the logging tasks of the pipline software
    project logfile - main log file that holds project specific history and variable information
    model logfiles - each run of a model results in a results pickle as well as a log file
    figure logfiles - figures may be manipulated after the run of a model

    '''

    def __init__(self):
        '''
        constructor

        '''

        self.log = {'current_state':'Initial'}

    def initialize(self,homeDir,load=False,configDict=None):
        self.projectID = os.path.split(homeDir)[-1]
        self.homeDir = homeDir
        self.modelDir = os.path.join(self.homeDir,'models')
        self.figDir  = os.path.join(self.homeDir, 'figs')
        self.dataDir = os.path.join(self.homeDir, 'data')

        if configDict == None:
            self.configDict = configDictDefault
        else:
            self.configDict = configDict

        ## error checking
        if type(self.configDict) != type({}):
            print "INPUT ERROR: in Logging.py configDict must be of type dict"

        ## setup the logger from existing or from new
        if load == False:
            self.log = self.set_var_defaults()
        elif load == True:
            self.log = self.read_project_log()

    def set_var_defaults(self):
        log = {}

        ## load default variables
        for key,item in self.configDict.iteritems():
            if re.search("\[|\{|None",str(item)):
                item = ast.literal_eval(str(item))

            log[key] = item

        return log

    ## effectivly the only action necessary to save a project in its current state
    def write(self):
        writeFile = open(os.path.join(self.homeDir,self.projectID+'.log'),'w')
        writer = csv.writer(writeFile)

        for key,item in self.log.iteritems():
            if item == None:
                item = 'None'
            elif type(item) != type('i am a string'):
                item = str(item)

            writer.writerow([key,item])
        writeFile.close()

    ## reads the log file assciated with the current project and returns a dict
    def read_project_log(self):
        projLog = os.path.join(self.homeDir,self.projectID+".log")
        
        if os.path.isfile(projLog) == False:
            print "ERROR: invalid model logfile specified",projLog
            return None
        else:
            logFileDict = {}
            reader = csv.reader(open(projLog,'r'))
            for linja in reader:

                if re.search("\[|\{|None",str(linja[1])):
                    try:
                        linja[1] = ast.literal_eval(str(linja[1]))
                    except:
                        print 'ERROR: Logger -- string literal conversion failed', linja[1]

                logFileDict[linja[0]] = linja[1]

            return logFileDict
