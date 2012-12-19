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
    Logger class to handle the logging interface for cytostream
    '''

    def __init__(self,homeDir,configDict=None):
        '''
        constructor

        '''

        ## variables
        self.projectID = os.path.split(homeDir)[-1]
        self.homeDir = homeDir
        self.logFilePath = os.path.join(self.homeDir,self.projectID+'.log')

        if configDict == None:
            self.configDict = configDictDefault
        else:
            self.configDict = configDict

        ## error checking
        if type(self.configDict) != type({}):
            print "INPUT ERROR: in Logging.py configDict must be of type dict"

        ## either load or create a new log file    
        if os.path.exists(self.logFilePath):
            self.log = self.read_project_log()
        else:
            self.log = {}

            for key,item in self.configDict.iteritems():
                if re.search("\[|\{|None",str(item)):
                    item = ast.literal_eval(str(item))

                self.log[key] = item

    ## effectivly the only action necessary to save a project
    def write(self):
        writeFile = open(self.logFilePath,'w')
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
