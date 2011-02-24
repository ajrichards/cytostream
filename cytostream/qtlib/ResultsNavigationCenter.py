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
    

        ## finalize layout
        if self.mainWindow == None:
            self.vboxTop.addLayout(hboxTop1)
            self.vboxTop.addLayout(hboxTop2)
        else:
            self.mainWindow.vboxTop.addLayout(hboxTop1)
            self.mainWindow.vboxTop.addLayout(hboxTop2)

    def generic_callback():
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
    
