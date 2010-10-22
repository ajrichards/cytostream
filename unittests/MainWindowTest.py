import sys,os,unittest,time
sys.path.append(os.path.join("..","cytostream"))
sys.path.append(os.path.join("..", "cytostream","qtlib"))

## test class for the main window function
class MainWindowTest(unittest.TestCase):

    def testMainWindow(self):
        from MainWindow import MainWindow
    
### Run the tests 
if __name__ == '__main__':
    unittest.main()
