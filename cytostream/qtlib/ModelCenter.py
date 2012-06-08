#!/usr/bin/python

'''
Cytostream
ModelCenter
The main widget for the model state

'''

__author__ = "A Richards"

import os,sys,re,time
import numpy as np
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import ProgressBar, KSelector, TextEntry

class WorkThread(QtCore.QThread):
    def __init__(self,mc,mainWindow,fileName):
        QtCore.QThread.__init__(self)
        self.mc = mc
        self.mainWindow = mainWindow
        self.fileName = fileName

    #def __del__(self):
    #    self.wait()

    def run(self):
        modelRunID = self.mainWindow.controller.log.log['selected_model']
        logFileName = self.fileName+"_%s"%(modelRunID)+".log"

        logFilePath = os.path.join(self.mainWindow.controller.homeDir,'models',logFileName)
        isFound = False
        while isFound == False:
            time.sleep(3)
            if os.path.exists(logFilePath):
                print 'found it'
                isFound = True

        finished = QtCore.pyqtSignal()
        self.finished.emit()

        return

class ModelCenter(QtGui.QWidget):
    def __init__(self, fileList, channelList,parent=None, runModelFn=None, mainWindow=None, 
                 alternateFiles=None, excludedChannels=[], excludedFiles=[],
                 returnBtnFn=None):
        QtGui.QWidget.__init__(self,parent)

        ## variables
        self.mainWindow = mainWindow
        self.fileList = fileList
        self.masterChannelList = channelList
        self.excludedChannels = excludedChannels
        self.excludedFiles = excludedFiles
        self.runModelFn = runModelFn

        ## handle alternate names
        if self.mainWindow == None:
            self.alternateFiles = [f for f in self.fileList]
            self.alternateChannels = [c for c in self.masterChannelList]
        else:
            self.alternateFiles = self.mainWindow.log.log['alternate_file_labels']
            self.alternateChannels = self.mainWindow.log.log['alternate_channel_labels']     

        if self.mainWindow != None:
            self.dpmmNiter = self.mainWindow.log.log['dpmm_niter']
            self.dpmmK = int(self.mainWindow.log.log['dpmm_k'])
        else:
            self.dpmmNiter = '1'
            self.dpmmK = 16

        if self.mainWindow != None:
            self.cleanBorderEvents = self.mainWindow.log.log['clean_border_events']
        else:
            self.cleanBorderEvents = True

        ## setup layouts
        self.grid = QtGui.QGridLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignTop)
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.setAlignment(QtCore.Qt.AlignTop)

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
        self.mainWindow.pDock.inactivate_all()
        
    def set_disable(self):
        '''
        disable buttons
        '''

        if self.mainWindow !=None:
            self.progressBar.button.setText('Please wait...')
            self.progressBar.button.setEnabled(False)
            self.widgetSubtitle.setText("Running model...")
            self.mainWindow.pDock.contBtn.setEnabled(False)
            self.mainWindow.moreInfoBtn.setEnabled(False)
            self.mainWindow.modelToRunSelector.setEnabled(False)
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
        self.widgetTitle = QtGui.QLabel('Data Modeling')
        self.widgetSubtitle = QtGui.QLabel('Select model for loaded data')
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
        self.progressBar = ProgressBar(parent=self,buttonLabel="Run",withLabel='Start model')
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
        self.chksSummaryLabel = QtGui.QLabel('Channels to include in model')

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

        self.fileSummaryLabel = QtGui.QLabel('Files to include in model')

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

    def generic_callback(self):
        print 'This button does nothing'

    def clean_border_events_callback(self):
        print 'clean border events'
        state = str(self.cleanBorderEventsBox.isChecked())
        
        if self.mainWindow != None:
            self.mainWindow.log.log['clean_border_events'] = state

    def init_model_process(self,command,script,fileList):
        if self.mainWindow != None:
            self.progressBar.button.setEnabled(0)
            self.progressBar.button.setText('Please wait...')
            self.mainWindow.pDock.contBtn.setEnabled(False)

        self.command = command
        self.script = script
        self.filesToRun = fileList
        self.nextFileToRun = 0
        self.submit_job()

    def submit_job(self):
        
        if self.nextFileToRun >= len(self.filesToRun):
            print 'no more files in the list'
            return

        fileName = self.filesToRun[self.nextFileToRun]
        print 'submitting process', fileName
        args = [self.script,"-h",self.mainWindow.controller.homeDir,"-f",fileName]
        self.process = QtCore.QProcess(self)
        self.process.startDetached(self.command,args)
        self.send_thread_to_wait_on_process_finish(fileName)
        #self.process.waitForFinished()
        
    def send_thread_to_wait_on_process_finish(self,fileName):
        if self.mainWindow == None:
            return

        self.workThread = WorkThread(self,self.mainWindow,fileName)
        self.connect(self.workThread, QtCore.SIGNAL("finished()"), self.on_process_finished)
        self.workThread.start()

    def on_process_finished(self):
        if self.mainWindow == None:
            return

        modelRunID = self.mainWindow.controller.log.log['selected_model']
        self.process.close()

        totalComplete = 0
        for dirFileName in os.listdir(os.path.join(self.mainWindow.controller.homeDir,'models')):
            for fileName in self.fileList:
                if dirFileName == fileName+"_%s"%(modelRunID)+".log":
                    totalComplete+=1
                
        percentComplete = (float(totalComplete) / float(len(self.fileList))) * 100.0
        print 'process finished',percentComplete,totalComplete
        self.progressBar.move_bar(int(round(percentComplete)))

        ## check to see if we need to send another file
        self.nextFileToRun += 1
        if self.nextFileToRun >= len(self.filesToRun):
            print 'all files have been run'
            return
        else:
            self.submit_job()

### Run the tests 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    fileList = ['file1','file2','file3']
    channelList = ['channel1', 'channel2', 'channel3']
    mc = ModelCenter(fileList,channelList)
    mc.show()
    sys.exit(app.exec_())
