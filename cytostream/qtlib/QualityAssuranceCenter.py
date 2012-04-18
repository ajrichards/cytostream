#!/usr/bin/python
'''
Cytostream
QualityAssuranceCenter
The main widget for the quality assurance state

'''

__author__ = "A Richards"

import sys,time,os
from PyQt4 import QtGui, QtCore
import numpy as np
from cytostream.qtlib import ProgressBar
from cytostream import Logger, Model


class QualityAssuranceCenter(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList,alternateChannelList=None, alternateFileList=None,mainWindow=None, 
                 parent=None,fontSize=11,showProgressBar=True,excludedChannels=[]):

        QtGui.QWidget.__init__(self,parent)

        ## arg variables
        self.setWindowTitle('Quality Assurance')
        self.fileList = fileList
        self.masterChannelList = masterChannelList
        self.alternateChannelList = alternateChannelList
        self.alternateFileList = alternateFileList
        self.mainWindow = mainWindow
        self.fontSize = fontSize
        self.showProgressBar = showProgressBar
        self.excludedChannels = [int(chan) for chan in excludedChannels]

        ## declared variables
        self.progressBar = None

        ## prepare model and log
        if self.mainWindow != None:
            self.controller = mainWindow.controller
            self.log = self.controller.log
        else:
            self.log = None

        ## prepare layout
        self.grid = QtGui.QGridLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignTop)
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.setAlignment(QtCore.Qt.AlignTop)

        ## verify or create alternate channel list
        if self.alternateChannelList == None:
            self.alternateChannelList = [chan for chan in self.masterChannelList]
         
        if self.alternateFileList == None:
            self.alternateFileList = [fileName for fileName in self.fileList]

        ## initialize view
        self.init_progressbar_view()
        

        ## finalize layout
        vbox.addLayout(self.hbox)
        self.setLayout(vbox)

    def set_enable_disable(self):
        '''
        enable/disable buttons
        
        '''
        
        self.mainWindow.pDock.contBtn.setEnabled(False)
        self.mainWindow.moreInfoBtn.setEnabled(True)
        self.mainWindow.recreateBtn.setEnabled(False)
        self.mainWindow.fileSelector.setEnabled(False)
        self.mainWindow.plotSelector.setEnabled(False)
        self.mainWindow.vizModeSelector.setEnabled(False)
        self.mainWindow.saveImgsBtn.setEnabled(False)
        self.mainWindow.subsampleSelector.setEnabled(True)
        self.mainWindow.saveImgsBtn.setEnabled(False)
        self.mainWindow.pDock.enable_disable_states()
        
    def init_progressbar_view(self):
        pbLayout1 = QtGui.QVBoxLayout()
        pbLayout1.setAlignment(QtCore.Qt.AlignTop)
        pbLayout2 = QtGui.QVBoxLayout()
        pbLayout2.setAlignment(QtCore.Qt.AlignCenter)
        pbLayout2a = QtGui.QHBoxLayout()
        pbLayout2a.setAlignment(QtCore.Qt.AlignCenter)
        pbLayout2b = QtGui.QHBoxLayout()
        pbLayout2b.setAlignment(QtCore.Qt.AlignCenter)        
        pbLayout3 = QtGui.QHBoxLayout()
        pbLayout3.setAlignment(QtCore.Qt.AlignCenter) 
        pbLayout4 = QtGui.QHBoxLayout()
        pbLayout4.setAlignment(QtCore.Qt.AlignCenter)
        
        ## label widget 
        pbLayout2a.addWidget(QtGui.QLabel('Quality Assurance'))
        pbLayout2b.addWidget(QtGui.QLabel('To browse the data images must be first created'))
                
        ## show the progress bar
        self.init_progressbar()

        ## finalize layout
        pbLayout2.addLayout(pbLayout2a)
        pbLayout2.addLayout(pbLayout2b)
        pbLayout1.addLayout(pbLayout2)
        pbLayout1.addLayout(pbLayout3)
        pbLayout1.addWidget(QtGui.QLabel('\t\t\t'))
        pbLayout1.addWidget(QtGui.QLabel('\t\t\t'))
        pbLayout1.addLayout(pbLayout4)
        pbLayout1.addLayout(self.pbarLayout1)
        self.hbox.addLayout(pbLayout1)
        
    def init_progressbar(self):
        ## add progress bar if loading
        self.progressBar = ProgressBar(parent=self,buttonLabel="Create",withLabel='Render images for all files in project')
        if self.mainWindow != None:
            pass
        else:
            self.progressBar.set_callback(lambda x=self.progressBar: self.generic_callback)

        buffer1 = QtGui.QLabel('\t\t\t')
        buffer2 = QtGui.QLabel('\t\t\t')
        buffer3 = QtGui.QLabel('\t\t\t')
        buffer4 = QtGui.QLabel('\t\t\t')
        buffer5 = QtGui.QLabel('\t\t\t')
        buffer6 = QtGui.QLabel('\t\t\t')
        pbarLayout1a = QtGui.QHBoxLayout()
        pbarLayout1a.setAlignment(QtCore.Qt.AlignCenter)
        pbarLayout1b = QtGui.QHBoxLayout()
        pbarLayout1b.setAlignment(QtCore.Qt.AlignCenter)
        self.pbarLayout1 = QtGui.QVBoxLayout()
        self.pbarLayout1.setAlignment(QtCore.Qt.AlignCenter)

        pbarLayout1a.addWidget(buffer6)
        pbarLayout1a.addWidget(buffer6)
        pbarLayout1b.addWidget(buffer3)
        pbarLayout1b.addWidget(self.progressBar)
        pbarLayout1b.addWidget(buffer4)
        self.pbarLayout1.addWidget(buffer1)
        self.pbarLayout1.addWidget(buffer2)
        self.pbarLayout1.addLayout(pbarLayout1a)
        self.pbarLayout1.addLayout(pbarLayout1b)
     
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
    dpc = QualityAssuranceCenter(fileList, masterChannelList,showProgressBar=True)
    dpc.show()
    sys.exit(app.exec_())
    
