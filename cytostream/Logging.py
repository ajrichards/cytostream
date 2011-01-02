import os,csv,re
import numpy as np

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
        self.log = {'currentState':'initial'}

    def initialize(self,projectID,homeDir,load=False):
        self.projectID = projectID
        self.homeDir = homeDir
        self.modelDir = os.path.join(self.homeDir,'models')
        self.figDir  = os.path.join(self.homeDir, 'figs')
        self.dataDir = os.path.join(self.homeDir, 'data')

        if load == False:
            self.log = self.set_var_defaults()
        elif load == True:
            self.log = self.read_project_log()

    def set_var_defaults(self):
        log = {}
        log['current_state'] = 'Data Processing'
        log['highest_State'] = 0
        log['input_data_type'] = 'fcs'
        log['subsample_qa'] = '1e3'
        log['subsample_analysis'] = '1e3'
        log['setting_max_scatter_display'] = '2e4'
        log['selected_file'] = None
        log['selected_model'] = None
        log['selected_transform'] = 'log'
        log['selected_k'] = 16
        log['model_to_run'] = None
        log['results_mode'] = 'modes'
        log['data_processing_mode'] = 'channel select'
        log['component_states'] = None
        log['excluded_files_qa'] = []
        log['excluded_files_analysis'] = []
        log['excluded_channels_qa'] = []
        log['excluded_channels_analysis'] = []

        return log

    ## effectivly the only action necessary to save a project in its current state
    def write(self):
        writer = csv.writer(open(os.path.join(self.homeDir,self.projectID+'.log'),'w'))
        
        for key,item in self.log.iteritems():
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

                if linja[0] == 'checksArray':
                    linja[1] = self.str2array(linja[1])

                logFileDict[linja[0]] = linja[1]
            
                if linja[0] == 'excludedFilesQA' or linja[0] == 'excludedChannels' or linja[0] == 'excludedFilesAnalysis':
                    linja[1] = re.sub("\s+|\[|\]|'","",linja[1]).split(",")

            return logFileDict

    ## given a model name read in a model log file and return a dictionary
    def read_model_log(self,modelName):
        longName = os.path.join(self.modelDir,modelName+".log")
        if os.path.isfile(longName) == False:
            print "ERROR: invalid model logfile specified",longName
            return None
        else:
            logFileDict = {}
            reader = csv.reader(open(longName,'r'))
            for linja in reader:
                logFileDict[linja[0]] = linja[1]
                  
            return logFileDict

    def str2array(self,myStr):
        if not re.search("^\[\[",myStr):
            return None

        myStr = myStr[1:-1]
        myStr = re.sub("\n", ",", myStr)
        myList = myStr.split(",")
        newList = []

        for l in myList:
            newList.append([int(float(i)) for i in re.sub("\[|\]","",l).split()])

        return np.array(newList)

    def str2list(self,myStr):
        if not re.search("^\[\[",myStr):
            return None

        myStr = myStr[1:-1]
        myStr = re.sub("\n", ",", myStr)
        myList = myStr.split(",")
        newList = []

        for l in myList:
            newList.append([int(float(i)) for i in re.sub("\[|\]","",l).split()])

        return newList

