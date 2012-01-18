#!/usr/bin/env python


import sys,os,unittest,time,re,time

import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('agg')

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
        self.fcsFileName = os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")    
        self.controller = Controller(debug=False)
        channelDict = {'fsc-h':0,'ssc-h':1}
        self.controller.create_new_project(self.homeDir,channelDict=channelDict,record=False)
        self.controller.load_files_handler([self.fcsFileName])
        self.controller.log.log['model_reference'] = '3FITC_4PE_004'
    
    
    def testLog(self):
        self.controller.save()
        self.assertTrue(os.path.isfile(os.path.join(self.controller.homeDir,"%s.log"%self.controller.projectID)))
    
    def testCreateNewProject(self):
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"data")))
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"figs")))
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"models")))
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"documents")))
    
        ## test that files can be loaded
        self.failIf(len(os.listdir(os.path.join(self.controller.homeDir,"data"))) != 3)
    
        ## test that events and channels may be retrieved
        fileName = re.sub('\s+','_',os.path.split(self.fcsFileName)[-1])
        fileName = re.sub('\.fcs|\.txt|\.out','',fileName)
        events = self.controller.model.get_events_from_file(fileName)
        self.assertEqual(events.shape[0],94569)
        self.assertEqual(events.shape[1],4)
        events = self.controller.get_events(fileName)
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
        events = self.controller.get_events(fileName,subsample=subsample)
        self.assertEqual(events.shape[0], 1000)

    def testProcessImagesQa(self):
        subsample = '1e3'
        self.controller.log.log['subsample_qa'] = subsample
        self.controller.handle_subsampling(subsample)
        self.controller.process_images('qa')
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,'figs','qa','3FITC_4PE_004_thumbs')))
    
    def testRunModel(self):
        excludedChannelInd = 1
        subsample = '1e3'
        self.controller.log.log['num_iters_mcmc'] = 1100
        self.controller.log.log['selected_k'] = 16
        self.controller.log.log['model_to_run'] = 'dpmm'
        self.controller.log.log['excluded_channels_analysis'] = [excludedChannelInd]
        self.controller.log.log['subsample_analysis'] = subsample
        
        ## run model
        self.controller.handle_subsampling(subsample)
        self.controller.run_selected_model(useSubsample=True)
        time.sleep(3)
        print 'model run'
        print os.listdir(os.path.join(self.homeDir,"models"))
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
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,'figs',modelRunID,'3FITC_4PE_004_thumbs')))

### Run the tests
if __name__ == '__main__':
    unittest.main()
