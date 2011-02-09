import sys,time,os
from PyQt4 import QtGui, QtCore
import numpy as np
from cytostream.qtlib import ProgressBar
from cytostream.qtlib.BlankPage import BlankPage
from cytostream import Logger, Model


class QualityAssuranceCenter(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList, alternateChannelList=None, alternateFileList=None,mainWindow=None, 
                 editBtnFn=None, parent=None,fontSize=11,showProgressBar=True,excludedChannels=[]):

        QtGui.QWidget.__init__(self,parent)

        ## arg variables
        self.setWindowTitle('Data Processing')
        self.fileList = fileList
        self.masterChannelList = masterChannelList
        self.alternateChannelList = alternateChannelList
        self.alternateFileList = alternateFileList
        self.mainWindow = mainWindow
        self.editBtnFn = editBtnFn
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

        ## checkbuttons
        if self.showProgressBar == False:
            self.make_channels_sheet()
            self.make_files_sheet()
            vbox.addLayout(self.hbox)
        else:
            self.init_no_file_view()
            vbox.addLayout(self.hbox)

        self.setLayout(vbox)

    def set_enable_disable(self):
        ## enable/disable buttons
        if self.showProgressBar == True and self.mainWindow !=None:
            self.nfEditBtn.setEnabled(True)
            self.mainWindow.pDock.contBtn.setEnabled(False)
            self.mainWindow.moreInfoBtn.setEnabled(False)
            self.mainWindow.fileSelector.setEnabled(False)
            self.mainWindow.pDock.enable_disable_states()
        else:
            self.mainWindow.pDock.contBtn.setEnabled(True)
            self.mainWindow.moreInfoBtn.setEnabled(True)
            self.mainWindow.fileSelector.setEnabled(True)
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
        nfLayout2a.addWidget(QtGui.QLabel('Quality Assurance'))
        nfLayout2b.addWidget(QtGui.QLabel('To browse the data images must be first created'))
        
        ## edit button
        self.nfEditBtn = QtGui.QPushButton("Edit Settings")
        self.nfEditBtn.setMaximumWidth(100)
        nfLayout3.addWidget(self.nfEditBtn)

        if self.editBtnFn == None:
            self.editBtnFn = self.generic_callback

        self.connect(self.nfEditBtn, QtCore.SIGNAL('clicked()'),self.editBtnFn)
        
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
        nfLayout1.addLayout(self.pbarLayout1)
        self.hbox.addLayout(nfLayout1)
        
    def init_progressbar(self):
        ## add progress bar if loading
        self.progressBar = ProgressBar(parent=self,buttonLabel="create",withLabel='Render images for all files in project')
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
               
    def init_qa_view(self):
        thumbDir = os.path.join(mainWindow.controller.homeDir,"figs",mainWindow.log.log['selected_file']+"_thumbs")
        
        if os.path.isdir(thumbDir) == True and len(os.listdir(thumbDir)) > 1:
            goFlag = mainWindow.display_thumbnails()

        if goFlag == False:
            print "WARNING: failed to display thumbnails not moving to results navigation"
            return False

        add_left_dock(mainWindow)
        mainWindow.mainWidget = QtGui.QWidget(mainWindow)
        mainWindow.progressBar = ProgressBar(parent=mainWindow.mainWidget,buttonLabel="Create the figures")
        mainWindow.progressBar.set_callback(mainWindow.run_progress_bar)
        hbl = QtGui.QHBoxLayout(mainWindow.mainWidget)
        hbl.addWidget(mainWindow.progressBar)
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        mainWindow.refresh_main_widget()
        add_left_dock(mainWindow)

    def generic_callback():
        print "generic callback"


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
    fileList = ['fileName1', 'fileName2']
    dpc = QualityAssuranceCenter(fileList, masterChannelList,showProgressBar=True)
    dpc.show()
    sys.exit(app.exec_())
    
