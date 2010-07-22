import sys,os,time
from PyQt4 import QtGui, QtCore


class ResultsNavigationDock(QtGui.QWidget):
    def __init__(self, resultsModeList, masterChannelList, parent=None, resultsModeDefault=None, resultsModeFn=None, 
                 viewAllFn=None,infoBtnFn=None):
        QtGui.QWidget.__init__(self,parent)

        self.setWindowTitle('Results Navigation')
        self.masterChannelList = masterChannelList

        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QVBoxLayout()
        hbox2 = QtGui.QVBoxLayout()
        hbox3 = QtGui.QVBoxLayout()

        ## results mode selector      
        hbox1.addWidget(QtGui.QLabel('Results Mode Selector'))
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        self.resultsModeSelector = QtGui.QComboBox(self)
        self.resultsModeSelector.setMaximumWidth(150)
        for resultsMode in resultsModeList:
            self.resultsModeSelector.addItem(resultsMode)

        hbox1.addWidget(self.resultsModeSelector)
        hbox1.setAlignment(QtCore.Qt.AlignCenter)

        if resultsModeDefault != None:
            if resultsModeList.__contains__(resultsModeDefault):
                self.resultsModeSelector.setCurrentIndex(resultsModeList.index(resultsModeDefault))
            else:
                print "ERROR: in results mode selector - bad specified resultsModeDefault"

        if resultsModeFn == None:
            resultsModeFn = self.generic_callback
        self.connect(self.resultsModeSelector, QtCore.SIGNAL("currentIndexChanged(int)"), resultsModeFn)
        
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
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor('white'))
        self.setPalette(palette)

    def get_selected_results_mode(self):
        rmInd = self.resultsModeSelector.currentIndex()
        rm = str(self.resultsModeSelector.currentText())

        return rm, rmInd

    def generic_callback(self):
        print 'callback does not do anything yet'


### Run the tests                                                                                                                                                       
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    masterChannelList = ['FL1-H', 'FL2-H', 'FSC-H', 'SSC-H']
    resultsModeList = ['results mode 1', 'results mode 2']
    rn = ResultsNavigationDock(resultsModeList,masterChannelList)
    rn.show()
    sys.exit(app.exec_())
