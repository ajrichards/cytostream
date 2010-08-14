import sys,os,unittest,time,re
from PyQt4 import QtGui, QtCore
import subprocess
from cytostream import *


BASEDIR = os.path.dirname(__file__)

## test class for the main window function
class OneDimViewerTest(unittest.TestCase):

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

    def _checkPaths(self):
        if os.path.isdir(os.path.join(BASEDIR,"..","cytostream","projects",)) == False:
            chk = False
        else:
            chk = True

        return chk

    def testNull(self):
        chk = self._checkPaths()
        self.failIf(chk == False)


        print 'testing...'
        print 'basedir', BASEDIR

    

### Run the tests 
if __name__ == '__main__':
    unittest.main()
