import sys,os,unittest,time,re
sys.path.append(os.path.join("..","cytostream"))
sys.path.append(os.path.join("..", "cytostream","qtlib"))
from PyQt4 import QtGui, QtCore
import subprocess
from Controller import Controller


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
        self.controller.create_new_project(self.fcsFileName)
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"data")))
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"figs")))
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,"models")))

    def testProcessImages(self):
        self.controller.log.log['subsample'] = '1e3'
        self.controller.handle_subsampling()
        self.controller.process_images('qa')
        self.failIf(len(os.listdir(os.path.join(self.controller.homeDir,'figs'))) != 7)
        self.assertTrue(os.path.isdir(os.path.join(self.controller.homeDir,'figs','3FITC_4PE_004_thumbs')))

### Run the tests 
if __name__ == '__main__':
    unittest.main()
