#!/usr/bin/python
'''
Cytostream
EditMenu
The edit widget for the data processing state
here global log file definations may be specified
'''
__author__ = "A Richards"

import sys
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import RadioBtnWidget

class EditMenu(QtGui.QWidget):
    def __init__(self, parent=None, openBtnFn=None,closeBtnFn=None,defaultTransform='log',mainWindow=None,defaultInputType='fcm'):
        QtGui.QWidget.__init__(self,parent)

        ## variables
        self.transformsList = ['log','logicle','none']
        self.inputTypeList   = ['fcm','tab-delimited','comma-delimited']
        self.defaultTransform = defaultTransform
        self.defaultInputType = defaultInputType
        self.selectedProject = None
        self.openBtnFn = openBtnFn
        self.parent = parent
        self.selectedTransform = None
        self.selectedInputDataType = None
        self.mainWindow = mainWindow

        ## setup layouts
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl1 = QtGui.QHBoxLayout()
        self.hbl1.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl2 = QtGui.QHBoxLayout()
        self.hbl2.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl3 = QtGui.QHBoxLayout()
        self.hbl3.setAlignment(QtCore.Qt.AlignCenter)

        ## set default transform
        if self.defaultTransform not in self.transformsList:
            print "ERROR: EditMenu -- specified defaultTransform not in transformList"
            self.defaultTransform = 'log'
            
        ## create selector widget
        self.transformSelector = RadioBtnWidget(self.transformsList,parent=self,callbackFn=self.transformation_callback,
                                                widgetLabel="Select transformation",default=self.defaultTransform)

        self.hbl1.addWidget(self.transformSelector)
        
        ## set default input data type
        if self.defaultInputType == 'tab':
            self.defaultInputType = 'tab-delimited'
        elif self.defaultInputType == 'comma':
            self.defaultInputType = 'comma-delimited'

        ## set default input type
        if self.defaultInputType not in self.inputTypeList:
            print "ERROR: EditMenu -- specified defaultInputType not in input type list"
            self.defaultInputType = 'fcm'
        
        ## input selector widget
        self.inputTypeSelector = RadioBtnWidget(self.inputTypeList,parent=self,callbackFn=self.input_type_callback,
                                                widgetLabel="Select input data type",default=self.defaultInputType)
            
        self.hbl2.addWidget(self.inputTypeSelector)

        ## create the buttons
        self.closeBtn = QtGui.QPushButton("save and return", self)
        self.closeBtn.setMaximumWidth(200)
        self.closeBtn.setMinimumWidth(200)
        self.hbl3.addWidget(self.closeBtn)
        if closeBtnFn == None:
            closeBtnFn = self.generic_callback

        self.connect(self.closeBtn, QtCore.SIGNAL('clicked()'),closeBtnFn)
                
        # finalize layout
        self.vbl.addLayout(self.hbl1)
        self.vbl.addLayout(self.hbl2)
        self.vbl.addLayout(self.hbl3)
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.vbl)

    ## enable/disable buttons
    def set_enable_disable(self):
        if self.mainWindow == None:
            return

        self.mainWindow.pDock.contBtn.setEnabled(False)
        self.mainWindow.moreInfoBtn.setEnabled(False)
        self.mainWindow.pDock.inactivate_all()
    
    def generic_callback(self):
        print 'This button does nothing'

    def transformation_callback(self):
        '''
        transformation selection callback 
        
        '''
        
        selectedTransform = self.transformSelector.selectedItem

        if selectedTransform == 'none':
            self.selectedTransform = 'None'
        else:
            self.selectedTransform = selectedTransform

        print 'saving', self.selectedTransform

        if self.mainWindow != None:
            self.mainWindow.controller.log.log['load_transform'] = self.selectedTransform
            self.mainWindow.controller.save()
    
    def input_type_callback(self,item=None):
        '''
        input data type selection 
        
        '''
        
        selectedInputType = self.inputTypeSelector.selectedItem

        if selectedInputType == 'comma-delimited':
            self.selectedInputType = 'comma'
        elif selectedInputType == 'tab-delimited':
            self.selectedInputType = 'tab'

        if self.mainWindow != None:
            self.mainWindow.controller.log.log['input_data_type'] = self.selectedInputDataType
            self.mainWindow.controller.save()

### Run the tests
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    oep = EditMenu()
    oep.show()
    sys.exit(app.exec_())
    
