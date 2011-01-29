import sys,time
from PyQt4 import QtGui, QtCore
import numpy as np
from cytostream.qtlib import ProgressBar
from cytostream.qtlib.BlankPage import BlankPage


class DataProcessingCenter(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList, alternateChannelList=None, loadFileFn=None, editBtnFn=None, parent=None,
                 fontSize=11,mainWindow=None,showProgressBar=False):

        QtGui.QWidget.__init__(self,parent)

        ## arg variables
        self.setWindowTitle('Data Processing')
        self.fileList = fileList
        self.masterChannelList = masterChannelList
        self.alternateChannelList = alternateChannelList
        self.loadFileFn = loadFileFn
        self.editBtnFn = editBtnFn
        self.fontSize = fontSize
        self.mainWindow = mainWindow
        self.showProgressBar = showProgressBar

        ## declared variables
        self.transformList = ['log','logicle']
        self.compensationList = []
        self.allFilePaths = []
        self.progressBar = None

        ## prepare layout
        self.grid = QtGui.QGridLayout()
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignTop)
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.setAlignment(QtCore.Qt.AlignTop)

        ## verify or create alternate channel list
        if self.alternateChannelList == None:
            self.alternateChannelList = ['chan-%s'%(num) for num in range(len(self.masterChannelList))]
         
        ## checkbuttons
        if len(self.fileList) > 0:
            self.make_check_buttons()
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
        
        ## load the files
        #self.mainWindow.load_files_with_progressbar(self.mainWindow.allFilePaths, self.progressBar)
        #self.mainWindow.allFilePaths = []
        #self.mainWindow.refresh_state()
       
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

    def make_summary_sheet(self):

        ## setup layouts
        ssLayout1 = QtGui.QHBoxLayout()
        ssLayout1.setAlignment(QtCore.Qt.AlignCenter)

        ## create a data dict
        dataDict = {}
        self.colNames = ["Name", "Events", "Channels"]
        
        for fileName in self.fileList:
            if dataDict.has_key('Name') == False:
                dataDict['Name'] = [fileName]
            else:
                dataDict['Name'].append(fileName)

            if dataDict.has_key('Events') == False:
                dataDict['Events'] = ['x']
            else:
                dataDict['Events'].append('y')

            if dataDict.has_key('Channels') == False:
                dataDict['Channels'] = ['x']
            else:
                dataDict['Channels'].append('y')

        print 'datadict', dataDict

        ## get row with maximum number of elements 
        mostVals = 0
        for valList in dataDict.itervalues():
            if len(valList) > mostVals:
                mostVals = len(valList)

        model = QtGui.QStandardItemModel(mostVals,len(dataDict.keys()))

        ## populate the model
        for col in range(len(self.colNames)):
            key = self.colNames[col]
            items = dataDict[key]

            ## set the header
            model.setHeaderData(col, QtCore.Qt.Horizontal, QtCore.QVariant(key))

            ## populate the rows
            for row in range(len(items)):
                item = items[row]
                model.setData(model.index(row,col), QtCore.QVariant(item))
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

    
    def make_check_buttons(self):
        cbLayout1 = QtGui.QVBoxLayout()
        cbLayout1.setAlignment(QtCore.Qt.AlignTop)

        cbLabelLayout = QtGui.QHBoxLayout()
        cbLabelLayout.setAlignment(QtCore.Qt.AlignCenter)
        cbLabelLayout.addWidget(QtGui.QLabel('Rename and excluded channels'))
        cbLayout1.addLayout(cbLabelLayout)
        
        self.gWidgets = {}
        for row in range(len(self.masterChannelList)):
            channel = self.masterChannelList[row]

            if row == 0:
                self.gWidgets[0] = {}
                self.gWidgets[0][0] = QtGui.QLabel(' ')
                self.grid.addWidget(self.gWidgets[0][0],0,0)

                self.gWidgets[row+1] = {}
                self.gWidgets[row+1][0] = QtGui.QLabel("Original ID")
                self.grid.addWidget(self.gWidgets[row+1][0],row+1,0)

                self.gWidgets[row+1][1] = QtGui.QLabel("Alternate ID")
                self.grid.addWidget(self.gWidgets[row+1][1],row+1,1)

                self.gWidgets[row+1][1] = QtGui.QLabel("Exclude")
                self.grid.addWidget(self.gWidgets[row+1][1],row+1,2)
                self.grid.setAlignment(self.gWidgets[row+1][1],QtCore.Qt.AlignCenter)

            self.gWidgets[row+2] = {}
            self.gWidgets[row+2][0] = QtGui.QLabel(channel)
            self.grid.addWidget(self.gWidgets[row+2][0],row+2,0)

            self.gWidgets[row+2][1] = QtGui.QLabel(self.alternateChannelList[row])
            self.grid.addWidget(self.gWidgets[row+2][1],row+2,1)

            cBox = QtGui.QCheckBox(self)
            self.gWidgets[row+2][2] = cBox
            self.grid.addWidget(self.gWidgets[row+2][2],row+2,2)
            self.grid.setAlignment(self.gWidgets[row+2][2],QtCore.Qt.AlignCenter)

            #self.gWidgets[0] = {}
            #self.gWidgets[0][col+1] = QtGui.QLabel(channel+"  ")
            #self.gWidgets[0][col+1].setAlignment(QtCore.Qt.AlignCenter)
            #grid.setAlignment(self.gWidgets[0][col+1],QtCore.Qt.AlignCenter)
            #grid.addWidget(self.gWidgets[0][col+1],0,col+1)
            #grid.setVerticalSpacing(1)
            #row = 0
                    
            #cBox = QtGui.QCheckBox(self)
            #self.gWidgets[row+1][col+1] = cBox
            ##self.gWidgets[row+1][col+1].setFocusPolicy(QtCore.Qt.NoFocus)
            #grid.addWidget(self.gWidgets[row+1][col+1],row+1,col+1)
            #grid.setAlignment(self.gWidgets[row+1][col+1],QtCore.Qt.AlignCenter)
            #self.connect(self.gWidgets[row+1][col+1], QtCore.SIGNAL('clicked()'),
            #             lambda x=(row+1,col+1): self.callback_channel_select(indices=x))

        ## add refresh and revert buttons
        hbox = QtGui.QHBoxLayout()
        self.refreshBtn = QtGui.QPushButton("Refresh")
        self.refreshBtn.setMaximumWidth(100)
        hbox.addWidget(self.refreshBtn)

        self.revertBtn = QtGui.QPushButton("Revert")
        self.revertBtn.setMaximumWidth(100)
        hbox.addWidget(self.revertBtn)

        self.renameBtn = QtGui.QPushButton("Rename")
        self.renameBtn.setMaximumWidth(100)
        hbox.addWidget(self.renameBtn)

        cbLayout1.addLayout(hbox)
        cbLayout1.addLayout(self.grid)
        self.hbox.addLayout(cbLayout1)    

    def generic_callback(self):
        print "generic callback"

    def callback_channel_select(self,indices=None):
        print 'callback for channel select'

        if indices != None:
            print indices

    def set_alternate_labels(self):
        print 'setting alternate labels'

    def select_all_channels(self,indices):
        row, col = indices
        
        if row != None:
            for i in range(len(self.masterChannelList)):
                self.gWidgets[row][i+1].setChecked(True)
        if col != None:
            for j in range(len(self.fileList)):
                self.gWidgets[j+1][col].setChecked(True)

    def unselect_all_channels(self,indices):
        row, col = indices
                            
        if row != None:
            for i in range(len(self.masterChannelList)):
                self.gWidgets[row][i+1].setChecked(False)
        if col != None:
            for j in range(len(self.fileList)):
                self.gWidgets[j+1][col].setChecked(False)

    def select_all_channels_verify(self):
        ## check the columns
        for col in range(len(self.masterChannelList)):
            allChecked = True
            for i in range(len(self.fileList)):
                if self.gWidgets[i+1][col+1].checkState() == 0:
                    allChecked = False
            self.gWidgets[len(self.fileList)+1][col+1].setChecked(allChecked)
       
        ## check the rows 
        for row in range(len(self.fileList)):
            allChecked = True
            for j in range(len(self.masterChannelList)):
                if self.gWidgets[row+1][j+1].checkState() == 0:
                    allChecked = False
            self.gWidgets[row+1][len(self.masterChannelList)+1].setChecked(allChecked)

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
    app = QtGui.QApplication(sys.argv)
    masterChannelList = ['FL1-H', 'FL2-H', 'FSC-H', 'SSC-H']
    fileList = [] #['file1', 'file2']
    dpc = DataProcessingCenter(fileList, masterChannelList)
    dpc.show()
    sys.exit(app.exec_())
    
