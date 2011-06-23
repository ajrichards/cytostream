#!/usr/bin/python

'''
Cytostream
ModelCenter
The main widget for the model state

'''

__author__ = "A Richards"

import sys,re
import numpy as np
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import ProgressBar, KSelector, TextEntry

class FileAlignerCenter(QtGui.QWidget):
    def __init__(self, fileList, channelList, mode='progressbar',parent=None, runFileAlignerFn=None, mainWindow=None, 
                 alternateFiles=None, excludedChannels=[], excludedFiles=[],modelToRun='dpmm',
                 returnBtnFn=None):
        QtGui.QWidget.__init__(self,parent)

        ## variables
        self.mainWindow = mainWindow
        self.fileList = fileList
        self.masterChannelList = channelList
        self.mode = mode
        self.excludedChannels = excludedChannels
        self.excludedFiles = excludedFiles
        self.modelToRun = modelToRun
        self.runFileAlignerFn = runFileAlignerFn

        ## handle alternate names
        if self.mainWindow == None:
            self.alternateFiles = [f for f in self.fileList]
            self.alternateChannels = [c for c in self.masterChannelList]
        else:
            self.alternateFiles = self.mainWindow.log.log['alternate_file_labels']
            self.alternateChannels = self.mainWindow.log.log['alternate_channel_labels']     


        ## defaults
        if self.mainWindow != None:
            self.numItersMCMC = self.mainWindow.log.log['num_iters_mcmc']
            self.dpmmK = int(self.mainWindow.log.log['dpmm_k'])
        else:
            self.phiRange = [0.4]
            self.phi2Default = 0.95
            self.minMergeSilValue = 0.3
            self.distanceMetric = 'mahalanobis'
            
        ## error checking
        if self.mode not in ['progressbar', 'edit']:
            print "ERROR: File Aligner Center -- bad input mode", self.mode

        ## setup layouts
        self.grid = QtGui.QGridLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignTop)
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.setAlignment(QtCore.Qt.AlignTop)

        ## initialize view 
        if self.mode == 'progressbar':
            self.init_progressbar_view()
        if self.mode == 'edit':
            self.add_model_specific_settings()
            self.make_channels_sheet()
            self.make_files_sheet()

            ## save button
            btnBox = QtGui.QHBoxLayout()
            btnBox.setAlignment(QtCore.Qt.AlignCenter)
            self.saveBtn = QtGui.QPushButton("save changes")
            self.saveBtn.setMaximumWidth(100)
            self.connect(self.saveBtn, QtCore.SIGNAL('clicked()'),self.save_callback)
            btnBox.addWidget(self.saveBtn)
       
            ## return button
            self.returnBtn = QtGui.QPushButton("return")
            self.returnBtn.setMaximumWidth(100)
            if self.mainWindow != None:
                self.connect(self.returnBtn, QtCore.SIGNAL('clicked()'),self.mainWindow.handle_model_edit_return)
            btnBox.addWidget(self.returnBtn)
       
        ## finalize layout
        vbox.addLayout(self.hbox)
        if self.mode == 'edit':
            vbox.addLayout(btnBox)
        self.setLayout(vbox)

    def set_enable_disable(self):
        '''
        enable/disable buttons
        '''

        if self.mode == 'progressbar' and self.mainWindow !=None:
            self.mainWindow.pDock.contBtn.setEnabled(False)
            self.mainWindow.moreInfoBtn.setEnabled(True)
            self.mainWindow.pDock.inactivate_all()
        elif self.mode == 'edit' and self.mainWindow !=None:
            self.mainWindow.pDock.contBtn.setEnabled(False)
            self.mainWindow.moreInfoBtn.setEnabled(True)
            self.mainWindow.pDock.inactivate_all()

    def set_disable(self):
        '''
        disable buttons
        '''

        if self.mode == 'progressbar' and self.mainWindow !=None:
            self.progressBar.button.setText('Please wait...')
            self.progressBar.button.setEnabled(False)
            self.widgetSubtitle.setText("Running file alignment...")
            self.mainWindow.pDock.contBtn.setEnabled(False)
            self.mainWindow.moreInfoBtn.setEnabled(False)
            self.mainWindow.subsampleSelector.setEnabled(False)
            self.mainWindow.modelToRunSelector.setEnabled(False)
            self.mainWindow.modelModeSelector.setEnabled(False)
            self.mainWindow.modelSettingsBtn.setEnabled(False)
            self.mainWindow.pDock.inactivate_all()

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
        self.widgetTitle = QtGui.QLabel('File Aligner')
        self.widgetSubtitle = QtGui.QLabel('Align the results of multiple runs to compare files')
        pbLayout2a.addWidget(self.widgetTitle)
        pbLayout2b.addWidget(self.widgetSubtitle)

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
        self.progressBar = ProgressBar(parent=self,buttonLabel="Run",withLabel='Start file alignment')
        if self.mainWindow != None:
            self.progressBar.set_callback(self.mainWindow.run_progress_bar)

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

    def make_channels_sheet(self):
        ## setup layouts
        ssLayout = QtGui.QVBoxLayout()
        ssLayout.setAlignment(QtCore.Qt.AlignCenter)
        ssLayout1 = QtGui.QHBoxLayout()
        ssLayout1.setAlignment(QtCore.Qt.AlignCenter)
        ssLayout2 = QtGui.QHBoxLayout()
        ssLayout2.setAlignment(QtCore.Qt.AlignCenter)

        ## set up the label
        self.chksSummaryLabel = QtGui.QLabel('Channels to base the alignment on')

        ## create the excluded channels panel 
        self.modelChannels = QtGui.QStandardItemModel()

        for row in range(len(self.masterChannelList)):
            channel = self.masterChannelList[row]
            altChannel = self.alternateChannels[row]
            item0 = QtGui.QStandardItem(str(row+1))
            item1 = QtGui.QStandardItem('%s' % altChannel)

            ## set which ones are checked
            check = QtCore.Qt.UnChecked if row in self.excludedChannels else QtCore.Qt.Checked
            item0.setCheckState(check)
            item0.setCheckable(True)
            item0.setEditable(False)
            item1.setEditable(False)
            self.modelChannels.appendRow([item0,item1])

        viewChannels = QtGui.QTreeView()
        viewChannels.setModel(self.modelChannels)
        self.modelChannels.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant('channel'))
        self.modelChannels.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelChannels.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant('name'))
        self.modelChannels.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)

        ## finalize layouts    
        ssLayout1.addWidget(self.chksSummaryLabel)
        ssLayout2.addWidget(viewChannels)
        ssLayout.addLayout(ssLayout1)
        ssLayout.addLayout(ssLayout2)
        self.hbox.addLayout(ssLayout)

    def make_files_sheet(self,firstRun=True):
        ## setup layouts
        if firstRun == True:
            ssLayout = QtGui.QVBoxLayout()
            ssLayout.setAlignment(QtCore.Qt.AlignCenter)
            ssLayout1 = QtGui.QHBoxLayout()
            ssLayout1.setAlignment(QtCore.Qt.AlignCenter)
            ssLayout2 = QtGui.QHBoxLayout()
            ssLayout2.setAlignment(QtCore.Qt.AlignCenter)

        self.fileSummaryLabel = QtGui.QLabel('Files to include in the alignment')

        ## create the file list panel 
        if firstRun == True:
            self.modelFiles = QtGui.QStandardItemModel()

        for row in range(len(self.fileList)):
            fileName = self.fileList[row]
            altFileName = self.alternateFiles[row]
            item1 = QtGui.QStandardItem(str(row+1))
            item2 = QtGui.QStandardItem('%s'%altFileName)

            ## set which ones are checked
            check = QtCore.Qt.UnChecked if row in self.excludedFiles else QtCore.Qt.Checked
            item1.setCheckState(check)
            item1.setCheckable(True)
            item1.setEditable(False)
            item2.setEditable(False)
            self.modelFiles.appendRow([item1,item2])

        ## setup the header 
        self.modelFiles.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant('file'))
        self.modelFiles.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelFiles.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant('name'))
        self.modelFiles.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        
        viewFiles = QtGui.QTreeView()
        viewFiles.setModel(self.modelFiles)

        ## finalize layout   
        if firstRun == True:
            ssLayout1.addWidget(self.fileSummaryLabel)
            ssLayout2.addWidget(viewFiles)
            ssLayout.addLayout(ssLayout1)
            ssLayout.addLayout(ssLayout2)
            self.hbox.addLayout(ssLayout)

    def add_model_specific_settings(self):
        '''
        initializes the first of three vertical panels 
        the widgets are specific to the selected model 
        to run

        '''

        mssLayout = QtGui.QVBoxLayout()
        mssLayout1 = QtGui.QVBoxLayout()
        mssLayout1.setAlignment(QtCore.Qt.AlignTop)
        mssLayout1 = QtGui.QVBoxLayout()
        mssLayout1.setAlignment(QtCore.Qt.AlignTop)
        mssLayout2 = QtGui.QVBoxLayout()
        mssLayout2.setAlignment(QtCore.Qt.AlignCenter)

        #if self.modelToRun in ['dpmm','k-means']:
        self.parametersLabel = QtGui.QLabel('Edit parameters')
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        hbox1.addWidget(self.parametersLabel)
        mssLayout1.addLayout(hbox1)
        
        hbox2b = QtGui.QHBoxLayout()
        hbox2b.setAlignment(QtCore.Qt.AlignCenter)
        self.phi1Entry = TextEntry("Phi1",textEntryDefault=self.phi1Default) 
        hbox2b.addWidget(QtGui.QLabel(" "))
        hbox2b.addWidget(self.phi1Entry)
        hbox2b.addWidget(QtGui.QLabel(" "))
        mssLayout1.addLayout(hbox2b)
            
        ## finalize layout
        mssLayout.addLayout(mssLayout1)
        mssLayout.addLayout(mssLayout2)
        self.hbox.addLayout(mssLayout)

    def save_callback(self):
        '''
        saves model parameters
        saves excluded channels
        saves excluded files
      
        '''

        print 'saving...'

        ## save parameters
        #if self.modelToRun == 'dpmm':
        #    numItersMCMC = self.mcmcItersEntry.get_text()
        #    dpmmK = self.kSelector.get_text()
        #
        #    if re.search("\D",numItersMCMC):
        #        msg = "The number of iterations for MCMC must be a numeric value"
        #        reply = QtGui.QMessageBox.warning(self, "Warning", msg)
        #        return None
        # 
        #    if self.mainWindow != None:
        #        self.mainWindow.log.log['num_mcmc_iters'] = numItersMCMC
        #        self.mainWindow.log.log['dpmm_k'] = dpmmK
        #        self.mainWindow.controller.save()

        ## excluded channels save
        #n = len(self.masterChannelList)
        #checkStates = [self.modelChannels.itemFromIndex(self.modelChannels.index(i,0)).checkState() for i in range(n)]
        #excludedChannels = np.where(np.array([i for i in checkStates]) == 0)[0].tolist()
        # 
        #if self.mainWindow != None:
        #    self.mainWindow.log.log['excluded_channels_analysis'] = excludedChannels
        #    self.mainWindow.controller.save()

    def generic_callback(self):
        print 'This button does nothing'

### Run the tests 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    fileList = ['file1','file2','file3']
    channelList = ['channel1', 'channel2', 'channel3']
    mode = 'edit' # edit, progressbar
    fac = FileAlignerCenter(fileList,channelList,mode=mode)
    fac.show()
    sys.exit(app.exec_())
