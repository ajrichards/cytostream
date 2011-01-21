import sys
from PyQt4 import QtGui, QtCore
import numpy as np

class DataProcessingCenter(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList, transformList, compensationList, currentAction, alternateChannelList = None, parent=None, checksArray=None,fontSize=11):
        QtGui.QWidget.__init__(self,parent)

        self.setWindowTitle('Data Processing')
        self.masterChannelList = masterChannelList
        self.alternateChannelList = alternateChannelList
        self.fileList = fileList
        self.transformList = transformList
        self.compensationList = compensationList
        self.currentAction = currentAction
        self.checksArray = checksArray
        self.fontSize = fontSize
        grid = QtGui.QGridLayout()

        ## verify or create alternate channel list
        if self.alternateChannelList == None:
            self.alternateChannelList = ['chan-%s'%(num) for num in range(len(self.masterChannelList))]
        
        ## prepare layout
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignTop)
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.setAlignment(QtCore.Qt.AlignTop)

        ## error checking
        if self.currentAction not in ['editor','channel select', 'transformation', 'compensation','add remove']:
            print "ERROR: invalid action specified in data processing center", self.currentAction
        
        if self.checksArray != None and type(self.checksArray) != type(np.array([])):
            print "ERROR: checksArray must be np.array not", type(self.checksArray)
            return None
    
        if self.checksArray != None and type(self.checksArray) == type(np.array([])):
            rows, cols = np.shape(self.checksArray)
            if rows != len(self.fileList) or cols != len(self.masterChannelList):
                print "ERROR: dimension mismatch", (len(self.fileList), len(self.masterChannelList)), (rows,cols)
                return None

        ## checkbuttons
        self.make_check_buttons(grid,self.hbox)
        self.make_chan_files_sheet(self.hbox)
        vbox.addLayout(self.hbox)
        self.setLayout(vbox)

    def make_chan_files_sheet(self,box):

        ## create a data dict
        dataDict = {}
        self.colNames = ["Name", "Events", "Channels"]
        
        for fileName in self.fileList:
            if dataDict.has_key('File name') == False:
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

        hbox = QtGui.QHBoxLayout()
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

        #tree = QtGui.QTreeView()
        #tree.setModel(model)
        table = QtGui.QTableView()
        table.setModel(model)

        ## finalize layout                                                                               
        hbox.addWidget(table)
        hbox.setAlignment(QtCore.Qt.AlignCenter)
        box.addLayout(hbox)

    def make_check_buttons(self,grid,box):
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignTop)

        hboxLabel = QtGui.QHBoxLayout()
        hboxLabel.setAlignment(QtCore.Qt.AlignCenter)
        hboxLabel.addWidget(QtGui.QLabel('Rename and excluded channels'))
        vbox.addLayout(hboxLabel)
        
        self.gWidgets = {}
        for row in range(len(self.masterChannelList)):
            channel = self.masterChannelList[row]

            if row == 0:
                self.gWidgets[0] = {}
                self.gWidgets[0][0] = QtGui.QLabel(' ')
                grid.addWidget(self.gWidgets[0][0],0,0)

                self.gWidgets[row+1] = {}
                self.gWidgets[row+1][0] = QtGui.QLabel("Original ID")
                grid.addWidget(self.gWidgets[row+1][0],row+1,0)

                self.gWidgets[row+1][1] = QtGui.QLabel("Alternate ID")
                grid.addWidget(self.gWidgets[row+1][1],row+1,1)

                self.gWidgets[row+1][1] = QtGui.QLabel("Exclude")
                grid.addWidget(self.gWidgets[row+1][1],row+1,2)
                grid.setAlignment(self.gWidgets[row+1][1],QtCore.Qt.AlignCenter)

            self.gWidgets[row+2] = {}
            self.gWidgets[row+2][0] = QtGui.QLabel(channel)
            grid.addWidget(self.gWidgets[row+2][0],row+2,0)

            self.gWidgets[row+2][1] = QtGui.QLabel(self.alternateChannelList[row])
            grid.addWidget(self.gWidgets[row+2][1],row+2,1)

            cBox = QtGui.QCheckBox(self)
            self.gWidgets[row+2][2] = cBox
            grid.addWidget(self.gWidgets[row+2][2],row+2,2)
            grid.setAlignment(self.gWidgets[row+2][2],QtCore.Qt.AlignCenter)


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

        vbox.addLayout(hbox)

        vbox.addLayout(grid)
        box.addLayout(vbox)
        

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
    fileList = ['file1', 'file2']
    transformList = ['transform1', 'transform2', 'transform3']
    compensationList = ['compensation1', 'compensation2']
    checksArray = np.array([[1,1,1,1],[0,0,0,0]])
    #['editor','channel select', 'transformation', 'compensation','add remove']:
    currentAction = 'channel select'
    dpc = DataProcessingCenter(fileList, masterChannelList, transformList, compensationList, currentAction,checksArray=checksArray)
    dpc.show()
    sys.exit(app.exec_())
    
