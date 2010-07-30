import sys
from PyQt4 import QtGui, QtCore

class DataProcessingDock(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList, transformList, compensationList, subsetList, parent=None, subsetDefault=None, contBtnFn=None, subsetFn=None):
        QtGui.QWidget.__init__(self,parent)

        self.setWindowTitle('Data Processing')
        self.masterChannelList = masterChannelList
        self.fileList = fileList
        self.transformList = transformList
        self.compensationList = compensationList

        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QVBoxLayout()
        hbox2 = QtGui.QVBoxLayout()
        hbox3 = QtGui.QVBoxLayout()

        ## subset selector 
        hbox1.addWidget(QtGui.QLabel('Subset Selector'))
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addLayout(hbox1)

        self.subsetSelector = QtGui.QComboBox(self)
        self.subsetSelector.setMaximumWidth(150)
        for subset in subsetList:
            self.subsetSelector.addItem(subset)
        hbox2.addWidget(self.subsetSelector)
        hbox2.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addLayout(hbox2)

        if subsetDefault != None:
            if subsetList.__contains__(subsetDefault):
                self.subsetSelector.setCurrentIndex(subsetList.index(subsetDefault))
            else:
                print "ERROR: in dpd - bad specified subsetDefault"

        if subsetFn != None:
            self.connect(self.subsetSelector,QtCore.SIGNAL('activated(QString)'), subsetFn)

        ## cont button
        contBtn = QtGui.QPushButton("Continue")
        contBtn.setMaximumWidth(80)
        hbox3.addWidget(contBtn)
        hbox3.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addLayout(hbox3)

        if contBtnFn != None:
            self.connect(contBtn, QtCore.SIGNAL('clicked()'),contBtnFn)

        ## finalize layout
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor('white'))
        self.setPalette(palette)

    def get_subsample(self):
        ssInd = self.subsetSelector.currentIndex()
        ss = str(self.subsetSelector.currentText())
        return ss, ssInd

    def disable_all(self):
        pass

    def enable_all(self):
        pass


### Run the tests                                                                                                                                                       
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    masterChannelList = ['FL1-H', 'FL2-H', 'FSC-H', 'SSC-H']
    fileList = ['file1', 'file2']
    transformList = ['transform1', 'transform2', 'transform3']
    compensationList = ['compensation1', 'compensation2']
    subsetList = ["1e3", "1e4","5e4","All Data"]
    dpc = DataProcessingDock(fileList,masterChannelList, transformList, compensationList, subsetList)
    dpc.show()
    sys.exit(app.exec_())
    
