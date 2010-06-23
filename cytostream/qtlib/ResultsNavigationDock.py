import sys,os,time
from PyQt4 import QtGui, QtCore


class ResultsNavigationDock(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList, transformList, compensationList, subsetList, parent=None, subsetDefault=None, contBtnFn=None, 
                 viewAllFn=None,infoBtnFn=None):
        QtGui.QWidget.__init__(self,parent)

        self.setWindowTitle('Results Navigation')
        self.masterChannelList = masterChannelList
        self.fileList = fileList
        self.transformList = transformList
        self.compensationList = compensationList

        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QVBoxLayout()
        hbox2 = QtGui.QVBoxLayout()
        hbox3 = QtGui.QVBoxLayout()
        hbox4 = QtGui.QVBoxLayout()

        ## message 
        viewAllBtn = QtGui.QPushButton("View All")
        viewAllBtn.setMaximumWidth(80)
        hbox2.addWidget(viewAllBtn)
        hbox2.setAlignment(QtCore.Qt.AlignCenter)
        
        if viewAllFn != None:
            self.connect(viewAllBtn, QtCore.SIGNAL('clicked()'),viewAllFn)

        infoBtn = QtGui.QPushButton("Show model info", self)
        infoBtn.setMaximumWidth(180)
        infoBtn.setMinimumWidth(180)
        hbox3.addWidget(infoBtn)
        hbox3.setAlignment(QtCore.Qt.AlignCenter)
        if infoBtnFn != None:
            self.connect(infoBtn, QtCore.SIGNAL('clicked()'),infoBtnFn)

        ### cont button
        #contBtn = QtGui.QPushButton("Continue")
        #contBtn.setMaximumWidth(80)
        #hbox4.addWidget(contBtn)
        #hbox4.setAlignment(QtCore.Qt.AlignCenter)
        #vbox.addLayout(hbox4)
        #if contBtnFn != None:
        #    self.connect(contBtn, QtCore.SIGNAL('clicked()'),contBtnFn)

        ## finalize layout
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        #vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor('white'))
        self.setPalette(palette)

### Run the tests                                                                                                                                                       
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    masterChannelList = ['FL1-H', 'FL2-H', 'FSC-H', 'SSC-H']
    fileList = ['file1', 'file2']
    transformList = ['transform1', 'transform2', 'transform3']
    compensationList = ['compensation1', 'compensation2']
    subsetList = ["1e3", "1e4","5e4","All Data"]
    rn = ResultsNavigationDock(fileList,masterChannelList, transformList, compensationList, subsetList)
    rn.show()
    sys.exit(app.exec_())
