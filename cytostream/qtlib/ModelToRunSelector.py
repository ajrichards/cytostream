#!/usr/bin/python                                                                                                                                                               
'''
Cytostream
modelToRunSelector

A bar of radio widgets to select from different models to run

'''

__author__ = "A Richards"

import sys,re
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import RadioBtnWidget

class ModelToRunSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of subsets. Upon selection variables corresponding to the
    selected subsets are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self, mtrList, color='white', parent=None, mtrDefault=None, mtrCallback=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## error checking
        if mtrDefault != None and mtrList.__contains__(mtrDefault) == False:
            print "ERROR: RadioBtnWidget - bad default specified",mtrDefault
            return None

        ## variables
        self.modelToRunList = mtrList
        self.color = color
        self.btns = {}
        self.btnGroup = QtGui.QButtonGroup(parent)

        ## setup layout
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)
        
        ## modelToRun selector
        self.modelToRunSelector = RadioBtnWidget(self.modelToRunList,parent=self,callbackFn=mtrCallback,widgetLabel="Model")
        hbox2.addWidget(self.modelToRunSelector)
        if mtrDefault != None:
            self.set_checked(mtrDefault)

        ## finalize layout
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def set_checked(self,modelToRunLabel):
        if self.modelToRunList.__contains__(modelToRunLabel) == False:
            print "ERROR: ModelToRunSelector - bad modelToRun label in set_checked"
            return None

        self.modelToRunSelector.btns[modelToRunLabel].setChecked(True)

    def generic_callback(self):
        print 'callback does not do anything yet'

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    mtrList = ['modelToRun1', 'modelToRun2']
    ms = ModelToRunSelector(mtrList)
    ms.show()
    sys.exit(app.exec_())
