import os,csv,re,ast
import numpy as np
from cytostream import configDictDefault

'''
Logger class to handle the logging tasks of the pipline software
project logfile - main log file that holds project specific history and variable information
model logfiles - each run of a model results in a results pickle as well as a log file
figure logfiles - figures may be manipulated after the run of a model -- those manipulations are documented here

log entries marked with 'setting' are not meant to be changed by the user


'''

class Logger():
    
    ## consttructor
    def __init__(self):
        self.log = {'current_state':'initial'}

    def initialize(self,projectID,homeDir,load=False,configDict=None):
        self.projectID = projectID
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
            #if type(item) == type([]):
            #    pass
            #elif item == '[]':
            #    item = []
            #elif re.search("\[",str(item)):
            #    item = [int(i) for i in item.split(";")]
            #  
            #if item == 'None':
            #    item = None
            # 
            #if re.search("filters_run_count",key):
            #    if item == '{}':
            #        item = {}
            #    else:
            #        parser = [re.sub("\{|\}|'","",p) for p in item.split(",")]
            #        item = {}
            #        for p in parser:
            #            k,v = p.split(":")
            #            item[k] = int(v)

            if re.search("\[|\{|None",str(item)):
                #try:
                item = ast.literal_eval(str(item))
                #except:
                #    print '..............weird string I am', item

            log[key] = item

        return log

    ## effectivly the only action necessary to save a project in its current state
    def write(self):
        writer = csv.writer(open(os.path.join(self.homeDir,self.projectID+'.log'),'w'))

        for key,item in self.log.iteritems():
            #if type(item) == type([]):
            #    item = "".join([str(i)+";" for i in item])[:-1]
            #    if item == '':
            #        item = '[]'

            if item == None:
                item = 'None'
            elif type(item) != type('i am a string'):
                item = str(item)

            writer.writerow([key,item])
            
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
                #if linja[1] == '[]':
                #    linja[1] = []
                #elif re.search("excluded",linja[0]):
                #    linja[1] = [int(i) for i in linja[1].split(";")]
                #elif linja[1] == 'None':
                #    linja[1] = None
                #

                #if re.search("filters_run_count",linja[0]):
                #    if linja[1] == '{}':
                #        linja[1] = {}
                #     else:
                #        parser = [re.sub("\{|\}|'","",p) for p in linja[1].split(",")]
                #        linja[1] = {}
                #        for p in parser:
                #            k,v = p.split(":")
                #            linja[1][k] = int(v)

                if re.search("\[|\{|None",str(linja[1])):
                    try:
                        linja[1] = ast.literal_eval(str(linja[1]))
                    except:
                        print '....................this is a weird string', linja[1]

                logFileDict[linja[0]] = linja[1]

            return logFileDict
