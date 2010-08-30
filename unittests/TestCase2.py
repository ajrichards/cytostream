#!/usr/bin/env python

import sys,os,unittest,time,re
from PyQt4 import QtGui, QtCore
import subprocess

import sys,os,re
if sys.platform == 'darwin':
    import matplotlib
    matplotlib.use('Agg')

BASEDIR = os.path.dirname(__file__)
START = False

from cytostream import NoGuiAnalysis

## test class for the main window function
class TestCase2(unittest.TestCase):

    def setUp(self):
        self._initialize()

    def _initialize(self):
        print 'initializing.................................................'
        self.projectID = 'utest'
        self.subsample = '1e3'
        makeQaFigs = True
        makeResultsFigs = True
        self.allFiles = [os.path.join(BASEDIR,"..","cytostream","example_data", "3FITC_4PE_004.fcs")]
        self.nga = NoGuiAnalysis(self.projectID,self.allFiles,self.subsample,makeQaFigs=makeQaFigs,makeResultsFigs=makeResultsFigs)
     
    def test_run_all(self):
        ## tests qc image files
        imgDir = os.path.join(BASEDIR,"..","cytostream","projects",self.projectID,"figs")
        pngCount = 0
        for img in os.listdir(imgDir):
            if re.search("\.png",img):
                pngCount += 1

        self.failIf(pngCount != 6)

        ## test qc image thumbs
        fileName = re.sub("\.pickle|\.fcs","",os.path.split(self.allFiles[0])[-1])
        imgDir = os.path.join(BASEDIR,"..","cytostream","projects",self.projectID,"figs","%s_thumbs"%fileName)
        pngCount = 0
        for img in os.listdir(imgDir):
            if re.search("\.png",img):
                pngCount += 1

        self.failIf(pngCount != 6)

        ## test results images
        modelName = "sub%s_dpmm"%(int(float(self.subsample)))
        imgDir = os.path.join(BASEDIR,"..","cytostream","projects",self.projectID,"figs",modelName)
        pngCount = 0
        for img in os.listdir(imgDir):
            if re.search("\.png",img):
                pngCount += 1

        self.failIf(pngCount != 6)

        ## test results image thumbs
        modelName = "sub%s_dpmm"%(int(float(self.subsample)))
        imgDir = os.path.join(BASEDIR,"..","cytostream","projects",self.projectID,"figs",modelName)
        pngCount = 0
        for img in os.listdir(imgDir):
            if re.search("\.png",img):
                pngCount += 1

        self.failIf(pngCount != 6)

        ## test verify model run
        selectedFile = os.path.split(self.allFiles[0])[-1]
        modelName = "%s_sub%s_dpmm"%(re.sub("\.fcs|\.pickle","",selectedFile),int(float(self.subsample)))
        modelType = 'components'
        statModelComponents,statModelClassesComponents = self.nga.controller.model.load_model_results_pickle(modelName,modelType)
        self.assertEqual(len(statModelClassesComponents),int(float(self.subsample)))
        modelType = 'modes'
        statModelModes,statModelClassesModes = self.nga.controller.model.load_model_results_pickle(modelName,modelType)
        self.assertEqual(len(statModelClassesModes),int(float(self.subsample)))
        #self.assertEqual(len(classesModes),int(float(self.subsample)))
                                                                                                                              
        #self.controller.log.log['numComponents'] = 16
        #self.controller.log.log['modelToRun'] = 'dpmm'
        #self.controller.run_selected_model()
        #selectedFile = self.controller.log.log['selectedFile']
        
        #classesComponents = self.verifyModelRun(modelName,'components')
        #classesModes = self.verifyModelRun(modelName,'modes')
        #self.assertEqual(len(classesComponents),int(float(self.subsample)))
        #self.assertEqual(len(classesModes),int(float(self.subsample)))

        


### Run the tests 
if __name__ == '__main__':
    unittest.main()
