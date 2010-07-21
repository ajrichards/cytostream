import sys,os,unittest,time,re
sys.path.append(os.path.join("..","Flow-GCMC"))
sys.path.append(os.path.join("..", "Flow-GCMC","qtlib"))
from PyQt4 import QtGui, QtCore
import subprocess

## test class for the main window function
class QualityAssuranceDockTest(unittest.TestCase):
    def setUp(self):
        masterChannelList = ['FL1-H', 'FL2-H', 'FSC-H', 'SSC-H']
        fileList = ['file1', 'file2']

    def testWindowFunction(self):        
        proc = subprocess.Popen("python %s"%os.path.join("..","Flow-GCMC","qtlib","QualityAssuranceDock.py"),
                                shell=True,
                                stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        while True:
            next_line = proc.stdout.readline()
            next_line = next_line.lower()
            self.assertEqual(re.search('err',next_line.lower()),None)
            if next_line == '' and proc.poll() != None:
                break
            
            proc.kill()
        
        if proc.stderr != None:
            print proc.stderr()
            self.assertEqual(proc.stderr,None)
            
### Run the tests 
if __name__ == '__main__':
    unittest.main()
