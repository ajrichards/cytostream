#!/usr/bin/python                                                                                                                                                               
'''
Cytostream
modelTypeSelector

A bar of radio widgets to select from different visualization modelTypes

'''

__author__ = "A Richards"

import sys,re
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import RadioBtnWidget

class ModelTypeSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of subsets. Upon selection variables corresponding to the
    selected subsets are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self, modelTypeList, color='white', parent=None, modelTypeDefault=None, modelTypeCallback=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## error checking
        if modelTypeDefault != None and modelTypeList.__contains__(modelTypeDefault) == False:
            print "ERROR: RadioBtnWidget - bad default specified",modelTypeDefault
            return None

        ## variables
        self.modelTypeList = modelTypeList
        self.color = color
        self.modelTypeList = modelTypeList
        self.btns = {}
        self.btnGroup = QtGui.QButtonGroup(parent)

        ## setup layout
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)
        
        ## modelType selector
        self.modelTypeSelector = RadioBtnWidget(self.modelTypeList,parent=self,callbackFn=modelTypeCallback,
                                                widgetLabel='Model Mode')
        hbox2.addWidget(self.modelTypeSelector)
        if modelTypeDefault != None:
            self.set_checked(modelTypeDefault)

        ## finalize layout
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def set_checked(self,modelTypeLabel):
        if self.modelTypeList.__contains__(modelTypeLabel) == False:
            print "ERROR: ModelTypeSelector - bad modelType label in set_checked"
            return None

        self.modelTypeSelector.btns[modelTypeLabel].setChecked(True)

    def generic_callback(self):
        print 'callback does not do anything yet'

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    modelTypeList = ['modelType1', 'modelType2']
    ms = ModelTypeSelector(modelTypeList)
    ms.show()
    sys.exit(app.exec_())
