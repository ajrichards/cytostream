#!/usr/bin/python                                                                                                                                                               
'''
Cytostream
modeSelector

A bar of radio widgets to select from different visualization modes

'''

__author__ = "A Richards"

import sys,re
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import RadioBtnWidget

class ModeSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of the visualization mode. Upon selection appropriate 
    changes are made to enable smooth transitions from one visualization mode to another.

    '''

    def __init__(self, modeList, color='white', parent=None, modeDefault=None, modeVizCallback=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## error checking
        if modeDefault != None and modeList.__contains__(modeDefault) == False:
            print "ERROR: RadioBtnWidget - bad default specified",modeDefault
            return None

        ## variables
        self.modeList = modeList
        self.color = color
        self.btns = {}
        self.btnGroup = QtGui.QButtonGroup(parent)

        ## setup layout
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)
        
        ## mode selector
        hbox1.addWidget(QtGui.QLabel('visualization mode'))
        self.modeSelector = RadioBtnWidget(self.modeList,parent=self,callbackFn=modeVizCallback)
        hbox2.addWidget(self.modeSelector)
        if modeDefault != None:
            self.set_checked(modeDefault)

        ## finalize layout
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def get_selected(self):
        return self.modeSelector.selectedItem

    def set_checked(self,modeLabel):
        if self.modeList.__contains__(modeLabel) == False:
            print "ERROR: ModeSelector - bad mode label in set_checked"
            return None

        self.modeSelector.btns[modeLabel].setChecked(True)
        self.modeSelector.selectedItem = modeLabel

    def generic_callback(self):
        print 'callback does not do anything yet'

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    modeList = ['mode1', 'mode2']
    ms = ModeSelector(modeList)
    ms.show()
    sys.exit(app.exec_())
