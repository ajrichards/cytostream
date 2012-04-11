#!/usr/bin/python

'''
this script activates the GUI

A. Richards
'''

import sys, getopt, os
from PyQt4 import QtGui

import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('agg')
from cytostream.qtlib import MainWindow


## check for the debug flag
try:
    optlist, args = getopt.getopt(sys.argv[1:],'p:d')
except getopt.GetoptError:
    print getopt.GetoptError
    print sys.argv[0] + "-p"
    print "Note: project (-p) flag to run the software with a given project"
    sys.exit()

debug = False
projectID = None
for o, a in optlist:
    if o == '-p':
        projectID = a
    if o == '-d':
        debug = True

class Main():
    def __init__(self):
        app = QtGui.QApplication(sys.argv)
        app.setOrganizationName("Duke University")
        app.setOrganizationDomain("duke.edu")
        app.setApplicationName("cytostream")
        mw = MainWindow(debug=debug,projectID=projectID)
        mw.show()
        app.exec_()

if __name__ == '__main__':
    main = Main()
