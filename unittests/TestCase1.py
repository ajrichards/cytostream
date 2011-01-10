#!/usr/bin/env python                                                                                                                                                                                                                       
import sys,os,unittest,time,re
from cytostream import NoGuiAnalysis, configDictDefault

'''
configDict - arg is not required although custom analyses are carried out using a custom dict as shown

notes:
    to retrieve file names and events from a given file see the method 'testFiles'

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

        ## run the no gui analysis
        filePathList = [os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")]
        projectID = 'utest'
        
        ## run the initial model for all files
        configDict1 = configDictDefault.copy()
        configDict1['excluded_channels_analysis'] = [1]
        configDict1['thumbnails_to_view'] = [(0,2),(0,3)]
        self.nga = NoGuiAnalysis(projectID,filePathList,configDict=configDict1,useSubsample=True,makeQaFigs=True)
        fileNameList = self.nga.get_file_names()
    
        for fileName in fileNameList:
            self.nga.make_results_figures(fileName,'run1')

        ## run the model again this time for only one file
        fileName = "3FITC_4PE_004"
        configDict2 = configDict1.copy()
        configDict2['data_in_focus'] = fileName
        self.nga.update()
        self.nga.run_model()
        self.nga.make_results_figures(fileName,'run2')

        ## run the model again this time for some filtered data
        ## filtering dict - key = (chan1Ind,chan2Ind) item = (chan1min,chan1max,chan2min,chan2max)
        filteringDict = {(0,3):(400,800,150,300)}
        subsample = int(float(self.nga.controller.log.log['subsample_analysis']))
        filterID = "%s_%s"%(subsample,'filter1')
        self.nga.handle_filtering(fileName,filteringDict)
        configDict2['data_in_focus'] = fileName
        configDict2['filter_in_focus'] = filterID
        self.nga.update()
        self.nga.run_model()
        self.nga.make_results_figures(fileName,'run3')
        
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

        ## check that qa figs were made
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,'figs','qa'))) != 3)
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
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,'figs', modelRunID))) != 3)
        self.assertTrue(os.path.isdir(os.path.join(self.nga.controller.homeDir,'figs',modelRunID,'3FITC_4PE_004_thumbs')))

        ## make sure there are less filtered events than unfiltered filteredEvents = self.nga.get_even
        subsample = int(float(self.nga.controller.log.log['subsample_analysis']))
        filteredEvents = self.nga.get_events("3FITC_4PE_004",filterID='%s_filter1'%(subsample))
        allEvents = self.nga.get_events("3FITC_4PE_004",subsample=self.nga.controller.log.log['subsample_analysis'])
        self.failIf(filteredEvents.shape[0] > allEvents.shape[0])

### Run the tests 
if __name__ == '__main__':
    unittest.main()
