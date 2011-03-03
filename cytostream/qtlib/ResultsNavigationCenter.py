#!/usr/bin/python
'''
Cytostream
ResultsNavigationCenter
The main widget for the quality assurance state

'''

__author__ = "A Richards"

import sys,time,os
from PyQt4 import QtGui, QtCore
import numpy as np
from cytostream.qtlib import ProgressBar
from cytostream import Logger, Model


class ResultsNavigationCenter(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList, alternateChannelList=None, alternateFileList=None,mainWindow=None, 
                 parent=None,fontSize=11,mode='menu'):

        QtGui.QWidget.__init__(self,parent)

        ## arg variables
        self.setWindowTitle('Results Navigation')
        self.fileList = fileList
        self.alternateChannelList = alternateChannelList
        self.alternateFileList = alternateFileList
        self.mainWindow = mainWindow
        self.fontSize = fontSize
        self.masterChannelList = masterChannelList
        self.mode = mode

        if mainWindow == None:
            self.modelsRunList = ['run1','run2','run3']
            self.modelLogList = None
        else:
            maxModelRun = int(mainWindow.log.log['models_run_count'])
            selectedFile = mainWindow.log.log['selected_file']
            self.modelsRunList = ['run'+str(i+1) for i in range(maxModelRun)]
            modelRunID = 'run1'
            self.modelLogList = []
            for modelRunID in self.modelsRunList:
                modelLog = self.mainWindow.controller.model.load_model_results_log(selectedFile,modelRunID)
                self.modelLogList.append(modelLog)

        ## eror checking 
        if self.mode not in ['menu']:
            print "ERROR: REsultsNavigationCenter -- invalid mode specified", self.mode

        ## declared variables
        
        ## prepare model and log
        if self.mainWindow != None:
            self.controller = mainWindow.controller
            self.log = self.controller.log
        else:
            self.log = None

        ## prepare layout
        vbl = QtGui.QVBoxLayout()
        self.vboxTop = QtGui.QVBoxLayout()
        self.vboxTop.setAlignment(QtCore.Qt.AlignTop)
        self.vboxCenter = QtGui.QVBoxLayout()
        self.vboxCenter.setAlignment(QtCore.Qt.AlignCenter)
        self.vboxBottom = QtGui.QVBoxLayout()
        self.vboxBottom.setAlignment(QtCore.Qt.AlignBottom)

        ## verify or create alternate channel list
        if self.alternateChannelList == None:
            self.alternateChannelList = [chan for chan in self.masterChannelList]
         
        if self.alternateFileList == None:
            self.alternateFileList = [fileName for fileName in self.fileList]

        ## initialize view
        self.init_results_navigation_menu_view()
        
        ## add dummy vars
        #self.vboxTop.addWidget(QtGui.QLabel("blah"))
        #self.vboxCenter.addWidget(QtGui.QLabel("blah"))
        #self.vboxBottom.addWidget(QtGui.QLabel("blah"))

        ## finalize layout
        if self.mainWindow == None:
            vbl.addLayout(self.vboxTop)
            vbl.addLayout(self.vboxCenter)
            vbl.addLayout(self.vboxBottom)
            self.setLayout(vbl)

    def set_enable_disable(self):
        '''
        enable/disable buttons
        
        '''
        
        if len(self.modelsRunList) > 1:
            self.mainWindow.pDock.contBtn.setEnabled(True)
        else:
            self.mainWindow.pDock.contBtn.setEnabled(False)

        self.mainWindow.moreInfoBtn.setEnabled(True)
        self.mainWindow.fileSelector.setEnabled(False)
        self.mainWindow.modeSelector.setEnabled(False)
        self.mainWindow.pDock.enable_disable_states()
        
    def init_results_navigation_menu_view(self):
        hboxTop1 = QtGui.QHBoxLayout()
        hboxTop1.setAlignment(QtCore.Qt.AlignCenter)
        hboxTop2 = QtGui.QHBoxLayout()
        hboxTop2.setAlignment(QtCore.Qt.AlignCenter)

        ## titles widgets
        self.widgetTitle = QtGui.QLabel('Results Navigation')
        self.widgetSubtitle = QtGui.QLabel('Project results by category')
        hboxTop1.addWidget(self.widgetTitle)
        hboxTop2.addWidget(self.widgetSubtitle)
                
        ## some other widget
        self.make_models_run_sheet()

        ## finalize layout
        if self.mainWindow == None:
            self.vboxTop.addLayout(hboxTop1)
            self.vboxTop.addLayout(hboxTop2)
        else:
            self.mainWindow.vboxTop.addLayout(hboxTop1)
            self.mainWindow.vboxTop.addLayout(hboxTop2)

    def make_models_run_sheet(self):
        ## setup layouts
        ssLayout = QtGui.QVBoxLayout()
        ssLayout.setAlignment(QtCore.Qt.AlignCenter)
        ssLayout1 = QtGui.QHBoxLayout()
        ssLayout1.setAlignment(QtCore.Qt.AlignCenter)
        ssLayout2 = QtGui.QHBoxLayout()
        ssLayout2.setAlignment(QtCore.Qt.AlignCenter)
        ssLayout3 = QtGui.QHBoxLayout()
        ssLayout3.setAlignment(QtCore.Qt.AlignCenter)

        ## set up the label
        self.chksSummaryLabel = QtGui.QLabel('List of models run')

        ## create the excluded channels panel 
        self.modelRuns = QtGui.QStandardItemModel()

        for row in range(len(self.modelsRunList)):
            modelID = self.modelsRunList[row]
            if self.modelLogList != None:
                item0 = QtGui.QStandardItem(modelID)
                item1 = QtGui.QStandardItem('%s' % self.modelLogList[row]['full model name'])
                item2 = QtGui.QStandardItem('%s' % self.modelLogList[row]['subsample'])
                item3 = QtGui.QStandardItem('%s' % self.modelLogList[row]['used channels'])
                item4 = QtGui.QStandardItem('%s' % self.modelLogList[row]['timestamp'])
            else:
                item0 = QtGui.QStandardItem(modelID)
                item1 = QtGui.QStandardItem('%s' % 'blah')
                item2 = QtGui.QStandardItem('%s' % 'blah')
                item3 = QtGui.QStandardItem('%s' % 'blah')
                item4 = QtGui.QStandardItem('%s' % 'blah')
           
            ## set which ones are checked
            item0.setCheckable(True)
            item0.setEditable(False)
            item1.setEditable(False)
            self.modelRuns.appendRow([item0,item1,item2,item3,item4])

        #viewChannels = QtGui.QTreeView()
        viewChannels = QtGui.QTableView()
        viewChannels.setModel(self.modelRuns)
        self.modelRuns.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant('Model ID'))
        self.modelRuns.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelRuns.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant('Model used'))
        self.modelRuns.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelRuns.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant('Subsample'))
        self.modelRuns.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelRuns.setHeaderData(3, QtCore.Qt.Horizontal, QtCore.QVariant('Used Channels'))
        self.modelRuns.setHeaderData(3, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelRuns.setHeaderData(4, QtCore.Qt.Horizontal, QtCore.QVariant('Timestamp'))
        self.modelRuns.setHeaderData(4, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)

        ## add navigate btn
        self.navigateBtn = QtGui.QPushButton("Navigate")
        self.navigateBtn.setMaximumWidth(120)
        self.navigateBtn.setMinimumWidth(120)
        self.connect(self.navigateBtn,QtCore.SIGNAL('clicked()'),self.navigate_callback)


        ## finalize layouts    
        ssLayout1.addWidget(self.chksSummaryLabel)
        ssLayout2.addWidget(viewChannels)
        ssLayout3.addWidget(self.navigateBtn)
        ssLayout.addLayout(ssLayout1)
        ssLayout.addLayout(ssLayout2)
        ssLayout.addLayout(ssLayout3)
        if self.mainWindow == None:
            self.vboxCenter.addLayout(ssLayout)
        else:
            self.mainWindow.vboxCenter.addLayout(ssLayout)

    def navigate_callback(self):
        n = len(self.modelsRunList)
        checkStates = [self.modelRuns.itemFromIndex(self.modelRuns.index(i,0)).checkState() for i in range(n)]
        selectedModels = np.where(np.array([i for i in checkStates]) == 2)[0].tolist()

        if len(selectedModels) > 1:
            msg = "Only one results set may be selected at a time"
            reply = QtGui.QMessageBox.warning(self, "Information", msg)
            return None
        elif len(selectedModels) == 0:
            msg = "Please select a results set to begin navigation"
            reply = QtGui.QMessageBox.warning(self, "Information", msg)
            return None

        selectedModelName = self.modelsRunList[selectedModels[0]]

        if self.mainWindow != None:
            self.mainWindow.log.log['selected_model'] = selectedModelName
            self.mainWindow.display_thumbnails()
        else:
            print 'selected model name', selectedModelName

    def generic_callback(self):
        print "generic callback"

                  
### Run the tests                                                            
if __name__ == '__main__':
    ''' 
    Note: to show the opening screen set fileList = [] 
          otherwise use fileList = ['3FITC_4PE_004']
    
    '''
    
    app = QtGui.QApplication(sys.argv)
    masterChannelList = ['FL1-H', 'FL2-H', 'FSC-H', 'SSC-H']
    fileList = ['fileName1', 'fileName2']
    dpc = ResultsNavigationCenter(fileList, masterChannelList,mode='menu')
    dpc.show()
    sys.exit(app.exec_())
    
