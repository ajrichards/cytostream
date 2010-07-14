import sys,os,unittest,time,re
sys.path.append(os.path.join("..","cytostream"))
sys.path.append(os.path.join("..", "cytostream","qtlib"))
from PyQt4 import QtGui, QtCore
import subprocess
from Controller import Controller
import numpy as np

## test class for the main window function
class RunModelTest(unittest.TestCase):
    def setUp(self):
        try:
            self.controller
        except:
            self._initialize()
    
    def _initialize(self):
        self.controller = Controller()
        self.controller.initialize_project("Demo") 
        self.fcsFileName = os.path.join("..","cytostream","example_data", "3FITC_4PE_004.fcs") 
        self.controller.log.log['selectedFile'] = os.path.split(self.fcsFileName)[-1]
        self.controller.create_new_project(self.fcsFileName)
        
        # subsampling
        self.controller.log.log['subsample'] = '1e3'
        self.controller.handle_subsampling()

        #self.controller.process_images('qa')

    def verifyModelRun(self,modelName):
       statModel,statModelClasses = self.controller.model.load_model_results_pickle(modelName)    
       return statModelClasses

    def testRunSelectedModel(self):
        # numcomponents
        self.controller.log.log['numComponents'] = 16
        self.controller.log.log['modelToRun'] = 'dpmm-cpu'
        self.controller.run_selected_model()
        modelName = "%s_sub1000_dpmm-cpu"%os.path.split(self.fcsFileName)[-1][:-4]
        classes = self.verifyModelRun(modelName)
        #self.assertEqual(np.unique(classes).size,self.controller.log.log['numComponents'])
        self.assertEqual(len(classes),1000)

        self.controller.process_images('results')



### Run the tests 
if __name__ == '__main__':
    unittest.main()
