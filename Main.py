#!/usr/bin/python

'''
this script activates the GUI

A. Richards
'''

## make imports
import sys,getopt
if sys.platform == 'darwin':
    import matplotlib
    matplotlib.use('Agg') 

from PyQt4 import QtGui
from cytostream.qtlib import MainWindow

## check for the debug flag
DEBUG = False
try:
    optlist, args = getopt.getopt(sys.argv[1:],'d')
except getopt.GetoptError:
    print getopt.GetoptError
    print sys.argv[0] + "-d"
    print "Note: debug (-d) flag to run the software in debug mode"
    sys.exit()

for o, a in optlist:
    if o == '-d':
        DEBUG = True

class Main():
    def __init__(self,debug=False):
        app = QtGui.QApplication(sys.argv)
        app.setOrganizationName("Duke University")
        app.setOrganizationDomain("duke.edu")
        app.setApplicationName("cytostream")
        mw = MainWindow(debug=debug)
        mw.show()
        app.exec_()

if __name__ == '__main__':
    main = Main(debug=DEBUG)
