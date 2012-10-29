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
        self.fileName = re.sub('\s+','_',os.path.split(self.fcsFileName)[-1])
        self.fileName = re.sub('\.fcs|\.txt|\.out','',self.fileName)
      
        self.controller = Controller(debug=False)
        channelDict = {'FSCH':0,'SSCH':1,'FL1H':2,'FL2H':3}
        self.controller.create_new_project(self.homeDir,channelDict=channelDict,record=False)
        self.controller.load_files_handler([self.fcsFileName])
        self.controller.log.log['model_reference'] = '3FITC_4PE_004'

        ## ensure we can open project with cytostream
        self.controller.log.log['current_state'] = "Quality Assurance"
        self.controller.log.log['highest_state'] = '2'
        self.controller.save()

    
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
        print '...testing subsampler'
        subsample = '1e3'
        self.controller.log.log['subsample_qa'] = subsample
        self.controller.handle_subsampling(subsample)
        events = self.controller.get_events(self.fileName,subsample=subsample)
        self.assertEqual(events.shape[0], 1000)
    
    def testProcessImagesQa(self):
        print '...testing qa images'
        subsample = '1e3'
        self.controller.log.log['subsample_qa'] = subsample
        self.controller.handle_subsampling(subsample)
        self.controller.process_images('qa')
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,'figs','qa','3FITC_4PE_004_thumbs')))
    
    def testRunModelDPMMM(self):
        print '...testing dpmm'
        excludedChannelInd = 1
        subsample = '1e3'
        self.controller.log.log['num_iters_mcmc'] = 1100
        self.controller.log.log['dpmm_k'] = 16
        self.controller.log.log['model_to_run'] = 'dpmm-mcmc'
        self.controller.log.log['excluded_channels_analysis'] = [excludedChannelInd]
        self.controller.log.log['subsample_run'] = subsample
        self.controller.log.log['subsample_analysis'] = subsample
        self.controller.save()

        ## prepare to run models
        self.controller.handle_subsampling(subsample)

        ## check that it works with cpu subprocessing
        self.controller.run_selected_model_cpu()
        time.sleep(1)
        labels1 = self.controller.get_labels(self.fileName,'run1')
        self.assertEqual(labels1.size,1000)        
        labels1,modelRunLog1 = self.controller.get_labels(self.fileName,'run1',getLog=True)
        self.assertTrue(len(modelRunLog1.keys()) > 5)
    
    '''
    def testRunModelKmeans(self):
        print '...testing kmeans'
        excludedChannelInd = 1
        subsample = '1e3'
        self.controller.log.log['dpmm_k'] = 16
        self.controller.log.log['model_to_run'] = 'kmeans'
        self.controller.log.log['excluded_channels_analysis'] = [excludedChannelInd]
        self.controller.log.log['subsample_run'] = subsample
        self.controller.log.log['subsample_analysis'] = subsample
        self.controller.save()

        ## run model
        self.controller.handle_subsampling(subsample)
        self.controller.run_selected_model_cpu()

        labels1 = self.controller.get_labels(self.fileName,'run1')
        self.assertEqual(labels1.size,1000)        
        modelRunLog1, labels1 = self.controller.get_labels(self.fileName,'run1',getLog=True)
        self.assertTrue(len(modelRunLog1.keys()) > 5)
        self.assertEqual(self.projectID,modelRunLog1['project id'])

        ## test process images after model run
        self.controller.process_images('analysis',modelRunID='run1')
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,'figs','run1','3FITC_4PE_004_thumbs')))
    '''

### Run the tests
if __name__ == '__main__':
    unittest.main()
