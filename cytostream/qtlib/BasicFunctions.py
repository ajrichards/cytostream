#!/usr/bin/python
'''
Cytostream
BasicFunctions
functions without cytostream dependencies

'''

from PyQt4 import QtCore,QtGui

__author__ = "A Richards"


class BlankPage(QtGui.QWidget):
    def __init__(self, parent, openBtnFn=None,closeBtnFn=None,rmBtnFn=None):
        QtGui.QWidget.__init__(self,parent)

        self.vbl = QtGui.QVBoxLayout()
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl1 = QtGui.QHBoxLayout()
        self.hbl1.setAlignment(QtCore.Qt.AlignCenter)
        self.label = QtGui.QLabel('Loading...')
        self.hbl1.addWidget(self.label)
        self.vbl.addLayout(self.hbl1)
        self.setLayout(self.vbl)

    def change_label(self,newLabel):
        self.label.setText(newLabel)

def move_transition(mainWindow,repaint=False):
    mainWindow.mainWidget = QtGui.QWidget(mainWindow)
    bp = BlankPage(parent=mainWindow.mainWidget)
    mainWindow.bp = BlankPage(parent=mainWindow.mainWidget)
    vbl = QtGui.QVBoxLayout()
    vbl.setAlignment(QtCore.Qt.AlignCenter)
    hbl = QtGui.QHBoxLayout()
    hbl.setAlignment(QtCore.Qt.AlignCenter)
    hbl.addWidget(bp)
    vbl.addLayout(hbl)
    mainWindow.mainWidget.setLayout(vbl)
    mainWindow.refresh_main_widget()
    if repaint == True:
        QtCore.QCoreApplication.processEvents() 


### Run the tests 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    bp = BlankPage(None)
    bp.show()
    sys.exit(app.exec_())
