import sys,time,os
from PyQt4 import QtGui, QtCore
import numpy as np
from cytostream.qtlib import ProgressBar
from cytostream.qtlib.BlankPage import BlankPage
from cytostream import Logger, Model


class DataProcessingCenter(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList, alternateChannelList=None, mainWindow=None, loadFileFn=None, editBtnFn=None, parent=None,
                 fontSize=11,showProgressBar=False,excludedChannels=[]):

        QtGui.QWidget.__init__(self,parent)

        ## arg variables
        self.setWindowTitle('Data Processing')
        self.fileList = fileList
        self.masterChannelList = masterChannelList
        self.alternateChannelList = alternateChannelList
        self.mainWindow = mainWindow
        self.loadFileFn = loadFileFn
        self.editBtnFn = editBtnFn
        self.fontSize = fontSize
        self.showProgressBar = showProgressBar
        self.excludedChannels = [int(chan) for chan in excludedChannels]

        ## declared variables
        self.transformList = ['log','logicle']
        self.compensationList = []
        self.allFilePaths = []
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
         
        ## checkbuttons
        if len(self.fileList) > 0:
            self.make_data_dict()
            self.make_channels_sheet()
            self.make_summary_sheet()
            vbox.addLayout(self.hbox)
        else:
            self.init_no_file_view()
            vbox.addLayout(self.hbox)

        self.setLayout(vbox)

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
        
        ## label widget 
        nfLayout2a.addWidget(QtGui.QLabel('Welcome to cytostream'))
        nfLayout2b.addWidget(QtGui.QLabel('To begin a project load your file(s)'))

        ## button widgets
        self.nfLoadBtn = QtGui.QPushButton("Load Files")
        self.nfLoadBtn.setMaximumWidth(100)
        nfLayout3.addWidget(self.nfLoadBtn)
        if self.loadFileFn == None:
            self.connect(self.nfLoadBtn, QtCore.SIGNAL('clicked()'),self.generic_callback)
        else:
            self.connect(self.nfLoadBtn, QtCore.SIGNAL('clicked()'),self.load_data_files)

        if self.showProgressBar == True:
            self.nfLoadBtn.setEnabled(False)

        self.nfEditBtn = QtGui.QPushButton("Edit Settings")
        self.nfEditBtn.setMaximumWidth(100)
        nfLayout3.addWidget(self.nfEditBtn)

        if self.editBtnFn == None:
            self.editBtnFn = self.generic_callback

        self.connect(self.nfEditBtn, QtCore.SIGNAL('clicked()'),self.editBtnFn)
        
        if self.showProgressBar == True:
            self.init_progressbar()

        ## finalize layout
        nfLayout2.addLayout(nfLayout2a)
        nfLayout2.addLayout(nfLayout2b)
        nfLayout1.addLayout(nfLayout2)
        nfLayout1.addLayout(nfLayout3)
        if self.progressBar != None:
            nfLayout1.addLayout(self.pbarLayout1)
        self.hbox.addLayout(nfLayout1)
    
    def init_progressbar(self):
        ## add progress bar if loading
        self.progressLabel = QtGui.QLabel('Carry out transformation and compensation')
        self.progressBar = ProgressBar(parent=self,buttonLabel="proceed")
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
        pbarLayout1a.addWidget(self.progressLabel)
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
        model1 = QtGui.QStandardItemModel()

        for row in range(len(self.masterChannelList)):
            channel = self.masterChannelList[row]
            item1 = QtGui.QStandardItem('%s' % channel)
            altChannel = self.alternateChannelList[row]

            ## set which ones are checked
            check = QtCore.Qt.Unchecked if row in self.excludedChannels else QtCore.Qt.Checked
            item1.setCheckState(check)
            item1.setCheckable(True)
            item1.setEditable(False)
            model1.appendRow(item1)
            
        self.view1 = QtGui.QListView()
        self.view1.setModel(model1)

        ## create the alternate channel list panel
        self.model2 = QtGui.QStandardItemModel()

        for row in range(len(self.masterChannelList)):
            channel = self.alternateChannelList[row]
            item2 = QtGui.QStandardItem('%s' % channel)
            altChannel = self.alternateChannelList[row]

            ## set which ones are checked
            check = QtCore.Qt.Unchecked
            item2.setCheckState(check)
            item2.setCheckable(False)
            item2.setEditable(True)
            self.model2.appendRow(item2)

        self.view2 = QtGui.QListView()
        self.view2.setModel(self.model2)

        ## setup save btn
        self.saveBtn = QtGui.QPushButton("Save labels")
        self.saveBtn.setMaximumWidth(100)
        self.connect(self.saveBtn, QtCore.SIGNAL('clicked()'),self.set_alternate_labels)

        ## finalize layouts
        ssLayout1.addWidget(self.chksSummaryLabel)
        ssLayout3.addWidget(self.saveBtn)
        ssLayout2.addWidget(self.view1)
        ssLayout2.addWidget(self.view2)
        ssLayout.addLayout(ssLayout1)
        ssLayout.addLayout(ssLayout2)
        ssLayout.addLayout(ssLayout3)
        self.hbox.addLayout(ssLayout)

    def make_data_dict(self):
        ## create a data dict
        self.dataDict = {}
        self.colNames = ["Name", "Events", "Channels"]
        
        for fileName in self.fileList:
            if self.dataDict.has_key('Name') == False:
                self.dataDict['Name'] = [fileName]
            else:
                self.dataDict['Name'].append(fileName)

            if self.dataDict.has_key('Events') == False:
                self.dataDict['Events'] = [self.get_num_events(fileName)]
            else:
                self.dataDict['Events'].append(self.get_num_events(fileName))

            if self.dataDict.has_key('Channels') == False:
                self.dataDict['Channels'] = [self.get_num_channels(fileName)]
            else:
                self.dataDict['Channels'].append(self.get_num_channels(fileName))

    def make_summary_sheet(self):
        ## setup layouts
        ssLayout1 = QtGui.QHBoxLayout()
        ssLayout1.setAlignment(QtCore.Qt.AlignCenter)

        ## get row with maximum number of elements 
        mostVals = 0
        for valList in self.dataDict.itervalues():
            if len(valList) > mostVals:
                mostVals = len(valList)

        model = QtGui.QStandardItemModel(mostVals,len(self.dataDict.keys()))

        ## populate the model
        for col in range(len(self.colNames)):
            key = self.colNames[col]
            items = self.dataDict[key]

            ## set the header
            model.setHeaderData(col, QtCore.Qt.Horizontal, QtCore.QVariant(key))

            ## populate the rows
            for row in range(len(items)):
                item = QtCore.QVariant(items[row])

                #item.setCheckable(True)
                #item.setEditable(False)
                model.setData(model.index(row,col),item)
                font = QtGui.QFont()
                font.setPointSize(self.fontSize)
                #font.setBold(True)
                model.setData(model.index(row,col), QtCore.QVariant(font), QtCore.Qt.FontRole)

        tree = QtGui.QTreeView()
        tree.setModel(model)
        #table = QtGui.QTableView()
        #table.setModel(model)

        ## finalize layout                                                                               
        ssLayout1.addWidget(tree)
        self.hbox.addLayout(ssLayout1)

    def generic_callback(self):
        print "generic callback"

    def set_alternate_labels(self):
        n = len(self.masterChannelList)
        altLabels = [str(self.model2.data(self.model2.index(i,0)).toString()) for i in range(n)]

        if self.log != None:
            self.log.log['alternate_channel_labels'] = altLabels
            self.controller.save()
        else:
            print altLabels


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
                  
    ## getter for external access to channel states
    def get_selected_channels(self):
        checkedBoxes = np.zeros((len(self.fileList),len(self.masterChannelList)))
        
        for row in range(len(self.fileList)):
            for col in range(len(self.masterChannelList)):
                if self.gWidgets[row+1][col+1].checkState() == 2:
                    checkedBoxes[row][col] = 1

        return checkedBoxes

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
    
