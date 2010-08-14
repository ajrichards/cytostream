import sys,re
from PyQt4 import QtGui, QtCore


class OneDimViewerDock(QtGui.QWidget):
    def __init__(self, fcsFileList, masterChannelList, parent=None, channelDefault=None, callBack=None):
        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.setWindowTitle('1-D Viewer')
        self.fcsFileList = fcsFileList
        self.masterChannelList = masterChannelList
        self.callBack = callBack


        ## setup layouts
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignBottom)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignTop)

        ## create checkboxes for each file
        self.chkBoxes = {}
        for fcsFileName in self.fcsFileList:
            fcsFileName = re.sub(".\fcs","",fcsFileName)
            self.chkBoxes[fcsFileName] = QtGui.QCheckBox(fcsFileName, self)
            self.chkBoxes[fcsFileName].setFocusPolicy(QtCore.Qt.NoFocus)
            self.chkBoxes[fcsFileName].toggle()
            vbox.addWidget(self.chkBoxes[fcsFileName])
            self.connect(self.chkBoxes[fcsFileName], QtCore.SIGNAL('clicked()'),lambda x=fcsFileName: self.generic_callback(fcsFileName=x))

        ## channel selector
        self.channelSelector = QtGui.QComboBox(self)
        self.channelSelector.setMaximumWidth(180)
        self.channelSelector.setMinimumWidth(180)
        
        for channel in self.masterChannelList:
            self.channelSelector.addItem(channel)
            hbox2.addWidget(self.channelSelector)

        if channelDefault != None:
            if self.masterChannelL.__contains__(channelDefault):
                self.channelSelectorSelector.setCurrentIndex(self.modelsRun.index(modelDefault))
            else:
                print "ERROR: in OneDimViewerDoc - bad specified channelDefault"

        if callBack == None:
            self.connect(self.channelSelector,QtCore.SIGNAL("currentIndexChanged(int)"), self.generic_callback)
        else:
            #self.connect(self.channelSelector,QtCore.SIGNAL("currentIndexChanged(int)"), self.callBack)
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

    def generic_callback(self,fcsFileName=None):
        print 'callback does not do anything'
        if fcsFileName != None:
            print fcsFileName

    def channel_callback(self):
        cInd = self.channelSelector.currentIndex()
        c = str(self.channelSelector.currentText())
        self.callBack(channel=c) 
        print 'selected', c
        #return ss, ssInd

    def update_toggle_btn(self):
        if self.resultsMode == 'components':
            self.resultsMode = 'modes'
            self.toggleBtn.setText('Show components')
            self.toggleLabel.setText('Showing modes')

        elif self.resultsMode == 'modes':
            self.resultsMode = 'components'
            self.toggleBtn.setText('Show modes')
            self.toggleLabel.setText('Showing components')

    def get_results_mode(self):
        return self.resultsMode

    def disable_all(self):
        pass
        #self.toggleLabel.setText('')
        #self.toggleBtn.setEnabled(False)
        #self.viewAllBtn.setEnabled(False)

    def enable_all(self):
        pass
        #self.toggleBtn.setEnabled(True)
        #self.viewAllBtn.setEnabled(True)
        #
        #if self.resultsMode == 'components':
        #    self.toggleLabel.setText('Showing components')
        #elif self.resultsMode == 'modes':
        #    self.toggleLabel.setText('Showing modes')

### Run the tests                                                                                                                                                       
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    masterChannelList = ['FL1-H', 'FL2-H', 'FSC-H', 'SSC-H']
    fcsFileList = ['fcsfile1', 'fcsfile2','fcsfile3']
    rn = OneDimViewerDock(fcsFileList,masterChannelList)
    rn.show()
    sys.exit(app.exec_())
