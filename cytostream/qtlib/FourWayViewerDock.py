import sys,re
from PyQt4 import QtGui, QtCore


class FourWayViewerDock(QtGui.QWidget):
    def __init__(self, fcsFileList, masterChannelList, parent=None, channelDefault=None, callBack=None):
        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.setWindowTitle('1-D Viewer')
        self.fcsFileList = fcsFileList
        self.masterChannelList = masterChannelList
        self.callBack = callBack

        ## setup layouts
        vbox = QtGui.QVBoxLayout()
        #vbox.setAlignment(QtCore.Qt.AlignCenter)
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignCenter)

        ## create checkboxes for each file
        self.chkBoxes = {}
        first = True
        for fcsFileName in self.fcsFileList:
            fcsFileName = re.sub(".\fcs","",fcsFileName)
            self.chkBoxes[fcsFileName] = QtGui.QCheckBox(fcsFileName, self)
            self.chkBoxes[fcsFileName].setFocusPolicy(QtCore.Qt.NoFocus)
            
            if first == True:
                self.chkBoxes[fcsFileName].toggle()
                first = False
           
            vbox.addWidget(self.chkBoxes[fcsFileName])
            self.connect(self.chkBoxes[fcsFileName], QtCore.SIGNAL('clicked()'),lambda x=fcsFileName: self.fcs_file_callback(fcsFileName=x))

        ## channel selector
        self.channelSelector = QtGui.QComboBox(self)
        self.channelSelector.setMaximumWidth(180)
        self.channelSelector.setMinimumWidth(180)
        
        for channel in self.masterChannelList:
            self.channelSelector.addItem(channel)
            
        hbox2.addWidget(self.channelSelector)
        hbox2.setAlignment(QtCore.Qt.AlignCenter)

        if channelDefault != None:
            if self.masterChannelL.__contains__(channelDefault):
                self.channelSelector.setCurrentIndex(self.modelsRun.index(modelDefault))
            else:
                print "ERROR: in OneDimViewerDoc - bad specified channelDefault"

        if callBack == None:
            self.connect(self.channelSelector,QtCore.SIGNAL("currentIndexChanged(int)"), self.generic_callback)
        else:
            self.connect(self.channelSelector,QtCore.SIGNAL("currentIndexChanged(int)"), self.channel_callback)

        ## finalize layout
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)
    
        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor('white'))
        self.setPalette(palette)

    def generic_callback(self):
        print 'callback does not do anything'

    def channel_callback(self):
        cInd = self.channelSelector.currentIndex()
        c = str(self.channelSelector.currentText())
        self.callBack(channel=c) 

    def fcs_file_callback(self,fcsFileName=None):
        if fcsFileName != None:
            print 'fcs callback', fcsFileName,self.fcsFileList.index(fcsFileName)

            fcsIndices = [0 for i in range(len(self.fcsFileList))]
        
            for fcsFileName in self.fcsFileList:
                if self.chkBoxes[fcsFileName].isChecked() == True:
                    fcsIndices[self.fcsFileList.index(fcsFileName)] = 1
            
            self.callBack(fcsIndices=fcsIndices)            

    def get_results_mode(self):
        return self.resultsMode

    def disable_all(self):
        self.channelSelector.setEnabled(False)

        for key in self.chkBoxes.keys():
            self.chkBoxes[key].setEnabled(False)

    def enable_all(self):
        self.channelSelector.setEnabled(True)

        for key in self.chkBoxes.keys():
            self.chkBoxes[key].setEnabled(True)

### Run the tests                                                                                                                                                       
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    masterChannelList = ['FL1-H', 'FL2-H', 'FSC-H', 'SSC-H']
    fcsFileList = ['fcsfile1', 'fcsfile2','fcsfile3']
    rn = FourWayViewerDock(fcsFileList,masterChannelList)
    rn.show()
    sys.exit(app.exec_())
