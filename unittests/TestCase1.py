#!/usr/bin/env python

import sys,os,unittest,time,re
from PyQt4 import QtGui, QtCore
import subprocess

import sys
if sys.platform == 'darwin':
    import matplotlib
    matplotlib.use('Agg')

from cytostream import Controller
import numpy as np
BASEDIR = os.path.dirname(__file__)

## test class for the main window function
class TestCase1(unittest.TestCase):
    def setUp(self):
        try:
            self.controller
        except:
            self._initialize()
    
    def _initialize(self):
        self.controller = Controller()
        self.controller.initialize_project("utest") 
        self.failIf(os.path.isfile(os.path.join(BASEDIR,"..","cytostream","example_data", "3FITC_4PE_004.fcs")) == False)
        self.fcsFileName = os.path.join(BASEDIR,"..","cytostream","example_data", "3FITC_4PE_004.fcs")

        if os.path.isfile(self.fcsFileName) == False:
            print "ERROR: fcsFileName is not true"

        self.controller.log.log['selectedFile'] = os.path.split(self.fcsFileName)[-1]
        self.controller.create_new_project(self.fcsFileName)
        
        # subsampling
        self.controller.log.log['subsample'] = '1e3'
        self.controller.handle_subsampling()

        # check image creation
        self.controller.process_images('qa')

    def verifyModelRun(self,modelName,modelType):
       statModel,statModelClasses = self.controller.model.load_model_results_pickle(modelName,modelType)    
       return statModelClasses

    def testRunSelectedModel(self):
        # numcomponents
        self.controller.log.log['numComponents'] = 16
        self.controller.log.log['modelToRun'] = 'dpmm'
        self.controller.run_selected_model()
        modelComponents = "%s_sub1000_dpmm"%os.path.split(self.fcsFileName)[-1][:-4]
        modelModes = "%s_sub1000_dpmm"%os.path.split(self.fcsFileName)[-1][:-4]
        classesComponents = self.verifyModelRun(modelComponents,'components')
        classesModes = self.verifyModelRun(modelModes,'modes')
        self.assertEqual(len(classesComponents),1000)
        self.assertEqual(len(classesModes),1000)

        # check image creation
        self.controller.process_images('results')

### Run the tests 
if __name__ == '__main__':
    unittest.main()