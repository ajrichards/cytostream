#!/usr/bin/python
'''
Cytostream
Preferences
a widget to edit application preferences
'''
__author__ = "A Richards"

import sys
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import RadioBtnWidget, KSelector, TextEntry

class PreferencesKmeans(QtGui.QWidget):
    def __init__(self, parent=None, mainWindow=None):
        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.modelTypeList = ['normal','onefit']
        self.parent = parent
        self.mainWindow = mainWindow
        
        if self.mainWindow == None:
            self.kmeansK = 16
            self.kmeansRepeats = 5
        else:
            self.kmeansK = self.mainWindow.controller.log.log['kmeans_k']
            self.kmeansRepeats = self.mainWindow.controller.log.log['kmeans_repeats']

        ## setup layouts
        self.masterBox = QtGui.QHBoxLayout()
        self.headerBox = QtGui.QHBoxLayout()
        self.headerBox.setAlignment(QtCore.Qt.AlignTop)
        self.footerBox = QtGui.QHBoxLayout()
        self.footerBox.setAlignment(QtCore.Qt.AlignBottom)
        self.titleBox =  QtGui.QHBoxLayout()
        self.titleBox.setAlignment(QtCore.Qt.AlignCenter)
        self.titleBox.addWidget(QtGui.QLabel('K-means\n\n\n\n'))
        self.arrayBox =  QtGui.QVBoxLayout()
        self.arrayBox.setAlignment(QtCore.Qt.AlignCenter)
        self.columnsBox =  QtGui.QHBoxLayout()
        self.columnsBox.setAlignment(QtCore.Qt.AlignCenter)
        self.col1Box = QtGui.QVBoxLayout()
        self.col1Box.setAlignment(QtCore.Qt.AlignTop)
        self.col2Box = QtGui.QVBoxLayout()
        self.col2Box.setAlignment(QtCore.Qt.AlignTop)
        self.col3Box = QtGui.QVBoxLayout()
        self.col3Box.setAlignment(QtCore.Qt.AlignTop)

        ## column 1 (file preferences)
        self.col1LabBox = QtGui.QVBoxLayout()
        self.col1LabBox.setAlignment(QtCore.Qt.AlignTop)
        self.col1LabBox.addWidget(QtGui.QLabel('General \n\n'))
        self.col1Box.addLayout(self.col1LabBox)

        self.modelTypeSelector = RadioBtnWidget(self.modelTypeList,parent=self,callbackFn=self.generic_callback,widgetLabel='Model Type')
        self.modelTypeSelector.btns['normal'].setChecked(True)
        self.col1Box.addWidget(self.modelTypeSelector)

        self.kSelector = KSelector(parent=self,kDefault=self.kmeansK)
        self.col1Box.addWidget(self.kSelector)

        ## column 2 (plots preferences)
        self.col2LabBox = QtGui.QVBoxLayout()
        self.col2LabBox.setAlignment(QtCore.Qt.AlignTop)
        self.col2LabBox.addWidget(QtGui.QLabel('Model \n\n'))
        self.col2Box.addLayout(self.col2LabBox)
        self.kmeansRepeatsEntry = TextEntry("number times to repeat",textEntryDefault=str(int(self.kmeansRepeats)))

        self.col2Box.addWidget(self.kmeansRepeatsEntry)

        ## column 3 (model preferences)
        #self.col3LabBox = QtGui.QVBoxLayout()
        #self.col3LabBox.setAlignment(QtCore.Qt.AlignTop)
        #self.col3LabBox.addWidget(QtGui.QLabel('model preferences\n\n'))
        #self.col3Box.addLayout(self.col3LabBox)

        ## btn
        self.closeBtn = QtGui.QPushButton("save and return", self)
        self.closeBtn.setMaximumWidth(200)
        self.closeBtn.setMinimumWidth(200)
        self.footerBox.setAlignment(QtCore.Qt.AlignCenter)
        self.footerBox.addWidget(QtGui.QLabel('\n\n\n\n'))
        self.footerBox.addWidget(self.closeBtn)
        if self.mainWindow == None:
            self.connect(self.closeBtn, QtCore.SIGNAL('clicked()'),self.generic_callback)
        else:
            self.connect(self.closeBtn, QtCore.SIGNAL('clicked()'),self.mainWindow.transitions.move_to_model_run)

        ## finalize layout
        self.columnsBox.addLayout(self.col1Box)
        self.columnsBox.addLayout(self.col2Box)
        #self.columnsBox.addLayout(self.col3Box)
        self.headerBox.addLayout(self.titleBox)
        self.arrayBox.addLayout(self.headerBox)
        self.arrayBox.addLayout(self.columnsBox)
        self.arrayBox.addLayout(self.footerBox)
        self.masterBox.addLayout(self.arrayBox)
        self.setLayout(self.masterBox)

    ## enable/disable buttons
    def set_enable_disable(self):
        if self.mainWindow == None:
            return
        self.mainWindow.pDock.contBtn.setEnabled(False)
        self.mainWindow.moreInfoBtn.setEnabled(False)
        self.mainWindow.pDock.inactivate_all()
    
    def generic_callback(self):
        print 'This button does nothing'

### Run the tests
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    oep = PreferencesKmeans()
    oep.show()
    sys.exit(app.exec_())
    
