import sys
from PyQt4 import QtGui, QtCore


class ResultsNavigationDock(QtGui.QWidget):
    def __init__(self, resultsModeList, masterChannelList, parent=None, resultsModeDefault=None, resultsModeFn=None, 
                 viewAllFn=None,infoBtnFn=None):
        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.setWindowTitle('Results Navigation')
        self.masterChannelList = masterChannelList
        self.resultsMode = 'components'

        ## setup layouts
        vbox = QtGui.QVBoxLayout()
        hbox0 = QtGui.QHBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        hbox3 = QtGui.QHBoxLayout()

        ## mode/component toggle button
        hbox0.setAlignment(QtCore.Qt.AlignCenter)
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        self.toggleLabel = QtGui.QLabel('Showing components')
        hbox0.addWidget(self.toggleLabel)
        self.toggleBtn = QtGui.QPushButton("Show modes",self)
        self.toggleBtn.setMaximumWidth(150)
        self.toggleBtn.setMinimumWidth(150)
        hbox1.addWidget(self.toggleBtn)

        if resultsModeFn == None:
            resultsModeFn = self.generic_callback

        self.connect(self.toggleBtn, QtCore.SIGNAL('clicked()'),self.update_toggle_btn)
        self.connect(self.toggleBtn, QtCore.SIGNAL('clicked()'), resultsModeFn)

        ## view all btn 
        self.viewAllBtn = QtGui.QPushButton("View All",self)
        self.viewAllBtn.setMaximumWidth(150)
        self.viewAllBtn.setMinimumWidth(150)
        hbox2.addWidget(self.viewAllBtn)
        hbox2.setAlignment(QtCore.Qt.AlignCenter)
        
        if viewAllFn != None:
            self.connect(self.viewAllBtn, QtCore.SIGNAL('clicked()'),viewAllFn)

        ## info button
        infoBtn = QtGui.QPushButton("Show model info", self)
        infoBtn.setMaximumWidth(150)
        infoBtn.setMinimumWidth(150)
        hbox3.addWidget(infoBtn)
        hbox3.setAlignment(QtCore.Qt.AlignCenter)
        if infoBtnFn != None:
            self.connect(infoBtn, QtCore.SIGNAL('clicked()'),infoBtnFn)

        ## finalize layout
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addLayout(hbox0)
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
        print 'callback does not do anything'

    def update_toggle_btn(self):
        if self.resultsMode == 'components':
            self.resultsMode = 'modes'
            self.toggleBtn.setText('Show components')
            self.toggleLabel.setText('Showing modes')

        elif self.resultsMode == 'modes':
            self.resultsMode = 'components'
            self.toggleBtn.setText('Show modes')
            self.toggleLabel.setText('Showing components')

        print 'should be updating toggle btn'

    def get_results_mode(self):
        return self.resultsMode

    def disable_all(self):
        self.toggleLabel.setText('')
        self.toggleBtn.setEnabled(False)
        self.viewAllBtn.setEnabled(False)

    def enable_all(self):
        self.toggleBtn.setEnabled(True)
        self.viewAllBtn.setEnabled(True)

        if self.resultsMode == 'components':
            self.toggleLabel.setText('Showing components')
        elif self.resultsMode == 'modes':
            self.toggleLabel.setText('Showing modes')

### Run the tests                                                                                                                                                       
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    masterChannelList = ['FL1-H', 'FL2-H', 'FSC-H', 'SSC-H']
    resultsModeList = ['results mode 1', 'results mode 2']
    rn = ResultsNavigationDock(resultsModeList,masterChannelList)
    rn.show()
    sys.exit(app.exec_())
