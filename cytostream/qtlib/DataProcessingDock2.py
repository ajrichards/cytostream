import sys
from PyQt4 import QtGui, QtCore
from BasicWidgets import RadioBtnWidget

class DataProcessingDock2(QtGui.QWidget):
    def __init__(self, callBackFn,  parent=None, default=None):
        QtGui.QWidget.__init__(self,parent)
        
        self.setWindowTitle('Data Processing')
        self.possibleActions = ['editor','channel select', 'transformation', 'compensation','add remove']

        ## setup alignment
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        
        ## setup widgets
        self.rbw = RadioBtnWidget(self.possibleActions,default=default,callBackFn=callBackFn)
        hbox1.addWidget(self.rbw)

        ## finalize layout
        vbox.addLayout(hbox1)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor('white'))
        self.setPalette(palette)

    def generic_callback(self):
        print 'callback fun'


    def disable_all(self):
        pass

    def enable_all(self):
        pass


### Run the tests                                                                                                                                                       
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    callBackFn = None
    dpc = DataProcessingDock2(callBackFn)
    dpc.show()
    sys.exit(app.exec_())
    
