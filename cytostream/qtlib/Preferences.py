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

class Preferences(QtGui.QWidget):
    def __init__(self, parent=None, mainWindow=None):
        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.loadTransformList = ['log','logicle','none']
        self.plotsTransformList = ['log','logicle']
        self.parent = parent
        self.mainWindow = mainWindow
        
        ## get default variables
        if self.mainWindow != None:
            defaultLoadTransform = self.mainWindow.controller.log.log['load_transform']
            defaultPlotsTransform = self.mainWindow.controller.log.log['plots_transform']
            defaultAutoComp       = self.mainWindow.controller.log.log['auto_compensation']
            defaultLogicleScaleMax = self.mainWindow.controller.log.log['logicle_scale_max']
        else:
            defaultLoadTransform = self.loadTransformList[0]
            defaultPlotsTransform = self.plotsTransformList[0]
            defaultAutoComp = True

        ## setup layouts
        self.masterBox = QtGui.QHBoxLayout()
        self.headerBox = QtGui.QHBoxLayout()
        self.headerBox.setAlignment(QtCore.Qt.AlignTop)
        self.footerBox = QtGui.QHBoxLayout()
        self.footerBox.setAlignment(QtCore.Qt.AlignBottom)
        self.titleBox =  QtGui.QHBoxLayout()
        self.titleBox.setAlignment(QtCore.Qt.AlignCenter)
        self.titleBox.addWidget(QtGui.QLabel('Cytostream Preferences\n\n\n\n'))
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
        self.col1LabBox.addWidget(QtGui.QLabel('file preferences\n\n'))
        self.col1Box.addLayout(self.col1LabBox)

        self.loadTransformSelector = RadioBtnWidget(self.loadTransformList,parent=self,callbackFn=self.generic_callback,widgetLabel='Load transformation')
        self.loadTransformSelector.btns[defaultLoadTransform].setChecked(True)
        self.col1Box.addWidget(self.loadTransformSelector)

        self.autoCompSelector = RadioBtnWidget(["True","False"],parent=self,callbackFn=self.generic_callback,widgetLabel='Auto compensation')
        self.autoCompSelector.btns[str(defaultAutoComp)].setChecked(True)
        self.col1Box.addWidget(self.autoCompSelector)

        ## column 2 (plots preferences)
        self.col2LabBox = QtGui.QVBoxLayout()
        self.col2LabBox.setAlignment(QtCore.Qt.AlignTop)
        self.col2LabBox.addWidget(QtGui.QLabel('plots preferences\n\n'))
        self.col2Box.addLayout(self.col2LabBox)

        self.plotsTransformSelector = RadioBtnWidget(self.plotsTransformList,parent=self,callbackFn=self.generic_callback,widgetLabel='Plots transformation')
        self.plotsTransformSelector.btns[defaultPlotsTransform].setChecked(True)
        self.col2Box.addWidget(self.plotsTransformSelector)

        ## column 3 (model preferences)
        self.col3LabBox = QtGui.QVBoxLayout()
        self.col3LabBox.setAlignment(QtCore.Qt.AlignTop)
        self.col3LabBox.addWidget(QtGui.QLabel('model preferences\n\n'))
        self.col3Box.addLayout(self.col3LabBox)


        ## btn
        self.closeBtn = QtGui.QPushButton("save and return", self)
        self.closeBtn.setMaximumWidth(200)
        self.closeBtn.setMinimumWidth(200)
        self.footerBox.setAlignment(QtCore.Qt.AlignCenter)
        self.footerBox.addWidget(QtGui.QLabel('\n\n\n\n'))
        self.footerBox.addWidget(self.closeBtn)
        self.connect(self.closeBtn, QtCore.SIGNAL('clicked()'),self.generic_callback)

        ## finalize layout
        self.columnsBox.addLayout(self.col1Box)
        self.columnsBox.addLayout(self.col2Box)
        self.columnsBox.addLayout(self.col3Box)
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
    
    def load_transform_selector_callback(self):
        pass


    def generic_callback(self):
        print 'This button does nothing'

    def transformation_callback(self,item=None):
        '''
        transformation selection callback 
        
        '''
        
        if item !=None:
            self.selectedTransform = item

            if self.mainWindow != None:
                self.mainWindow.log.log['selected_transform'] = self.selectedTransform
                self.mainWindow.controller.save()

### Run the tests
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    oep = Preferences()
    oep.show()
    sys.exit(app.exec_())
    
