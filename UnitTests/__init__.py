import unittest,getopt,sys,os


## parse inputs                                                                                                                      
try:
    optlist, args = getopt.getopt(sys.argv[1:],'va')
except getopt.GetoptError:
    print getopt.GetoptError
    print sys.argv[0] + "-a -v"
    print "Note: fileName (-a) flag to run all tests (default is a subset)"
    print "      projName (-v) verbose flag (default is False)"
    sys.exit()

VERBOSE = False
RUNALL = False

for o, a in optlist:
    if o == '-v':
        VERBOSE = True
    #if o == '-a':
    #    RUNALL = True

if VERBOSE == True:
    ### GUI Visual Tests
    from MainWindowTest import *
    MainWindowTestSuite = unittest.TestLoader().loadTestsFromTestCase(MainWindowTest)
    mainWindowSuite = unittest.TestSuite([MainWindowTestSuite])

    from DataProcessingCenterTest import *
    DataProcessingCenterTestSuite = unittest.TestLoader().loadTestsFromTestCase(DataProcessingCenterTest)
    dataProcessingCenterSuite = unittest.TestSuite([DataProcessingCenterTestSuite])

    from DataProcessingDockTest import *
    DataProcessingDockTestSuite = unittest.TestLoader().loadTestsFromTestCase(DataProcessingDockTest)
    dataProcessingDockSuite = unittest.TestSuite([DataProcessingDockTestSuite])

    from ThumbnailViewerTest import *
    ThumbnailViewerTestSuite = unittest.TestLoader().loadTestsFromTestCase(ThumbnailViewerTest)
    thumbnailViewerdataSuite = unittest.TestSuite([ThumbnailViewerTestSuite])



### non GUI Tests
from ControllerTest import *
ControllerTestSuite = unittest.TestLoader().loadTestsFromTestCase(ControllerTest)
controllerSuite = unittest.TestSuite([ControllerTestSuite])

from ModelTest import *
ModelTestSuite = unittest.TestLoader().loadTestsFromTestCase(ModelTest)
modelSuite = unittest.TestSuite([ModelTestSuite])

from RunModelTest import *
RunModelTestSuite = unittest.TestLoader().loadTestsFromTestCase(RunModelTest)
runSuite = unittest.TestSuite([RunModelTestSuite])
