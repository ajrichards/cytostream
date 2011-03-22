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

from TestCase2 import *
TestCase2Suite = unittest.TestLoader().loadTestsFromTestCase(TestCase2)
runSuite = unittest.TestSuite([TestCase2Suite])

from TestCase3 import *
TestCase3Suite = unittest.TestLoader().loadTestsFromTestCase(TestCase3)
runSuite = unittest.TestSuite([TestCase3Suite])

from TestCase4 import *
TestCase4Suite = unittest.TestLoader().loadTestsFromTestCase(TestCase4)
runSuite = unittest.TestSuite([TestCase4Suite])

from DistanceCalculatorTest import DistanceCalculatorTest
DistanceCalculatorSuite = unittest.TestLoader().loadTestsFromTestCase(DistanceCalculatorTest)
caculatorSuite = unittest.TestSuite([DistanceCalculatorSuite])

#from FileAlignerTest1 import FileAlignerTest1
#FileAlignerTestSuite1 = unittest.TestLoader().loadTestsFromTestCase(FileAlignerTest1)
#from FileAlignerTest2 import FileAlignerTest2
#FileAlignerTestSuite2 = unittest.TestLoader().loadTestsFromTestCase(FileAlignerTest2)

#fileAlignerSuite = unittest.TestSuite([FileAlignerTestSuite1,FileAlignerTestSuite2])
