#!/usr/bin/python

'''
Cytostream
ModelCenter
The main widget for the model state

'''

__author__ = "A Richards"

import sys
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import ProgressBar

class ModelCenter(QtGui.QWidget):
    def __init__(self, fileList, channelList, mode='progressbar',parent=None, runModelFn=None, mainWindow=None, 
                 alternateFiles=None, alternateChannels=None, excludedChannels=[], excludedFiles=[]):
        QtGui.QWidget.__init__(self,parent)

        ## variables
        self.mainWindow = mainWindow
        self.fileList = fileList
        self.masterChannelList = channelList
        self.mode = mode
        self.excludedChannels = excludedChannels
        self.excludedFiles = excludedFiles
        self.alternateFiles = alternateFiles
        self.alternateChannels = alternateChannels

        ## error checking
        if self.mode not in ['progressbar', 'edit']:
            print "ERROR: ModelCenter -- bad input mode", self.mode

        ## setup layouts
        self.grid = QtGui.QGridLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignTop)
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.setAlignment(QtCore.Qt.AlignTop)

        ## variable preparation
        if self.alternateFiles == None:
            self.alternateFiles = [f for f in self.fileList]
        if self.alternateChannels == None:
            self.alternateChannels = [c for c in self.masterChannelList]

        ## initialize view 
        if self.mode == 'progressbar':
            self.init_progressbar_view()
        if self.mode == 'edit':
            self.make_channels_sheet()
            self.make_files_sheet()

        ## finalize layout
        vbox.addLayout(self.hbox)
        self.setLayout(vbox)


    def set_enable_disable(self):
        '''
        enable/disable buttons
        '''

        if self.mode == 'progressbar' and self.mainWindow !=None:
            self.mainWindow.pDock.contBtn.setEnabled(False)
            self.mainWindow.moreInfoBtn.setEnabled(True)
            self.mainWindow.fileSelector.setEnabled(False)
            self.mainWindow.pDock.inactivate_all()
        elif self.mode == 'edit' and self.mainWindow !=None:
            self.mainWindow.fileSelector.setEnables(False)
            self.mainWindow.pDock.contBtn.setEnabled(False)
            self.mainWindow.moreInfoBtn.setEnabled(True)
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
        pbLayout2a.addWidget(QtGui.QLabel('Data Modeling'))
        pbLayout2b.addWidget(QtGui.QLabel('Select model for loaded data'))

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

    def make_channels_sheet(self):
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
        self.chksSummaryLabel = QtGui.QLabel('Select included channels and edit labels')

        ## create the excluded channels panel 
        self.modelChannels = QtGui.QStandardItemModel()

        for row in range(len(self.masterChannelList)):
            channel = self.masterChannelList[row]
            altChannel = self.alternateChannels[row]
            item0 = QtGui.QStandardItem(str(row+1))
            item1 = QtGui.QStandardItem('%s' % channel)
            item2 = QtGui.QStandardItem('%s' % altChannel)

            ## set which ones are checked
            check = QtCore.Qt.UnChecked if row in self.excludedChannels else QtCore.Qt.Checked
            item0.setCheckState(check)
            item0.setCheckable(True)
            item0.setEditable(False)
            item1.setEditable(False)
            item2.setEditable(True)
            self.modelChannels.appendRow([item0,item1,item2])

        viewChannels = QtGui.QTreeView()
        viewChannels.setModel(self.modelChannels)
        self.modelChannels.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant('channel'))
        self.modelChannels.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelChannels.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant('original'))
        self.modelChannels.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelChannels.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant('alternate '))
        self.modelChannels.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)

        ## setup save btn 
        self.saveBtn = QtGui.QPushButton("save changes")
        self.saveBtn.setMaximumWidth(100)
        self.connect(self.saveBtn, QtCore.SIGNAL('clicked()'),self.channels_save_callback)

        ## finalize layouts    
        ssLayout1.addWidget(self.chksSummaryLabel)
        ssLayout3.addWidget(self.saveBtn)
        ssLayout2.addWidget(viewChannels)
        ssLayout.addLayout(ssLayout1)
        ssLayout.addLayout(ssLayout2)
        ssLayout.addLayout(ssLayout3)
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
            ssLayout3 = QtGui.QHBoxLayout()
            ssLayout3.setAlignment(QtCore.Qt.AlignCenter)

        self.fileSummaryLabel = QtGui.QLabel('Select files to include in model run')

        ## create the file list panel 
        if firstRun == True:
            self.modelFiles = QtGui.QStandardItemModel()

        for row in range(len(self.fileList)):
            fileName = self.fileList[row]
            altFileName = self.alternateFiles[row]
            item1 = QtGui.QStandardItem(str(row+1))
            item2 = QtGui.QStandardItem('%s'%fileName)
            item3 = QtGui.QStandardItem('%s'%altFileName)

            ## set which ones are checked
            check = QtCore.Qt.UnChecked if row in self.excludedFiles else QtCore.Qt.Checked
            item1.setCheckState(check)
            item1.setCheckable(True)
            item1.setEditable(False)
            item2.setEditable(False)
            item3.setEditable(True)
            self.modelFiles.appendRow([item1,item2,item3])

        ## setup the header 
        self.modelFiles.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant('file'))
        self.modelFiles.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelFiles.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant('original'))
        self.modelFiles.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelFiles.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant('alternate'))
        self.modelFiles.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        
        viewFiles = QtGui.QTreeView()
        viewFiles.setModel(self.modelFiles)

        ## setup save btn
        if firstRun == True:
            self.saveFilesBtn = QtGui.QPushButton("save changes")
            self.saveFilesBtn.setMaximumWidth(100)
            self.connect(self.saveFilesBtn, QtCore.SIGNAL('clicked()'),self.files_save_callback)

        ## finalize layout   
        if firstRun == True:
            ssLayout1.addWidget(self.fileSummaryLabel)
            ssLayout2.addWidget(viewFiles)
            ssLayout3.addWidget(self.saveFilesBtn)
            ssLayout.addLayout(ssLayout1)
            ssLayout.addLayout(ssLayout2)
            ssLayout.addLayout(ssLayout3)
            self.hbox.addLayout(ssLayout)

    def channels_save_callback(self):
        '''
        saves alternate channel names
        saves excluded channels for quality assurance
        
        '''

        n = len(self.masterChannelList)
        altLabels = [str(self.modelChannels.data(self.modelChannels.index(i,2)).toString()) for i in range(n)]
        checkStates = [self.modelChannels.itemFromIndex(self.modelChannels.index(i,0)).checkState() for i in range(n)]
        excludedChannels = np.where(np.array([i for i in checkStates]) == 0)[0].tolist()

        if self.log != None:
            self.log.log['alternate_channel_labels'] = altLabels
            self.log.log['excluded_channels_qa'] = excludedChannels
            self.controller.save()

    def files_add_callback(self):
        if self.mainWindow != None:
            self.load_data_files()
        else:
            print 'load data file btn'

    def files_save_callback(self):
        '''
        saves alternate file names
        
        '''

        n = len(self.fileList)
        altFiles = [str(self.modelFiles.data(self.modelFiles.index(i,2)).toString()) for i in range(n)]

        if self.log != None:
            self.log.log['alternate_file_labels'] = altFiles
            self.controller.save()
        else:
            print 'alternate file names', altFiles

    def files_remove_callback(self):
        '''
        remove selected files from list
        
        '''

        n = len(self.fileList)
        checkStates = [self.modelFiles.itemFromIndex(self.modelFiles.index(i,0)).checkState() for i in range(n)]
        filesToRemove = np.where(np.array([i for i in checkStates]) == 2)[0].tolist()

        if len(filesToRemove) > 0:
            includedIndices = list(set(range(n)).difference(set(filesToRemove)))
            
            if len(filesToRemove) > 1:
                reply = QtGui.QMessageBox.question(self, self.mainWindow.controller.appName,
                                                   "Are you sure you want to completely remove %s files?"%(len(filesToRemove)),
                                                   QtGui.QMessageBox.Yes,QtGui.QMessageBox.No)
            else:
                reply = QtGui.QMessageBox.question(self, self.mainWindow.controller.appName,
                                                   "Are you sure you want to completely remove this file?",QtGui.QMessageBox.Yes,
                                                   QtGui.QMessageBox.No)
                
            if reply == QtGui.QMessageBox.Yes:
                ## remove all files associated with each fcs file
                if self.log != None:
                    for indToRemove in filesToRemove:
                        fileToRemove = self.fileList[indToRemove]
                        self.controller.rm_fcs_file(fileToRemove)

                ## reset file list and recreate widget
                self.fileList = np.array(self.fileList)[includedIndices].tolist()
                self.modelFiles.clear()
                self.make_files_sheet(firstRun=False)

            ## refresh log
            self.files_save_callback()
        else:
            msg = "Select one or more files in order to carry out file removal"
            reply = QtGui.QMessageBox.warning(self, "Warning", msg)





    def generic_callback(self):
        print 'This button does nothing'

    def set_message(self,msg):
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        self.msg = QtGui.QLabel(msg)
        hbl.addWidget(self.msg)
        self.vbl.addLayout(hbl)

### Run the tests 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    fileList = ['file1','file2','file3']
    channelList = ['channel1', 'channel2', 'channel3']
    mode = 'edit' # edit, progressbar
    mc = ModelCenter(fileList,channelList,mode=mode)
    mc.show()
    sys.exit(app.exec_())
