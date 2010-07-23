import sys,os,time
from PyQt4 import QtGui, QtCore


class QualityAssuranceDock(QtGui.QWidget):
    def __init__(self, fileList, masterChannelList, transformList, compensationList, subsetList, parent=None, subsetDefault=None, contBtnFn=None, viewAllFn=None):
        QtGui.QWidget.__init__(self,parent)

        self.setWindowTitle('Quality Assurance')
        self.masterChannelList = masterChannelList
        self.fileList = fileList
        self.transformList = transformList
        self.compensationList = compensationList

        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QVBoxLayout()
        hbox2 = QtGui.QVBoxLayout()
        hbox3 = QtGui.QVBoxLayout()

        ## message 
        viewAllBtn = QtGui.QPushButton("View All")
        viewAllBtn.setMaximumWidth(80)
        hbox2.addWidget(viewAllBtn)
        hbox2.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addLayout(hbox2)
        
        if viewAllFn != None:
            self.connect(viewAllBtn, QtCore.SIGNAL('clicked()'),viewAllFn)

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
    qad = QualityAssuranceDock(fileList,masterChannelList, transformList, compensationList, subsetList)
    qad.show()
    sys.exit(app.exec_())
