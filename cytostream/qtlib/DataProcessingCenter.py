import sys,time,os
from PyQt4 import QtGui, QtCore
import numpy as np
from cytostream.qtlib import ProgressBar
from cytostream.qtlib.BlankPage import BlankPage
from cytostream import Logger, Model


class DataProcessingCenter(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList, alternateChannelList=None, alternateFileList=None,mainWindow=None, loadFileFn=None, 
                 editBtnFn=None, parent=None,fontSize=11,showProgressBar=False,excludedChannels=[]):

        QtGui.QWidget.__init__(self,parent)

        ## arg variables
        self.setWindowTitle('Data Processing')
        self.fileList = fileList
        self.masterChannelList = masterChannelList
        self.alternateChannelList = alternateChannelList
        self.alternateFileList = alternateFileList
        self.mainWindow = mainWindow
        self.loadFileFn = loadFileFn
        self.editBtnFn = editBtnFn
        self.fontSize = fontSize
        self.showProgressBar = showProgressBar
        self.excludedChannels = [int(chan) for chan in excludedChannels]

        ## declared variables
        self.transformList = ['log','logicle']
        self.compensationList = []
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

        ## checkbuttons
        if len(self.fileList) > 0:
            self.make_channels_sheet()
            self.make_files_sheet()
            vbox.addLayout(self.hbox)
        else:
            self.init_no_file_view()
            vbox.addLayout(self.hbox)

        self.setLayout(vbox)

        ## save the initial results for alternate channels and files
        self.channels_save_callback()
        self.files_save_callback()

    def set_enable_disable(self):
        ## enable/disable buttons
        if self.showProgressBar == True and self.mainWindow !=None:
            self.nfLoadBtn.setEnabled(False)
            self.nfEditBtn.setEnabled(True)
            self.mainWindow.pDock.contBtn.setEnabled(False)
            self.mainWindow.moreInfoBtn.setEnabled(False)
            self.mainWindow.subsetSelector.setEnabled(False)
            self.mainWindow.pDock.inactivate_all()
        elif len(self.fileList) == 0 and self.mainWindow !=None:
            self.nfLoadBtn.setEnabled(True)
            self.nfEditBtn.setEnabled(True)
            self.mainWindow.pDock.contBtn.setEnabled(False)
            self.mainWindow.moreInfoBtn.setEnabled(False)
            self.mainWindow.subsetSelector.setEnabled(False)
            self.mainWindow.pDock.inactivate_all()
        else:
            self.mainWindow.pDock.contBtn.setEnabled(True)
            self.mainWindow.moreInfoBtn.setEnabled(True)
            self.mainWindow.subsetSelector.setEnabled(True)
            self.mainWindow.pDock.enable_disable_states()

    def init_no_file_view(self):
        nfLayout1 = QtGui.QVBoxLayout()
        nfLayout1.setAlignment(QtCore.Qt.AlignTop)
        nfLayout2 = QtGui.QVBoxLayout()
        nfLayout2.setAlignment(QtCore.Qt.AlignCenter)
        nfLayout2a = QtGui.QHBoxLayout()
        nfLayout2a.setAlignment(QtCore.Qt.AlignCenter)
        nfLayout2b = QtGui.QHBoxLayout()
        nfLayout2b.setAlignment(QtCore.Qt.AlignCenter)        
        nfLayout3 = QtGui.QHBoxLayout()
        nfLayout3.setAlignment(QtCore.Qt.AlignCenter) 
        nfLayout4 = QtGui.QHBoxLayout()
        nfLayout4.setAlignment(QtCore.Qt.AlignCenter)
        
        ## label widget 
        nfLayout2a.addWidget(QtGui.QLabel('Welcome to cytostream'))
        
        if self.showProgressBar == False:
            nfLayout2b.addWidget(QtGui.QLabel('To begin a project load your file(s)'))
        else:
            nfLayout2b.addWidget(QtGui.QLabel('File compensation and transformation'))

        ## button widgets
        self.nfLoadBtn = QtGui.QPushButton("Load Files")
        self.nfLoadBtn.setMaximumWidth(100)
        nfLayout3.addWidget(self.nfLoadBtn)
        if self.loadFileFn == None:
            self.connect(self.nfLoadBtn, QtCore.SIGNAL('clicked()'),self.generic_callback)
        else:
            self.connect(self.nfLoadBtn, QtCore.SIGNAL('clicked()'),self.load_data_files)

        self.nfEditBtn = QtGui.QPushButton("Edit Settings")
        self.nfEditBtn.setMaximumWidth(100)
        nfLayout3.addWidget(self.nfEditBtn)

        if self.editBtnFn == None:
            self.editBtnFn = self.generic_callback

        self.connect(self.nfEditBtn, QtCore.SIGNAL('clicked()'),self.editBtnFn)
        
        ## show files to be loaded ici
        if self.showProgressBar == True and self.mainWindow!=None:
            nfLayout4.addWidget(QtGui.QLabel('\t\t\t'))
            self.modelLoad = QtGui.QStandardItemModel()

            for p in range(len(self.mainWindow.allFilePaths)):
                fullPath = self.mainWindow.allFilePaths[p]
                fileName = os.path.split(fullPath)[-1]
                item0 = QtGui.QStandardItem(str(p+1))
                item1 = QtGui.QStandardItem('%s'%fileName)

                ## populate model
                item0.setEditable(False)
                item1.setEditable(False)
                self.modelLoad.appendRow([item0,item1])
            
            self.modelLoad.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant('#'))
            self.modelLoad.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignLeft),QtCore.Qt.TextAlignmentRole)
            self.modelLoad.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant('files to load'))
            self.modelLoad.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignLeft),QtCore.Qt.TextAlignmentRole)

            viewLoad = QtGui.QTreeView()
            viewLoad.setModel(self.modelLoad)
            nfLayout4.addWidget(viewLoad)
            nfLayout4.addWidget(QtGui.QLabel('\t\t\t'))

            ## show the progress bar
            self.init_progressbar()

        ## finalize layout
        nfLayout2.addLayout(nfLayout2a)
        nfLayout2.addLayout(nfLayout2b)
        nfLayout1.addLayout(nfLayout2)
        nfLayout1.addLayout(nfLayout3)
        nfLayout1.addWidget(QtGui.QLabel('\t\t\t'))
        nfLayout1.addWidget(QtGui.QLabel('\t\t\t'))
        nfLayout1.addLayout(nfLayout4)
        if self.progressBar != None:
            nfLayout1.addLayout(self.pbarLayout1)
        self.hbox.addLayout(nfLayout1)
        
    def init_progressbar(self):
        ## add progress bar if loading
        self.progressBar = ProgressBar(parent=self,buttonLabel="proceed",withLabel='load files into project')
        if self.mainWindow != None:
            self.progressBar.set_callback(lambda x=self.progressBar: self.mainWindow.load_files_with_progressbar(x))

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
               
    def load_data_files(self):
        self.mainWindow.allFilePaths = [str(pathName) for pathName in self.loadFileFn()]
        self.mainWindow.mainWidget = QtGui.QWidget(self)
        bp = BlankPage(parent=self.mainWindow.mainWidget)
        vbl = QtGui.QVBoxLayout()
        vbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        hbl.addWidget(bp)
        vbl.addLayout(hbl)
        self.mainWindow.mainWidget.setLayout(vbl)
        self.mainWindow.refresh_main_widget()
        self.mainWindow.refresh_state()

    def generic_callback():
        print "generic callback"

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
            altChannel = self.alternateChannelList[row]
            item0 = QtGui.QStandardItem(str(row+1))
            item1 = QtGui.QStandardItem('%s' % channel)
            item2 = QtGui.QStandardItem('%s' % altChannel)

            ## set which ones are checked
            check = QtCore.Qt.Unchecked if row in self.excludedChannels else QtCore.Qt.Checked
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

    def make_files_sheet(self, firstRun=True):
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

        self.fileSummaryLabel = QtGui.QLabel('Select files for removal and edit labels')

        ## create the file list panel
        if firstRun == True:
            self.modelFiles = QtGui.QStandardItemModel()
        
        for row in range(len(self.fileList)):
            fileName = self.fileList[row]
            altFileName = self.alternateFileList[row]
            item1 = QtGui.QStandardItem(str(row+1))
            item2 = QtGui.QStandardItem('%s'%fileName)
            item3 = QtGui.QStandardItem('%s'%altFileName)
            item4 = QtGui.QStandardItem('%s'%self.get_num_channels(fileName))
            item5 = QtGui.QStandardItem('%s'%self.get_num_events(fileName))
            
            ## set which ones are checked
            check = QtCore.Qt.Unchecked
            item1.setCheckState(check)
            item1.setCheckable(True)
            item1.setEditable(False)
            item2.setEditable(False)
            item3.setEditable(True)
            item4.setEditable(False)
            item4.setEditable(False)
            self.modelFiles.appendRow([item1,item2,item3,item4,item5])

        ## setup the header
        self.modelFiles.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant('file'))
        self.modelFiles.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelFiles.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant('original'))
        self.modelFiles.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelFiles.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant('alternate'))
        self.modelFiles.setHeaderData(2, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelFiles.setHeaderData(3, QtCore.Qt.Horizontal, QtCore.QVariant('channels'))
        self.modelFiles.setHeaderData(3, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)
        self.modelFiles.setHeaderData(4, QtCore.Qt.Horizontal, QtCore.QVariant('events'))
        self.modelFiles.setHeaderData(4, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignCenter),QtCore.Qt.TextAlignmentRole)

        viewFiles = QtGui.QTreeView()
        viewFiles.setModel(self.modelFiles)

        ## setup save btn
        if firstRun == True:
            self.saveFilesBtn = QtGui.QPushButton("save changes")
            self.saveFilesBtn.setMaximumWidth(100)
            self.connect(self.saveFilesBtn, QtCore.SIGNAL('clicked()'),self.files_save_callback)
                
            self.addFileBtn = QtGui.QPushButton("add")
            self.addFileBtn.setMaximumWidth(100)
            self.connect(self.addFileBtn, QtCore.SIGNAL('clicked()'),self.files_add_callback)

            self.removeFileBtn = QtGui.QPushButton("remove")
            self.removeFileBtn.setMaximumWidth(100)
            self.connect(self.removeFileBtn, QtCore.SIGNAL('clicked()'),self.files_remove_callback)

        ## finalize layout
        if firstRun == True:
            ssLayout1.addWidget(self.fileSummaryLabel)
            ssLayout2.addWidget(viewFiles)
            ssLayout3.addWidget(self.saveFilesBtn)
            ssLayout3.addWidget(self.addFileBtn)
            ssLayout3.addWidget(self.removeFileBtn)
            ssLayout.addLayout(ssLayout1)
            ssLayout.addLayout(ssLayout2)
            ssLayout.addLayout(ssLayout3)
            self.hbox.addLayout(ssLayout)

    def generic_callback(self):
        print "generic callback"

    def channels_save_callback(self):
        ''' 
        saves alternate channel names
        saves excluded channels for quality assurance

        '''

        print 'channels save'

        n = len(self.masterChannelList)
        altLabels = [str(self.modelChannels.data(self.modelChannels.index(i,2)).toString()) for i in range(n)]
        checkStates = [self.modelChannels.itemFromIndex(self.modelChannels.index(i,0)).checkState() for i in range(n)]
        excludedChannels = np.where(np.array([i for i in checkStates]) == 0)[0].tolist()

        if self.log != None:
            self.log.log['alternate_channel_labels'] = altLabels
            self.log.log['excluded_channels_qa'] = excludedChannels
            self.controller.save()
        
        #print 'alternate channels', altLabels
        #print 'excluded channels', excludedChannels

    def files_add_callback(self):
        print 'should be adding files'
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
            print '\tincluded files', includedIndices

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
            
    def get_num_events(self,fileName):
        '''
        fetch the number of events in a file

        '''

        if self.log != None:
            events = self.controller.model.get_events(fileName,subsample='original')
            return len(events)
        else:
            return 'na'

    def get_num_channels(self,fileName):
        '''
        fetch the numbe of channels in a file

        '''

        if self.log != None:
            fileChannels = self.controller.model.get_file_channel_list(fileName)
            return len(fileChannels)
        else:
            return 'na'
                  
### Run the tests                                                            
if __name__ == '__main__':
    ''' 
    Note: to show the opening screen set fileList = [] 
          otherwise use fileList = ['3FITC_4PE_004']
    
    '''
    
    app = QtGui.QApplication(sys.argv)
    masterChannelList = ['FL1-H', 'FL2-H', 'FSC-H', 'SSC-H']
    fileList = ['file1','file2','file3']
    dpc = DataProcessingCenter(fileList, masterChannelList)
    dpc.show()
    sys.exit(app.exec_())
    
