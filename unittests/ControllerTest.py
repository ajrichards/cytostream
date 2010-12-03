import sys,os,unittest,time,re
from cytostream import Controller

import numpy as np

## test class for the main window function
class ControllerTest(unittest.TestCase):
    def setUp(self):
        try:
            self.controller
        except:
            self._initialize()
    
    def _initialize(self):
        self.controller = Controller()
        self.controller.initialize_project("utest") 
        self.fcsFileName = os.path.join("..","cytostream","example_data", "3FITC_4PE_004.fcs") 
        self.controller.log.log['selectedFile'] = os.path.split(self.fcsFileName)[-1]

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
        self.controller.load_fcs_files([self.fcsFileName])
        self.failIf(len(os.listdir(os.path.join(self.controller.homeDir,"data"))) != 2)
    
        ## test that events and channels may be retrieved
        fileName = re.sub('\s+','_',os.path.split(self.fcsFileName)[-1])
        fileName = re.sub('\.fcs|\.txt|\.out','',fileName)
        events = self.controller.model.get_events(fileName,subsample='original')
        self.assertEqual(events.shape[0],94569)
        self.assertEqual(events.shape[1],4)

        fileChannels = self.controller.model.get_file_channel_list(fileName,subsample='original')
        self.assertEqual(len(fileChannels),4)

    def testSubsampling(self):
        subsample = '1e3'
        self.controller.log.log['subsample'] = subsample
        self.controller.handle_subsampling()
        fileName = re.sub('\s+','_',os.path.split(self.fcsFileName)[-1])
        fileName = re.sub('\.fcs|\.txt|\.out','',fileName)
        events = self.controller.model.get_events(fileName,subsample=subsample)
        print events.shape
    
        
    
    #def testProcessImages(self):
    #    self.controller.log.log['subsample'] = '1e3'
    #    self.controller.handle_subsampling()
    #    self.controller.process_images('qa')
    #    self.failIf(len(os.listdir(os.path.join(self.controller.homeDir,'figs'))) != 7)
    #    self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,'figs','3FITC_4PE_004_thumbs')))

### Run the tests 
if __name__ == '__main__':
    unittest.main()
