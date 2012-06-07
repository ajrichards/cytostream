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
from cytostream import modelsInfo

class ModelToRunSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of subsets. Upon selection variables corresponding to the
    selected subsets are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self, color='white', parent=None, mainWindow=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## error checking
        #if mtrDefault != None and mtrList.__contains__(mtrDefault) == False:
        #    print "ERROR: RadioBtnWidget - bad default specified",mtrDefault
        #    return None

        ## variables
        self.modelToRunList = modelsInfo.keys()
        self.color = color
        self.btns = {}
        self.btnGroup = QtGui.QButtonGroup(parent)
        self.mainWindow = mainWindow
        self.selectedModel = 'dpmm-mcmc'

        if self.mainWindow != None:
            self.selectedModel = self.mainWindow.controller.log.log['model_to_run']
        if self.selectedModel not in self.modelToRunList:
            self.selectedModel = self.modelToRunList[0]

        ## setup layout
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)
        
        ## modelToRun selector
        mtrCallback = self.model_to_run_select_callback
        self.modelToRunSelector = RadioBtnWidget(self.modelToRunList,parent=self,widgetLabel="Model",callbackFn=mtrCallback)
        hbox2.addWidget(self.modelToRunSelector)
        self.set_checked(self.selectedModel)
        
        ## finalize layout
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def model_to_run_select_callback(self):
        validModels = ['kmeans','dpmm-mcmc']
        selectedModel = self.modelToRunSelector.selectedItem
 
        if selectedModel not in validModels:
            msg = "Selected model '%s' not in current list of valid models"%selectedModel
            if self.mainWindow == None:
                print "WARNING",msg
            else:
                self.mainWindow.display_warning(msg)
            self.set_checked('dpmm-mcmc')
            self.selectedModel = 'dpmm-mcmc'
        else:
            self.selectedModel = selectedModel

        if self.mainWindow != None:
            self.mainWindow.controller.log.log['model_to_run'] = self.selectedModel
            self.mainWindow.controller.save()

    def set_checked(self,modelToRunLabel):
        if self.modelToRunList.__contains__(modelToRunLabel) == False:
            print "ERROR: ModelToRunSelector - bad modelToRun label in set_checked"
            return None

        self.modelToRunSelector.btns[modelToRunLabel].setChecked(True)

    def generic_callback(self):
        print 'callback does not do anything yet'

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ms = ModelToRunSelector()
    ms.show()
    sys.exit(app.exec_())
