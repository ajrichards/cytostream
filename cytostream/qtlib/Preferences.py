#!/usr/bin/python
'''
Cytostream
Preferences
a widget to edit application preferences
'''
__author__ = "A Richards"

import sys
from PyQt4 import QtGui, QtCore

class Preferences(QtGui.QWidget):
    def __init__(self, parent=None, openBtnFn=None,closeBtnFn=None,defaultTransform=None,mainWindow=None):
        QtGui.QWidget.__init__(self,parent)

        ## variables
        self.transformsList = ['log','logicle']
        self.defaultTransform = defaultTransform
        self.selectedProject = None
        self.openBtnFn = openBtnFn
        self.parent = parent
        self.selectedTransform = None
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

        ## set up main widget label
        self.hbl1.addWidget(QtGui.QLabel('select transformation'))
        
        ## set default transform
        if self.defaultTransform == None:
            self.defaultTransform = 'log'
        elif self.defaultTransform not in self.transformsList:
            print "ERROR: EditMenu -- specified defaultTransform not in transformList"
            self.defaultTransform = 'log'
            
        ## add transformations as option
        self.btns = {}
        vbox = QtGui.QVBoxLayout()
        for bLabel in self.transformsList:
            rad = QtGui.QRadioButton(bLabel)
            self.btns[bLabel] = rad
            self.connect(self.btns[bLabel], QtCore.SIGNAL('clicked()'),lambda item=bLabel:self.transformation_callback(item))
            vbox.addWidget(self.btns[bLabel])

            if self.defaultTransform != None and bLabel == self.defaultTransform:
                self.btns[bLabel].setChecked(True)
        self.hbl2.addLayout(vbox)

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
    
