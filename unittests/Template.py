import sys,os,unittest,time,re

from SimulatedData2 import case1, case2, case3
from SimulatedData2 import case1Labels, case2Labels, case3Labels

BASEDIR = os.path.dirname(__file__)


## test class for the main window function
class MultivarTestPDF(unittest.TestCase):

    _initialized = False    

    def setUp(self):
        if self._initialized == False:
            self._initialize()

    def _initialize(self):
        print 'do something it initialize--this is only done once'
        self.__class__._initialized = True

    def testSomthing(self):
        print 'run a set of tests here'
        self.assertTrue(self._initialized)
   
    def testSomethingElse(self):
        print 'run another set of tests here'
        self.assertTrue(self._initialized)

 

### Run the tests 
if __name__ == '__main__':
    unittest.main()
