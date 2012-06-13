#!/usr/bin/env python
                                                                              
import sys,os,unittest,time,re
import numpy as np
from cytostream import NoGuiAnalysis

'''
description - Shows the user how to run an original set of files using one set of parameters.  Then
              a filter is created (gate) and the model is run again on the resulting filter.
 
'''

__author__ = "AJ Richards"

class TestCase2(unittest.TestCase):
    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        ## declare variables
        projectID = 'utest'
        homeDir =  os.path.join(BASEDIR,"cytostream","projects", projectID)
        filePathList = [os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")]
        self.fileName = '3FITC_4PE_004'
        channelDict = {'FSCH':0,'SSCH':1,'FL1H':2,'FL2H':3}
        
        ## run the initial model for all files
        self.nga = NoGuiAnalysis(homeDir,channelDict,filePathList,useSubsample=True,makeQaFigs=False,record=False)
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
        filterID = 'ftr1'
        modelMode = 'components'
        fileNameList =self. nga.get_file_names()
        clusterIDs = [1,2]
        for fileName in fileNameList:
            self.nga.handle_filtering(filterID,fileName,parentModelRunID,'components',clusterIDs)

        ## set subsample to filter id
        self.nga.set('subsample_run','ftr1')

        ## run the second model
        self.nga.run_model()

        ## ensure project was created
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,"data"))) < 2)

        modelLog1, modelLabels1 = self.nga.get_labels(self.fileName,'run1',modelType='components',getLog=True)
        modelLog2, modelLabels2 = self.nga.get_labels(self.fileName,'run2',modelType='components',getLog=True)

        ## ensure we end up with the correct number of labels
        clusterLabels = []
        for lab in clusterIDs:
            clusterInds = np.where(modelLabels1 == lab)[0]
            clusterLabels.extend(clusterInds.tolist())

        self.assertEqual(modelLabels2.shape[0],len(clusterLabels))

### Run the tests 
if __name__ == '__main__':
    unittest.main()
