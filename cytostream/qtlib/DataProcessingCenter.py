import sys
from PyQt4 import QtGui, QtCore
import numpy as np

class DataProcessingCenter(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList, transformList, compensationList, currentAction, parent=None, checksArray=None):
        QtGui.QWidget.__init__(self,parent)

        self.setWindowTitle('Data Processing')
        self.masterChannelList = masterChannelList
        self.fileList = fileList
        self.transformList = transformList
        self.compensationList = compensationList
        self.currentAction = currentAction
        self.checksArray = checksArray
        grid = QtGui.QGridLayout()

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
        self.make_check_buttons(grid)
        self.setLayout(grid)

    def make_check_buttons(self,grid):
        self.gWidgets = {}

        for col in range(len(self.masterChannelList)):
            channel = self.masterChannelList[col]
            self.gWidgets[0] = {}
            self.gWidgets[0][col+1] = QtGui.QLabel(channel+"  ")
            self.gWidgets[0][col+1].setAlignment(QtCore.Qt.AlignCenter)
            grid.setAlignment(self.gWidgets[0][col+1],QtCore.Qt.AlignCenter)
            grid.addWidget(self.gWidgets[0][col+1],0,col+1)

            for row in range(len(self.fileList)):
                grid.setVerticalSpacing(1)
                if col == 0:
                    self.gWidgets[row+1] = {}
                    fileName = self.fileList[row]
                    self.gWidgets[row+1][0] = QtGui.QLabel(fileName)
                    grid.addWidget(self.gWidgets[row+1][0],row+1,0)
                    
                    if row == 0:
                        self.gWidgets[len(self.fileList)+1] = {}
                        self.gWidgets[len(self.fileList)+1][0] = QtGui.QLabel("select channels")
                        grid.addWidget(self.gWidgets[len(self.fileList)+1][0],len(self.fileList)+1,0)
                    
                ## channel select
                if self.currentAction in ['channel select']:
                    cBox = QtGui.QCheckBox(self)
                    self.gWidgets[row+1][col+1] = cBox
                    self.gWidgets[row+1][col+1].setFocusPolicy(QtCore.Qt.NoFocus)
                    self.gWidgets[row+1][col+1].setEnabled(False)
                    grid.addWidget(self.gWidgets[row+1][col+1],row+1,col+1)
                    grid.setAlignment(self.gWidgets[row+1][col+1],QtCore.Qt.AlignCenter)
                    self.connect(self.gWidgets[row+1][col+1], QtCore.SIGNAL('clicked()'),
                                     lambda x=(row+1,col+1): self.callback_channel_select(indices=x))                    

                    if col == 0:
                        cBox = QtGui.QCheckBox(self)
                        self.gWidgets[row+1][len(self.masterChannelList)+1] = cBox
                        self.gWidgets[row+1][len(self.masterChannelList)+1].setFocusPolicy(QtCore.Qt.NoFocus)
                        grid.addWidget(self.gWidgets[row+1][len(self.masterChannelList)+1],row+1,len(self.masterChannelList)+1)
                        grid.setAlignment(self.gWidgets[row+1][len(self.masterChannelList)+1],QtCore.Qt.AlignCenter)
                        self.connect(self.gWidgets[row+1][len(self.masterChannelList)+1], QtCore.SIGNAL('clicked()'),
                                     lambda x=(row+1,len(self.masterChannelList)+1): self.callback_channel_select(indices=x))
                   
                    if row == 0:
                        cBox = QtGui.QCheckBox(self)
                        self.gWidgets[len(self.fileList)+1][col+1] = cBox
                        self.gWidgets[len(self.fileList)+1][col+1].setFocusPolicy(QtCore.Qt.NoFocus)
                        grid.addWidget(self.gWidgets[len(self.fileList)+1][col+1],len(self.fileList)+1,col+1)
                        grid.setAlignment(self.gWidgets[len(self.fileList)+1][col+1],QtCore.Qt.AlignCenter)
                        self.connect(self.gWidgets[len(self.fileList)+1][col+1], QtCore.SIGNAL('clicked()'),
                                     lambda x=(len(self.fileList)+1,col+1): self.callback_channel_select(indices=x))

                ## transformation
                if self.currentAction in ['transformation']: 
                   
                    transformSelector = QtGui.QComboBox(self)
                    transformSelector.setMaximumWidth(150)

                    for transform in self.transformList:
                        transformSelector.addItem(transform)
            
                    self.gWidgets[row+1][col+1] = transformSelector
                    grid.addWidget(self.gWidgets[row+1][col+1],row+1,col+1)

                    if col == 0:
                        transformSelector = QtGui.QComboBox(self)
                        transformSelector.setMaximumWidth(150)

                        for transform in ["    "]+self.transformList:
                            transformSelector.addItem(transform)
            
                        self.gWidgets[row+1][len(self.masterChannelList)+1] = transformSelector
                        grid.addWidget(self.gWidgets[row+1][len(self.masterChannelList)+1],row+1,len(self.masterChannelList)+1)

                ## compensation  
                if self.currentAction in ['compensation']:
                    compsSelector = QtGui.QComboBox(self)
                    compsSelector.setMaximumWidth(150)

                    for comps in self.compensationList:
                        compsSelector.addItem(comps)
            
                    self.gWidgets[row+1][col+1] = compsSelector
                    grid.addWidget(self.gWidgets[row+1][col+1],row+1,col+1)
                    
                    if col == 0:
                        compsSelector = QtGui.QComboBox(self)
                        compsSelector.setMaximumWidth(150)
                        
                        for comps in ["    "] + self.compensationList:
                            compsSelector.addItem(comps)
            
                        self.gWidgets[row+1][len(self.masterChannelList)+1] = compsSelector
                        grid.addWidget(self.gWidgets[row+1][len(self.masterChannelList)+1],row+1,len(self.masterChannelList)+1)
                
                if col == 0 and row == 0:
                    self.gWidgets[0][0] = QtGui.QLabel("File name"+"    ")
                    self.gWidgets[0][0].setAlignment(QtCore.Qt.AlignCenter)
                    grid.setAlignment(self.gWidgets[0][0],QtCore.Qt.AlignCenter)
                    grid.addWidget(self.gWidgets[0][0],0,0)
         
                    if self.currentAction in ['transformation']:
                        self.gWidgets[0][len(self.masterChannelList)+1] = QtGui.QLabel("transform all"+"  ")
                        self.gWidgets[0][len(self.masterChannelList)+1].setAlignment(QtCore.Qt.AlignCenter)
                        grid.setAlignment(self.gWidgets[0][len(self.masterChannelList)+1],QtCore.Qt.AlignCenter)
                        grid.addWidget(self.gWidgets[0][len(self.masterChannelList)+1],0,len(self.masterChannelList)+1)
                    
                    if self.currentAction in ['compensation']:
                        self.gWidgets[0][len(self.masterChannelList)+1] = QtGui.QLabel("tompensation all"+"  ")
                        self.gWidgets[0][len(self.masterChannelList)+1].setAlignment(QtCore.Qt.AlignCenter)
                        grid.setAlignment(self.gWidgets[0][len(self.masterChannelList)+1],QtCore.Qt.AlignCenter)
                        grid.addWidget(self.gWidgets[0][len(self.masterChannelList)+1],0,len(self.masterChannelList)+1)

                    if self.currentAction in ['channel select']:
                        self.gWidgets[0][len(self.masterChannelList)+1] = QtGui.QLabel("select files"+"  ")
                        self.gWidgets[0][len(self.masterChannelList)+1].setAlignment(QtCore.Qt.AlignCenter)
                        grid.setAlignment(self.gWidgets[0][len(self.masterChannelList)+1],QtCore.Qt.AlignCenter)
                        grid.addWidget(self.gWidgets[0][len(self.masterChannelList)+1],0,len(self.masterChannelList)+1)

        ## handle the defaults
        if self.checksArray != None and self.currentAction in ['channel select']:

            for row in range(len(self.fileList)):
                for col in range(len(self.masterChannelList)):
                    if self.checksArray[row][col] == 1:
                        self.gWidgets[row+1][col+1].setChecked(True)
            
            self.select_all_channels_verify()


    def generic_callback(self):
        print "generic callback"

    def callback_channel_select(self,indices=None):
        if indices != None:
            row, col = indices
            if row == len(self.fileList)+1:
                if self.gWidgets[row][col].checkState() == 2:
                    self.select_all_channels((None,col))
                else:
                    self.unselect_all_channels((None,col))

            if col == len(self.masterChannelList)+1:
                if self.gWidgets[row][col].checkState() == 2:
                    self.select_all_channels((row,None))
                else:
                    self.unselect_all_channels((row,None))

        ## check and make sure the select all checks make sense
        self.select_all_channels_verify()

        ## for debugging
        #sc = self.get_selected_channels()
        #print sc, "\n"

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
    
