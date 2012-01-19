#!/usr/bin/env python                                                                                                                                                                                                                       
import sys,os,unittest,time,re
from cytostream import NoGuiAnalysis, configDictDefault

'''
description - Shows the user how import a custom config file to specify one set of parameters.  Then 
              the paramerters are altered and the model is run again.
              
              Note that the import and use of configDictDefault is only necessary for certain variables
              Most variables maybe be changed using nga.set(), however it may also be programatically convenient

A. Richards
'''


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
        #filePathList = [os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")]
        #channelDict = {'fsc-h':0,'ssc-h':1}
        
        selectedFiles = ["J6901HJ1-06_CMV_CD8","J6901HJ1-06_CMV_CD4","J6901HJ1-06_SEB_CD8","J6901HJ1-06_SEB_CD4"]
        filePathList = []
        for selectedFile in selectedFiles:
            filePath = os.path.join("/","home","clemmys","research","manuscripts","PositivityThresholding","scripts","data","eqapol11C",selectedFile+".fcs")
            filePathList.append(filePath)
        channelDict = {'fsc-a':0, 'fsc-h':1, 'fsc-w':2, 'ssc-a':3, 'ssc-h':4, 'ssc-w':5, 'time':6}

        ## run the initial model for all files
        self.fileList = selectedFiles
        configDict = configDictDefault.copy()
        configDict['num_iters_mcmc'] = 1100
        configDict['subsample_qa'] = 500
        configDict['subsample_analysis'] = 500

        self.nga = NoGuiAnalysis(homeDir,channelDict,filePathList,configDict=configDict,useSubsample=True,makeQaFigs=False,record=False)
        self.nga.run_model()
        fileNameList = self.nga.get_file_names()
    
        ## create all pairwise figs for all files
        #for fileName in fileNameList:
        #    self.nga.make_results_figures(fileName,'run1')
        
        ## run the model again 
        #fileName = "3FITC_4PE_004"
        #self.nga.set('excluded_channels_analysis',[1])
        #self.nga.set('thumbnails_to_view', [(0,2),(0,3)])
        #self.nga.set('subsample_analysis', 1000)
        #self.nga.run_model()
        #self.nga.make_results_figures(fileName,'run2')
    

    def tests(self):
        time.sleep(3)

        ## ensure project was created
        self.assertTrue(os.path.isfile(os.path.join(self.nga.controller.homeDir,"%s.log"%self.nga.controller.projectID)))
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,"data"))) < 2)
                
        ## get events
        events = self.nga.get_events(fileNameList[0],subsample=self.nga.controller.log.log['subsample_qa'])
        self.assertEqual(events.shape[0], int(float(self.nga.controller.log.log['subsample_qa']))) 

        ## check that qa figs were made
        #self.assertTrue(os.path.isdir(os.path.join(self.nga.controller.homeDir,'figs','qa','3FITC_4PE_004_thumbs')))
        
        ## check that model results can be retrieved
        modelRunID = 'run1'
        componentModel, componentClasses = self.nga.get_model_results(fileNameList[0],modelRunID,'components')
        self.assertEqual(componentClasses.size,500)
        modesModel, modesClasses = self.nga.get_model_results(fileNameList[0],modelRunID,'modes')
        self.assertEqual(modesClasses.size,500)
        
        ## check that information can be retrieved from model log file
        modelLog = self.nga.get_model_log(fileNameList[0],modelRunID)
        self.assertEqual('utest',modelLog['project id'])

        ## check that analysis figs were made
        #self.assertTrue(os.path.isdir(os.path.join(self.nga.controller.homeDir,'figs',modelRunID,'3FITC_4PE_004_thumbs')))

        #modelRunID = 'run2'
        #componentModel, componentClasses = self.nga.get_model_results(fileNameList[0],modelRunID,'components')
        #self.assertEqual(componentClasses.size,1000)
        #modesModel, modesClasses = self.nga.get_model_results(fileNameList[0],modelRunID,'modes')
        #self.assertEqual(modesClasses.size,1000)
        
        ## check that analysis figs were made
        #modelRunID = 'run2'
        #self.assertTrue(os.path.isdir(os.path.join(self.nga.controller.homeDir,'figs',modelRunID,'3FITC_4PE_004_thumbs')))

### Run the tests 
if __name__ == '__main__':
    unittest.main()
