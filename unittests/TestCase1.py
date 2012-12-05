#!/usr/bin/env python                                                                                                                                                                                                                       
import sys,os,unittest,time,re
from cytostream import NoGuiAnalysis, Controller


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
        self.controller = Controller(debug=False)
        self.dataDir = os.path.realpath(os.path.join(self.controller.baseDir,'example_data'))
        self.projectDir = os.path.realpath(os.path.join(self.controller.baseDir,'projects'))

        ## declare variables
        projectID = 'utest'
        homeDir =  os.path.join(self.projectDir, projectID)
        filePathList = [os.path.join(self.dataDir,"3FITC_4PE_004.fcs")]
        self.fileName = '3FITC_4PE_004'
        
        ## run the initial model for all files
        self.nga = NoGuiAnalysis(homeDir,filePathList)
    
        subsample = 500
        self.nga.set('dpmm_niter',1)
        self.nga.set('dpmm_burnin',999)
        self.nga.set('dpmm_k',16)
        self.nga.set('subsample_qa', subsample)
        self.nga.set('subsample_run', subsample)
        self.nga.set('subsample_analysis', subsample)
        self.nga.set('model_to_run','dpmm-mcmc')
        self.nga.set('excluded_channels_analysis',[])
    
    def tests(self):

        ## run the model
        self.nga.run_model()
        self.fileNameList = self.nga.get_file_names()
        testFileName = self.fileNameList[0]
        time.sleep(2)

        ## ensure project was created
        self.assertTrue(os.path.isfile(os.path.join(self.nga.controller.homeDir,"%s.log"%self.nga.controller.projectID)))
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,"data"))) < 2)
                
        ## get events
        events = self.nga.get_events(self.fileNameList[0],subsample=self.nga.controller.log.log['subsample_qa'])
        self.assertEqual(events.shape[0], int(float(self.nga.controller.log.log['subsample_qa']))) 

        ## check that model results can be retrieved
        modelRunID = 'run1'
        run1Labels,run1Log = self.nga.load_labels(testFileName,'run1',getLog=True)


        self.assertEqual(run1Labels.size,500)
        self.assertEqual('utest',run1Log['project id'])
                
        ## check that information can be retrieved from model log file
        #modelLog = self.nga.get_model_log(self.fileNameList[0],modelRunID)



### Run the tests 
if __name__ == '__main__':
    unittest.main()
