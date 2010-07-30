import sys
from PyQt4 import QtGui, QtCore
from cytostream import ProgressBar

class ModelCenter(QtGui.QWidget):
    def __init__(self, parent=None, runModelFn=None):
        QtGui.QWidget.__init__(self,parent)

        ## variables
        ## setup layouts
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)

        hbl1 = QtGui.QHBoxLayout()
        hbl1.setAlignment(QtCore.Qt.AlignCenter)
        hbl1.addWidget(QtGui.QLabel('Run selected model'))

        self.progressBar = ProgressBar(parent=self)
        if runModelFn == None:
            runModelFn = self.generic_callback
        self.progressBar.set_callback(runModelFn)
        
        hbl2 = QtGui.QHBoxLayout()
        hbl2.setAlignment(QtCore.Qt.AlignCenter)
        hbl2.addWidget(self.progressBar)
        
        # finalize layout
        self.vbl.addLayout(hbl1)
        self.vbl.addLayout(hbl2)
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.vbl)


    def generic_callback(self):
        print 'This button does nothing'


    def set_message(self,msg):
        hbl = QtGui.QHBoxLayout()
        hbl.setAlignment(QtCore.Qt.AlignCenter)
        self.msg = QtGui.QLabel(msg)
        hbl.addWidget(self.msg)
        self.vbl.addLayout(hbl)

### Run the tests                                                                                                                                                                
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mc = ModelCenter()
    mc.show()
    sys.exit(app.exec_())
    
