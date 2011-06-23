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
