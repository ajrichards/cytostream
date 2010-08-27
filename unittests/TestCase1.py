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
    
    def testTestCase1(self):
        self.projectID = 'utest'
        self.allFiles = [os.path.join(BASEDIR,"..","cytostream","example_data", "3FITC_4PE_004.fcs")]
        self.subsample = '1e3'
        self.controller = Controller()
        self.controller.initialize_project(self.projectID)

        firstFile = True
        goFlag = True
        for fileName in self.allFiles:
            if os.path.isfile(fileName) == False:
                print 'ERROR: Bad file name skipping', fileName
                continue

            fileName = str(fileName)
            if firstFile == True:
                self.controller.create_new_project(fileName)
                firstFile = False
            else:
                goFlag = self.controller.load_additional_fcs_files(fileName)

        if self.controller.homeDir == None:
            print "ERROR: project failed to initialize"
            return
        else:
            print "project created."

        # handle subsampling 
        self.controller.log.log['subsample'] = self.subsample
        self.controller.handle_subsampling()
        self.controller.save()

        # create quality assurance images
        self.controller.process_images('qa')

        ## run models
        for fileName in self.allFiles:
            self.failIf(os.path.isfile(fileName) == False)
            self.controller.log.log['selectedFile'] = os.path.split(fileName)[-1]
            print 'running model on', self.controller.log.log['selectedFile']
            self.runSelectedModel()

        ## create figures 
        print 'creating results images'
        self.controller.process_images('results')

    def verifyModelRun(self,modelName,modelType):
       statModel,statModelClasses = self.controller.model.load_model_results_pickle(modelName,modelType)    
       return statModelClasses

    def runSelectedModel(self):
        # numcomponents
        self.controller.log.log['numComponents'] = 16
        self.controller.log.log['modelToRun'] = 'dpmm'
        self.controller.run_selected_model()
        selectedFile = self.controller.log.log['selectedFile']
        modelName = "%s_sub%s_dpmm"%(re.sub("\.fcs|\.pickle","",selectedFile),int(float(self.subsample)))
        classesComponents = self.verifyModelRun(modelName,'components')
        classesModes = self.verifyModelRun(modelName,'modes')
        self.assertEqual(len(classesComponents),int(float(self.subsample)))
        self.assertEqual(len(classesModes),int(float(self.subsample)))

        # check image creation
        self.controller.process_images('results')

### Run the tests 
if __name__ == '__main__':
    unittest.main()
