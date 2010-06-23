import sys,os,time
from PyQt4 import QtGui, QtCore


class DataProcessingCenter(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList, transformList, compensationList, parent=None):
        QtGui.QWidget.__init__(self,parent)

        #self.setWindowTitle('Data Processing')
        self.masterChannelList = masterChannelList
        self.fileList = fileList
        self.transformList = transformList
        self.compensationList = compensationList

        grid = QtGui.QGridLayout()

        pos = [(0, 0), (0, 1), (0, 2), (0, 3),
               (1, 0), (1, 1), (1, 2), (1, 3),
               (2, 0), (2, 1), (2, 2), (2, 3),
               (3, 0), (3, 1), (3, 2), (3, 3 ),
               (4, 0), (4, 1), (4, 2), (4, 3)]
        
        ## checkbuttons
        self.make_check_buttons(grid)
        self.setLayout(grid)

    def make_check_buttons(self,grid):
        gWidgets = {}

        for col in range(len(self.masterChannelList)):
            channel = self.masterChannelList[col]
            gWidgets[0] = {}
            gWidgets[0][col+1] = QtGui.QLabel(channel+"  ")
            gWidgets[0][col+1].setAlignment(QtCore.Qt.AlignCenter)
            grid.setAlignment(gWidgets[0][col+1],QtCore.Qt.AlignCenter)
            grid.addWidget(gWidgets[0][col+1],0,col+1)
            
            for row in range(len(self.fileList)):
                #print dir(grid)
                grid.setVerticalSpacing(1)
                if col == 0:
                    gWidgets[row+1] = {}
                    fileName = self.fileList[row]
                    gWidgets[row+1][0] = QtGui.QLabel(fileName)
                    grid.addWidget(gWidgets[row+1][0],row+1,0)

                cBox = QtGui.QCheckBox(self)
                gWidgets[row+1][col+1] = cBox
                grid.addWidget(gWidgets[row+1][col+1],row+1,col+1)
                grid.setAlignment(gWidgets[row+1][col+1],QtCore.Qt.AlignCenter)

                #print row, col, len(self.fileList)
                
                if col != 0:
                    continue

                # add transform    
                transformSelector = QtGui.QComboBox(self)
                transformSelector.setMaximumWidth(150)

                for transform in self.transformList:
                    transformSelector.addItem(transform)
            
                gWidgets[row+1][len(self.masterChannelList)+2] = transformSelector
                grid.addWidget(gWidgets[row+1][len(self.masterChannelList)+2],row+1,len(self.masterChannelList)+2)

                # add compensation  
                compsSelector = QtGui.QComboBox(self)
                compsSelector.setMaximumWidth(150)

                for comps in self.compensationList:
                    compsSelector.addItem(comps)
            
                gWidgets[row+1][len(self.masterChannelList)+3] = compsSelector
                grid.addWidget(gWidgets[row+1][len(self.masterChannelList)+3],row+1,len(self.masterChannelList)+3)

                if col == 0 and row == 0:
                    gWidgets[0][0] = QtGui.QLabel("File name"+"    ")
                    gWidgets[0][0].setAlignment(QtCore.Qt.AlignCenter)
                    grid.setAlignment(gWidgets[0][0],QtCore.Qt.AlignCenter)
                    grid.addWidget(gWidgets[0][0],0,0)
         

                    gWidgets[0][len(self.masterChannelList)+2] = QtGui.QLabel("Transform"+"  ")
                    gWidgets[0][len(self.masterChannelList)+2].setAlignment(QtCore.Qt.AlignCenter)
                    grid.setAlignment(gWidgets[0][len(self.masterChannelList)+2],QtCore.Qt.AlignCenter)
                    grid.addWidget(gWidgets[0][len(self.masterChannelList)+2],0,len(self.masterChannelList)+2)
                    

                    gWidgets[0][len(self.masterChannelList)+3] = QtGui.QLabel("Compensation"+"  ")
                    gWidgets[0][len(self.masterChannelList)+3].setAlignment(QtCore.Qt.AlignCenter)
                    grid.setAlignment(gWidgets[0][len(self.masterChannelList)+3],QtCore.Qt.AlignCenter)
                    grid.addWidget(gWidgets[0][len(self.masterChannelList)+3],0,len(self.masterChannelList)+3)



### Run the tests                                                                                                                                                                
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    masterChannelList = ['FL1-H', 'FL2-H', 'FSC-H', 'SSC-H']
    fileList = ['file1', 'file2']
    transformList = ['transform1', 'transform2', 'transform3']
    compensationList = ['compensation1', 'compensation2']
    dpc = DataProcessingCenter(fileList, masterChannelList, transformList, compensationList)
    dpc.show()
    sys.exit(app.exec_())
    
