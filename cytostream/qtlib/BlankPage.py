import sys,os,time,re
from PyQt4 import QtGui, QtCore
from random import randint

class BlankPage(QtGui.QWidget):
    def __init__(self, parent, openBtnFn=None,closeBtnFn=None,rmBtnFn=None):
        QtGui.QWidget.__init__(self,parent)

        self.vbl = QtGui.QVBoxLayout()
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl1 = QtGui.QHBoxLayout()
        self.hbl1.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl1.addWidget(QtGui.QLabel('Loading...'))
        self.vbl.addLayout(self.hbl1)
        self.setLayout(self.vbl)


### Run the tests 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    bp = BlankPage()
    bp.show()
    sys.exit(app.exec_())
    
