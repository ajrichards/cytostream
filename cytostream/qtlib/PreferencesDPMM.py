#!/usr/bin/python
'''
Cytostream
Preferences
a widget to edit application preferences
'''
__author__ = "A Richards"

import sys
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import RadioBtnWidget
from KSelector import KSelector
from TextEntry import TextEntry

class PreferencesDPMM(QtGui.QWidget):
    def __init__(self, parent=None, mainWindow=None):
        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.modelTypeList = ['normal','onefit']
        self.parent = parent
        self.mainWindow = mainWindow
        
        if self.mainWindow == None:
            self.dpmmK = 16
            self.dpmmNiter = 1
            self.dpmmBurnin = 1099
        else:
            self.dpmmK = self.mainWindow.controller.log.log['dpmm_k']
            self.dpmmNiter = self.mainWindow.controller.log.log['dpmm_niter']
            self.dpmmBurnin = self.mainWindow.controller.log.log['dpmm_burnin']

        ## setup layouts
        self.masterBox = QtGui.QHBoxLayout()
        self.headerBox = QtGui.QHBoxLayout()
        self.headerBox.setAlignment(QtCore.Qt.AlignTop)
        self.footerBox = QtGui.QHBoxLayout()
        self.footerBox.setAlignment(QtCore.Qt.AlignBottom)
        self.titleBox =  QtGui.QHBoxLayout()
        self.titleBox.setAlignment(QtCore.Qt.AlignCenter)
        self.titleBox.addWidget(QtGui.QLabel('Dirichlet process mixture model preferences (DPMM)\n\n\n\n'))
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

        self.kSelector = KSelector(parent=self,kDefault=int(self.dpmmK))
        self.col1Box.addWidget(self.kSelector)

        ## column 2 (plots preferences)
        self.col2LabBox = QtGui.QVBoxLayout()
        self.col2LabBox.setAlignment(QtCore.Qt.AlignTop)
        self.col2LabBox.addWidget(QtGui.QLabel('MCMC \n\n'))
        self.col2Box.addLayout(self.col2LabBox)
        self.dpmmNiterEntry = TextEntry("number iterations to save (niter)",textEntryDefault=str(int(self.dpmmNiter)))
        self.dpmmBurninEntry = TextEntry("number iterations to burnin",textEntryDefault=str(int(self.dpmmBurnin)))

        self.col2Box.addWidget(self.dpmmNiterEntry)
        self.col2Box.addWidget(self.dpmmBurninEntry)

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
    oep = PreferencesDPMM()
    oep.show()
    sys.exit(app.exec_())
    
