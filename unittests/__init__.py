import unittest,getopt,sys,os
import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('agg')

## parse inputs                                                                                                                      
try:
    optlist, args = getopt.getopt(sys.argv[1:],'v')
except getopt.GetoptError:
    print getopt.GetoptError
    print sys.argv[0] + "-a"
    print "      projName (-v) verbose flag (default is False)"
    sys.exit()

VERBOSE = False
RUNALL = False

for o, a in optlist:
    if o == '-v':
        VERBOSE = True

### non GUI Tests
from ControllerTest import *
ControllerTestSuite = unittest.TestLoader().loadTestsFromTestCase(ControllerTest)
controllerSuite = unittest.TestSuite([ControllerTestSuite])

from ModelTest import *
ModelTestSuite = unittest.TestLoader().loadTestsFromTestCase(ModelTest)
modelSuite = unittest.TestSuite([ModelTestSuite])

from TestCase1 import *
TestCase1Suite = unittest.TestLoader().loadTestsFromTestCase(TestCase1)
runSuite = unittest.TestSuite([TestCase1Suite])

## filtering
from TestCase2 import *
TestCase2Suite = unittest.TestLoader().loadTestsFromTestCase(TestCase2)
runSuite = unittest.TestSuite([TestCase2Suite])

from DistanceCalculatorTest import DistanceCalculatorTest
DistanceCalculatorSuite = unittest.TestLoader().loadTestsFromTestCase(DistanceCalculatorTest)
caculatorSuite = unittest.TestSuite([DistanceCalculatorSuite])
