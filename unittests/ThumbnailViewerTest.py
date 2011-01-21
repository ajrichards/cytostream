import sys,os,unittest,time,re
sys.path.append(os.path.join("..","cytostream"))
sys.path.append(os.path.join("..", "cytostream","qtlib"))
from PyQt4 import QtGui, QtCore
import subprocess

## test class for the main window function
class ThumbnailViewerTest(unittest.TestCase):

    def testWindowFunction(self):
        proc = subprocess.Popen("python %s"%os.path.join("..","cytostream","qtlib","ThumbnailViewer.py"),
                                shell=True,
                                stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        while True:
            next_line = proc.stdout.readline()
            next_line = next_line.lower()
            self.assertEqual(re.search('err',next_line.lower()),None)
            if next_line == '' and proc.poll() != None:
                break

            print next_line
            proc.kill()
            
        if proc.stderr != None:
            print "std error", proc.stderr()
            self.assertEqual(proc.stderr,None)

### Run the tests 
if __name__ == '__main__':
    unittest.main()
