#!/usr/bin/env python                                                                                                                                                                                                                       
import sys,os,unittest,time,re
from cytostream import NoGuiAnalysis

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
        homeDir =  os.path.join(BASEDIR,"cytostream","projects", projectID)

        ## run the initial model for all files
        self.nga = NoGuiAnalysis(homeDir,filePathList,useSubsample=True,makeQaFigs=False,record=False)
        self.nga.set('num_iters_mcmc', 1200)
        self.nga.set('model_mode', 'onefit')
        self.nga.set('model_reference', "3FITC_4PE_004")
        self.nga.set('model_reference_run_id', 'run1')
        self.nga.set('thumbnail_results_default','components')
        self.nga.run_model()

        ## create all pairwise figs for all files
        fileNameList = self.nga.get_file_names()
        for fileName in fileNameList:
            self.nga.make_results_figures(fileName,'run1')
                        
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
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,'figs', modelRunID))) != 2)
        self.assertTrue(os.path.isdir(os.path.join(self.nga.controller.homeDir,'figs',modelRunID,'3FITC_4PE_004_thumbs')))

        ## check that model file used 'onefit' and that the reference is nonzero


### Run the tests 
if __name__ == '__main__':
    unittest.main()
