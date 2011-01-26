#!/usr/bin/env python

import sys,os,unittest,time,re
from cytostream import Controller

## test class for the main window function
class ControllerTest(unittest.TestCase):
    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        self.projectID = 'utest'
        self.homeDir = os.path.join(BASEDIR,"cytostream","projects",self.projectID)
        self.controller = Controller()
        self.controller.initialize_project("utest") 
        self.fcsFileName = os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")

    def testLog(self):
        self.controller.save()
        self.assertTrue(os.path.isfile(os.path.join(self.controller.homeDir,"%s.log"%self.controller.projectID)))

    def testCreateNewProject(self):
        ## test creation of a project
        self.controller.create_new_project(view=None,projectID='utest')
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"data")))
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"figs")))
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"models")))
    
        ## test that files can be loaded
        self.controller.load_files_handler([self.fcsFileName])
        self.failIf(len(os.listdir(os.path.join(self.controller.homeDir,"data"))) != 2)
    
        ## test that events and channels may be retrieved
        fileName = re.sub('\s+','_',os.path.split(self.fcsFileName)[-1])
        fileName = re.sub('\.fcs|\.txt|\.out','',fileName)
        events = self.controller.model.get_events(fileName,subsample='original')
        self.assertEqual(events.shape[0],94569)
        self.assertEqual(events.shape[1],4)

        fileChannels = self.controller.model.get_file_channel_list(fileName)
        self.assertEqual(len(fileChannels),4)

    def testSubsampling(self):
        subsample = '1e3'
        self.controller.log.log['subsample_qa'] = subsample
        self.controller.handle_subsampling(subsample)
        fileName = re.sub('\s+','_',os.path.split(self.fcsFileName)[-1])
        fileName = re.sub('\.fcs|\.txt|\.out','',fileName)
        events = self.controller.model.get_events(fileName,subsample=subsample)
        self.assertEqual(events.shape[0], 1000)
    
    def testProcessImagesQa(self):
        subsample = '1e3'
        self.controller.log.log['subsample_qa'] = subsample
        self.controller.handle_subsampling(subsample)
        self.controller.process_images('qa')
        self.failIf(len(os.listdir(os.path.join(self.controller.homeDir,'figs','qa'))) != 7)
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,'figs','qa','3FITC_4PE_004_thumbs')))

    def testRunModel(self):
        excludedChannelInd = 1
        self.controller.log.log['num_iters_mcmc'] = 1100
        self.controller.log.log['selected_k'] = 16
        self.controller.log.log['model_to_run'] = 'dpmm'
        self.controller.log.log['excluded_channels_analysis'] = [excludedChannelInd]
        self.controller.log.log['subsample_analysis'] = '1e3'
        self.controller.run_selected_model(useSubsample=True,cleanBorderEvents=True)
        fileName = "3FITC_4PE_004"
        fileChannels = self.controller.model.get_file_channel_list(fileName)    
        excludedChannel = fileChannels[excludedChannelInd]

        ## check components and modes
        statModelComponents, statModelComponentClasses = self.controller.model.load_model_results_pickle(fileName,'run1',modelType='components')
        statModelModes, statModelModeClasses = self.controller.model.load_model_results_pickle(fileName,'run1',modelType='modes')
        self.assertEqual(statModelComponentClasses.size,1000)
        self.assertEqual(statModelModeClasses.size,1000)

        ## check IR from log file
        modelRunID = 'run1'
        modelLog = self.controller.model.load_model_results_log(fileName,modelRunID)
        self.assertEqual(self.projectID,modelLog['project id'])
        self.assertEqual(excludedChannel,modelLog['unused channels'])

        ## test process images after model run
        subsample = self.controller.log.log['subsample_analysis']
        self.controller.handle_subsampling(subsample)
        self.controller.process_images('analysis',modelRunID=modelRunID)

        self.failIf(len(os.listdir(os.path.join(self.controller.homeDir,'figs', modelRunID))) != 4)
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,'figs',modelRunID,'3FITC_4PE_004_thumbs')))

### Run the tests
if __name__ == '__main__':
    unittest.main()
