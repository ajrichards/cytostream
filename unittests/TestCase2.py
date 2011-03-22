#!/usr/bin/env python
                                                                              
import sys,os,unittest,time,re
from cytostream import NoGuiAnalysis

'''
description - Shows the user how to run an original set of files using one set of parameters.  Then
              a filter is created (gate) and the model is run again on the resulting filter.  Finally,
              a third gate is created from the second gate and the model is run again.

filteringDict = {(chanX_index, chanY_index):(chanX_min,chanX_max,chanY_min,chanY_max)} 

A. Richards
 
'''

class TestCase2(unittest.TestCase):
    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        ## necessary variables   
        filePathList = [os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")]
        projectID = 'utest'
        homeDir =  os.path.join(BASEDIR,"cytostream","projects", projectID)

        ## run the initial model for all files
        self.nga = NoGuiAnalysis(homeDir,filePathList,useSubsample=True,makeQaFigs=False,record=False)
        self.nga.set('subsample_qa', 1000)
        self.nga.set('subsample_analysis', 1000)
        self.nga.run_model()

        fileNameList = self.nga.get_file_names()

        ## create all pairwise figs for all files
        for fileName in fileNameList:
            self.nga.make_results_figures(fileName,'run1')

        ## gate the data with a rectangle gate (filter)
        subset = str(int(float(self.nga.get('subsample_analysis'))))
        filterID1 = "%s_%s"%(subset,'filter1')
        filteringDict1 = {(0,3):(400,800,150,300)}
        self.nga.handle_filtering(fileName,filteringDict1)
        self.nga.set('filter_in_focus',filterID1)
        self.nga.run_model()
        self.nga.make_results_figures(fileName,'run2')

        ## create a gate to filter the filtered data
        self.nga.set('subsample_analysis',filterID1)
        filteringDict2 = {(0,3):(700,750,250,300)}
        self.nga.handle_filtering(fileName,filteringDict2)
        filterID2 = "%s_%s"%(subset,'filter2')
        self.nga.set('filter_in_focus',filterID2)
        self.nga.run_model()
        self.nga.make_results_figures(fileName,'run3')

        ## return filter in focus to default
        self.nga.set('filter_in_focus','None')

    def tests(self):
        ## ensure project was created
        self.assertTrue(os.path.isfile(os.path.join(self.nga.controller.homeDir,"%s.log"%self.nga.controller.projectID)))
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,"data"))) < 2)
        
        ## get file names
        fileNameList = self.nga.get_file_names()
        self.assertEqual(len(fileNameList),1)

        ## get events
        events = self.nga.get_events(fileNameList[0],subsample=self.nga.controller.log.log['subsample_qa'])
        self.assertEqual(events.shape[0], int(float(self.nga.controller.log.log['subsample_qa'])))
        
        ## check that model results can be retrieved
        modelRunID = 'run1'
        subsample = 1000
        componentModel, componentClasses = self.nga.get_model_results(fileNameList[0],modelRunID,'components')
        self.assertEqual(componentClasses.size,subsample)
        modesModel, modesClasses = self.nga.get_model_results(fileNameList[0],modelRunID,'modes')
        self.assertEqual(modesClasses.size,subsample)
        
        ## check that information can be retrieved from model log file
        modelLog = self.nga.get_model_log(fileNameList[0],modelRunID)
        self.assertEqual('utest',modelLog['project id'])

        ## check that analysis figs were made
        self.assertTrue(os.path.isdir(os.path.join(self.nga.controller.homeDir,'figs',modelRunID,'3FITC_4PE_004_thumbs')))

        ## check run2 and relevant results
        filterID = "%s_%s"%(subsample,'filter1')
        events = self.nga.get_events(fileNameList[0],subsample=filterID)  
        self.failIf(subsample < events.shape[0])


### Run the tests 
if __name__ == '__main__':
    unittest.main()
