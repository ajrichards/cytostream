#!/usr/bin/env python                                                                                                                                                                                                                       
import sys,os,unittest,time,re
from cytostream import NoGuiAnalysis, configDictDefault

'''
description - Shows the user how a normal analysis is carried out.
              If initial parameters other than the transform need to be changed
              then the configDict mechanism may be used (shown).

              Otherwise import a custom config file to specify one set of parameters.  Then 
              the paramerters are altered and the model is run again.
              
              Note that the import and use of configDictDefault is only necessary for certain variables
              Most variables maybe be changed using nga.set(), however it may also be programatically convenient

'''

__author__ = "AJ Richards"

class TestCase1(unittest.TestCase):
    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        ## basic variables
        projectID = 'utest'
        homeDir =  os.path.join(BASEDIR,"cytostream","projects", projectID)

        ## specify variables needed for NoGuiAnalysis
        filePathList = [os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")]
        channelDict = {'FSCH':0,'SSCH':1,'FL1H':2,'FL2H':3}
    
        ## shows how to set parameters before analysis is begun
        configDict = configDictDefault.copy()
        configDict['dpmm_niters'] = 100
        configDict['dpmm_burnin'] = 900
        configDict['subsample_qa'] = 500             # num. events for qa plots
        configDict['subsample_analysis'] = 500       # num. events for model run and plots
        self.nga.set('excluded_channels_analysis') = [channelDict['FSCH']]

        ## initialize the analysis class
        self.nga = NoGuiAnalysis(homeDir,channelDict,filePathList,configDict=configDict,
                                 makeQaFigs=False,record=False)
        
        ## normal method to set parameters
        self.nga.set('model_to_run','dpmm-mcmc')

        ## run the model
        self.nga.run_model()
        self.fileNameList = self.nga.get_file_names()
    
    def tests(self):
        time.sleep(2)

        ## ensure project was created
        self.assertTrue(os.path.isfile(os.path.join(self.nga.controller.homeDir,"%s.log"%self.nga.controller.projectID)))
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,"data"))) < 2)
                
        ## get events
        events = self.nga.get_events(self.fileNameList[0],subsample=self.nga.controller.log.log['subsample_qa'])
        self.assertEqual(events.shape[0], int(float(self.nga.controller.log.log['subsample_qa']))) 

        ## check that model results can be retrieved
        modelRunID = 'run1'
        componentModel, componentClasses = self.nga.get_model_results(self.fileNameList[0],modelRunID,'components')
        self.assertEqual(componentClasses.size,500)
                
        ## check that information can be retrieved from model log file
        modelLog = self.nga.get_model_log(self.fileNameList[0],modelRunID)
        self.assertEqual('utest',modelLog['project id'])


### Run the tests 
if __name__ == '__main__':
    unittest.main()
