#!/usr/bin/env python                                                                                                                                                                                                                       
import sys,os,unittest,time,re
from cytostream import NoGuiAnalysis, configDictDefault

'''
description - Shows the user how to run an original set of files using one set of parameters.  Then 
              the model is run again this time using a reference file---referred to in the software 
              as 'onefit'.  This means that the model is run on a single reference file then all other 
              files in the project are fit using the results from that model run.

A. Richards
'''


class TestCase3(unittest.TestCase):
    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        ## run the no gui analysis
        filePathList = [os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs"),
                        os.path.join(BASEDIR,"cytostream","example_data", "duplicate.fcs")]

        projectID = 'utest'
        
        ## run the initial model for all files
        configDict = configDictDefault.copy()
        configDict['num_iters_mcmc'] = 1200
        configDict['plots_to_view'] = [(0,2),(0,3)]
        configDict['model_mode'] = 'onefit'
        configDict['model_reference'] = "3FITC_4PE_004"
        configDict['model_reference_run_id'] = 'run1'

        self.nga = NoGuiAnalysis(projectID,filePathList,configDict=configDict,useSubsample=True,makeQaFigs=True)
        fileNameList = self.nga.get_file_names()
    
        ## create all pairwise figs for all files
        for fileName in fileNameList:
            self.nga.make_results_figures(fileName,'run1')
        
        ## run the model again this time for only one file while using more of the config file functionality
        #fileName = "3FITC_4PE_004"
        #self.nga.set('model_mode','onefit')
        #self.nga.set('thumbnails_to_view', [(0,2),(0,3)])
        #self.nga.set('file_in_focus',fileName)
        #self.nga.run_model()
        #self.nga.make_results_figures(fileName,'run2')
                
    def tests(self):
        ## ensure project was created
        self.assertTrue(os.path.isfile(os.path.join(self.nga.controller.homeDir,"%s.log"%self.nga.controller.projectID)))
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,"data"))) < 2)
        
        ## get file names 
        fileNameList = self.nga.get_file_names()
        self.assertEqual(len(fileNameList),2)

        ## get events
        events = self.nga.get_events(fileNameList[0],subsample=self.nga.controller.log.log['subsample_qa'])
        self.assertEqual(events.shape[0], int(float(self.nga.controller.log.log['subsample_qa']))) 

        ## check that qa figs were made
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,'figs','qa'))) != 6)
        self.assertTrue(os.path.isdir(os.path.join(self.nga.controller.homeDir,'figs','qa','3FITC_4PE_004_thumbs')))
        
        ## check that model results can be retrieved
        modelRunID = 'run1'
        componentModel, componentClasses = self.nga.get_model_results(fileNameList[0],modelRunID,'components')
        self.assertEqual(componentClasses.size,int(float(self.nga.controller.log.log['subsample_analysis'])))
        modesModel, modesClasses = self.nga.get_model_results(fileNameList[0],modelRunID,'modes')
        self.assertEqual(modesClasses.size,int(float(self.nga.controller.log.log['subsample_analysis'])))
        
        ## check that information can be retrieved from model log file
        modelLog = self.nga.get_model_log(fileNameList[0],modelRunID)
        self.assertEqual('utest',modelLog['project id'])

        ## check that analysis figs were made
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,'figs', modelRunID))) != 6)
        self.assertTrue(os.path.isdir(os.path.join(self.nga.controller.homeDir,'figs',modelRunID,'3FITC_4PE_004_thumbs')))

        ## check that model file used 'onefit' and that the reference is nonzero


### Run the tests 
if __name__ == '__main__':
    unittest.main()
