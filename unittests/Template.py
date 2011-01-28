import sys,os,unittest,time,re

BASEDIR = os.path.dirname(__file__)

## test class for the main window function
class TemplateTest(unittest.TestCase):

    def setUp(self):
        try:
            self.goFlag
        except:
            self._initialize()

    def _initialize(self):
        print 'do something it initialize'
        self.goFlag = True

    def testSomthing(self):
        print 'run tests here'
        self.assertTrue(self.goFlag)
    

### Run the tests 
if __name__ == '__main__':
    unittest.main()
