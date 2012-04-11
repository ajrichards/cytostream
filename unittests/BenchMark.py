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
        
    def testRunModel(self):
        excludedChannelInd = 1
        subsample = 'original'
        self.controller.log.log['num_iters_mcmc'] = 10000
        self.controller.log.log['selected_k'] = 96
        self.controller.log.log['model_to_run'] = 'dpmm'
        self.controller.log.log['excluded_channels_analysis'] = [excludedChannelInd]
        self.controller.log.log['subsample_analysis'] = subsample
        
        ## run model
        self.controller.handle_subsampling(subsample)
        timeBegin = time.time()
        self.controller.run_selected_model()
        timeEnd = time.time()
        runTime = timeEnd - timeBegin
        print "Runtime", runTime
        fileName = "3FITC_4PE_004"
        fileChannels = self.controller.model.get_file_channel_list(fileName)    
        excludedChannel = fileChannels[excludedChannelInd]

        ## check components and modes
        statModelComponents, statModelComponentClasses = self.controller.model.load_model_results_pickle(fileName,'run1',
                                                                                                         modelType='components')
        statModelModes, statModelModeClasses = self.controller.model.load_model_results_pickle(fileName,'run1',
                                                                                               modelType='modes')
        
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
