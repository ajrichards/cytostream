#!/usr/bin/python

'''
this script activates the GUI

A. Richards
'''

import sys, getopt, os
from PyQt4 import QtGui
from cytostream.qtlib import MainWindow

import sys
if sys.platform == 'darwin':
    import matplotlib
    matplotlib.use('Agg')

class Main():
    def __init__(self):
        app = QtGui.QApplication(sys.argv)
        app.setOrganizationName("Duke University")
        app.setOrganizationDomain("duke.edu")
        app.setApplicationName("cytostream")
        mw = MainWindow()
        mw.show()
        app.exec_()

if __name__ == '__main__':
    main = Main()
