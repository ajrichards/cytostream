#!/usr/bin/env python
                                                                              
import sys,os,unittest,time,re
import numpy as np
from cytostream import NoGuiAnalysis,Controller

'''
description - Shows the user how to run an original set of files using one set of parameters.  Then
              a filter is created (gate) and the model is run again on the resulting filter.
 
'''

__author__ = "AJ Richards"

class TestCase2(unittest.TestCase):
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
        #self.nga = NoGuiAnalysis(homeDir,channelDict,filePathList,useSubsample=True,makeQaFigs=False,record=False)
        subsample = 1000
        self.nga.set('subsample_qa', subsample)
        self.nga.set('subsample_run', subsample)
        self.nga.set('subsample_analysis', subsample)
        self.nga.set('model_to_run','kmeans')
        self.nga.set('excluded_channels_analysis',[])

    def tests(self):

        ## run the first model
        self.nga.run_model()

        ## create a filter that consists of clusters 1 and 2
        parentModelRunID = 'run1'
        filterID = 'filter12'
        fileNameList = self. nga.get_file_names()
        clusterIDs = [1,2]
        for fileName in fileNameList:
            self.nga.handle_filtering_by_clusters(filterID,fileName,clusterIDs,parentModelRunID)

        testFileName = fileNameList[0]
        run1Labels,run1Log = self.nga.load_labels(testFileName,'run1',getLog=True)
        filter1Labels,filter1Log = self.nga.load_labels(testFileName,filterID,getLog=True)

        totalEventsInCluster = np.where(run1Labels==1)[0].size + np.where(run1Labels==2)[0].size
        self.assertEqual(np.where(filter1Labels==1)[0].size,totalEventsInCluster) 

        ## set the filter so that the next model run uses the filter
        self.nga.set('model_filter',filterID)

        ## run the second model
        self.nga.run_model()
        run2Labels,run2Log = self.nga.load_labels(testFileName,'run2',getLog=True)

        self.assertEqual(totalEventsInCluster,run2Labels.size)

### Run the tests 
if __name__ == '__main__':
    unittest.main()
